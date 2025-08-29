from django import forms
from .models import Membre
from django.utils import timezone
from django.core.exceptions import ValidationError

class MembreForm(forms.ModelForm):
    # Champ date_naissance personnalisé avec Flatpickr (JJ-MM-AAAA)
    date_naissance = forms.DateField(
        input_formats=['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y'],  # JJ-MM-AAAA, AAAA-MM-JJ, JJ/MM/AAAA
        widget=forms.TextInput(attrs={
            'class': 'date-picker form-control',
            'placeholder': 'JJ-MM-AAAA'
        })
    )

    class Meta:
        model = Membre
        fields = '__all__'
        exclude = ['code', 'qrcode', 'date_enregistrement', 'date_mise_a_jour', 'date_expiration']
        widgets = {
            'observations': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'province': forms.Select(attrs={'class': 'form-select'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),  # ✅ nouveau champ
        }
        labels = {
            'nom': 'Nom',
            'post_nom': 'Post-nom',
            'prenom': 'Prénom',
            'lieu_naissance': 'Lieu de naissance',
            'date_naissance': 'Date de naissance',
            'statut': 'Statut du membre',  # ✅ ajout du label
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajout des classes Bootstrap par défaut
        for field in self.fields:
            if field not in ['sexe', 'province', 'categorie', 'statut', 'observations', 'adresse', 'date_naissance']:
                if self.fields[field].widget.__class__.__name__ not in ['CheckboxInput', 'RadioSelect']:
                    self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Personnalisation spécifique
        self.fields['photo'].required = False
        self.fields['telephone'].widget.attrs.update({'placeholder': '+243...'})
        self.fields['email'].widget.attrs.update({'placeholder': 'exemple@email.com'})

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone and not telephone.isdigit():
            raise ValidationError("Le numéro de téléphone ne doit contenir que des chiffres")
        return telephone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email
    
    def clean_date_naissance(self):
        date_naissance = self.cleaned_data.get('date_naissance')
        if date_naissance:
            today = timezone.now().date()
            # Vérification futur
            if date_naissance > today:
                raise ValidationError("La date de naissance ne peut pas être dans le futur")
            # Vérification âge ≥ 18
            age = today.year - date_naissance.year - (
                (today.month, today.day) < (date_naissance.month, date_naissance.day)
            )
            if age < 18:
                raise ValidationError("Le membre doit avoir au moins 18 ans")
        return date_naissance



###################################################################################################################
from django import forms
from .models import Duplicata

class DuplicataForm(forms.ModelForm):
    class Meta:
        model = Duplicata
        fields = ['membre', 'numero_carte']
        widgets = {
            'membre': forms.Select(attrs={'class': 'form-select'}),
            'numero_carte': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de la carte'}),
        }
        labels = {
            'membre': 'Membre',
            'numero_carte': 'Numéro de la carte',
        }

    def clean_numero_carte(self):
        numero_carte = self.cleaned_data.get('numero_carte')
        if Duplicata.objects.filter(numero_carte=numero_carte).exists():
            raise forms.ValidationError("Ce numéro de duplicata existe déjà.")
        return numero_carte
