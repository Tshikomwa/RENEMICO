from django import forms
from .models import Contribution

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['mois', 'montant']
        widgets = {
            'mois': forms.DateInput(
                attrs={'type': 'month', 'class': 'form-control'},
                format='%Y-%m'
            ),
            'montant': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Montant en entier'}
            ),
        }
        labels = {
            'mois': 'Mois de la contribution',
            'montant': 'Montant',
        }

    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à zéro.")
        return montant

#######################################################################################################
from django import forms
from .models import Operation

class OperationForm(forms.ModelForm):
    class Meta:
        model = Operation
        fields = ['date', 'motif', 'montant', 'percu_par', 'type_operation']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'motif': forms.TextInput(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'percu_par': forms.TextInput(attrs={'class': 'form-control'}),
            'type_operation': forms.Select(attrs={'class': 'form-select'}),
        }
