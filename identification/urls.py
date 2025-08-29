from django.urls import path
from .views import (
    dashboard,
    enregistrement_membre,
    liste,
    generer_carte,
    renouveler_carte,
    detail_membre,
    modifier_membre,
    supprimer_membre,
    afficher_qrcode,
    get_image
)
from . import views



app_name = "identification"

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('enregistrement/', enregistrement_membre, name='enregistrement_membre'),
    path('liste/', liste, name='liste'),
    path("export-excel/", views.export_excel, name="export_excel"),
    path('detail/<int:membre_id>/', views.detail_membre, name='detail_membre'),
    path('modifier/<int:membre_id>/', views.modifier_membre, name='modifier_membre'),
    # URL pour générer le PDF d'un membre
    path('membre/<int:membre_id>/pdf/', views.generate_pdf, name='generate_pdf'),
    ############################################################################################################

    path('carte/<int:membre_id>/', generer_carte, name='generer_carte'),
    path('renouveler/<int:membre_id>/', renouveler_carte, name='renouveler_carte'),
    path('supprimer/<int:membre_id>/', supprimer_membre, name='supprimer_membre'),
    path('qrcode/<int:pk>/', afficher_qrcode, name='afficher_qrcode'),
    path('image/<int:membre_id>/<str:field_name>/', get_image, name='get_image'),
    ############################################################################################################
    path("reactiver/<int:membre_id>/", views.reactiver_carte, name="reactiver_carte"),
    path('cartes-renouvelees/', views.cartes_renouvelees_liste, name='cartes_renouvelees_liste'),
    ############################################################################################################
    path('duplicata/creer/', views.duplicata_creer, name="duplicata_creer"),
    path('duplicata/liste/', views.duplicata_liste, name="duplicata_liste"),
]