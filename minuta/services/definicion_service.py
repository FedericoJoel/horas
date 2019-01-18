from minuta.models import Definicion, Tema


class DefinicionService:

    def crear(tema:Tema, texto:str) -> Definicion:

        definicion = Definicion(tema=tema, texto=texto)
        definicion.save()
        return definicion