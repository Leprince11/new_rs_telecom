from django.urls import path
from . import views

urlpatterns = [
    #gestion du copmte rendu d'activite
    path('', views.getcra,name='cra'),
    path('CRA', views.created_cra_datetime,name='creer_cra'),
    path('liste_cra', views.initcra,name='listcra'),
    path('rapport', views.rapport,name='rapport'),
    path('generate_cra_pdf/<uuid:user_id>/', views.generate_cra_pdf, name='generate_cra_pdf'),
    path('manage_event/', views.manage_cra, name='manage_cra_create'),
    path('manage_event/<uuid:id_cra>/', views.manage_cra, name='manage_cra_update')


]