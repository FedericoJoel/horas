from django import template

register = template.Library()

@register.filter(name='definicion_de_tema')
def definicion_de_tema(definiciones, id):
    return list(filter(lambda definicion: definicion.tema_id == id, definiciones))