from django.db import models
import datetime
from django.utils import timezone


class Empresa(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Programador(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    mail = models.EmailField(null=True, blank=True)
    es_socio = models.BooleanField(default=True)

    def __str__(self):
        return  self.nombre + ' ' + self.apellido


class Proyecto(models.Model):
    nombre = models.CharField(max_length=50)
    empresa = models.ForeignKey(Empresa, related_name='proyectos', on_delete=models.CASCADE)
    horas = models.IntegerField()
    fecha_limite = models.DateField(null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    programadores = models.ManyToManyField(Programador)
    responsable = models.ForeignKey(Programador, related_name='proyectos', on_delete=models.CASCADE)
    pago = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre


class Movimiento(models.Model):
    TYPES = (
        ('C', 'Cobro'),
        ('P', 'Pago'),
    )
    concepto = models.CharField(max_length=200)
    programador = models.ForeignKey(Programador, related_name='movimientos', on_delete=models.CASCADE)
    monto = models.FloatField()
    descripcion = models.TextField()
    fecha = models.DateField(null=True, blank=True)
    proyecto = models.ForeignKey(Proyecto, related_name="movimientos", on_delete=models.CASCADE)
    tipo = models.CharField(choices=TYPES, max_length=1, default='C')

    def __str__(self):
        return self.concepto

class Ticket(models.Model):
    PRIORITIES = (
        ('C', 'Critico'),
        ('A', 'Alto'),
        ('M', 'Medio'),
        ('B', 'Bajo'),
    )

    STATUS = (
        ('P', 'Pendiente'),
        ('E', 'En progreso'),
        ('B', 'Bloqueado'),
        ('R', 'Resuelto'),
        ('C', 'Cerrado'),
    )

    TIPOS = (
        ('A', 'Agregado'),
        ('M', 'Modificacion'),
        ('E', 'Error'),
        ('O', 'Otro'),
    )

    titulo = models.TextField()
    descripcion = models.TextField()
    prioridad = models.CharField(choices=PRIORITIES, max_length=1, default='M')
    status = models.CharField(choices=STATUS, max_length=1, default='P')
    proyecto = models.ForeignKey(Proyecto, related_name="tickets", on_delete=models.CASCADE)
    fecha_apertura = models.DateTimeField(default=timezone.now)
    fecha_estimada = models.DateTimeField(null=True, blank=True)
    tipo = models.CharField(choices=TIPOS, max_length=1, default='O')

    def __str__(self):
        return  self.titulo

class Hora(models.Model):
    cantidad_horas = models.IntegerField()
    fecha = models.DateField(null=True, blank=True)
    ticket = models.ForeignKey(Ticket, related_name="horas_aplicadas", on_delete=models.CASCADE)
    programador = models.ForeignKey(Programador, related_name="horas_aplicadas", on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, related_name="horas_aplicadas", on_delete=models.CASCADE)
    descripcion = models.TextField()

    def __str__(self):
        return self.descripcion

class Respuesta(models.Model):
    fecha = models.DateTimeField(null=True, blank=True)
    texto = models.TextField()
    ticket = models.ForeignKey(Ticket, related_name="respuestas", on_delete=models.CASCADE)

    def __str__(self):
        return self.texto

class Asistente(models.Model):
    empresa = models.ForeignKey(Empresa, related_name='empleados', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    mail = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class Minuta(models.Model):
    fecha = models.DateField(null=True, blank=True)
    proyecto = models.ForeignKey(Proyecto, related_name='minutas', on_delete=models.CASCADE)
    motivo = models.CharField(max_length=100)
    descripcion = models.TextField()
    asistentes = models.ManyToManyField(Asistente)

    def __str__(self):
        return self.motivo


class Responsabilidad(models.Model):
    responsables = models.ManyToManyField(Asistente)
    tarea = models.TextField()
    fecha = models.DateField(null=True, blank=True)
    minuta = models.ForeignKey(Minuta, related_name='responsabilidades', on_delete=models.CASCADE)

    def __str__(self):
        return self.tarea


class Tema(models.Model):
    titulo = models.CharField(max_length=50)
    minuta = models.ForeignKey(Minuta, related_name='temas', on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo


class Definicion(models.Model):
    texto = models.TextField()
    tema = models.ForeignKey(Tema, related_name='definiciones', on_delete=models.CASCADE)

    def __str__(self):
        return self.texto


