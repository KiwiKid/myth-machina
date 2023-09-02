from django.urls import path

from . import views

urlpatterns = [
    path('', views.map, name='map_view'),
    path('map', views.map_points, name='map_points_view'),
    #   path('data', views.map, name='map_data'),
    path('home', views.home, name='home_view'),
    path('note/', views.note_view, name='note_view'),
    path('notes/', views.bulk_notes_view, name='bulk_notes_view'),
    path('note/<int:note_id>/', views.delete_note_view,
         name='delete_note_view'),
    #  path('search', views.seach, name='place_view')
]
