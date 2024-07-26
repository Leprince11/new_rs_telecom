from pulls.models import Users, Mission
from django.core.exceptions import ValidationError
import uuid
from django.db import models

class Justificatifs(models.Model):
    id_justificatif = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_justificatif = models.CharField(max_length=255)
    description = models.TextField()
    name_justificatif = models.CharField(max_length=255)
    montant = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name_justificatif
    
class CompteRendu(models.Model):
    id_mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='comptes_rendus')
    id_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='comptes_rendus')
    date_created = models.DateTimeField(auto_now_add=True)
    id_justificatif = models.ForeignKey(Justificatifs, on_delete=models.CASCADE, related_name='comptes_rendus')

    def __str__(self):
        return f"Compte Rendu {self.id}"
    

class CRA(models.Model):  
    choose_categorie = (
        (1, "Mission"),
        (2, "Absence"),
        (3, "Ferie"),
    )
    id_cra = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_cra = models.DateField(auto_now_add=True, null=True)
    categorie = models.CharField(max_length=255,choices=choose_categorie,default=1)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)



    def __str__(self):
        return f"{self.categorie} from {self.start_date} to {self.end_date}"

    class Meta:
        db_table = 'compte_rendu_activite'
   