from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import date
import uuid
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import qrcode
import os

class CustomUser(AbstractUser):
    # Niveaux hiérarchiques
    class NiveauHierarchique(models.TextChoices):
        PRESIDENT_NATIONAL = 'PRESIDENT_NATIONAL', _('Président National')
        PRESIDENT_PROVINCIAL = 'PRESIDENT_PROVINCIAL', _('Président Provincial')
        SECRETAIRE_GENERAL = 'SECRETAIRE_GENERAL', _('Secrétaire Général')
        OPERATEUR = 'OPERATEUR', _('Opérateur(trice)')
        ADMIN_SYSTEME = 'ADMIN_SYSTEME', _('Administrateur Système')

    # Champs supplémentaires
    phone = models.CharField(
        _('numéro de téléphone'),
        max_length=20,
        unique=True,
        help_text=_('Format international: +243xxxxxxxxx')
    )
    
    level = models.CharField(
        _('niveau hiérarchique'),
        max_length=20,
        choices=NiveauHierarchique.choices,
        default=NiveauHierarchique.OPERATEUR
    )
    
    photo = models.ImageField(
        _('photo de profil'),
        upload_to='users/photos/',
        null=True,
        blank=True
    )
    
    qrcode = models.ImageField(
        _('QR Code'),
        upload_to='users/qrcodes/',
        null=True,
        blank=True
    )
    
    is_verified = models.BooleanField(
        _('vérifié'),
        default=False
    )
    
    last_activity = models.DateTimeField(
        _('dernière activité'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"

    def save(self, *args, **kwargs):
        # Génération du username si vide
        if not self.username:
            self.username = self.generate_username()
            
        # Traitement de la photo avant sauvegarde
        if self.photo:
            self.resize_photo()
            
        super().save(*args, **kwargs)
        
        # Génération du QR Code après sauvegarde
        if not self.qrcode:
            self.generate_qrcode()
            super().save(update_fields=['qrcode'])

    def generate_username(self):
        """Génère un username unique basé sur le nom et prénom"""
        base = f"{self.first_name[0] if self.first_name else 'X'}{self.last_name[0] if self.last_name else 'X'}"
        base += f"{date.today().day:02d}{date.today().month:02d}"
        
        username = base.upper()
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base}{counter}".upper()
            counter += 1
            
        return username

    def resize_photo(self):
        """Redimensionne la photo de profil"""
        try:
            img = Image.open(self.photo)
            
            # Redimensionner si trop grande
            if img.width > 800 or img.height > 800:
                output_size = (800, 800)
                img.thumbnail(output_size, Image.Resampling.LANCZOS)
                
                # Sauvegarder dans un buffer
                buffer = BytesIO()
                img.save(buffer, format=img.format, quality=85)
                
                # Sauvegarder le fichier
                file_name = os.path.basename(self.photo.name)
                self.photo.save(file_name, ContentFile(buffer.getvalue()), save=False)
                
        except Exception as e:
            # Ne pas bloquer la sauvegarde si problème avec la photo
            pass

    def generate_qrcode(self):
        """Génère un QR Code avec les informations de l'utilisateur"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            data = f"USER:{self.username}\nNAME:{self.get_full_name()}\nPHONE:{self.phone}"
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Sauvegarde dans un buffer
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            
            # Sauvegarde dans le modèle
            file_name = f'qrcode_{self.username}.png'
            self.qrcode.save(file_name, ContentFile(buffer.getvalue()), save=False)
            
        except Exception as e:
            # Ne pas bloquer la sauvegarde si problème avec le QR Code
            pass

    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Retourne le prénom de l'utilisateur"""
        return self.first_name

    def send_welcome_email(self, password):
        """Envoie un email de bienvenue avec les identifiants"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = _("Bienvenue sur notre plateforme")
        message = _(
            f"Bonjour {self.get_full_name()},\n\n"
            f"Votre compte a été créé avec succès.\n\n"
            f"Voici vos identifiants :\n"
            f"Nom d'utilisateur: {self.username}\n"
            f"Mot de passe temporaire: {password}\n\n"
            f"Veuillez changer votre mot de passe après votre première connexion.\n\n"
            f"Cordialement,\n"
            f"L'équipe technique"
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False
        )