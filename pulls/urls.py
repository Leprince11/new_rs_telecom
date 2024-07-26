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

    path("Informations", views.profil, name="profil"),
    path('Informations/<uuid:user_id>/', views.profil, name='edith_profil'),
    path('Informations/update_profile/', views.update_profile_ajax, name='update_profile'),
    path('change_pass', views.change_password, name='change_passe'),
    path("verification", views.verification, name="verification"),

    #gestion de fiche de paie
    path('Employes', views.fiche_paie,name='employes'),
    path('employes_all', views.getEmploye,name='getEmployes'),
    



    path('Home', views.home , name='dashboard'),

]