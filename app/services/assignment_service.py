from collections import defaultdict
from decimal import Decimal
from django.utils import timezone
from .models import Letrado, Consulta, Assignment, Tipologia
import math

def assign_consultas_from_queryset(consultas_qs):
    """
    Asigna todas las consultas del queryset. Devuelve lista de Assignment objects creados.
    """
    # 1) Lista de consultas nuevas a asignar (filtrar por es_nueva())
    consultas = [c for c in consultas_qs if c.es_nueva()]
    assigned_objs = []

    # 2) cargar letrados activos que no estén a 0%
    letrados = list(Letrado.objects.filter(activo=True).exclude(porcentaje__lte=0))
    if not letrados:
        raise Exception("No hay letrados activos con porcentaje > 0.")

    # 3) Agrupar por tipología para filtrar candidatos por consulta
    tip_map = defaultdict(list)
    for l in letrados:
        for t in l.tipologias.all():
            tip_map[t.id].append(l)

    # 4) Pre-cálculo de porcentajes efectivos por día (sum sobre candidatos por consulta)
    total_porcentaje = sum([float(l.porcentaje) for l in letrados])

    # 5) Contador actual por letrado (hoy) — se puede rellenar desde DB si se guarda el contador diario
    today = timezone.localdate()
    assigned_today = defaultdict(int)
    from django.db.models import Count
    counts = Assignment.objects.filter(asignado_en__date=today).values('letrado').annotate(c=Count('id'))
    for row in counts:
        assigned_today[row['letrado']] = row['c']

    # 6) Greedy: para cada consulta, elegir candidato con menor (assigned_today / target_share)
    for c in consultas:
        candidatos = []
        # Si nom_letrado pertenece a nuestro equipo y está activo -> asignar directamente
        if c.nom_letrado:
            try:
                direct = Letrado.objects.get(nombre__iexact=c.nom_letrado.strip())
                if direct.activo and float(direct.porcentaje) > 0:
                    a = Assignment.objects.create(consulta=c, letrado=direct)
                    assigned_objs.append(a)
                    assigned_today[direct.id] += 1
                    continue
            except Letrado.DoesNotExist:
                pass

        # Filtrar candidatos por tipología
        if c.tipologia_id and c.tipologia_id in tip_map:
            candidatos = tip_map[c.tipologia_id].copy()
        else:
            # si la consulta no tiene tipologia o tipologia no mapeada -> candidatos = todos
            candidatos = letrados.copy()

        # si urgente -> filtrar por acepta_urgentes
        if c.urgente_sn:
            candidatos = [l for l in candidatos if l.acepta_urgentes]

        # Si quedaron 0 candidatos -> fallback a todos que acepten urgentes si urgente, else a todos activos
        if not candidatos:
            candidatos = [l for l in letrados if (l.acepta_urgentes if c.urgente_sn else True)]
            if not candidatos:
                candidatos = letrados.copy()

        # Calcular target_share individual (proporción de total_porcentaje)
        # target_perc = l.porcentaje / total_porcentaje
        # objetivo absoluto = total_remaining_consultas * target_perc  -> aproximación
        # Usamos ratio = assigned_today / target_perc  y elegimos menor ratio
        ratios = []
        for l in candidatos:
            perc = float(l.porcentaje)
            target_share = (perc / total_porcentaje) if total_porcentaje>0 else 1/len(candidatos)
            current = assigned_today.get(l.id, 0)
            # evitar division por 0
            ratio = current / (target_share if target_share>0 else 1)
            ratios.append((ratio, l))
        # elegir el candidato con ratio mínimo (menos servido respecto a su cuota)
        ratios.sort(key=lambda x: (x[0], -float(x[1].porcentaje)))
        chosen = ratios[0][1]
        a = Assignment.objects.create(consulta=c, letrado=chosen)
        assigned_objs.append(a)
        assigned_today[chosen.id] = assigned_today.get(chosen.id, 0) + 1

    return assigned_objs
