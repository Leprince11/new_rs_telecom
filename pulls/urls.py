from django.urls import path
from . import views

urlpatterns = [
    # route de lier au compte
    path('', views.login , name='login'),
    path('Inscription', views.register , name='register'),
    path('Connexion',views.login,name='login'),
    path('logout/', views.logout, name='logout'),
    path('Mot de passe oublier', views.forget , name='forget'),
    path('Confirmation/<client_id>/', views.send_confirmation , name='confirmation'),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),







    path('Home', views.home , name='dashboard'),
    #gestion du copmte rendu d'activite
    path('CRA', views.getcra,name='cra'),
    #gestion de demande de conges
    path('conge', views.conge,name='conge'),
    #gestion de fiche de paie
    path('fiche_de_paie', views.fiche_paie,name='fiche_paie'),
    #gestion de note de fraie
    path('note_de_fraie', views.note_frais,name='note_frais'),




]
