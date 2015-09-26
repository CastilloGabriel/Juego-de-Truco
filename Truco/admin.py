from django.contrib import admin
from Truco.models import Partida, Carta, Jugador #Agregar modelos para ver su comportamiento desde el /admin


# Register your models here.
admin.site.register(Partida)	#Incluye el modelo Partida en el admin
admin.site.register(Carta)		#Incluye el modelo Carta en el admin
admin.site.register(Jugador)	#Incluye el modelo Jugador en el admin