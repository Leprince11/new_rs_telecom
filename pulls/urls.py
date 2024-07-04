from django.urls import path
from . import views

urlpatterns = [
    # Portail administration pour l'authentification de R&S-TELECOM
    path('', views.login , name='login'),
    path('Inscription', views.register , name='register'),
    path('Connexion',views.login,name='login'),
    path('logout/', views.logout, name='logout'),
    path('Authentification/', views.opt, name='opt'),
    path('Mot de passe oublier', views.forget , name='forget'),
    path('Confirmation/<client_id>/', views.send_confirmation , name='confirmation'),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path('Confirme/', views.admin_confirm_two_factor_auth, name='admin_confirm'),

    path('anonymise',views.anonymise, name='anonymise'),

    path("profil", views.profil, name="profil"),
    path("verification", views.verification, name="verification"),
    path('change_pass', views.change_password, name='change_passe'),
    



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