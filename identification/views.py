# identification/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from django.db.models import Q
from django.forms import modelform_factory
from io import BytesIO
import qrcode
from PIL import Image, ExifTags
from .forms import MembreForm
from .models import Membre
from django.shortcuts import render
from .models import Membre
from django.utils import timezone
from django.db.models import Sum
from finance.models import Operation
from finance.models import Contribution


# Vue pour le tableau de bord identification
##################################################################################################

def dashboard(request):
    today = timezone.now().date()

    # Membres actifs
    membres_actifs = Membre.objects.filter(statut="actif").count()

    # Membres inactifs
    membres_inactifs = Membre.objects.filter(statut="inactif").count()

    # Cartes valides (non expirées)
    cartes_valides = Membre.objects.filter(date_expiration__gte=today).count()

    # Cartes expirées
    cartes_expirees = Membre.objects.filter(date_expiration__lt=today).count()

    # Cartes renouvelées
    cartes_renouvelees = Membre.objects.filter(carte_renouvelee=True).count()

    # Duplicatas # Comptage des membres ayant au moins 1 duplicata
    duplicatas = Membre.objects.filter(duplicata_set__isnull=False).distinct().count()

    total_contributions = Contribution.objects.aggregate(Sum('montant'))['montant__sum'] or 0
        
    # Autres données de statistiques que vous pourriez vouloir
    nombre_contributions = Contribution.objects.count()
    moyenne_contributions = total_contributions / nombre_contributions if nombre_contributions > 0 else 0

    # Finance
    total_entrees = Operation.objects.filter(type_operation="ENTREE").aggregate(Sum('montant'))['montant__sum'] or 0
    total_sorties = Operation.objects.filter(type_operation="SORTIE").aggregate(Sum('montant'))['montant__sum'] or 0
    solde = total_entrees - total_sorties



    context = {
        "membres_actifs": membres_actifs,
        "membres_inactifs": membres_inactifs,
        "cartes_valides": cartes_valides,
        "cartes_expirees": cartes_expirees,
        "cartes_renouvelees": cartes_renouvelees,
        "duplicatas": duplicatas,

    # Résumé financier
        "total_contributions": total_contributions,
        "nombre_contributions": nombre_contributions,
        "moyenne_contributions": moyenne_contributions,
        "total_entrees": f"{total_entrees:,.2f}",
        "total_sorties": f"{total_sorties:,.2f}",
        "solde": f"{solde:,.2f}",
    }

    return render(request, "dashboard.html", context)



#################################################################################################
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect
from .forms import MembreForm
from .models import Membre

def enregistrement_membre(request):
    enregistrement_reussi = False
    echec_enregistrement = False

    if request.method == 'POST':
        form = MembreForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                membre = form.save(commit=False)
                
                # Dates d'enregistrement et mise à jour
                membre.date_enregistrement = timezone.now().date()
                membre.date_mise_a_jour = timezone.now().date()
                
                # Générer la date d'expiration 3 ans après l'enregistrement
                membre.date_expiration = membre.date_enregistrement + timedelta(days=365*3)
                
                # Sauvegarde initiale
                membre.save()
                
                # Génération du QR code
                qr_code = generer_qrcode(membre)
                membre.qrcode.save(f'qrcode_{membre.pk}.png', qr_code)
                membre.save()
                
                enregistrement_reussi = True
                return redirect('identification:liste')
            except Exception as e:
                echec_enregistrement = True
                print("❌ Erreur lors de l'enregistrement :", e)
        else:
            echec_enregistrement = True
            print("❌ Erreurs du formulaire :", form.errors)
    else:
        form = MembreForm()

    context = {
        'form': form,
        'enregistrement_reussi': enregistrement_reussi,
        'echec_enregistrement': echec_enregistrement
    }
    return render(request, 'enregistrement.html', context)


########################################################################################
# Vue pour la liste des membres
from django.shortcuts import render
from django.db.models import Q, Count
from .models import Membre

def liste(request):
    membres = Membre.objects.all()
     # Membres actifs
    membres_actifs = Membre.objects.filter(statut="actif").count()

    # Membres inactifs
    membres_inactifs = Membre.objects.filter(statut="inactif").count()

    # Ajoutez ces lignes dans votre vue
    hommes_count = Membre.objects.filter(sexe="M").count()
    femmes_count = Membre.objects.filter(sexe="F").count()

    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        membres = membres.filter(
            Q(nom__icontains=search_query) |
            Q(post_nom__icontains=search_query) |
            Q(prenom__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(province__icontains=search_query) |
            Q(categorie__icontains=search_query) |
            Q(statut__icontains=search_query)  # ✅ ajouté
        )

    # Tri par date d'enregistrement (du plus récent au plus ancien)
    membres = membres.order_by('-date_enregistrement')

    # Total
    total_membres = membres.count()

    # Statistiques (par sexe, catégorie, province)
    stats_sexes = membres.values('sexe').annotate(total=Count('sexe'))
    stats_categories = membres.values('categorie').annotate(total=Count('categorie'))
    stats_provinces = membres.values('province').annotate(total=Count('province'))
    

    context = {
        'membres': membres,
        'total_membres': total_membres,
        'membres_actifs': membres_actifs,  # Ajouté
        'membres_inactifs': membres_inactifs,  # Ajouté
        'hommes_count': hommes_count,
        'femmes_count': femmes_count,
        'search_query': search_query,
        'stats_sexes': stats_sexes,
        'stats_categories': stats_categories,
        'stats_provinces': stats_provinces,
        'SEXE_CHOICES': Membre._meta.get_field('sexe').choices,
        'CATEGORIE_CHOICES': Membre._meta.get_field('categorie').choices,
        'PROVINCE_CHOICES': Membre._meta.get_field('province').choices,
        'show_finance_buttons': False,  # 👈 Ajouté ici
    }
    return render(request, 'liste.html', context)


######################################################################################


######################################################################################
# identification/views.py
from django.http import HttpResponse
from openpyxl import Workbook
from .models import Membre

def export_excel(request):
    # Création du fichier Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Membres"

    # En-têtes du tableau
    headers = [
        "Code", "Nom", "Post-Nom", "Prénom", "Sexe",
        "Catégorie", "Province", "Statut"
    ]
    ws.append(headers)

    # Récupération des données
    membres = Membre.objects.all()

    for membre in membres:
        ws.append([
            membre.code,
            membre.nom,
            membre.post_nom,
            membre.prenom,
            membre.get_sexe_display(),
            membre.get_categorie_display(),
            membre.get_province_display(),
            "Actif" if membre.statut == "actif" else "Inactif"
        ])

    # Réponse HTTP avec fichier Excel
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="membres.xlsx"'
    wb.save(response)
    return response

######################################################################################

# Vue pour voir les détails d'un membre
def detail_membre(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    return render(request, 'detail.html', {'membre': membre})
######################################################################################
# Vue pour modifier un membre
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from .models import Membre
from .forms import MembreForm   # ✅ importe ton vrai formulaire

# Vue pour modifier un membre
def modifier_membre(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    modification_reussie = False
    echec_modification = False

    if request.method == 'POST':
        form = MembreForm(request.POST, request.FILES, instance=membre)
        if form.is_valid():
            try:
                membre = form.save(commit=False)
                membre.date_mise_a_jour = timezone.now().date()
                membre.save()

                # ⚡ Si tu veux regénérer un QR code à chaque modification :
                qr_code = generer_qrcode(membre)
                membre.qrcode.save(f'qrcode_{membre.pk}.png', qr_code)
                membre.save()

                modification_reussie = True
                return redirect('identification:detail_membre', membre_id=membre.id)
            except Exception as e:
                echec_modification = True
                print("❌ Erreur lors de la modification :", e)
        else:
            echec_modification = True
            print("❌ Erreurs du formulaire :", form.errors)
    else:
        form = MembreForm(instance=membre)

    context = {
        'form': form,
        'membre': membre,
        'modification_reussie': modification_reussie,
        'echec_modification': echec_modification
    }
    return render(request, 'modifier.html', context)

######################################################################################
# Vue pour générer une carte d'identité
def generer_carte(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    
    if not membre.qrcode:
        qr_code = generer_qrcode(membre)
        membre.qrcode.save(f'qrcode_{membre.pk}.png', qr_code)
        membre.save()
    
    return render(request, 'carte.html', {'membre': membre})

###################################################################################

# Vue pour renouveler une carte
def renouveler_carte(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    membre.date_mise_a_jour = timezone.now()
    
    # Regénérer le QR code
    qr_code = generer_qrcode(membre)
    membre.qrcode.save(f'qrcode_{membre.pk}.png', qr_code)
    membre.save()
    
    return redirect('generer_carte', membre_id=membre.id)

#########################################################################################
# Fonction pour générer le QR code
def generer_qrcode(membre, size=200):
    date_enregistrement = membre.date_enregistrement.strftime('%d-%m-%Y')
    

    content = (
    f"Code : {membre.code}\n"
    f"Nom : {membre.nom}\n"
    f"Post-Nom : {membre.post_nom}\n"
    f"Prénom : {membre.prenom}\n"
    f"Catégorie : {membre.categorie}\n"
    f"Date d'enregistrement : {date_enregistrement}\n"
    "À vérifier l’authenticité sur www.renemico.com"
)

    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size))

    image_stream = BytesIO()
    img.save(image_stream, format='PNG')
    image_stream.seek(0)

    return ContentFile(image_stream.getvalue(), f'qrcode_{membre.pk}.png')

##########################################################################################
# Vue pour afficher le QR code
def afficher_qrcode(request, pk):
    membre = get_object_or_404(Membre, pk=pk)
    
    if not membre.qrcode:
        qr_code = generer_qrcode(membre)
        membre.qrcode.save(f'qrcode_{membre.pk}.png', qr_code)
        membre.save()
    
    return HttpResponse(membre.qrcode.read(), content_type="image/png")

##############################################################################

# Vue pour supprimer un membre
def supprimer_membre(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    
    if request.method == 'POST':
        membre.delete()
        return redirect('identification:liste')
    
    return render(request, 'supprimer.html', {'membre': membre})

########################################################################################
from django.http import HttpResponse
from PIL import Image, ExifTags
from io import BytesIO

def get_image(request, membre_id, field_name):
    membre = get_object_or_404(Membre, id=membre_id)

    if field_name == 'photo':
        field_data = membre.photo
    elif field_name == 'qrcode':
        field_data = membre.qrcode
    else:
        return HttpResponse("Champ image invalide", status=400)

    if not field_data:
        return HttpResponse("Image non trouvée", status=404)

    try:
        # Ouvrir l'image
        image = Image.open(field_data.path)

        # Corriger l'orientation EXIF si nécessaire
        try:
            exif = image._getexif()
            if exif:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                
                orientation_value = exif.get(orientation)
                
                if orientation_value == 3:
                    image = image.rotate(180, expand=True)
                elif orientation_value == 6:
                    image = image.rotate(270, expand=True)
                elif orientation_value == 8:
                    image = image.rotate(90, expand=True)
        except:
            pass

        # Préparer la réponse
        image_bytes = BytesIO()
        format_extension = field_data.path.split('.')[-1].lower()
        
        if format_extension in ['jpeg', 'jpg']:
            image_format = 'JPEG'
        elif format_extension == 'png':
            image_format = 'PNG'
        else:
            return HttpResponse("Format d'image non supporté", status=400)

        image.save(image_bytes, format=image_format)
        image_bytes.seek(0)

        return HttpResponse(image_bytes.read(), content_type=f"image/{image_format.lower()}")

    except Exception as e:
        return HttpResponse(f"Erreur de traitement de l'image: {str(e)}", status=500)
    
##############################################################################################################
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .models import Membre

def reactiver_carte(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    aujourd_hui = timezone.now().date()

    # Vérifier si la carte est encore valide
    expiration_reelle = membre.date_expiration
    if expiration_reelle > aujourd_hui:
        # Carte encore valide : ne pas réactiver
        messages.warning(
            request,
            f"La carte de {membre.nom} {membre.post_nom} est encore valide jusqu'au {expiration_reelle:%d/%m/%Y}. "
            "Si la carte a été perdue ou endommagée, veuillez créer un duplicata plutôt que de tenter une réactivation. "
            "Si le compte est inactif, veuillez changer le statut en actif."
        )
    else:
        # Carte expirée : prolongation de 3 ans à partir de la dernière expiration
        nouvelle_expiration = membre.date_expiration + timedelta(days=3*365)
        membre.date_expiration = nouvelle_expiration
        membre.statut = "actif"
        membre.save()
        messages.success(
            request,
            f"La carte de {membre.nom} {membre.post_nom} a été réactivée avec succès jusqu'au {membre.date_expiration:%d/%m/%Y}."
        )

    return redirect("identification:dashboard")


################################################################################################################
# views.py
from django.shortcuts import render
from .models import Membre

def cartes_renouvelees_liste(request):
    # Tous les membres dont la carte a été renouvelée
    membres_renouveles = Membre.objects.filter(carte_renouvelee=True).order_by('-date_mise_a_jour')

    context = {
        'membres': membres_renouveles
    }
    return render(request, 'cartes_renouvelees_liste.html', context)

################################################################################################################
from django.shortcuts import render, redirect
from .models import Membre, Duplicata
from .forms import DuplicataForm

def duplicata_creer(request):
    if request.method == "POST":
        form = DuplicataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('identification:duplicata_liste')
    else:
        form = DuplicataForm()
    return render(request, "duplicata_form.html", {"form": form})
#################################################################################################################

from django.shortcuts import render, redirect
from .models import Membre, Duplicata
from .forms import DuplicataForm

def duplicata_liste(request):
    # Récupère tous les duplicatas, éventuellement par ordre décroissant
    duplicatas = Duplicata.objects.select_related('membre').order_by('-date_creation')
    
    context = {
        "duplicatas": duplicatas,
    }
    return render(request, "duplicata_liste.html", context)

##############################################################################################################
# 1. IMPORTS
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, landscape
from io import BytesIO
from django.shortcuts import get_object_or_404
from .models import Membre
import os
from datetime import datetime
from reportlab.lib.colors import black, red, blue
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageEnhance
from django.contrib.staticfiles import finders
from PIL import Image as PILImage

def generate_pdf(request, membre_id):
    # Récupérer les données du membre
    membre = get_object_or_404(Membre, id=membre_id)

    # Création du PDF en format paysage
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Chemin pour le logo
    logo_path = finders.find('images/logo2.png')  # Rechercher le fichier dans les fichiers statiques

    if logo_path:  # Si le logo est trouvé
        c.drawImage(logo_path, width - 145, height - 140, width=1.9*inch, height=1.9*inch)
    else:
        c.drawString(width - 180, height - 100, "Logo non disponible")

    # Agrandissement et placement des en-têtes, centrés sur la gauche
    c.setFont("Helvetica-Bold", 25)  # Taille augmentée pour plus de lisibilité
    c.setFillColor(black)  # Définir la couleur du texte sur noir
    c.drawCentredString(width / 2 - 65, height - 53, "REPUBLIQUE DEMOCRATIQUE DU CONGO")

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(blue)  # Définir la couleur du texte sur rouge
    c.drawCentredString(width / 2 - 65, height - 83, "REGROUPEMENT DES NEGOCIANTS MINIERS DU CONGO")

    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(red)  # Définir la couleur du texte sur bleu
    c.drawCentredString(width / 2 - 65, height - 123, "RENEMICO")

    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(black)  # Définir la couleur du texte sur noir
    c.drawCentredString(width / 2 - 65, height - 143, "*******************************************************************************************************************")

    c.setFont("Helvetica-Bold", 40)
    c.setFillColor(blue)  # Définir la couleur du texte sur bleu
    c.drawCentredString(width / 2 - 65, height - 178, "CARTE DE MEMBRE")

    # === Ajouter un logo en arrière-plan (filigrane) ===


    # chemin vers ton logo
    watermark_path = finders.find('images/logo2.png')

    if watermark_path and os.path.exists(watermark_path):
        # Ouvrir avec PIL
        wm_img = Image.open(watermark_path).convert("RGBA")

        # Réduire l’opacité (0 = transparent, 1 = opaque)
        alpha = 0.12  
        enhancer = ImageEnhance.Brightness(wm_img.split()[3])  # canal alpha
        wm_img.putalpha(enhancer.enhance(alpha))

        # Sauvegarde temporaire en PNG (avec transparence)
        temp_wm = "temp_watermark.png"
        wm_img.save(temp_wm, format="PNG")

        # Placer au centre de la page
        wm_reader = ImageReader(temp_wm)
        c.drawImage(
            wm_reader,
            100, 100,  # position bas-gauche (ajuste selon besoin)
            width - 200, height - 200,  # couvre presque toute la page
            mask="auto"
        )

        # Supprimer le temporaire
        os.remove(temp_wm)

    # Placer la photo du membre à gauche

    if membre.photo:
        photo_path = membre.photo.path
        if os.path.exists(photo_path):
            # Ouvrir l'image avec PIL pour vérifier l'orientation
            img = Image.open(photo_path)

            # Vérifier et appliquer la rotation en fonction des métadonnées EXIF
            try:
                # Récupérer les métadonnées EXIF
                exif = img._getexif()
                if exif is not None:
                    orientation = exif.get(0x0112)

                    # Appliquer la rotation nécessaire
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError):
                # Pas de métadonnées EXIF ou erreur de lecture
                pass

            # Convertir en RGB si l'image a un canal alpha (RGBA)
            if img.mode in ('RGBA', 'LA'):
                # Créer un fond blanc
                background = Image.new('RGB', img.size, (255, 255, 255))
                # Coller l'image sur le fond blanc en préservant l'alpha
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Sauvegarder temporairement l'image corrigée
            temp_path = "temp_rotated_photo.jpg"
            img.save(temp_path, format='JPEG', quality=95)

            # Dessiner l'image dans le PDF
            c.drawImage(temp_path, 10, height - 450, width=2.5*inch, height=3.4*inch)

            # Supprimer le fichier temporaire
            os.remove(temp_path)
        else:
            c.drawString(60, height - 430, "Photo non disponible")


    # Largeur fixe pour les labels
    label_width = 180  # largeur réservée pour le texte des labels
    x_start = 200      # position de départ horizontale
    x_value_start = x_start + label_width  # position pour les valeurs
    x_second_column = 700  # position pour SEXE (deuxième colonne)

    # Préparer les informations (sans SEXE, car on le gère à part avec NOM)
    info_lines = [
        ("NOM", f"{membre.nom.upper()}"),
        ("POST-NOM", f"{membre.post_nom.upper()}"),
        ("PRÉNOM", f"{membre.prenom.upper()}"),
        ("PROVINCE", f"{membre.get_province_display().upper()}"),
        ("FONCTION", f"{membre.fonction.upper() if hasattr(membre, 'fonction') else 'NON RENSEIGNÉ'}"),
        ("CATÉGORIE", f"{membre.get_categorie_display().upper()}"), 
    ]

    # Position verticale de départ
    y_position = height - 225
    line_spacing = 45  # espacement entre les lignes

    # Boucle pour dessiner chaque ligne
    for label, value in info_lines:
        c.setFont("Helvetica-Bold", 25)
        c.setFillColor(black)  # couleur noire pour labels et valeurs

        # Dessiner le label
        c.drawString(x_start, y_position, label)

        # Dessiner la valeur suivie de ":" (collé à la valeur)
        value_text = f": {value}"
        c.drawString(x_value_start, y_position, value_text)

        # Cas spécial : NOM → ajouter SEXE à droite (seulement F ou M)
        if label == "NOM":
            sexe_label = "SEXE"
            sexe_value = "M" if membre.get_sexe_display().upper().startswith("M") else "F"

            gap = 10  # petit espace entre label et valeur

            # dessiner le label SEXE
            c.drawString(x_second_column, y_position, sexe_label)

            # mesurer largeur du label
            label_width_sexe = c.stringWidth(sexe_label, "Helvetica-Bold", 28)

            # dessiner la valeur juste après le label
            c.drawString(x_second_column + label_width_sexe + gap, y_position, f": {sexe_value}")


        # Descendre pour la ligne suivante
        y_position -= line_spacing

    # Informations
    code_membre = membre.code
    date_enregistrement = membre.date_enregistrement.strftime('%d-%m-%Y')
    date_expiration = membre.date_expiration.strftime('%d-%m-%Y') if membre.date_expiration else "NON DÉFINIE"

    # Modifier la police et ajuster la position
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(red)
    y_position -= 2  # Espacement avant d'ajouter ces informations

    # Positions horizontales pour chaque info
    x_code = 20
    x_delivree = 200
    x_expiration = 500

    # Afficher les titres sur la même ligne
    c.drawString(x_code, y_position, "CODE")
    c.drawString(x_delivree, y_position, "Délivrée le")
    c.drawString(x_expiration, y_position, "Expiration")

    # Espacement vertical pour les valeurs
    y_position -= 25

    # Changer couleur pour les valeurs
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(black)

    # Afficher les valeurs en dessous des titres correspondants
    c.drawString(x_code, y_position, code_membre.upper())
    c.drawString(x_delivree, y_position, date_enregistrement)
    c.drawString(x_expiration, y_position, date_expiration)


    # === Nouvelle image à ajouter ===
    logo_path = finders.find('images/pca.png')  # Remplacez par votre image

    if logo_path:  # Si le logo est trouvé
        c.drawImage(logo_path, 655, height - 500, width=2.5*inch, height=2.5*inch, mask='auto')  # 'mask=auto' pour gérer la transparence
    else:
        c.drawString(480, height - 578, "Logo non disponible")
    
    

    ##########################################################################################

    # Dessiner une nouvelle page pour le verso
    c.showPage()
    # === Ajouter un logo en arrière-plan (filigrane) ===


    # chemin vers ton logo
    watermark_path = finders.find('images/logo2.png')

    if watermark_path and os.path.exists(watermark_path):
        # Ouvrir avec PIL
        wm_img = Image.open(watermark_path).convert("RGBA")

        # Réduire l’opacité (0 = transparent, 1 = opaque)
        alpha = 0.12  
        enhancer = ImageEnhance.Brightness(wm_img.split()[3])  # canal alpha
        wm_img.putalpha(enhancer.enhance(alpha))

        # Sauvegarde temporaire en PNG (avec transparence)
        temp_wm = "temp_watermark.png"
        wm_img.save(temp_wm, format="PNG")

        # Placer au centre de la page
        wm_reader = ImageReader(temp_wm)
        c.drawImage(
            wm_reader,
            100, 100,  # position bas-gauche (ajuste selon besoin)
            width - 200, height - 200,  # couvre presque toute la page
            mask="auto"
        )

        # Supprimer le temporaire
        os.remove(temp_wm)

    # Placer le QR code à gauche, sous la photo ou à côté des infos
    if membre.qrcode:
        qrcode_path = membre.qrcode.path
        if os.path.exists(qrcode_path):
            # Ajuster la position et la taille
            qr_x = 10       # distance depuis le bord gauche
            qr_y = height - 225  # ajuster selon la position verticale souhaitée
            qr_width = 3*inch   # largeur agrandie
            qr_height = 3*inch  # hauteur agrandie
            c.drawImage(qrcode_path, qr_x, qr_y, width=qr_width, height=qr_height)
        else:
            c.drawString(10, height - 500, "QR Code non disponible")

    # === DRC ===
    logo_path = finders.find('images/am.png')  # Remplacez par votre image

    if logo_path:  # Si le logo est trouvé
        c.drawImage(logo_path, 700, height - 170, width=1.8*inch, height=1.8*inch, mask='auto')  # 'mask=auto' pour gérer la transparence
    else:
        c.drawString(480, height - 578, "Logo non disponible")

    #################################################################################################################################

    # Informations
    # Données fictives
    code_membre = membre.code
    site_membre = membre.site

    # Définir police et couleur
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(black)

    # Position de départ (haut de page - marge)
    y_position = height - 120  

    # Décaler vers la droite (par ex. 350px depuis la gauche)
    x_label = width - 600   # position des labels
    x_value = width - 375    # position des valeurs à droite


    # Afficher Code
    c.drawString(x_label, y_position, "Code Membre")
    c.drawString(x_value, y_position, f": {code_membre}")

    # Ligne suivante pour Site
    y_position -= 40
    c.drawString(x_label, y_position, "Secteur d'Activité (Site)")
    c.drawString(x_value, y_position, f": {site_membre}")


    # === Nouvelle image à ajouter ===
    logo_path = finders.find('images/ap.png')

    if logo_path and os.path.exists(logo_path):
        # Ouvrir l'image avec PIL pour récupérer ses dimensions
        img = PILImage.open(logo_path)
        orig_width, orig_height = img.size

        # Nouvelle largeur souhaitée
        new_width = 11.7*inch  # exemple : augmenter largeur

        # Calcul de la hauteur pour garder le ratio
        new_height = (orig_height / orig_width) * new_width

        # Dessiner l'image dans le PDF
        c.drawImage(logo_path, 0, height - 350, width=new_width, height=new_height, mask='auto')
    else:
        c.drawString(480, height - 578, "Logo non disponible")




    c.setFont("Helvetica-Bold", 25)
    c.setFillColor(black)  # Définir la couleur du texte sur black
    c.drawCentredString(width / 2 , height - 480, "Les autorités tant civiles que militaires sont priées d'apporter")

    c.setFont("Helvetica-Bold", 25)
    c.setFillColor(black)  # Définir la couleur du texte sur black
    c.drawCentredString(width / 2 , height - 510, "leur assistance au porteur de la présente")

    # Finaliser le PDF
    c.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')