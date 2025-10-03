# app/models.py
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

class Tipologia(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)

    def __str__(self): return self.nombre

class Letrado(models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    acepta_urgentes = models.BooleanField(default=False)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)  # 0-100
    horario = models.JSONField(null=True, blank=True)  # ejemplo: {"lun":["09:00","19:00"], ...}
    activo = models.BooleanField(default=True)  # si de vacaciones => false
    max_consultas_coordinador = models.IntegerField(default=10)  # ej. Rocío
    tipologias = models.ManyToManyField(Tipologia, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    asignadas = models.IntegerField(default=0)  # para estadísticas
    finalizadas = models.IntegerField(default=0)  # para estadísticas
    


    def __str__(self): return self.nombre

class Consulta(models.Model):
    ritm = models.CharField(max_length=100, unique=True)  # número de consulta
    nom_letrado = models.CharField(max_length=200, null=True, blank=True)  # nombre desde Excel
    tipologia = models.ForeignKey(Tipologia, null=True, on_delete=models.SET_NULL)
    fecha_alta = models.DateTimeField()
    fecha_fin_sla = models.DateTimeField()
    urgente_sn = models.BooleanField(default=False)
    ultima_actuacion = models.CharField(max_length=200, null=True, blank=True)  # para reglas
    datos_raw = models.JSONField(null=True, blank=True)  # para cualquier otra columna
    creada_en = models.DateTimeField(auto_now_add=True)

    def es_nueva(self):
        if self.nom_letrado and self.nom_letrado.strip() and self.nom_letrado.lower() != "sin asignar":
            # si tiene nom_letrado y es de nuestro equipo -> no nueva salvo regla
            return False
        if self.ultima_actuacion and self.ultima_actuacion.lower() in ("respuesta de oficina", "discrepancia oficina"):
            return False
        return True

class Assignment(models.Model):
    consulta = models.OneToOneField(Consulta, on_delete=models.CASCADE)
    letrado = models.ForeignKey(Letrado, on_delete=models.PROTECT)
    asignado_en = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, default="En proceso")
    revisado = models.BooleanField(default=False)
    comentarios = models.TextField(null=True, blank=True)
    historial = models.JSONField(default=list)  # para guardar cambios de estado, etc.
    prioridad = models.IntegerField(default=0)  # para ordenación manual
    fecha_limite = models.DateTimeField(null=True, blank=True)  # para seguimiento
    notificaciones_enviadas = ArrayField(models.DateTimeField(), default=list)  # fechas de notificaciones enviadas
    ultima_notificacion = models.DateTimeField(null=True, blank=True)  # para evitar spam
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)
    finalizada_en = models.DateTimeField(null=True, blank=True)    
    datos_extra = models.JSONField(null=True, blank=True)  # para cualquier otro dato adicional
    asignada_por = models.CharField(max_length=200, null=True, blank=True)  # nombre del coordinador que asignó
    reasignacion = models.TextField(null=True, blank=True)  # motivo de reasignación si aplica
    prioridad_urgente = models.BooleanField(default=False)  # si es urgente y debe priorizarse
    coste_real = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)    

