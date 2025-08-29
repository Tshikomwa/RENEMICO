from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser

LEVEL_CHOICES = [
    ('PRESIDENT_NATIONAL', 'Président National'),
    ('PRESIDENT_PROVINCIAL', 'Président Provincial'),
    ('SECRETAIRE_GENERAL', 'Secrétaire Général'),
    ('OPERATEUR', 'Opérateur(trice)'),
    ('ADMIN_SYSTEME', 'Administrateur Système'),
]

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        label="Prénom",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'})
    )
    
    last_name = forms.CharField(
        label="Nom",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'})
    )
    
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'})
    )
    
    phone = forms.CharField(
        label="Téléphone",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre numéro de téléphone'})
    )
    
    level = forms.ChoiceField(
        label="Niveau hiérarchique",
        choices=LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    photo = forms.ImageField(
        label="Photo de profil",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'level', 'photo', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmation du mot de passe'})
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")
        return email
        
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exists():
            raise ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return phone

#########################################################################################################################

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre nom d\'utilisateur'})
    )
    
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrez votre mot de passe'})
    )
    
    remember_me = forms.BooleanField(
        label="Se souvenir de moi",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

##############################################################################################################################
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from datetime import date
import random
import re
from django.core.mail import send_mail
from django.conf import settings
from PIL import Image
from io import BytesIO

LEVEL_CHOICES = [
    ('PRESIDENT_NATIONAL', 'Président National'),
    ('PRESIDENT_PROVINCIAL', 'Président Provincial'),
    ('SECRETAIRE_GENERAL', 'Secrétaire Général'),
    ('OPERATEUR', 'Opérateur(trice)'),
    ('ADMIN_SYSTEME', 'Administrateur Système'),
]

class CustomUserForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Prénom",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'})
    )
    
    last_name = forms.CharField(
        label="Nom",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'})
    )
    
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'})
    )
    
    phone = forms.CharField(
        label="Téléphone",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre numéro de téléphone'})
    )
    
    level = forms.ChoiceField(
        label="Niveau hiérarchique",
        choices=LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    photo = forms.ImageField(
        label="Photo de profil",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'level', 'photo')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'})
        
        if self.instance and self.instance.pk:
            self.setup_for_edit()
        else:
            self.setup_for_create()

    def setup_for_edit(self):
        """Configuration spécifique pour l'édition"""
        # Ne pas permettre de changer l'email pour les non-admins
        if not (self.instance and self.instance.is_superuser):
            self.fields['email'].disabled = True

    def setup_for_create(self):
        """Configuration spécifique pour la création"""
        # Générer un mot de passe par défaut
        self.fields['password'] = forms.CharField(
            widget=forms.HiddenInput(),
            required=False,
            initial=self.generate_temp_password()
        )

    def clean_email(self):
        email = self.cleaned_data.get('email').lower().strip()
        if not email:
            raise forms.ValidationError("Ce champ est obligatoire")
            
        # Vérification de l'unicité
        queryset = CustomUser.objects.filter(email=email)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
            
        if queryset.exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée")
            
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Ce champ est obligatoire")
            
        # Nettoyage du numéro de téléphone
        phone = re.sub(r'[^\d+]', '', phone)
        
        if not phone.startswith('+243'):
            phone = '+243' + phone[-9:]
            
        if len(phone) != 13 or not phone[1:].isdigit():
            raise forms.ValidationError("Format invalide. Exemple: +243812345678")
            
        # Vérification de l'unicité
        queryset = CustomUser.objects.filter(phone=phone)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
            
        if queryset.exists():
            raise forms.ValidationError("Ce numéro de téléphone est déjà utilisé")
            
        return phone

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        
        # Pour l'édition, la photo existante est conservée si aucune nouvelle n'est fournie
        if self.instance and self.instance.pk and not photo:
            return self.instance.photo
            
        if not photo and not self.instance.pk:
            raise forms.ValidationError("Une photo de profil est requise")
            
        if photo:
            # Validation de l'image
            try:
                img = Image.open(photo)
                
                # Vérification du format
                if img.format not in ['JPEG', 'PNG']:
                    raise forms.ValidationError("Seuls les formats JPEG et PNG sont acceptés")
                    
                # Vérification de la taille
                if photo.size > 2 * 1024 * 1024:
                    raise forms.ValidationError("La taille maximale est de 2MB")
                    
                # Redimensionnement si nécessaire
                if img.width > 800 or img.height > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    
                    # Sauvegarde de l'image redimensionnée
                    buffer = BytesIO()
                    img.save(buffer, format=img.format, quality=85)
                    photo.file = buffer
                    photo.size = buffer.tell()
                    
            except Exception as e:
                raise forms.ValidationError(f"Erreur de traitement de l'image: {str(e)}")
            
        return photo

    def save(self, commit=True):
        """Sauvegarde de l'utilisateur avec gestion des cas spéciaux"""
        user = super().save(commit=False)
        
        # Génération du username pour les nouveaux utilisateurs
        if not user.username:
            user.username = self.generate_username(user)
            
        # Gestion du mot de passe pour les nouveaux utilisateurs
        if not user.pk and 'password' in self.cleaned_data:
            user.set_password(self.cleaned_data['password'])
            
        if commit:
            user.save()
            
            # Envoi d'email pour les nouveaux utilisateurs
            if not user.pk and 'password' in self.cleaned_data:
                self.send_welcome_email(user, self.cleaned_data['password'])
                
        return user

    def generate_username(self, user):
        """Génère un username unique basé sur les informations de l'utilisateur"""
        base = f"{user.first_name[0] if user.first_name else 'X'}{user.last_name[0] if user.last_name else 'X'}"
        base += f"{date.today().day:02d}{date.today().month:02d}"
        
        username = base
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1
            
        return username.upper()

    def generate_temp_password(self):
        """Génère un mot de passe temporaire sécurisé"""
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        return f"REN-{''.join(random.choices(chars, k=6))}"

    def send_welcome_email(self, user, password):
        """Envoie les informations de connexion par email"""
        subject = "Vos identifiants - Plateforme de Gestion"
        message = (
            f"Bonjour {user.first_name} {user.last_name},\n\n"
            f"Votre compte a été créé avec succès.\n\n"
            f"Identifiant: {user.username}\n"
            f"Mot de passe temporaire: {password}\n\n"
            f"Veuillez changer votre mot de passe après votre première connexion.\n\n"
            f"Cordialement,\n"
            f"L'équipe technique"
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )