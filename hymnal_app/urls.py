from . import views
from django.urls import path

urlpatterns = [
    path('', views.index),
    path('user/create_user', views.create_user),
    path('user/login', views.login),
    path('dashboard', views.dashboard),
    path('user/logout', views.logout),
    path('set/create_form', views.create_form),
    path('set/create_song', views.create_song),
    path('set/create_set', views.create_set),
    path('set/view_user_sets', views.view_user_sets),
    path('set/view/<int:set_id>', views.view_set),
    path('set/delete/<int:set_id>', views.delete_set),
    # path('song/format', views.format_song),
    path('song/edit/<int:song_id>', views.edit_song),
    path('song/view/<int:song_id>', views.view_song),
    path('song/delete_song/<int:song_id>', views.delete_song),
    path('set/song/delete_song/<int:song_id>/<int:set_id>', views.delete_song_from_set),
    path('song/remove_from_queue/<int:song_id>', views.remove_from_queue),
    path('song/push_to_queue/<int:song_id>', views.push_to_queue),
    path('song/<int:song_id>/move_up', views.shift_song_up_in_queue),
    path('song/<int:song_id>/move_down', views.shift_song_down_in_queue),
    path('set/song/add_to_set/<int:song_id>/<int:set_id>', views.add_song_to_set),
    #path('song/<int>', views.view_song),
    #path('song/<int>/edit/confirm', views.confirm_edit),
    path('test_route', views.test_route),
    path('song/delete_all_songs', views.delete_all_songs) #Delete this route later
]