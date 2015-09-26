#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django import forms
from Truco.models import *
from django.http import HttpResponseRedirect
from django.forms.widgets import PasswordInput
from exep import PartidaLlena

# Funciones auxiliares:

def cambiar_quiero(equipo):
    if equipo == 1:
        return 2
    return 1

def manejador_estado(lista_cantos):
    status = ""
    if lista_cantos.count(3):
        status = "El oponente canto Falta Envido."
    elif lista_cantos.count(2):
        status = "El oponente canto Real Envido."
    elif lista_cantos.count(1):
        status = "El oponente canto Doble Envido."
    elif lista_cantos.count(0):
        status = "El oponente canto Envido."
    if lista_cantos.count(6):
        status = "El oponente canto Vale Cuatro."
    elif lista_cantos.count(5):
        status = "El oponente canto Re Truco."
    elif lista_cantos.count(4):
        status = "El oponente canto Truco."
    return status
# Fin de funciones auxiliares.

# Clase necesaria para el muestreo del lobby.
class LobbyTable(object):
    creador = ""            # Nombre del creador de la partida.
    estado = ""             # 'Disponible', si hay 1 solo jugador en la partida. 'Lleno' si hay 2 jugadores.
    puntos_a_jugar = 15     # Puntos que se jugaran en una partida, por defecto 15.
    numero_de_jugadores = 0 # Cantidad de Jugadores que habra en la Partida.
    puntos_equipo1 = 0      # Puntos que el jugador 1 posee.
    puntos_equipo2 = 0      # Puntos que el jugador 2 posee.
    gameid = 0              # ID de la partida.

# Clase necesaria para el formulario de registro.
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=32)                       # Nombre del usuario.
    password = forms.CharField(max_length=64, widget=PasswordInput) # Contrasena del usuario.
    password_conf = forms.CharField(max_length=64,
                                    widget=PasswordInput)           # Confirmacion de contrasena.
    email = forms.EmailField()                                      # Email del usuario.


# Redirige al 'main.html' donde se muestra la pagina principal.
def homepage(request):
    user = get_user(request)
    username = user.username
    return render_to_response('main.html',{'username':username})

# Formulario de registro del usuario. Crea un usuario y lo guarda en la
# base de datos. Redirige al logueo para que el usuario se pueda loguear.
def register_user(request):
    state = ''
    if request.POST:
        form = RegisterForm(request.POST)
        if form.is_valid() :
            if form.cleaned_data["password"] == form.cleaned_data["password_conf"]:
                user = User.objects.create_user(form.cleaned_data["username"],
                                                form.cleaned_data["email"],
                                                form.cleaned_data["password"])
                user.save()
                state = "Registrado exitosamente."
                return HttpResponseRedirect('/login/')
            else:
                state = "No coinciden contrasena."
        else:
            state = "Asegurarse de haber completado todo."
    form = RegisterForm()
    return render_to_response('register.html', {'state':state, 'form':form})

# Formulario de logueo del usuario. Redirige al lobby en caso de exito,
# o al mismo loguin en caso de error.
def login_user(request):
    state = "Por favor, loguearse a continuacion."
    username = password = ''
    if request.POST: # Si la forma ya fue enviada...
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "Te has logueado con exito"
                return HttpResponseRedirect('/lobby/')
            else:
                state = "Tu cuenta no esta activa, por favor registrate."
        else:
            state = "Tu nombre de usuario/contrasena es incorrecta."
    return render_to_response('auth.html',{'state':state, 'username': username})


# Deslogua a un usuario redirigiendolo a la pagina principal.
@login_required(login_url='/login/')    # Decorador que sirve para ascerosarse que el usuario esta logueado.
def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')

# Crea una partida y le une su primer jugador.
@login_required(login_url='/login/')    # Decorador que sirve para ascerosarse que el usuario esta logueado.
def crear_partida(request):
    user = get_user(request)
    numero_de_jugadores = int(request.POST.get('numero_de_jugadores'))
    game = Partida(creador=user.username, puntos_a_jugar=request.POST.get('puntos'),
                   numero_de_jugadores=numero_de_jugadores)
    game.save()
    equipo1 = Equipo(gid=game, nro_equipo=1, pie=numero_de_jugadores-1)
    equipo1.save()
    equipo2 = Equipo(gid=game, nro_equipo=2, pie=numero_de_jugadores)
    equipo2.save()
    game.agregar_jugador(user)
    canto = Cantos(partida=game)
    canto.save()
    url ='/join/{0}'.format(game.id)
    print(url)
    return HttpResponseRedirect(url)

# Une un jugador a una partida previamente creada.
@login_required(login_url='/login/')    # Decorador que sirve para ascerosarse que el usuario esta logueado.
def unirse_partida(request, gid):
    try:
        user = get_user(request)
        game = Partida.objects.get(id=gid)
        game.save()
        url ='/join/{0}'.format(game.id)
        return HttpResponseRedirect(url)
    except:
        return HttpResponseRedirect('/lobby/')

# Instancia del objeto ShowBottons que mostrara los botones en la partida.
#botones = ShowButton()
#se_canto_algo = False               # Nos dice si hubo algun canto.
#lista_cantos = []

@login_required(login_url='/login/')    # Decorador que sirve para ascerosarse que el usuario esta logueado.
# En esta instancia estamos dentro de la partida y vemos que accion eligio el jugador.
def jugar(request, gid):
    status = ""                         # Mensaje que se mostrara por pantalla al jugador.
    game = Partida.objects.get(id=gid)  # Esta es la partida en curso.
    equipo1 = game.equipo_set.get(nro_equipo=1) # Equipo 1.
    equipo2 = game.equipo_set.get(nro_equipo=2) # Equipo 2.
    user = get_user(request)            # Contiene el usuario que hizo el pedido.
    can_accept = False
    # Veamos si el usuario es de esta partida, en caso contrario, tratamos de
    # unirlo, y si no podemos, informamos que no existe.
    try:
        player = user.jugador
        if player not in list(equipo1.jugador_set.all()) and\
           player not in list(equipo2.jugador_set.all()):
            try:
                game.agregar_jugador(user)
            except PartidaLlena:
                return HttpResponseRedirect('/lobby/')
    except Jugador.DoesNotExist:
        try:
            player = game.agregar_jugador(user)
        except PartidaLlena:
            return HttpResponseRedirect('/lobby/')

    if game.cant_jugadores_en_partida() == game.numero_de_jugadores and\
       (game.puntos_a_jugar > equipo1.puntaje or\
       game.puntos_a_jugar > equipo2.puntaje):

        mostrar_can = None
        equipo = game.obtener_equipo_de_turno()
        mi_equipo = player.tid
        can_accept = False



        if player.nro_jugador == player.tid.pie:
            if (game.pausa and player.tid.nro_equipo == game.cantos.quiero):
                can_accept = True
                if 'quiero' in request.POST:
                    q = int(request.POST.get("quiero"))
                    game.pausa = False
                    game.save()
                    if q:
                        if not game.cantos.estado_envido == "":
                            game.dar_puntos_envido()
                            game.cantos.quiero = 0
                            game.cantos.save()
                    else:
                        if not game.cantos.estado_envido == "":
                            game.dar_puntos_envido_no_querido()
                        else:
                            if equipo == equipo1:
                                equipo1.puntaje += game.cantos.estado_truco
                                equipo1.save()
                            else:
                                equipo2.puntaje += game.cantos.estado_truco
                                equipo2.save()
                            game.cambiar_mano()
                        can_accept = False
            if (game.turno_equipo() == player.tid.nro_equipo or game.pausa) and\
               (game.cantos.quiero == player.tid.nro_equipo or\
                game.cantos.quiero == 0):
                mostrar_can = game.cantos.posible_cantar()
                if 'canto' in request.POST:
                    canto = request.POST.get('canto')
                    game.cantos.quiero = cambiar_quiero(player.tid.nro_equipo)
                    game.pausa = True
                    game.save()
                    if not canto in ["t", "rt", "vc"]:
                        game.cantos.estado_envido += canto
                        game.setear_tantos_en_equipos()
                        game.cantos.save()
                    else:
                        game.cantos.incrementar_truco()

        if not game.pausa and game.turno == player.nro_jugador:
            game.save()
            mano = list(Carta.objects.filter(jugada=0, jid=player))
            if 'carta' in request.POST:
                carta = request.POST.get('carta')
                c = mano[int(carta)]
                c.jugada = game.ronda
                c.save()
                # game.ganador_ronda ya setea la siguiente ronda, el siguiente
                # turno.
                if game.ganador_ronda():
                    equipo_ganador = game.ganador_mano()
                    if equipo_ganador is not None:
                        game.cambiar_mano()
                        game.ronda = 1
                        game.ganadores = ""
                        game.save()
                    else:
                        game.av_ronda()
                else:
                    game.av_turno()
        else:
            status = "Esperando al oponente."
        mano = list(Carta.objects.filter(jugada=0, jid=player))
        jugadas = list(Carta.objects.filter(gid=game).exclude(jugada=0).order_by('jugada', 'jid'))

        jugadas1 = jugadas[0::game.numero_de_jugadores]
        jugadas2 = jugadas[1::game.numero_de_jugadores]
        if game.numero_de_jugadores == 4:
            jugadas3 = jugadas[2::game.numero_de_jugadores]
            jugadas4 = jugadas[3::game.numero_de_jugadores]
            return render_to_response('partida4.html', {'mano':mano,
                                                       'game':game,
                                                       'equipo':mi_equipo,
                                                       'player':player,
                                                       'jugadas1':jugadas1,
                                                       'jugadas2':jugadas2,
                                                       'jugadas3':jugadas3,
                                                       'jugadas4':jugadas4,
                                                       'mostrar_can':mostrar_can,
                                                       'status':status,
                                                       'can_accept':can_accept
                                                       })
        elif game.numero_de_jugadores == 6:
            jugadas5 = jugadas[4::game.numero_de_jugadores]
            jugadas6 = jugadas[5::game.numero_de_jugadores]
            return render_to_response('partida6.html', {'mano':mano,
                                                       'game':game,
                                                       'equipo':mi_equipo,
                                                       'player':player,
                                                       'jugadas1':jugadas1,
                                                       'jugadas2':jugadas2,
                                                       'jugadas3':jugadas3,
                                                       'jugadas4':jugadas4,
                                                       'jugadas5':jugadas5,
                                                       'jugadas6':jugadas6,
                                                       'mostrar_can':mostrar_can,
                                                       'status':status,
                                                       'can_accept':can_accept
                                                       })
        elif game.numero_de_jugadores == 2:
            return render_to_response('partida.html', {'mano':mano,
                                                   'game':game,
                                                   'equipo':mi_equipo,
                                                   'player':player,
                                                   'jugadas1':jugadas1,
                                                   'jugadas2':jugadas2,
                                                   'mostrar_can':mostrar_can,
                                                   'status':status,
                                                   'can_accept':can_accept
                                                   })
    status = 0
    return render_to_response('partida.html', {'status':status})

# Se realiza el muestreo del lobby, viendo en ella las partidas ya creadas, o dando la
# opcion de crear una partida.
# Si esta llena la partida, muestra los puntos de cada jugador para que se pueda
# ver el estado de la misma.
@login_required(login_url='/login/')    # Decorador que sirve para ascerosarse que el usuario esta logueado.
def muestreo_lobby(request):
    lista_partidas = []
    if request.method == 'GET':
        user = get_user(request)
        for partida in Partida.objects.all():
            tabla_lobby = LobbyTable()
            tabla_lobby.creador = partida.creador
            tabla_lobby.gameid = partida.id
            tabla_lobby.puntos_a_jugar = partida.puntos_a_jugar
            tabla_lobby.numero_de_jugadores = partida.numero_de_jugadores
            if partida.numero_de_jugadores == partida.cant_jugadores_en_partida():
                tabla_lobby.estado = "Lleno"
                equipo1 = Equipo.objects.get(gid=partida, nro_equipo=1)
                equipo2 = Equipo.objects.get(gid=partida, nro_equipo=2)
                tabla_lobby.puntos_equipo1 = equipo1.puntaje
                tabla_lobby.puntos_equipo2 = equipo2.puntaje
            else :
                tabla_lobby.estado = "Disponible"
            lista_partidas.append(tabla_lobby)
        return render_to_response('lobby.html',{'tabla':lista_partidas})
