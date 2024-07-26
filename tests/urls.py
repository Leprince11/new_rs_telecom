from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    #path pour ajout de leads 
    path('add_company/', views.add_company, name='add_company'),
    path('add_company/check-name/', views.check_name, name='check_name'), # ajax
    path('add_company/check-offre/',views.check_offer_name,name='check_offer'),
    path('add_company/check-date',views.check_offer_date,name='check_date_publication'),
    path('add_company/submit-form/', views.submit_form, name='submit-form'), # soumission du formulaire avec futures vérifs coté serveur 

    #path pour le choix des leads 
    path('choix_leads/',views.choix_leads,name='choix_leads'),
    # visualisation des leads présents dans le fichier csv ou dans la base de données 
    path('visualisationLeads/', views.visualisation_leads, name='visualisation_leads'),
    #interface pour la maj des leads 
    path('update/',views.view_leads,name='view_leads'),
   
    #barre de recherche
    path('update/search-results/', views.search_results, name='search_results'),
    #pour le formulaire maj des laeds 
    
    path('submit-form-update/',views.update_lead,name='submit_form_update'),

    path('display-leads/search-results/', views.search_results, name='search_results'),
    #pour la suppression des leads ( affichage du tableau des leads + logique de suppression du lead )
    path('display-leads/', views.display_leads, name='display_leads'),
   path('display-leads/delete-lead/', views.delete_lead, name='delete_lead'),
    #path pour la génération des leads 
    path('GenerateLead/', views.scrapingPage, name='scraping_lead'),
    path('GenerateLead/start-scraping/' , views.start_scraping , name='start_scraping'),
    #récupération des données du fichier csv pour le nom des villes 
    path('update/<int:id>/', views.update_lead_view, name='update_lead'),
    path('GenerateLead/search-city/', views.search_city, name='search_city'),
    path('statsleads/',views.statistiques_leads,name='statistiques_leads'),
    #détails de l'entreprise 

    # AJOUT MANUEL du descriptif de mission ainsi que d'autres détails selon la pondération de l'importance du critére de besoin
    path('search_results/', views.search_results, name='search_results'),
    path('matching-cv/', views.matching_cv_view, name='matching_cv'),
    path('process_matching/', views.process_matching, name='process_matching'),
    path('upload_cv/', views.upload_cv, name='upload_cv'),
    path('delete_cv/<str:cv_id>/', views.delete_cv, name='delete_cv'),
    
    path('choix-du-lead/',views.template_choix_leads , name = 'choix_lead_job_matching'),
    #path à la vue qui se charge de renvoyer les mots clés changés du lead et proposition de vouloir les changer ou pas , puis procéder au processus du matching lead-CV 
    path('matching-lead-cv/<int:lead_id>/',views.changer_mots_cle_lead, name='lead_matched'),
    path('process_matching_v2/', views.process_matching_v2, name='process_matching_v2'),
    path('history/', views.history, name='history'),
    path('programmation-leads/',views.programmation_view,name='programmation_leads'),
    path('recup-donnees-programmees/', views.recup_donnees_programmees, name='recup_donnees_programmees'),
    path('programmation-leads/search-city/', views.search_city, name='search_city'),
    path('lead/<int:lead_id>/', views.company_detail, name='lead_detail'),
    path('GenerateLead/lead_details/', views.lead_details, name='lead_details'),
    path('cv-tech/<int:cv_id>/', views.cv_detail, name='cv_detail'),
    path('interface-cv/',views.cv_interface,name='cv_interface'),
    path('facturation/<int:fac_id>/', views.fac_detail, name='fac_detail'),
    path('process_matching_v3/', views.process_matching_v3, name='process_matching_v3'),
    path('add_comment/',views.add_comment,name='add_comment'),
    path('update_comment_status/', views.update_comment_status, name='update_comment_status'),
    path('matching/',views.matching,name='matching'),
    path('api/leads-stats/', views.get_leads_stats, name='leads_stats'),
    path('feedback/',views.feedback , name='feedback'),
    path('add_feedback/', views.add_feedback, name='add_feedback'),
    path('pin_feedback/<int:id>/', views.pin_feedback, name='pin_feedback'),
    path('unpin_feedback/<int:id>/', views.unpin_feedback, name='unpin_feedback'),
    path('commentaires/<int:cv_id>/', views.historique_commentaires, name='commentaires'),
    ]


if settings.DEBUG:
    urlpatterns += static(settings.CV_URL, document_root=settings.CV_ROOT)