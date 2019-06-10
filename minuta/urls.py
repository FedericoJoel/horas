from rest_framework import routers
from minuta.views import EmpresaViewSet, ProyectoViewSet, MinutaViewSet, AsistenteViewSet, TemaViewSet, DefinicionViewSet, ResponsabilidadViewSet, HoraViewSet, ProgramadorViewSet, MovimientoViewSet, CotizacionDelMes, CotizacionAjuste
from django.urls import path
from rest_framework_simplejwt import views as jwt_views


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
    path('cotizacion/', CotizacionDelMes.as_view(), name='cotizacion_del_mes'),
    path('cotizacion/con_ajuste/', CotizacionAjuste.as_view(), name='cotizacion_con_ajuste'),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh')
]

urlpatterns += router.urls