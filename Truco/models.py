#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from constants import *
from exep import PartidaLlena
import random

    
    
    

# Funciones auxiliares:

# Son las se~nas del truco.
# Se definen en constants.py las constantes, ellas son:
# MACHO = 7
# HEMBRA = 6
# SIETE_ESPADA = 5
# SIETE_ORO = 4
# TRES = 3
# DOS = 2
# UNO = 1
# NO_SEN = 0 >>> Son las cartas sin se~nas.
def sen(x, y):
    if x == 1:
        if y == ESPADA:
            return MACHO        # Este es el 1 de espada.
        elif y == BASTO:
            return HEMBRA       # Este es el 1 de basto.
        else:
            return UNO          # Este es el 1 de copa u oro.
    if x == 7:
        if y == ESPADA:
            return SIETE_ESPADA # Este es el 7 de espada.
        elif y == ORO:
            return SIETE_ORO    # Este es el 7 de oro.
        else:
            return NO_SEN       # Estas son las cartas sin senias.
    if x == 3:
        return TRES             # Estos son los 3 de espada, oro, copa y basto.
    if x == 2:
        return DOS              # Estos son los 2 de espada, oro, copa y basto.
    else:
        return NO_SEN           # Mas cartas sin senias.


# Devuelve un mazo de 40 cartas, contieniendo el rango de {1...7} U {10...12}
# de cada palo.
def get_mazo():
    cartas = range(1,8) + range(10, 13)
    mazo = []
    for p in [ESPADA, BASTO, COPA, ORO]:
        for i in cartas:
            c = (i, p)
            mazo.append(c)
    return mazo

#Aca tenemos una lista de los palos que se jugaran en este truco.
palos = ['espada', 'basto', 'copa', 'oro']


# Suma los puntos correspondientes al envido y al truco de ambos jugadores
# al llegar a la tecera ronda.


# Dado una lista de 1, 2 o 3 cartas, devuelve la suma de ellas para realizar el
# envido.
def sumar_cartas(cartas):
    # Controlar que este funcionando bien. Seria buena idea hacer un testcase para
    # Partida.tantos() y uno para este.
    cartas = cartas.order_by('-valor')
    suma = 0
    if len(cartas) != 0:
        if len(cartas) == 1:
            if cartas[0].valor <= 7:
                suma = cartas[0].valor
        elif len(cartas) == 2:
            if cartas[0].valor <= 7:
                suma = cartas[0].valor + cartas[1].valor + 20
            elif cartas[1].valor <= 7:
                suma = cartas[1].valor + 20
            else:
                suma = 20
        else:
            if cartas[0].valor <= 7:
                suma = cartas[0].valor + cartas[1].valor + 20
            elif cartas[1].valor <= 7:
                suma = cartas[1].valor + cartas[2].valor + 20
            elif cartas[2].valor <= 7:
                suma = cartas[2].valor + 20
            else:
                suma = 20
    return suma

# Fin funciones auxiliares.


class Carta(models.Model):
    valor = models.IntegerField(default=0)              # El valor varia de 1 a 7 y de 10 a 12.
    palo = models.IntegerField(default=0)               # Los palos son: espada, basto, copa, oro.
    rank = models.IntegerField(default=0)               # Si es una carta de valor, ve el ranking.
    jugada = models.IntegerField(default=0)             # Contiene las cartas jugadas.
    gid = models.ForeignKey('Partida', null=True)       # Game ID.
    jid = models.ForeignKey('Jugador', null=True)       # Jugador ID.

    objects = models.Manager()

    # Las siguientes definiciones sirven para hacer las comparaciones de las
    # cartas, es decir, si tengo 2 cartas (carta_1,carta_2) se pueden realizar
    # los metodos:
    #   carta_1 < carta_2
    #   carta_1 <= carta_2
    #   carta_1 > carta_2
    #   carta_1 >= carta_2
    #   carta_1 = carta_2
    #   carta_1 != carta_2

    def __lt__(self, y):
        if self.rank != y.rank:
            return self.rank < y.rank
        else:
            return self.valor < y.valor

    def __le__(self, y):
        if self.rank != y.rank:
            return self.rank <= y.rank
        else:
            return self.valor <= y.valor

    def __eq__(self, y):
        if self.rank != y.rank:
            return self.rank == y.rank
        else:
            return self.valor == y.valor

    def __gt__(self, y):
        if self.rank != y.rank:
            return self.rank > y.rank
        else:
            return self.valor > y.valor

    def __ge__(self, y):
        if self.rank != y.rank:
            return self.rank >= y.rank
        else:
            return self.valor >= y.valor

    def __ne__(self, y):
        if self.rank != y.rank:
            return self.rank != y.rank
        else:
            return self.valor != y.valor

    # Devuelve el nombre de un archivo .jpeg que contiene la imagen de la carta
    # para ser mostrada.
    def img_name(self):
        return '{0}_{1}.jpeg'.format(self.valor, palos[self.palo])

    # Devuelve el nombre de un archivo que contiene la imagen de la carta sin
    # la extension del mismo.
    def repr_carta(self):
        return '{0}_{1}'.format(self.valor, self.palo)


class Partida(models.Model):
    creador = models.CharField(max_length=32)           # Nombre del creador de la partida.
    numero_de_jugadores = models.IntegerField(default=0)# Cantidad de jugadores que habra en la partida.
    puntos_a_jugar = models.IntegerField(default=15)    # Es 15 o 30 dependiendo de la eleccion del creador.
    ronda = models.IntegerField(default=1)              # Varia de 1 a 3 dependiendo de la ronda en la que se encuentre.
    turno = models.IntegerField(default=1)              # Varia de 1 a 2 dependiendo de a quien le toque.
    j_es_mano = models.IntegerField(default=1)          # Contiene el jugador que es mano en ese momento.
    pausa = models.BooleanField(default=False)          # Nos dice si hay que esperar alguna respuesta.
    ganadores = models.CharField(default="", max_length=3, null=True) # Contiene el equipo ganador de cada ronda. 0 si hay empate

    def ganador_ronda(self):
        """
        Actualiza en self.ganador_ronda el equipo ganador de la ronda:
        '0' -> Empate.
        '1' -> Equipo 1 Gano.
        '2' -> Equipo 2 Gano.
        Actualiza el turno como asi tambien la ronda a jugar.
        Retorna True si ya se pudo establecer el ganador de la ronda.
        Retorna False si aun no se puede establecer el ganador de la ronda.
        """
        if Carta.objects.filter(gid=self, jugada=self.ronda).count() == self.numero_de_jugadores:
            cartas_equipo1 = Carta.objects.filter(gid=self, jugada=self.ronda,
                                              jid__tid__nro_equipo = 1)
            cartas_equipo2 = Carta.objects.filter(gid=self, jugada=self.ronda,
                                              jid__tid__nro_equipo = 2)
            carta_equipo1 = max(cartas_equipo1)
            carta_equipo2 = max(cartas_equipo2)

            if carta_equipo1 == carta_equipo2:
                self.ganadores += "0"
                nro_jugador = carta_equipo1.jid.nro_jugador
            elif carta_equipo1 < carta_equipo2:
                nro_jugador = carta_equipo2.jid.nro_jugador
                self.ganadores += "2"
            else:
                nro_jugador = carta_equipo1.jid.nro_jugador
                self.ganadores += "1"
            self.turno = nro_jugador
            self.save()
            return True
        else:
            return False


    def ganador_mano(self):
        """
        Retorna el equipo ganador de la mano.
        None si faltan rondas por jugar.
        """
        ganador = None
        if len(self.ganadores) >= 2:
            empates = self.ganadores.count("0")
            equipo1 = self.ganadores.count("1")
            equipo2 = self.ganadores.count("2")
            if empates == 2 and len(self.ganadores) == 2:
                return None
            elif empates == 3:
                ganador = self.equipo_set.get(gid=self, es_mano=True)
            elif equipo2 < equipo1:
                ganador = self.equipo_set.get(gid=self, nro_equipo=1)
            elif equipo1 < equipo2:
                ganador = self.equipo_set.get(gid=self, nro_equipo=2)
            elif empates == 1 and len(self.ganadores) == 3:
                ganador = self.equipo_set.get(gid=self, nro_equipo=int(self.ganadores[0]))
            else:
                return None
            ganador.puntaje += self.cantos.estado_truco + 1
            ganador.save()
        return ganador


    def av_turno(self):
        """
        Solamente avanza de turno, cuando llega al maximo numero de jugador
        le devuelve el turno al primero.
        No setea el primer turno de las rondas.
        """
        pos = self.turno + 1
        self.turno = pos % (self.numero_de_jugadores+1)
        if self.turno == 0:
            self.turno += 1
        self.save()

    def cambiar_mano(self):
        """
        Setea al siguiente jugador mano de las 3 rondas a jugar.
        Resetea los cantos para las siguientes rondas.
        Tambien Setea el nuevo pie de cada equipo.
        Reparte ahora también las cartas.
        """
        equipo1 = self.equipo_set.get(gid=self, nro_equipo=1)
        equipo2 = self.equipo_set.get(gid=self, nro_equipo=2)

        self.cantos.resetear_cantos()
        mano_otro_equipo = self.j_es_mano
        self.j_es_mano += 1
        if self.numero_de_jugadores == 2 and self.j_es_mano == 3:
            self.j_es_mano = 1
        elif self.numero_de_jugadores == 4 and self.j_es_mano == 5:
            self.j_es_mano = 1
        elif self.numero_de_jugadores == 6 and self.j_es_mano == 7:
            self.j_es_mano = 1
        if equipo1.es_mano:
            equipo1.es_mano = False
            equipo2.es_mano = True
        else:
            equipo2.es_mano = False
            equipo1.es_mano = True
        equipo1.av_pie()
        equipo2.av_pie()
        equipo1.save()
        equipo2.save()
        self.save()
        self.repartir()

    def av_ronda(self):
        """
        Setea la siguiente ronda.
        """
        print "Se termino la ronda: %d" % self.ronda
        self.ronda += 1
        self.save()

    def turno_equipo(self):
        """
        Devuelve el numero del equipo que tiene
        el turno.
        """
        if self.turno % 2:
            return 1
        else:
            return 2


    def agregar_jugador(self, user):
        """
        Agrega al usuario al equipo correspondiente.
        Retorna el jugador creado.
        """
        cant_jugadores_partida = self.cant_jugadores_en_partida()
        equipo1 = self.equipo_set.get(gid=self, nro_equipo=1)
        equipo2 = self.equipo_set.get(gid=self, nro_equipo=2)
        nro_jugadores_equipo1 = equipo1.jugador_set.count()
        nro_jugadores_equipo2 = equipo2.jugador_set.count()
        if cant_jugadores_partida < self.numero_de_jugadores:
            # Vemos si agregarlo al equipo 1.
            if nro_jugadores_equipo1 <= nro_jugadores_equipo2:
                cant_jugadores_partida += 1
                jugador = Jugador(usuario=user, tid=equipo1, nro_jugador=cant_jugadores_partida)
                jugador.save()
            # Sino, lo agregamos al equipo 2.
            else:
                cant_jugadores_partida += 1
                jugador = Jugador(usuario=user, tid=equipo2, nro_jugador=cant_jugadores_partida)
                jugador.save()
            if cant_jugadores_partida == self.numero_de_jugadores:
                self.repartir()
            self.save()
            return jugador
        else:
            raise PartidaLlena #acordarse de hacer un try except para esto.

    def repartir(self):
        """
        Reparte de manera aleatoria las cartas y lo guarda en la base de datos.
        """
        self.limpiar_mazo()
        equipos = Equipo.objects.filter(gid=self)
        cartas = random.sample(get_mazo(), self.numero_de_jugadores*3)
        for e in equipos:
            players = e.jugador_set.all()
            for p in players:
                for i in range(0, 3):
                    val, pal= cartas.pop()
                    c = Carta(valor=val, palo=pal, rank=sen(val,pal), jid=p,
                              gid=self)
                    c.save()



    def limpiar_mazo(self):
        """
        Limpia las cartas del mazo borrandolas de la base de datos.
        """
        cartas = Carta.objects.filter(gid=self)
        for c in cartas:
            c.delete()

    def cant_jugadores_en_partida(self):
        """
        Retorna la cantidad de jugadores en la partida actual.
        """
        equipo1 = self.equipo_set.get(gid=self, nro_equipo=1)
        equipo2 = self.equipo_set.get(gid=self, nro_equipo=2)
        nro_jugadores_equipo1 = equipo1.jugador_set.count()
        nro_jugadores_equipo2 = equipo2.jugador_set.count()
        return nro_jugadores_equipo1 + nro_jugadores_equipo2

    def obtener_equipo_de_turno(self):
        """
        Retorna el equipo del turno del jugador actual.
        """
        equipo1 = self.equipo_set.get(gid=self, nro_equipo=1)
        equipo2 = self.equipo_set.get(gid=self, nro_equipo=2)
        nro_equipo_en_turno = self.turno % 2
        if nro_equipo_en_turno == 1:
            return equipo1
        elif nro_equipo_en_turno == 0:
            return equipo2
        return None

    def setear_tantos_en_equipos(self):
        """
        Setea en el canto correspondiente los puntos del equipo.
        """
        equipo1 = self.equipo_set.get(gid=self, nro_equipo=1)
        equipo2 = self.equipo_set.get(gid=self, nro_equipo=2)
        jugadores_e1 = equipo1.jugador_set.all()
        jugadores_e2 = equipo2.jugador_set.all()
        puntos_e1 = []
        puntos_e2 = []
        for j in jugadores_e1:
            puntos_e1.append(j.tantos())
        for j in jugadores_e2:
            puntos_e2.append(j.tantos())
        self.cantos.tantos_e1 = max(puntos_e1)
        self.cantos.tantos_e2 = max(puntos_e2)
        self.cantos.save()

    def obtener_ganador_envido(self):
        if self.cantos.tantos_e1 < self.cantos.tantos_e2:
            return self.equipo_set.get(gid=self, nro_equipo=2)
        elif self.cantos.tantos_e2 < self.cantos.tantos_e1:
            return self.equipo_set.get(gid=self, nro_equipo=1)
        else:
            equipo1 = self.equipo_set.get(gid=self, nro_equipo=1)
            equipo2 = self.equipo_set.get(gid=self, nro_equipo=2)
            if equipo1.es_mano:
                return equipo1
            else:
                return equipo2

    def dar_puntos_envido(self):
        equipo = self.obtener_ganador_envido()
        for can in self.cantos.estado_envido:
            if can == 'e':
                equipo.puntaje += 2
            elif can == 'r':
                equipo.puntaje += 3
            elif can == 'f':
                total = self.puntos_a_jugar - equipo.puntaje
                equipo.puntaje += total
        equipo.save()

    def dar_puntos_envido_no_querido(self):
        if self.cantos.quiero == 1:
            e = 2
        else:
            e = 1
        equipo = self.equipo_set.get(gid=self, nro_equipo=e)
        for can in self.cantos.estado_envido:
            equipo.puntaje += 1
        equipo.save()


class Equipo(models.Model):
    gid = models.ForeignKey(Partida)            # Game ID.
    nro_equipo = models.IntegerField(default=0) # Varia en 1 ó 2.
    pie = models.IntegerField(default=1)        # Contiene nro_jugador pie.
    puntaje = models.IntegerField(default=0)    # Contiene el puntaje acumulado del equipo.
    es_mano = models.BooleanField(default=False)# Nos dice si el equipo es el mano o no.
    objects = models.Manager()

    def buenas(self):
        """
        Retorna un booleano que nos informe si estamos en las buena o no.
        """
        game = self.gid
        if game.puntos_a_jugar == 30 and self.puntaje < 15:
            return False
        return True
    
    def av_pie(self):
        """
        Avanza el pie a la posicion que le corresponde
        en la proxima mano.
        """
        pos = self.pie + 2
        self.pie = ((pos-1) % self.gid.numero_de_jugadores)+1
        self.save()

class Jugador(models.Model):
    usuario = models.OneToOneField(User)            # Representa al usuario dentro de la partida.
    tid = models.ForeignKey(Equipo)                 # ID del jugador dentro del equipo.
    nro_jugador = models.IntegerField(default=0)    # Numero de Jugador que tendra en la partida.
    objects = models.Manager()

    # Obtiene las cartas del mismo palo, las suma y obtiene los puntajes.
    def tantos(self):
        """
        Obtiene las cartas del mismo palo, las suma y obtiene los puntajes.
        """
        e = Carta.objects.filter(palo=ESPADA, jid=self)
        espada = sumar_cartas(e)
        b = Carta.objects.filter(palo=BASTO, jid=self)
        basto = sumar_cartas(b)
        c = Carta.objects.filter(palo=COPA, jid=self)
        copa = sumar_cartas(c)
        o = Carta.objects.filter(palo=ORO, jid=self)
        oro = sumar_cartas(o)
        return max(espada, basto, copa, oro)     # Obtiene los puntos totales que ha acumulador el jugador.

    # Acumula m puntos al puntaje que tenia el jugador.
    def sumar_puntos(self, m):
        self.puntaje += m
        self.save()

    def dar_carta(self,val,pal):
        c = Carta(valor=val, palo=pal, rank=sen(val,pal), jid=self, gid=self.tid.gid)
        c.save()
    def jugar_carta(self,val,pal,rond):
        carta = Carta.objects.get(jid=self,valor=val,palo=pal)
        carta.jugada = rond
        carta.save()

class Cantos(models.Model):
    partida = models.OneToOneField(Partida)
    tantos_e1 = models.IntegerField(default=0)
    tantos_e2 = models.IntegerField(default=0)
    quiero = models.IntegerField(default=0)
    estado_truco = models.IntegerField(default=0)
    estado_envido = models.CharField(default="",max_length=4,null=True)
    respuesta = models.BooleanField(default=False)
    ultimo = models.CharField(default="", max_length=2, null=True)

    def ultimo_canto(self):
        return self.ultimo

    def incrementar_truco(self):
        trc = ['t', 'rt', 'vc']
        self.estado_truco += 1
        if self.estado_truco > 3:
            self.estado_truco = 0
        self.ultimo = trc[self.estado_truco-1]
        self.save()

    def cantar_envido(self, c):
        """
        Keyword Arguments:
        c -- 'e' para envido, 'r' para real envido
              o 'f' para falta envido.
        """
        self.estado_envido += c
        self.ultimo = c
        self.respuesta = False
        self.save()

    def aceptar(self):
        """
        Acepta el ultimo envido/Truco que fue cantado
        """
        self.respuesta = True

    def resetear_cantos(self):
        self.tantos_e1 = 0
        self.tantos_e2 = 0
        self.quiero = 0
        self.estado_truco = 0
        self.estado_envido = ""
        self.ultimo = ""
        self.respuesta = False
        self.save()
                
    def posible_cantar(self):
        """
        Devuelve una lista de strings que representan las cosas que es posible 
        cantar.
        """
        can = []
        trc = [("Truco",'t'),("Re Truco","rt"),("Vale Cuatro","vc")]
        if self.partida.ronda == 1:
            if not 'f' in self.estado_envido:
                can.append(("Falta envido",'f'))
                if not 'r' in self.estado_envido:
                    can.append(("Real envido",'r'))
                    if self.estado_envido.count('e') < 2:
                        can.append(("Envido",'e'))
        if self.estado_truco < 3:
            can.append(trc[self.estado_truco])
        if self.estado_truco == 1 and self.estado_envido == "" and \
           self.partida.ronda == 1:
            can.append(("Envido es primero", "env_primero"))
        return can
