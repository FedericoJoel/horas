from functools import reduce

from minuta.models import Movimiento, Hora,Programador
from django.db.models import Sum, OuterRef, Subquery, FloatField, Case, When
from django.db import connection


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def programadores_cotizacion(fecha_desde, fecha_hasta):
    cursor = connection.cursor()
    cursor.execute('''
                SELECT 
                    minuta_programador.id, minuta_programador.nombre, minuta_programador.apellido,
                    CASE WHEN (SELECT SUM(minuta_movimiento.monto) FROM minuta_movimiento where minuta_movimiento.programador_id = minuta_programador.id and minuta_movimiento.monto < 0 and minuta_movimiento.fecha >= %s and minuta_movimiento.fecha <= %s) is null then 0 else (SELECT SUM(minuta_movimiento.monto) FROM minuta_movimiento where minuta_movimiento.programador_id = minuta_programador.id and minuta_movimiento.monto < 0 and minuta_movimiento.fecha >= %s and minuta_movimiento.fecha <= %s) end as total_gastos,
                    CASE WHEN (select sum(minuta_hora.cantidad_horas) from minuta_hora where minuta_hora.programador_id = minuta_programador.id and minuta_hora.fecha >= %s and minuta_hora.fecha <= %s) is null then 0 else (select sum(minuta_hora.cantidad_horas) from minuta_hora where minuta_hora.programador_id = minuta_programador.id and minuta_hora.fecha >= %s and minuta_hora.fecha <= %s) end as total_horas
                    from minuta_programador
                    where minuta_programador.es_socio = 1
        
        ''',[fecha_desde,fecha_hasta,fecha_desde,fecha_hasta,fecha_desde,fecha_hasta,fecha_desde,fecha_hasta])
    row = dictfetchall(cursor)
    return row


class Cotizador:

    def cotizarMes(fecha_desde, fecha_hasta):
        programadores = programadores_cotizacion(fecha_desde, fecha_hasta)
        ganancia = Movimiento.objects.filter(programador__es_socio=True).aggregate(Sum('monto'))

        horas_totales = sum([pr['total_horas'] for pr in programadores])

        for programador in programadores:
            porcentaje = programador['total_horas'] / horas_totales
            cobro = ganancia['monto__sum'] * porcentaje
            total = ganancia['monto__sum'] * cobro + programador['total_gastos']
            programador.update({'porcentaje': porcentaje * 100, 'cobro': cobro, 'total':total})

        return programadores