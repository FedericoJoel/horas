from rest_framework import viewsets
from .models import Empresa, Proyecto, Asistente, Minuta, Tema, Definicion, Responsabilidad, Programador, Hora, Movimiento, Ticket
from .serializers import EmpresaSerializer, ProyectoSerializer, AsistenteSerializer, MinutaSerializer, TemaSerializer, DefinicionSerializer, ResponsabilidadSerializer, ProgramadorSerializer, HoraSerializer, MovimientoSerializer, TicketSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from minuta.services.minuta_service import MinutaService
from rest_framework.views import APIView
from minuta.services.cotizador_service import Cotizador
from rest_framework.permissions import IsAuthenticated



class TicketViewset(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer


class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer


class ProgramadorViewSet(viewsets.ModelViewSet):
    queryset = Programador.objects.all()
    serializer_class = ProgramadorSerializer


class HoraViewSet(viewsets.ModelViewSet):
    queryset = Hora.objects.all()
    serializer_class = HoraSerializer


class ResponsabilidadViewSet(viewsets.ModelViewSet):
    queryset = Responsabilidad.objects.all()
    serializer_class = ResponsabilidadSerializer


class AsistenteViewSet(viewsets.ModelViewSet):
    queryset = Asistente.objects.all()
    serializer_class = AsistenteSerializer


class MinutaViewSet(viewsets.ModelViewSet):
    queryset = Minuta.objects.all()
    serializer_class = MinutaSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        proyecto = Proyecto.objects.filter(id=request.data.get('proyecto')).first()
        asistentes = list(Asistente.objects.filter(pk__in=request.data.get('asistentes')))

        for responsabilidad in request.data.get('responsabilidades'):
            responsables = list(Asistente.objects.filter(pk__in=responsabilidad['responsables']))
            responsabilidad.update({'responsables': responsables})

        request.data.update({'proyecto': proyecto, 'asistentes':asistentes})

        minuta = MinutaService.crear(**request.data)
        headers = self.get_success_headers(minuta.id)
        return Response(minuta.id, status=status.HTTP_201_CREATED, headers=headers)


class TemaViewSet(viewsets.ModelViewSet):
    queryset = Tema.objects.all()
    serializer_class = TemaSerializer


class DefinicionViewSet(viewsets.ModelViewSet):
    queryset = Definicion.objects.all()
    serializer_class = DefinicionSerializer


class MovimientoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Movimiento.objects.all()
    serializer_class = MovimientoSerializer


class CotizacionDelMes(APIView):

    def get(self, request):
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        cotizacion = Cotizador.cotizarMes(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
        return Response(cotizacion)


class CotizacionAjuste(APIView):

    def get(self, request):
        mes = request.query_params.get('mes')
        return Response(Cotizador.cotizarAjuste(mes))
