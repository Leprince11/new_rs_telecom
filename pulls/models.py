from django.db import models
import uuid
from django.utils import timezone

class User(models.Model):
    id_user        = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    users_name     = models.CharField(max_length=255)
    users_fname    = models.CharField(max_length=255)
    created_date   = models.DateTimeField(default=timezone.now)
    delete_date    = models.DateTimeField(null=True)
    update_date    = models.DateTimeField(null=True)
    users_phone    = models.CharField(max_length=255,null=True)
    users_company  = models.CharField(max_length=255)
    # users_tjm      = models.CharField(max_length=255,null=True)
    users_mail     = models.CharField(max_length=50,unique=True)
    users_type     = models.CharField(max_length=255)
    users_password = models.CharField(max_length=128)
    users_region   = models.CharField(max_length=255)
    users_address  = models.CharField(max_length=255)
    users_postal   =models.CharField(max_length=10,null=True)
    users_is_active= models.BooleanField(default=True)
    users_preavis  = models.BooleanField(default=True)

    class Meta:
        db_table = 'users'

class Group(models.Model):
    id_goupe = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    type_users = models.CharField(max_length=50)
    class Meta:
        db_table = 'Type_collaborateur'

class Mission(models.Model):
    id_mission = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    start_mission= models.DateTimeField()
    end_mission= models.DateTimeField()
    client_mission=models.CharField(max_length=255)

class CRA(models.Model):
    id_cra=models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    created_cra=models.DateField(auto_now_add=True)
    abscence=models.BooleanField(default=True)
    mission=models.BooleanField(default=True)
    astreintes=models.BooleanField(default=True)
    mission=models.BooleanField(default=True)
    class Meta:
        db_table = 'Compte_rendu_activite'


class Conge(models.Model):
    id_conge=models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    created_date=models.DateField(auto_now_add=True)
    delete_date=models.DateTimeField(null=True)
    update_date = models.DateTimeField(null=True)
    class Meta:
        db_table = 'Conge'

