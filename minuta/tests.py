from django.test import TestCase
from minuta.services.cotizador_service import Cotizador
# Create your tests here.
from .models import Minuta

class AnimalTestCase(TestCase):

    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        cotizador = Cotizador
        cotizador.cotizarMes()


