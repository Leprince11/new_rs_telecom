from django.db import models
import uuid
import pyotp # type: ignore
import qrcode # type: ignore
import qrcode.image.svg # type: ignore
from typing import Optional

class Clients(models.Model):
    id_client = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_name = models.CharField(max_length=255)
    client_location=models.CharField(max_length=255,null=True)
    client_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.client_name

class Users(models.Model):
    USER_TYPES = [
        ('con', 'Consultant'),
        ('stt', 'Freelance'),
        ('com', 'Commercial'),
        ('it', 'IT'),
        ('admin', 'Direction'),
        ('sup', 'Super Admin'),
    ]
    id_user = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    users_name = models.CharField(max_length=255)
    users_fname = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    delete_date = models.DateTimeField(null=True)
    update_date = models.DateTimeField(null=True)
    users_phone = models.CharField(max_length=255, null=True, blank=True)
    users_company = models.CharField(max_length=255)
    users_mail = models.CharField(max_length=50, unique=True)
    users_type = models.CharField(max_length=255)
    users_bio = models.CharField(max_length=255 , null=True, blank=True)
    users_password = models.CharField(max_length=128)
    users_region = models.CharField(max_length=255)
    users_address = models.CharField(max_length=255)
    users_postal = models.CharField(max_length=5, null=True)
    users_is_active = models.BooleanField(default=True)
    users_preavis = models.BooleanField(default=True)
    profile_photo = models.ImageField(upload_to='photos_profil/', null=True, blank=True)
    url_photo_profile=models.CharField(max_length=50,null=True)
    mission = models.ForeignKey('Mission', on_delete=models.CASCADE, related_name='all_mission', null=True, blank=True)
    client = models.ForeignKey('Clients', on_delete=models.SET_NULL, related_name='users', null=True, blank=True)

    class Meta:
        db_table = 'Employés'

class Groups(models.Model):
    id_group = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(Users, related_name='groups')

    class Meta:
        db_table = 'Type_Colaborateur'

class Mission(models.Model):
    id_mission = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mission_name = models.CharField(max_length=255,blank=True)
    mission_description = models.TextField(null=True,blank=True)
    mission_manager = models.CharField(max_length=100,null=True,blank=True)
    mission_start = models.DateTimeField(null=True)
    mission_end = models.DateTimeField(null=True)
    mission_created = models.DateTimeField(auto_now_add=True,null=True)
    mission_deleted = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.mission_name



class UserTwoFactorAuthData(models.Model):
    user = models.OneToOneField(
        Users,
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

