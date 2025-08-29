from django.db import models
from django.utils import timezone
import uuid
from datetime import timedelta
from django.core.exceptions import ValidationError

class Membre(models.Model):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    PROVINCE_CHOICES = [
        ('BAS-UELE', 'Bas-Uele'),
        ('EQUATEUR', 'Équateur'),
        ('HAUT-KATANGA', 'Haut-Katanga'),
        ('HAUT-LOMAMI', 'Haut-Lomami'),
        ('HAUT-UELE', 'Haut-Uele'),
        ('ITURI', 'Ituri'),
        ('KASAI', 'Kasaï'),
        ('KASAI-CENTRAL', 'Kasaï-Central'),
        ('KASAI-ORIENTAL', 'Kasaï-Oriental'),
        ('KINSHASA', 'Kinshasa'),
        ('KONGO-CENTRAL', 'Kongo-Central'),
        ('KWANGO', 'Kwango'),
        ('KWILU', 'Kwilu'),
        ('LOMAMI', 'Lomami'),
        ('LUALABA', 'Lualaba'),
        ('MAI-NDOMBE', 'Mai-Ndombe'),
        ('MANIEMA', 'Maniema'),
        ('MONGALA', 'Mongala'),
        ('NORD-KIVU', 'Nord-Kivu'),
        ('NORD-UBANGI', 'Nord-Ubangi'),
        ('SANKURU', 'Sankuru'),
        ('SUD-KIVU', 'Sud-Kivu'),
        ('SUD-UBANGI', 'Sud-Ubangi'),
        ('TANGANYIKA', 'Tanganyika'),
        ('TSHOPO', 'Tshopo'),
        ('TSHUAPA', 'Tshuapa'),
    ]
    
    CATEGORIE_CHOICES = [
        ('Membre Honneur', "Membre d'Honneur"),
        ('Membre Effectif', "Membre Effectif"),
        ('Membre Fondateur', "Membre Fondateur"),
        ('Membre Co-fondateur', "Membre Co-fondateur"),
    ]

    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
    ]
    
    # Informations de base
    code = models.CharField(max_length=20, unique=True, blank=True)
    province = models.CharField(max_length=30, choices=PROVINCE_CHOICES)
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES)
    fonction = models.CharField(max_length=15,blank=True,null=True,default="Membre")
    site = models.CharField(max_length=150,blank=True,null=True)
    nom = models.CharField(max_length=100)
    post_nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)
    
    # Contact
    adresse = models.CharField(max_length=200, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Identification
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    qrcode = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    
    # Dates
    date_enregistrement = models.DateField(default=timezone.now)
    date_mise_a_jour = models.DateField(auto_now=True)
    date_expiration = models.DateField(null=True, blank=True)  # <- Ajouter ce champ
    
    # Autres
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    
    profession = models.CharField(max_length=100, blank=True, null=True)
    observations = models.TextField(blank=True, null=True)

    # Renouvellemnt
    carte_renouvelee = models.BooleanField(default=False)

     # ✅ Ta validation se met ici
    def clean(self):
        """Validation personnalisée : l’âge doit être >= 18 ans"""
        super().clean()
        if self.date_naissance:
            today = timezone.now().date()
            age = today.year - self.date_naissance.year - (
                (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
            )
            if age < 18:
                raise ValidationError({"date_naissance": "Le membre doit avoir au moins 18 ans."})
            
    class Meta:
        verbose_name = "Membre"
        verbose_name_plural = "Membres"
        ordering = ['nom', 'post_nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.post_nom} {self.prenom} ({self.code})"

    def save(self, *args, **kwargs):
        # ✅ Conversion automatique en MAJUSCULES
        if self.nom:
            self.nom = self.nom.upper()
        if self.post_nom:
            self.post_nom = self.post_nom.upper()
        if self.prenom:
            self.prenom = self.prenom.upper()
        if self.lieu_naissance:
            self.lieu_naissance = self.lieu_naissance.upper()
        if self.fonction:
            self.fonction = self.fonction.upper()
        if self.site:
            self.site = self.site.upper()
        if self.profession:
            self.profession = self.profession.upper()
        if self.adresse:
            self.adresse = self.adresse.upper()
        
        # ✅ Génération automatique du code si absent
        if not self.code:
            self.code = str(uuid.uuid4())[:8].upper()

        # ✅ Date d’expiration auto si vide
        if not self.date_expiration:
            self.date_expiration = self.date_enregistrement + timedelta(days=3*365)

        super().save(*args, **kwargs)

    @property
    def est_expiree(self):
        """Retourne True si la carte est expirée"""
        return self.date_expiration and self.date_expiration < timezone.now().date()



###############################################################################################################
   
class Duplicata(models.Model):
    membre = models.ForeignKey(
        Membre,
        on_delete=models.CASCADE,
        related_name="duplicata_set"  # <-- anciennement "duplicatas"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    numero_carte = models.CharField(max_length=100)

    def __str__(self):
        return f"Duplicata de {self.membre.nom} ({self.date_creation.date()})"


