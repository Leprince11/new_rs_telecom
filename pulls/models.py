from django.db import models
import uuid
import pyotp
import qrcode
import qrcode.image.svg
from typing import Optional

class User(models.Model):
    id_user        = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    users_name     = models.CharField(max_length=255)
    users_fname    = models.CharField(max_length=255)
    created_date   = models.DateTimeField(auto_now_add=True)
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
    verifopt       = models.BooleanField(default=False)

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

    categorie_choices={
        '1':'Mission',
        '2':'congé',
    }

    id_cra=models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    created_cra=models.DateField(auto_now_add=True)
    start_date = models.DateField(default=None)
    end_date = models.DateField(default=None)
    categorie=models.CharField(max_length=255,choices=categorie_choices,default='1')
    class Meta:
        db_table = 'Compte_rendu_activite'


class Conge(models.Model):
    id_conge=models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    created_date=models.DateField(auto_now_add=True)
    delete_date=models.DateTimeField(null=True)
    update_date = models.DateTimeField(null=True)
    class Meta:
        db_table = 'Conge'


class UserTwoFactorAuthData(models.Model):
    user = models.OneToOneField(
        User,
        related_name='two_factor_auth_data',
        on_delete=models.CASCADE
    )
    otp_secret = models.CharField(max_length=255)
    session_identifier = models.CharField(max_length=255,default='default_value')
    qr_code=models.CharField(max_length=255,default='None')
    is_active=models.BooleanField(default=False)

    def generate_qr_code(self, name: Optional[str] = None) -> str:
        totp = pyotp.TOTP(self.otp_secret)
        qr_uri = totp.provisioning_uri(
            name=name,
            issuer_name='R&S-TELECOM'
        )

        image_factory = qrcode.image.svg.SvgPathImage
        qr_code_image = qrcode.make(
            qr_uri,
            image_factory=image_factory
        )

        return qr_code_image.to_string().decode('utf_8')
    
    def validate_otp(self, otp: str) -> bool:
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(otp)
    
    def rotate_session_identifier(self):
        self.session_identifier = uuid.uuid4()
        self.save(update_fields=["session_identifier"])

    class Meta:
        db_table = "pulls_usertwofactorauthdata"

