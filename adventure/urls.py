from django.conf.urls import url
from . import api

urlpatterns = [
    url('init', api.initialize),
    url('move', api.move),
    url('say', api.say),
    url('get_rooms', api.get_rooms),
    url('make_dungeon', api.make_dungeon),
    url('set_players', api.set_players),
]