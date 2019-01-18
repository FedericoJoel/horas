from django import forms
from django.contrib import admin
from .models import Empresa, Proyecto, Minuta, Asistente, Tema, Responsabilidad, Definicion

admin.site.register(Empresa)
admin.site.register(Proyecto)


class DefinicionInLine(admin.StackedInline):
        model = Definicion


class TemaAdmin(admin.ModelAdmin):
    model = Tema
    inlines = [DefinicionInLine]


class MinutaAdmin(admin.ModelAdmin):
    model = Minuta
    list_display = ('motivo', 'fecha', 'proyecto', 'descripcion', 'asistentes_display', 'temas')
    search_fields = ['motivo']

    def asistentes_display(self, obj):
        s = ' '.join(asistente.nombre.capitalize() +' '+ asistente.apellido.capitalize() +',' for asistente in obj.asistentes.all())
        return s[0: len(s)-1]

    asistentes_display.short_description = 'ASISTENTES'

    def temas(self, obj):
        s = ' '.join(tema.titulo.capitalize() + ',' for tema in Tema.objects.all().filter(minuta = obj))
        return s[0: len(s)-1]


admin.site.register(Minuta, MinutaAdmin)
admin.site.register(Asistente)
admin.site.register(Tema, TemaAdmin)
admin.site.register(Responsabilidad)
admin.site.register(Definicion)
