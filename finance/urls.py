from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path('liste/', views.liste_membres_finance, name='liste_membres_finance'),
    path("historique/<int:membre_id>/", views.historique, name="historique"),
    path("ajouter/<int:membre_id>/", views.ajouter, name="ajouter"),
    path('contribution/modifier/<int:contribution_id>/', views.modifier_contribution, name='modifier_contribution'),
    path('contribution/supprimer/<int:contribution_id>/', views.supprimer_contribution, name='supprimer_contribution'),

     # 1. Facture PDF pour une contribution
    path('facture/<int:pk>/', views.generer_facture_contribution, name='generer_facture_contribution'),

    # 2. Historique d’un membre (PDF & Excel)

    path("membre/<int:membre_id>/historique.pdf", views.historique_membre_pdf, name="membre_historique_pdf"),
    path("membre/<int:membre_id>/historique.xlsx", views.historique_membre_excel, name="membre_historique_excel"),

    # 3. Historique de tous les membres (PDF & Excel)
    path("tous/historique.pdf", views.tous_historique_pdf, name="tous_historique_pdf"),
    path("tous/historique.xlsx", views.tous_historique_excel, name="tous_historique_excel"),

    ###########################################################################################################
    path('liste_operations', views.liste_operations, name="liste_operations"),
    path('ajouter/', views.ajouter_operation, name="ajouter_operation"),
    path('modifier/<int:pk>/', views.modifier_operation, name="modifier_operation"),
    path('supprimer/<int:pk>/', views.supprimer_operation, name="supprimer_operation"),
    path('detail/<int:pk>/', views.detail_operation, name="detail_operation"),
    path("operations/export/excel/", views.export_excel_operations, name="export_excel_operations"),
    path("operations/export/pdf/<str:periode>/", views.export_pdf_operations, name="export_pdf_operations"),


]
