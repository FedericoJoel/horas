from rest_framework import serializers

from .models import Empresa, Proyecto, Asistente, Minuta, Tema, Definicion, Responsabilidad, Programador, Hora, Movimiento


class EmpresaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Empresa
        fields = '__all__'


class ProgramadorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Programador
        fields = ('id', 'nombre', 'apellido', 'mail', 'es_socio')


class HoraSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hora
        fields = ('id', 'programador', 'proyecto', 'cantidad_horas', 'descripcion', 'fecha')


class ProyectoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proyecto
        fields = '__all__'


class AsistenteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Asistente
        fields = ('id', 'empresa', 'nombre', 'apellido', 'mail')


class DefinicionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Definicion
        fields = ('id', 'tema', 'texto')


class TemaSerializer(serializers.ModelSerializer):
    definiciones = DefinicionSerializer(many=True, read_only=True)

    class Meta:
        model = Tema
        fields = ('id', 'minuta', 'titulo', 'definiciones')

        
class MinutaSerializer(serializers.ModelSerializer):
    temas = TemaSerializer(many=True, read_only=True)
    asistentes_detalle = serializers.SerializerMethodField()

    def get_asistentes_detalle(self, obj):
        asis = Minuta.objects.get(id=obj.id).asistentes.all()
        ser = AsistenteSerializer(asis, many=True)
        return ser.data

    class Meta:
        model = Minuta
        fields = ('id', 'fecha', 'proyecto', 'motivo', 'descripcion', 'asistentes', 'temas', 'asistentes_detalle')


class ResponsabilidadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Responsabilidad
        fields = ('id', 'minuta', 'fecha', 'tarea', 'responsables')


class MovimientoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Movimiento
        fields = ('id', 'concepto', 'monto', 'programador', 'descripcion')