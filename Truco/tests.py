from django.test import TestCase
from Truco.models import Partida, Jugador, Carta, Equipo, Cantos
from django.contrib.auth.models import User
from constants import *
from django.test.client import Client

class TrucoBaseTestCase(TestCase):

    def setUp(self):
        """Creo 2 usuarios: user1 y user2.
        Creo una partida.
        Creo los equipos, y finalmente llamo a la funcion agregar_jugador para
        que haga lo que tenga que hacer."""
        self.user1 = User.objects.create_user('user1', 'lennon@thebeatles.com', 'user1')
        self.user1.save()
        self.user2 = User.objects.create_user('user2', 'ringo@thebeatles.com', 'user2')
        self.user2.save()
        self.partida = Partida(creador=self.user1.username,numero_de_jugadores = 2)
        self.partida.save()
        equipo1 = Equipo(gid=self.partida, nro_equipo=1)
        equipo1.save()
        equipo2 = Equipo(gid=self.partida, nro_equipo=2)
        equipo2.save()
        canto = Cantos(partida=self.partida)
        canto.save()
        self.partida.agregar_jugador(self.user1)
        self.partida.agregar_jugador(self.user2)

class PartidaModelTestCase(TrucoBaseTestCase):
    """Test de partida"""

    def test_agregar_usuarios(self):
        """ Agregue dos usuarios a la partida en setup..."""
        #Cuento los jugadores de los equipos, deberian haber 2.
        equipo1 = self.partida.equipo_set.get(gid=self.partida, nro_equipo=1)
        equipo2 = self.partida.equipo_set.get(gid=self.partida, nro_equipo=2)
        nro_jugadores_equipo1 = equipo1.jugador_set.count()
        nro_jugadores_equipo2 = equipo2.jugador_set.count()
        self.assertEqual(nro_jugadores_equipo1 + nro_jugadores_equipo2, 2)
        self.assertEqual(nro_jugadores_equipo1, 1)
        self.assertEqual(nro_jugadores_equipo2, 1)

    def test_repartir_limpiar_mazo(self):
        """se creo y se repartio en setup..."""
 
        #reviso si cada jugador tiene las 3 cartas
        lista_equip = self.partida.equipo_set.all()
        for equipo in lista_equip:
            lista_jug = equipo.jugador_set.all()
            for jugador in lista_jug:
                self.assertEqual(jugador.carta_set.all().count(), 3)
        #limpio el mazo    
        self.partida.limpiar_mazo()
        #los jugadores no deberian tener ninguna carta asociada
        lista_equip = self.partida.equipo_set.all()
        for equipo in lista_equip:
            lista_jug = equipo.jugador_set.all()
            for jugador in lista_jug:
                self.assertEqual(jugador.carta_set.all().count(), 0)

    def test_ganador_mano_a(self):
        """testeo la funcion ganador_mano seteandole una serie de valores al atributo ganadores
        para los cuales se que valores deberia devolver """
        self.partida.ganadores ="120"
        self.partida.save()
        ganador_e = self.partida.ganador_mano()
        ganador_esperado = self.partida.equipo_set.get(nro_equipo=1)
        self.assertEqual(ganador_e.nro_equipo, ganador_esperado.nro_equipo)

    def test_ganador_mano_b(self):
        """testeo la funcion ganador_mano seteandole una serie de valores al atributo ganadores
        para los cuales se que valores deberia devolver """
        self.partida.ganadores ="210"
        self.partida.save()
        ganador_e = self.partida.ganador_mano()
        ganador_esperado = self.partida.equipo_set.get(nro_equipo=2)
        self.assertEqual(ganador_e.nro_equipo, ganador_esperado.nro_equipo)

    def test_ganador_mano_c(self):
        """testeo la funcion ganador_mano seteandole una serie de valores al atributo ganadores
        para los cuales se que valores deberia devolver """
        self.partida.ganadores ="000"
        self.partida.save()
        ganador_esperado = self.partida.equipo_set.get(nro_equipo=1)
        ganador_esperado.es_mano = True
        ganador_esperado.save()
        ganador_e = self.partida.ganador_mano()
        self.assertEqual(ganador_e.nro_equipo, ganador_esperado.nro_equipo)

    def test_ganador_ronda(self):
        """Este test setea ciertos valores en los atributos de la partida,
         luego reparte cartas determinadas a los distintos jugadores
         y finalmente llama a la funcion testeada y comprueba que haga lo que se
         espera, principalmente debe llenar el tributo ganadores de partida
         de acuerdo a quien gano la ronda.(ver especificacion de la funcion)"""
        self.partida.limpiar_mazo()
        player1 = Jugador.objects.get(tid__gid=self.partida,nro_jugador=1)
        player2 = Jugador.objects.get(tid__gid=self.partida,nro_jugador=2)
        player1.dar_carta(4,BASTO)
        player2.dar_carta(4,COPA)
        player1.dar_carta(6,BASTO)
        player2.dar_carta(6,COPA)
        player1.dar_carta(1,ESPADA)
        player2.dar_carta(1,BASTO)
        #juego las cartas.
        player1.jugar_carta(4,BASTO,1)
        player2.jugar_carta(4,COPA,1)
        player1.jugar_carta(6,BASTO,2)
        player2.jugar_carta(6,COPA,2)
        player1.jugar_carta(1,ESPADA,3)
        player2.jugar_carta(1,BASTO,3)
        #la primera ronda es parda por ende en el atributo ganadores de partida en
        # la primera posicion debe haber un 0
        self.partida.ganadores = ""
        self.partida.ronda = 1
        self.partida.save()
        self.partida.ganador_ronda()
        self.assertEqual(self.partida.ganadores, "0")
        self.partida.ronda += 1
        self.partida.ganador_ronda()
        self.assertEqual(self.partida.ganadores, "00")
        self.partida.ronda += 1
        self.partida.ganador_ronda()
        self.assertEqual(self.partida.ganadores, "001")
    def test_cant_jugadores_en_partida(self):
        """test corto para la funcion cant_jugadores_en_partida, como hay dos jugadores
        en la partida deberia retornar 2"""
        self.assertEqual(self.partida.cant_jugadores_en_partida(), 2)
    def test_setear_tantos_en_equipos(self):
        """test_setear_tantos_en_equipos..."""
        self.partida.limpiar_mazo()
        player1 = Jugador.objects.get(tid__gid=self.partida,nro_jugador=1)
        player2 = Jugador.objects.get(tid__gid=self.partida,nro_jugador=2)
        player1.dar_carta(4,BASTO)
        player2.dar_carta(4,COPA)
        player1.dar_carta(6,BASTO)
        player2.dar_carta(6,COPA)
        player1.dar_carta(1,ESPADA)
        player2.dar_carta(1,BASTO)
        #juego las cartas.
        player1.jugar_carta(4,BASTO,1)
        player2.jugar_carta(4,COPA,1)
        player1.jugar_carta(6,BASTO,2)
        player2.jugar_carta(6,COPA,2)
        player1.jugar_carta(1,ESPADA,3)
        player2.jugar_carta(1,BASTO,3)
        #llamo a la funcion testeada
        self.partida.setear_tantos_en_equipos()
        self.assertEqual(self.partida.cantos.tantos_e1, 30)
        self.assertEqual(self.partida.cantos.tantos_e1,30)

class CantosModelTestCase(TrucoBaseTestCase):
    def test_posible_cantar(self):
        """testeamos posible_cantar de cantos."""
        self.partida.cantos.resetear_cantos()
        self.partida.cantos.estado_envido = "eer"
        #self.partida.cantos.estado_truco = 
        self.partida.cantos.save()
        lista_cantos = self.partida.cantos.posible_cantar()
        #lista cantos es una lista con los cantos que se pueden
        #realizar dado un estado.
        #self.assertTrue(("vale_cuatro","vc") in lista_cantos)
        self.assertTrue(("Falta envido",'f') in lista_cantos)

class TrucoViewTestCaseRegistro(TestCase):
    """Test para la vista de registro """

    def test_registro_un_usuario_exito(self):
        """resgistro un usuario sin errores"""
        response = self.client.post('/signin/', {'username': 'test', 'password': 'test',
         'email': 'test@test.com', 'password_conf': 'test'}, follow=True)
        #se deberia redirigir a el usuario a la pantalla de login.
        self.assertRedirects(response, '/login/')

    def test_registro_un_usuario_fallido_password_conf(self):
        """Intento crear un usuario pero la contrasenia y la confirmacion de esta son distintas"""
        response = self.client.post('/signin/', {'username': 'test0', 'password': 'test0',
         'email': 'test@test.com', 'password_conf': 'test'})
        self.assertEqual(response.context['state'], "No coinciden contrasena.")

    def test_registro_un_usuario_fallido_datos_no_validos(self):
        """Intento crear un usuario pero los datos suministrados por el usuario son incorrectos"""
        response = self.client.post('/signin/', {'username': 'test', 'password': 'test',
         'email': 'error', 'password_conf': 'test'}, follow=True)
        self.assertEqual(response.context['state'], "Asegurarse de haber completado todo.")

class TrucoViewTestCaseLogin(TestCase):

    def setUp(self):
        #registro dos usuarios.
        response = self.client.post('/signin/', {'username': 'test', 'password': 'test',
         'email': 'test@test.com', 'password_conf': 'test'})
        response = self.client.post('/signin/', {'username': 'test0', 'password': 'test0',
         'email': 'test@test.com', 'password_conf': 'test0'})

    def test_login_exitoso(self):
        response = self.client.post('/login/', {'username': 'test', 'password': 'test'},
         follow=True)
        #se deberia redirigir a el usuario a la pantalla de lobby si se logueo exitosamente
        self.assertRedirects(response, '/lobby/')

    def test_login_cotrasenia_erronea(self):
        response = self.client.post('/login/', {'username': 'test', 'password': 'error'},
         follow=True)
        #se deberia dar un mensaje de error
        self.assertEqual(response.context['state'], "Tu nombre de usuario/contrasena es incorrecta.")

class TrucoViewTestCaseCrearUnirseLobby(TestCase):

    def setUp(self):
        #registro un usuario.
        self.client_a = Client()
        self.client_b = Client()
        self.client_c = Client()

        # Creo y logueo al usuario test
        response = self.client_a.post('/signin/', {'username': 'test', 'password': 'test',
         'email': 'test@test.com', 'password_conf': 'test'}, follow=True)
        self.assertRedirects(response, '/login/')# si todo funciono bien me redirige a login
        response = self.client_a.post('/login/', {'username': 'test', 'password': 'test'},
         follow=True)
        #se deberia redirigir a el usuario a la pantalla de lobby si se logueo exitosamente
        self.assertRedirects(response, '/lobby/')

        #Creo y logueo al usuario test1
        response = self.client_b.post('/signin/', {'username': 'test1', 'password': 'test1',
                                                   'email': 'test1@test1.com', 'password_conf': 'test1'}, follow=True)
        self.assertRedirects(response, '/login/')# si todo funciono bien me redirige a login
        response = self.client_b.post('/login/', {'username': 'test1', 'password': 'test1'},
                                      follow=True)
        #se deberia redirigir a el usuario a la pantalla de lobby si se logueo exitosamente
        self.assertRedirects(response, '/lobby/')
        response = self.client_c.post('/signin/', {'username': 'test2', 'password': 'test2',
                                                   'email': 'test2@test2.com', 'password_conf': 'test2'}, follow=True)
        self.assertRedirects(response, '/login/') # si todo funciono bien me redirige a login
        response = self.client_c.post('/login/', {'username': 'test2', 'password': 'test2'},
                                      follow=True)
        #se deberia redirigir a el usuario a la pantalla de lobby si se logueo exitosamente
        self.assertRedirects(response, '/lobby/')

        #url de la partida a crearse
        self.url_juego = '/join/1/'

    def test_partida_llena_url(self):
        """
        Estado Previo:
        3 usuarios logueados
        Situacion:
        El primer usuario crea la partida.
        Los usuarios restantes desean unirse a la partida mediante la url /join/<id_partida>
        Resultado Esperado:
        El tercer usuario en intentar unirse es redireccionado al lobby.
        """
        response = self.client_a.post('/crear/', {'puntos': '15','numero_de_jugadores':'2',}, follow=True)
        self.assertContains(response,"Esperando al otro jugador...") # Se creo existosamente la partida        
        response = self.client_b.get(self.url_juego)
        self.assertContains(response, "Te uniste a una partida")
        response = self.client_c.get(self.url_juego)
        self.assertRedirects(response, '/lobby/')
        
    def test_crear_partida(self):
        #self.client.login(username = 'test', password = 'test')
        response = self.client_a.post('/crear/', {'puntos': '15','numero_de_jugadores':'2',},
         follow=True)
        self.assertContains(response,"Esperando al otro jugador...")
        
    def test_crear_y_partida_unirse(self):
        #test crea la partida a 15 puntos.
        response = self.client_a.post('/crear/', {'puntos': '15','numero_de_jugadores':'2',},
         follow=True)
        self.assertContains(response,"Esperando al otro jugador...")
        #test1 se une a ella solicitando la url /join/1/.
        response = self.client_b.get(self.url_juego)
        self.assertContains(response,"Te uniste a una partida")
    def test_lobby(self):
        #test crea una partida a 15 puntos.
        response = self.client_a.post('/crear/', {'puntos': '15','numero_de_jugadores':'2',},
         follow=True)
        self.assertContains(response,"Esperando al otro jugador...")
        #con test 2 hago un pedido del lobbby
        response = self.client_b.get('/lobby/')
        #deberia existir una sola partida, la creada por test.
        lista_partidas = response.context['tabla']
        self.assertEqual(len(lista_partidas),1)
        partida = lista_partidas[0]
        self.assertEqual(partida.creador,'test')

class TrucoViewTestCaseJugar(TestCase):
    def setUp(self):
        #registro un usuario.
        self.client_a = Client()
        self.client_b = Client()

        # Creo y logueo al usuario test
        response = self.client_a.post('/signin/', {'username': 'test', 'password': 'test',
         'email': 'test@test.com', 'password_conf': 'test'}, follow=True)
        self.assertRedirects(response, '/login/')# si todo funciono bien me redirige a login
        response = self.client_a.post('/login/', {'username': 'test', 'password': 'test'},
         follow=True)
        #se deberia redirigir a el usuario a la pantalla de lobby si se logueo exitosamente
        self.assertRedirects(response, '/lobby/')

        #Creo y logueo al usuario test1
        response = self.client_b.post('/signin/', {'username': 'test1', 'password': 'test1',
         'email': 'test1@test1.com', 'password_conf': 'test1'}, follow=True)
        self.assertRedirects(response, '/login/')# si todo funciono bien me redirige a login
        response = self.client_b.post('/login/', {'username': 'test1', 'password': 'test1'},
         follow=True)
        #se deberia redirigir a el usuario a la pantalla de lobby si se logueo exitosamente
        self.assertRedirects(response, '/lobby/')
        #url de la partida a crearse
        self.url_juego = '/join/1/'
        #test crea una partida y test1 se une.
        response = self.client_a.post('/crear/', {'puntos': '15','numero_de_jugadores':'2',},
         follow=True)
        #test1 se une a ella solicitando la url /join/1/.
        response = self.client_b.get(self.url_juego)

    def test_envido_no_querido(self):
        #test canta el envido.
        response = self.client_a.post(self.url_juego, {'canto': 'e',},
         follow=True)
        #test1 no lo acepta.
        response = self.client_b.post(self.url_juego, {'quiero': '0',},
         follow=True)
        game = response.context['game']
        #test esta en el equipo 1. por ende su equipo debe tener 1 punto.
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        self.assertEqual(test.tid.puntaje,1)

    def test_envido_querido(self):
        response = self.client_a.get(self.url_juego,
         follow=True)
        #borro las cartas de ambos jugadores
        game = response.context['game']
        Carta.objects.filter(gid=game).delete()
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        test1 = Jugador.objects.get(tid__gid=game, nro_jugador=2)
        #les doy nuevas cartas
        test.dar_carta(1,ESPADA)
        test.dar_carta(1,BASTO)
        test.dar_carta(7,ESPADA)
        test1.dar_carta(4,ESPADA)
        test1.dar_carta(4,BASTO)
        test1.dar_carta(5,ESPADA)
        #test canta el envido.
        response = self.client_a.post(self.url_juego, {'canto': 'e',},
         follow=True)
        #test1  lo acepta.
        response = self.client_b.post(self.url_juego, {'quiero': '1',},
         follow=True)
        game = response.context['game']
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        test1 = Jugador.objects.get(tid__gid=game, nro_jugador=2)
        #el equipo ganador debe tener 2 puntos.
        self.assertEqual(test1.tid.puntaje==2 and test.tid.puntaje==0, True)

    def test_jugar_callado(self):
        response = self.client_a.get(self.url_juego,
         follow=True)
        #borro las cartas de ambos jugadores
        game = response.context['game']
        Carta.objects.filter(gid=game).delete()
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        test1 = Jugador.objects.get(tid__gid=game, nro_jugador=2)
        #les doy nuevas cartas
        test.dar_carta(1,ESPADA)
        test.dar_carta(1,BASTO)
        test.dar_carta(7,ESPADA)
        test1.dar_carta(4,ESPADA)
        test1.dar_carta(4,BASTO)
        test1.dar_carta(5,ESPADA)
        #Ahora los hago jugar si cantar nada.
        response = self.client_a.post(self.url_juego, {'carta': '0',},
         follow=True)
        response = self.client_b.post(self.url_juego, {'carta': '0',},
         follow=True)
        response = self.client_a.post(self.url_juego, {'carta': '1',},
         follow=True)
        response = self.client_b.post(self.url_juego, {'carta': '1',},
         follow=True)
        #En este punto test1 ya perdio la mano entonces el equipo de test tiene que tener 1 punto.
        game = response.context['game']
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        self.assertEqual(test.tid.puntaje,1)

    def test_cantar_truco_aceptado(self):
        response = self.client_a.get(self.url_juego,
         follow=True)
        response = self.client_b.get(self.url_juego, follow=True)
        #borro las cartas de ambos jugadores
        game = response.context['game']
        Carta.objects.filter(gid=game).delete()
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        test1 = Jugador.objects.get(tid__gid=game, nro_jugador=2)
        #les doy nuevas cartas
        test.dar_carta(1,ESPADA)
        test.dar_carta(1,BASTO)
        test.dar_carta(7,ESPADA)
        test1.dar_carta(4,ESPADA)
        test1.dar_carta(4,BASTO)
        test1.dar_carta(5,ESPADA)
        #test canta el truco.
        response = self.client_a.post(self.url_juego, {'canto': 't',},
         follow=True)
        #test1  lo acepta.
        response = self.client_b.post(self.url_juego, {'quiero': '1',},
         follow=True)

        response = self.client_a.post(self.url_juego, {'carta': '0',},
         follow=True)
        response = self.client_b.post(self.url_juego, {'carta': '0',},
         follow=True)
        response = self.client_a.post(self.url_juego, {'carta': '1',},
         follow=True)
        response = self.client_b.post(self.url_juego, {'carta': '1',},
         follow=True)
        #En este punto test1 ya perdio la mano entonces el equipo de test tiene que tener 2 puntos.
        game = response.context['game']
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        self.assertEqual(test.tid.puntaje,2)

    def test_envido_y_truco_queridos(self):
        response = self.client_a.get(self.url_juego,
         follow=True)
        #borro las cartas de ambos jugadores
        game = response.context['game']
        Carta.objects.filter(gid=game).delete()
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        test1 = Jugador.objects.get(tid__gid=game, nro_jugador=2)
        #les doy nuevas cartas
        test.dar_carta(1,ESPADA)
        test.dar_carta(1,BASTO)
        test.dar_carta(7,ESPADA)
        test1.dar_carta(4,ESPADA)
        test1.dar_carta(4,BASTO)
        test1.dar_carta(5,ESPADA)
        #test canta el envido.
        response = self.client_a.post(self.url_juego, {'canto': 'e',},
         follow=True)
        #test  lo acepta.
        response = self.client_b.post(self.url_juego, {'quiero': '1',},
         follow=True)
        #test canta el truco.
        response = self.client_a.post(self.url_juego, {'canto': 't',},
         follow=True)
        #test1  lo acepta.
        response = self.client_b.post(self.url_juego, {'quiero': '1',},
         follow=True)

        response = self.client_a.post(self.url_juego, {'carta': '0',},
         follow=True)
        response = self.client_b.post(self.url_juego, {'carta': '0',},
         follow=True)
        response = self.client_a.post(self.url_juego, {'carta': '1',},
         follow=True)
        response = self.client_b.post(self.url_juego, {'carta': '1',},
         follow=True)
        #En este punto test1 ya perdio la mano.
        #test1 gano el envido con 29
        game = response.context['game']
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        test1 = Jugador.objects.get(tid__gid=game, nro_jugador=2)
        self.assertEqual(test1.tid.puntaje,2)
        self.assertEqual(test.tid.puntaje,1)

    def test_envido_envido_querido(self):
        response = self.client_a.get(self.url_juego,
         follow=True)
        #borro las cartas de ambos jugadores
        game = response.context['game']
        Carta.objects.filter(gid=game).delete()
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        test1 = Jugador.objects.get(tid__gid=game, nro_jugador=2)
        #les doy nuevas cartas
        test.dar_carta(1,ESPADA)
        test.dar_carta(1,BASTO)
        test.dar_carta(7,ESPADA)
        test1.dar_carta(4,ESPADA)
        test1.dar_carta(4,BASTO)
        test1.dar_carta(5,ESPADA)
        #test canta el envido.
        response = self.client_a.post(self.url_juego, {'canto': 'e',},
         follow=True)
        #test1 canta el envido-envido
        response = self.client_b.post(self.url_juego, {'canto': 'e',},
         follow=True)
        #test  lo acepta.
        response = self.client_a.post(self.url_juego, {'quiero': '1',},
         follow=True)
        #test1 deberia tener 4 puntos.(gano con 29)
        game = response.context['game']
        test1 = Jugador.objects.get(tid__gid=game, nro_jugador=2)
        self.assertEqual(test1.tid.puntaje,4)

    def test_t_rt_vc(self):
        response = self.client_a.get(self.url_juego,
         follow=True)
        response = self.client_b.get(self.url_juego, follow=True)
        #borro las cartas de ambos jugadores
        game = response.context['game']
        Carta.objects.filter(gid=game).delete()
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        test1 = Jugador.objects.get(tid__gid=game, nro_jugador=2)
        #les doy nuevas cartas
        test.dar_carta(1,ESPADA)
        test.dar_carta(1,BASTO)
        test.dar_carta(7,ESPADA)
        test1.dar_carta(4,ESPADA)
        test1.dar_carta(4,BASTO)
        test1.dar_carta(5,ESPADA)
        #test canta el truco.
        response = self.client_a.post(self.url_juego, {'canto': 't',},
         follow=True)
        #test1  canta el re truco.
        response = self.client_b.post(self.url_juego, {'canto': 'rt',},
         follow=True)
        #test canta el vale cuatro.
        response = self.client_a.post(self.url_juego, {'canto': 'vc',},
         follow=True)
        #test1 lo acepta.
        response = self.client_b.post(self.url_juego, {'quiero': '1',},
         follow=True)

        response = self.client_a.post(self.url_juego, {'carta': '0',},
         follow=True)
        response = self.client_b.post(self.url_juego, {'carta': '0',},
         follow=True)
        response = self.client_a.post(self.url_juego, {'carta': '1',},
         follow=True)
        response = self.client_b.post(self.url_juego, {'carta': '1',},
         follow=True)
        #En este punto test1 ya perdio la mano entonces el equipo de test tiene que tener 2 puntos.
        game = response.context['game']
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        self.assertEqual(test.tid.puntaje,4)

    def test_envido_envido_real_envido_no_querido(self):
        response = self.client_a.get(self.url_juego,
         follow=True)
        #borro las cartas de ambos jugadores
        game = response.context['game']
        Carta.objects.filter(gid=game).delete()
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        test1 = Jugador.objects.get(tid__gid=game, nro_jugador=2)
        #les doy nuevas cartas
        test.dar_carta(1,ESPADA)
        test.dar_carta(1,BASTO)
        test.dar_carta(7,ESPADA)
        test1.dar_carta(4,ESPADA)
        test1.dar_carta(4,BASTO)
        test1.dar_carta(5,ESPADA)
        #test canta el envido.
        response = self.client_a.post(self.url_juego, {'canto': 'e',},
         follow=True)
        #test1 canta el envido-envido
        response = self.client_b.post(self.url_juego, {'canto': 'e',},
         follow=True)
        #canta el real envido.
        response = self.client_a.post(self.url_juego, {'canto': 'r',},
         follow=True)
        #test no lo acepta.
        response = self.client_b.post(self.url_juego, {'quiero': '0',},
         follow=True)
        #test deberia tener 4 puntos.
        game = response.context['game']
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        self.assertEqual(test.tid.puntaje,4)

    def test_envido_envido_real_envido_falta_env_no_querido(self):
        response = self.client_a.get(self.url_juego,
         follow=True)
        #borro las cartas de ambos jugadores
        game = response.context['game']
        Carta.objects.filter(gid=game).delete()
        test = Jugador.objects.get(tid__gid=game, nro_jugador=1)
        test1 = Jugador.objects.get(tid__gid=game, nro_jugador=2)
        #les doy nuevas cartas
        test.dar_carta(1,ESPADA)
        test.dar_carta(1,BASTO)
        test.dar_carta(7,ESPADA)
        test1.dar_carta(4,ESPADA)
        test1.dar_carta(4,BASTO)
        test1.dar_carta(5,ESPADA)
        #test canta el envido.
        response = self.client_a.post(self.url_juego, {'canto': 'e',},
         follow=True)
        #test1 canta el envido-envido
        response = self.client_b.post(self.url_juego, {'canto': 'e',},
         follow=True)
        #test canta el real envido.
        response = self.client_a.post(self.url_juego, {'canto': 'r',},
         follow=True)
        #test1 canta la falta.
        response = self.client_b.post(self.url_juego, {'canto': 'f',},
         follow=True)
        #test no lo acepta.
        response = self.client_a.post(self.url_juego, {'quiero': '0',},
         follow=True)
        #test1 deberia tener 4 puntos.
        game = response.context['game']
        test1 = Jugador.objects.get(tid__gid=game, nro_jugador=2)
        self.assertEqual(test.tid.puntaje,7)
