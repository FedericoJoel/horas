from typing import List
from minuta.models import Minuta, Proyecto, Asistente
from minuta.services.tema_service import TemaService
from minuta.services.responsabilidad_service import ResponsabilidadService
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def enviar_mail(minuta: Minuta):

    temas = []
    for tema in minuta.temas.all():
        definiciones = []
        for definicion in tema.definiciones.all():
            definiciones.append(definicion)
        temas.append({'tema': tema, 'definiciones': definiciones})

    responsabilidades = []
    for responsabilidad in minuta.responsabilidades.all():
        responsables = []
        for responsable in responsabilidad.responsables.all():
            responsables.append(responsable)
        responsabilidades.append({'responsabilidad': responsabilidad, 'responsables': responsables})

    html_message = render_to_string('minuta_email.html', {'motivo':minuta.motivo, 'descripcion':minuta.descripcion, 'asistentes': minuta.asistentes.all(), 'temas': temas, 'responsabilidades':responsabilidades})
    plain_message = strip_tags(html_message)

    send_mail(
        'Minuta: ' + minuta.motivo,
        plain_message,
        'joaquinmazoud@gmail.com',
        ['joaquinmazoud@gmail.com'],
        html_message=html_message,
        fail_silently=False,
    )


class MinutaService:

    def crear(fecha:str, motivo:str, asistentes:List[Asistente], proyecto:Proyecto, descripcion:str, temas, responsabilidades) -> Minuta:

        minuta = Minuta(fecha=fecha, motivo=motivo, proyecto=proyecto, descripcion=descripcion)
        minuta.save()
        for asistente in asistentes:
            minuta.asistentes.add(asistente)

        for tema in temas:
            TemaService.crear(minuta=minuta, **tema)

        for responsabilidad in responsabilidades:
            ResponsabilidadService.crear(minuta=minuta, **responsabilidad)

        enviar_mail(minuta=minuta)
        return minuta


