from typing import List

from minuta.models import Responsabilidad, Minuta, Asistente


class ResponsabilidadService:

    def crear(minuta:Minuta, responsables:List[Asistente], tarea:str, fecha:str) -> Responsabilidad:

        responsabilidad = Responsabilidad(minuta=minuta, tarea=tarea, fecha=fecha)
        responsabilidad.save()

        for responsable in responsables:
            responsabilidad.responsables.add(responsable)

        return responsabilidad
