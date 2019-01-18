from rest_framework import routers
from minuta.views import EmpresaViewSet, ProyectoViewSet, MinutaViewSet, AsistenteViewSet, TemaViewSet, DefinicionViewSet, ResponsabilidadViewSet, HoraViewSet, ProgramadorViewSet, MovimientoViewSet, CotizacionDelMes
from django.urls import path

router = routers.DefaultRouter()
router.register(r'empresas', EmpresaViewSet)
router.register(r'proyectos', ProyectoViewSet)
router.register(r'asistentes', AsistenteViewSet)
router.register(r'minutas', MinutaViewSet)
router.register(r'temas', TemaViewSet)
router.register(r'definiciones', DefinicionViewSet)
router.register(r'programadores', ProgramadorViewSet)
router.register(r'responsabilidades', ResponsabilidadViewSet)
router.register(r'horas', HoraViewSet)
router.register(r'movimientos', MovimientoViewSet)

urlpatterns = [
    path('cotizacion/', CotizacionDelMes.as_view(), name='cotizacion_del_mes')
]

urlpatterns += router.urls