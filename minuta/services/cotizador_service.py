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


def programadores_ajuste(mes):
    cursor = connection.cursor()
    cursor.execute('''
                SELECT 
                    minuta_programador.id, minuta_programador.nombre, minuta_programador.apellido,
                    CASE WHEN (SELECT SUM(minuta_movimiento.monto)
                                FROM minuta_movimiento
                                 where minuta_movimiento.programador_id = minuta_programador.id
                                  and minuta_movimiento.monto < 0 
                                  and cast(strftime('%%m', minuta_movimiento.fecha) as int) = %s ) is null
                                   then 0 
                                   else (SELECT SUM(minuta_movimiento.monto) 
                                        FROM minuta_movimiento 
                                        where minuta_movimiento.programador_id = minuta_programador.id
                                         and minuta_movimiento.monto < 0 
                                         and cast(strftime('%%m', minuta_movimiento.fecha) as int) = %s) 
                                          end as total_gastos,
                                          
                    CASE WHEN (select sum(minuta_hora.cantidad_horas)
                                from minuta_hora
                                 where minuta_hora.programador_id = minuta_programador.id
                                  and  cast(strftime('%%m', minuta_hora.fecha) as int) = %s ) is null 
                                  then 0 
                                  else (select sum(minuta_hora.cantidad_horas)
                                        from minuta_hora 
                                        where minuta_hora.programador_id = minuta_programador.id
                                          and  cast(strftime('%%m', minuta_hora.fecha) as int) = %s )
                                          end as total_horas_mes,
                                          
                    CASE WHEN (SELECT SUM(minuta_movimiento.monto)
                                FROM minuta_movimiento
                                 where minuta_movimiento.programador_id = minuta_programador.id
                                  and (%s - cast(strftime('%%m', minuta_movimiento.fecha) as int)) <= 3  
                                  and (%s - cast(strftime('%%m', minuta_movimiento.fecha) as int)) > 0) is null 
                                   then 0 
                                   else (SELECT SUM(minuta_movimiento.monto) 
                                        FROM minuta_movimiento 
                                        where minuta_movimiento.programador_id = minuta_programador.id
                                          and (%s - cast(strftime('%%m', minuta_movimiento.fecha) as int)) <= 3  
                                          and (%s - cast(strftime('%%m', minuta_movimiento.fecha) as int)) > 0) 
                                          end as total_ganancia_ajuste,                      
                                          
                    CASE WHEN (select sum(minuta_hora.cantidad_horas)
                                from minuta_hora
                                 where minuta_hora.programador_id = minuta_programador.id
                                  and (%s - cast(strftime('%%m', minuta_hora.fecha) as int)) <= 3  
                                  and (%s - cast(strftime('%%m', minuta_hora.fecha) as int)) > 0) is null 
                                  then 0 
                                  else (select sum(minuta_hora.cantidad_horas)
                                        from minuta_hora 
                                        where minuta_hora.programador_id = minuta_programador.id
                                          and (%s - cast(strftime('%%m', minuta_hora.fecha) as int)) <= 3  
                                          and (%s - cast(strftime('%%m', minuta_hora.fecha) as int)) > 0)
                                          end as total_horas_ajuste
                    from minuta_programador
                    where minuta_programador.es_socio = 1

        ''', [mes,mes,mes,mes,mes,mes,mes,mes,mes,mes,mes,mes])
    row = dictfetchall(cursor)
    return row


class Cotizador:

    def cotizarMes(fecha_desde, fecha_hasta):
        programadores = programadores_cotizacion(fecha_desde, fecha_hasta)
        ganancia = Movimiento.objects.filter(programador__es_socio=True, fecha__gte=fecha_desde, fecha__lte=fecha_hasta).aggregate(Sum('monto'))

        horas_totales = sum([pr['total_horas'] for pr in programadores])

        for programador in programadores:
            porcentaje = programador['total_horas'] / horas_totales
            cobro = ganancia['monto__sum'] * porcentaje
            total = ganancia['monto__sum'] * cobro + programador['total_gastos']
            programador.update({'porcentaje': porcentaje * 100, 'cobro': cobro, 'total':total})

        return programadores

    def cotizarAjuste(mes):
        programadores  = programadores_ajuste(mes)
        horas_totales = sum([pr['total_horas_ajuste'] for pr in programadores])
        ganancia_total = sum([pr['total_ganancia_ajuste'] for pr in programadores])

        for programador in programadores:
            porcentaje_horas = programador['total_horas_ajuste'] / horas_totales
            porcentaje_ganancia = programador['total_ganancia_ajuste'] / ganancia_total
            diferencia_porcentaje = porcentaje_ganancia - porcentaje_horas
            adicional = ganancia_total * diferencia_porcentaje
            programador.update({'porcentaje_horas_ajuste': porcentaje_horas})

        return programadores
        # cantidad total de horas del periodo
        # porcentaje que cada uno trabajo de esas horas
        # sumar el total de ganancia de los tres meses
        # calcular la ganancia total de cada uno durante los 3 meses
        # ver que porcentaje es eso de la total