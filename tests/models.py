from django.db import models 
from pulls.models import Users  # Import du modèle User de l'application pulls

class Leads(models.Model):
    nom = models.CharField(max_length=255, null=False)  # company_name
    nom_offre = models.CharField(max_length=255, null=False)  # job_title
    nombre_offres = models.IntegerField(null=False, default=1)
    localisation_du_lead = models.CharField(max_length=255, null=False)  # location
    porteur_lead = models.CharField(max_length=255, null=True,default='non mentionné')
    url_profil_porteur_lead = models.URLField(null=True,default='non mentionné')
    adresse_mail_de_contact = models.EmailField(null=True,default='non mentionné')
    telephone = models.CharField(max_length=20, null=True,default='non mentionné')
    secteur_activite = models.CharField(max_length=255, null=True,default='non mentionné')
    taille_entreprise = models.CharField(max_length=255, null=True,default='non mentionné')
    chiffre_d_affaires = models.CharField(max_length=255, null=True,default='non mentionné')
    source_lead = models.CharField(max_length=255, null=True, default='apec')  
    statut_du_lead = models.CharField(max_length=50, choices=[('nouveau', 'Nouveau'), ('en_cours', 'En cours'), ('converti', 'Converti')], null=True)
    date_publication_offre = models.DateField(null=True)
    date_maj_lead = models.DateField(null=True)
    remarques = models.TextField(null=True, blank=True)
    priorite = models.CharField(max_length=50, choices=[('haute', 'Haute'), ('moyenne', 'Moyenne'), ('basse', 'Basse')], null=True)
    description_job = models.TextField(null=True)  # job_description
    lien_vers_lead = models.URLField(null=True)
    type_contrat = models.CharField(max_length=255, null=True,default='CDI')  # Added field for contract type

    class Meta:
        db_table = 'leads'  # Définir explicitement le nom de la table
        app_label = 'tests'

    def __str__(self):
        return self.nom


class Feedback(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='nouveau')
    is_pinned = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_modified = models.BooleanField(default=False)