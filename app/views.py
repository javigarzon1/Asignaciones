# app/views.py
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from .models import Consulta, Tipologia
from .services.assignment_service import assign_consultas_from_queryset

class UploadExcelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        f = request.FILES.get('file')
        if not f:
            return Response({"detail":"No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        # leer excel
        df = pd.read_excel(f)
        sensitive_cols = [c for c in df.columns if 'nif' in c.lower() or 'cuenta' in c.lower() or 'dni' in c.lower()]
        df = df.drop(columns=[c for c in sensitive_cols if c in df.columns], errors='ignore')

        created = []
        for _, row in df.iterrows():
            try:
                tip = None
                if 'Tipologia' in row and not pd.isna(row['Tipologia']):
                    tip, _ = Tipologia.objects.get_or_create(nombre=str(row['Tipologia']).strip())
                fecha_alta = pd.to_datetime(row.get('FECHA ALTA')) if 'FECHA ALTA' in row else timezone.now()
                fecha_fin = pd.to_datetime(row.get('FECHA FIN SLA')) if 'FECHA FIN SLA' in row else fecha_alta
                consulta = Consulta.objects.create(
                    ritm = str(row.get('RITM', '')).strip(),
                    nom_letrado = str(row.get('NOM LETRADO', '')).strip(),
                    tipologia = tip,
                    fecha_alta = fecha_alta,
                    fecha_fin_sla = fecha_fin,
                    urgente_sn = (str(row.get('URGENTE SN', 'no')).strip().lower() in ('si','sí','s','yes','true')),
                    ultima_actuacion = str(row.get('ULTIMA ACTUACION', '')).strip(),
                    datos_raw = row.to_dict()
                )
                created.append(consulta)
            except Exception as e:
                # loggear y continuar
                print("error creando consulta", e)
                continue

        # Lanzar asignación para las consultas nuevas (podemos filtrar por las creadas en esta subida)
        consultas_qs = Consulta.objects.filter(id__in=[c.id for c in created])
        assigned = assign_consultas_from_queryset(consultas_qs)

        return Response({"created": len(created), "assigned": len(assigned)})
