from minuta.models import Tema, Minuta
from minuta.services.definicion_service import DefinicionService


class TemaService:

    def crear(minuta:Minuta, titulo:str, definiciones) -> Tema:
        tema =Tema(titulo=titulo, minuta=minuta)
        tema.save()

        for definicion in definiciones:
            DefinicionService.crear(tema=tema, **definicion)

        return tema