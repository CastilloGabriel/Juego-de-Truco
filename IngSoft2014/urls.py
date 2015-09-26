from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'IngSoft2014.views.home', name='home')
    # url(r'^blog/', include('blog.urls'))
    url(r'^$', 'Truco.views.homepage'),             # URL para la pagina de inicio.
    url(r'^login/', 'Truco.views.login_user'),      # URL para el logueo.
    url(r'^admin/', include(admin.site.urls)),      # URL para el sitio de admin.
    url(r'^signin/', 'Truco.views.register_user'),  # URL para el registro.
    url(r'^logout/', 'Truco.views.logout_user'),    # URL para desloguearse.
    url(r'^join/(\d+)/$', 'Truco.views.jugar'),     # URL para jugar.
    url(r'^lobby/', 'Truco.views.muestreo_lobby'),  # URL del lobby.
    url(r'^crear/', 'Truco.views.crear_partida'),   # URL para crear una partida.
)
