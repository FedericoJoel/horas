from django.db import models


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
        return self.apellido


class Proyecto(models.Model):
    nombre = models.CharField(max_length=50)
    empresa = models.ForeignKey(Empresa, related_name='proyectos', on_delete=models.CASCADE)
    horas_presupuestada = models.IntegerField()
    fecha_limite = models.DateField(null=True, blank=True)
    programadores = models.ManyToManyField(Programador)

    def __str__(self):
        return self.nombre


class Movimiento(models.Model):
    concepto = models.CharField(max_length=200)
    programador = models.ForeignKey(Programador, related_name='movimientos', on_delete=models.CASCADE)
    monto = models.FloatField()
    descripcion = models.TextField()
    fecha = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.concepto


class Hora(models.Model):
    cantidad_horas = models.IntegerField()
    fecha = models.DateField(null=True, blank=True)
    programador = models.ForeignKey(Programador, related_name="horas", on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, related_name="horas", on_delete=models.CASCADE)
    descripcion = models.TextField()

    def __str__(self):
        return self.descripcion


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


