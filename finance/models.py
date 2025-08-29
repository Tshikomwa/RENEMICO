from django.db import models
from identification.models import Membre
from django.utils import timezone

class Contribution(models.Model):
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name="contributions")
    mois = models.DateField(default=timezone.now)  # Exemple : 2025-08-01 pour août 2025
    montant = models.IntegerField()
    date_paiement = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("membre", "mois")  # Un membre paie une seule fois par mois
        ordering = ["-date_paiement"]

    def __str__(self):
        return f"{self.membre.nom} {self.membre.post_nom} - {self.mois.strftime('%B %Y')}"

########################################################################################################
from django.db import models
from django.utils import timezone

class Operation(models.Model):
    TYPE_CHOICES = (
        ('ENTREE', 'Entrée'),
        ('SORTIE', 'Sortie'),
    )

    date = models.DateField(default=timezone.now)
    motif = models.CharField(max_length=255)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    percu_par = models.CharField(max_length=100)
    type_operation = models.CharField(max_length=10, choices=TYPE_CHOICES)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_type_operation_display()} - {self.date} - {self.motif} : {self.montant} FC"
