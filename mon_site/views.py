from django.shortcuts import render
from django.views.generic import TemplateView

# Vue basée sur une fonction
def home_view(request):
    context = {
        'page_title': 'Accueil - RENEMICO',
        'active_page': 'home',
    }
    return render(request, 'home.html', context)

# Ou vue basée sur une classe (alternative)
class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Accueil - RENEMICO',
            'active_page': 'home',
        })
        return context

# Vues pour les autres pages (exemples)
def about_view(request):
    return render(request, 'about.html', {'active_page': 'about'})

def services_view(request):
    return render(request, 'services.html', {'active_page': 'services'})

def members_view(request):
    return render(request, 'members.html', {'active_page': 'members'})

def news_view(request):
    return render(request, 'news.html', {'active_page': 'news'})

def contact_view(request):
    return render(request, 'contact.html', {'active_page': 'contact'})

def join_view(request):
    return render(request, 'join.html', {'active_page': 'join'})


######################################################################################################
from django.shortcuts import render

# Liste des provinces
def province(request):
    return render(request, "provinces/province.html")

# Provinces individuelles
def province_bas_uele(request):
    return render(request, "provinces/bas_uele.html")

def province_equateur(request):
    return render(request, "provinces/equateur.html")

def province_haut_katanga(request):
    return render(request, "provinces/haut_katanga.html")

def province_haut_lomami(request):
    return render(request, "provinces/haut_lomami.html")

def province_haut_uele(request):
    return render(request, "provinces/haut_uele.html")

def province_ituri(request):
    return render(request, "provinces/ituri.html")

def province_kasai(request):
    return render(request, "provinces/kasai.html")

def province_kasai_central(request):
    return render(request, "provinces/kasai_central.html")

def province_kasai_oriental(request):
    return render(request, "provinces/kasai_oriental.html")

def province_kinshasa(request):
    return render(request, "provinces/kinshasa.html")

def province_kongo_central(request):
    return render(request, "provinces/kongo_central.html")

def province_lomami(request):
    return render(request, "provinces/lomami.html")

def province_lualaba(request):
    return render(request, "provinces/lualaba.html")

def province_mai_ndombe(request):
    return render(request, "provinces/mai_ndombe.html")

def province_maniema(request):
    return render(request, "provinces/maniema.html")

def province_mongala(request):
    return render(request, "provinces/mongala.html")

def province_nord_kivu(request):
    return render(request, "provinces/nord_kivu.html")

def province_nord_ubangi(request):
    return render(request, "provinces/nord_ubangi.html")

def province_sankuru(request):
    return render(request, "provinces/sankuru.html")

def province_sud_kivu(request):
    return render(request, "provinces/sud_kivu.html")

def province_sud_ubangi(request):
    return render(request, "provinces/sud_ubangi.html")

def province_tanganyika(request):
    return render(request, "provinces/tanganyika.html")

def province_tshopo(request):
    return render(request, "provinces/tshopo.html")

def province_tshuapa(request):
    return render(request, "provinces/tshuapa.html")

def province_kwango(request):
    return render(request, 'provinces/kwango.html')

def province_kwilu(request):
    return render(request, 'provinces/kwilu.html')



######################################################################################################################
######################################################################################################
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import Http404
from .forms import RegisterForm, LoginForm
from .models import CustomUser

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f"Compte créé avec succès pour {user.get_full_name()} !")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création du compte : {str(e)}")
        else:
            error_msg = "Veuillez corriger les erreurs suivantes :"
            for field, errors in form.errors.items():
                field_label = form.fields[field].label or field
                error_list = ', '.join(errors)
                error_msg += f"\n- {field_label}: {error_list}"
            messages.error(request, error_msg)
    else:
        form = RegisterForm()

    return render(request, 'login/register.html', {'form': form, 'title': "Création de compte"})

#######################################################################################################################

def login_view(request):
    if request.user.is_authenticated:
        return redirect_user_by_level(request.user)
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue {user.get_full_name()}!")
                return redirect_user_by_level(user)
            else:
                messages.error(request, "Identifiant et/ou mot de passe incorrects. Veuillez réessayer.")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = LoginForm()

    return render(request, 'login/login.html', {'form': form, 'title': "Connexion - RENEMICO"})

def redirect_user_by_level(user):
    """
    Redirige l'utilisateur vers le dashboard spécifique selon son niveau hiérarchique.
    Lève une exception 404 si le niveau n'est pas reconnu.
    """
    if not hasattr(user, 'level') or not user.level:
        raise Http404("Niveau hiérarchique non défini")

    redirect_mapping = {
        'PRESIDENT_NATIONAL': 'president_national_dashboard',
        'PRESIDENT_PROVINCIAL': 'president_provincial_dashboard',
        'SECRETAIRE_GENERAL': 'secretaire_general_dashboard',
        'OPERATEUR': 'operateur_dashboard',
        'ADMIN_SYSTEME': 'admin_systeme_dashboard',
    }

    user_level = user.level.upper()
    if user_level not in redirect_mapping:
        raise Http404(f"Niveau hiérarchique '{user.level}' non reconnu")

    return redirect(redirect_mapping[user_level])

############################################################################################################

from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    """Vue personnalisée pour la déconnexion"""
    logout(request)
    return redirect('login')  # Redirige vers la page de connexion après déco


#################################################################################################################
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def admin_systeme_dashboard(request):
    # Vous pouvez ajouter ici toute logique spécifique au tableau de bord admin
    context = {
        'title': 'Tableau de Bord Administrateur Système',
        'user': request.user,
    }
    return render(request, 'dashboard/admin_systeme_dashboard.html', context)

################################################################################################################

@login_required
def operateur_dashboard(request):
    # Vous pouvez ajouter ici toute logique spécifique au tableau de bord opérateur
    context = {
        'title': 'Tableau de Bord Ope=érateur',
        'user': request.user,
    }
    return render(request, 'dashboard/operateur_dashboard.html', context)

#########################################################################################################
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta
from identification.models import Membre
from finance.models import Contribution

@login_required
def president_national_dashboard(request):
    # Membres actifs

    membres_actifs = Membre.objects.filter(statut='actif').count()

    # Provinces couvertes (supposons que chaque Membre a un champ province)
    provinces_couvertes = Membre.objects.values('province').distinct().count()

    # Fonds Nationaux (somme des contributions)
    fonds_nationaux = Contribution.objects.aggregate(total=Sum('montant'))['total'] or 0

    # Croissance mensuelle (comparaison avec le mois précédent)
    today = now().date()
    first_day_this_month = today.replace(day=1)
    last_month_end = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_month_end.replace(day=1)

    this_month_total = Contribution.objects.filter(
        date_paiement__gte=first_day_this_month
    ).aggregate(Sum('montant'))['montant__sum'] or 0

    last_month_total = Contribution.objects.filter(
        date_paiement__range=(first_day_last_month, last_month_end)
    ).aggregate(Sum('montant'))['montant__sum'] or 0

    croissance = 0
    if last_month_total > 0:
        croissance = ((this_month_total - last_month_total) / last_month_total) * 100

    context = {
        'title': 'Tableau de Bord Président National',
        'user': request.user,
        'membres_actifs': membres_actifs,
        'provinces_couvertes': provinces_couvertes,
        'fonds_nationaux': fonds_nationaux,
        'croissance': round(croissance, 2)
    }
    return render(request, 'dashboard/president_national_dashboard.html', context)


##########################################################################################################
@login_required
def president_provincial_dashboard(request):
    context = {
        'title': 'Tableau de Bord Président Provincial',
        'user': request.user,
    }
    return render(request, 'dashboard/president_provincial_dashboard.html', context)

##########################################################################################################
@login_required
def secretaire_general_dashboard(request):
    context = {
        'title': 'Tableau de Bord Secrétaire Général',
        'user': request.user,
    }
    return render(request, 'dashboard/secretaire_general_dashboard.html', context)

#########################################################################################################
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import CustomUser
import datetime


def users(request):
    # Récupérer tous les utilisateurs triés par nom
    users_list = CustomUser.objects.all().order_by('last_name')
    
    # Pagination - 10 utilisateurs par page
    paginator = Paginator(users_list, 10)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users,
    }
    return render(request, 'login/users.html', context)

#######################################################################################################
from django.http import HttpResponse, Http404
from django.conf import settings
from PIL import Image, ExifTags
from io import BytesIO
import os

def get_image(request, user_id, field_name):
    """
    Vue pour servir les images (photo ou QR code) avec :
    - Correction de l'orientation EXIF
    - Gestion des erreurs robuste
    - Cache optimisé
    - Support multi-format
    """
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        raise Http404("Utilisateur non trouvé")

    # Validation du champ image
    valid_fields = ['photo', 'qrcode']
    if field_name not in valid_fields:
        return HttpResponse(
            f"Champ d'image invalide. Choisissez parmi : {', '.join(valid_fields)}", 
            status=400
        )

    image_field = getattr(user, field_name)
    
    # Gestion des champs vides
    if not image_field:
        if field_name == 'photo':
            # Générer une image par défaut avec les initiales
            return generate_default_avatar(user)
        raise Http404(f"L'image {field_name} n'existe pas pour cet utilisateur")

    try:
        # Vérification physique du fichier
        if not os.path.exists(image_field.path):
            raise FileNotFoundError

        # Traitement de l'image avec Pillow
        with Image.open(image_field.path) as img:
            # Correction de l'orientation EXIF
            img = correct_image_orientation(img)
            
            # Détermination du format
            content_type, img_format = get_image_format(image_field.path)
            
            # Préparation de la réponse
            response = prepare_image_response(img, img_format, content_type)
            
            # Ajout des headers de cache
            add_cache_headers(response)
            
            return response

    except Exception as e:
        # Journalisation de l'erreur (à implémenter selon votre configuration)
        # logger.error(f"Erreur traitement image {field_name} user {user_id}: {str(e)}")
        
        if field_name == 'photo':
            return generate_default_avatar(user)
        raise Http404("Erreur de traitement de l'image")

def correct_image_orientation(img):
    """Corrige l'orientation de l'image basée sur les métadonnées EXIF"""
    try:
        exif = img._getexif()
        if exif:
            for tag, value in ExifTags.TAGS.items():
                if value == 'Orientation':
                    orientation = tag
                    break
            
            if orientation in exif:
                orientation_value = exif[orientation]
                
                rotations = {
                    3: Image.ROTATE_180,
                    6: Image.ROTATE_270,
                    8: Image.ROTATE_90
                }
                
                if orientation_value in rotations:
                    img = img.transpose(rotations[orientation_value])
    except (AttributeError, KeyError, IndexError):
        pass
    
    return img

def get_image_format(image_path):
    """Détermine le format et le content-type de l'image"""
    ext = os.path.splitext(image_path)[1].lower()
    
    if ext in ['.jpg', '.jpeg']:
        return 'image/jpeg', 'JPEG'
    elif ext == '.png':
        return 'image/png', 'PNG'
    else:
        raise ValueError("Format d'image non supporté")

def prepare_image_response(img, img_format, content_type):
    """Prépare la réponse HTTP avec l'image"""
    buffer = BytesIO()
    img.save(buffer, format=img_format)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type=content_type)
    response['Content-Length'] = buffer.getbuffer().nbytes
    return response

def add_cache_headers(response, days=30):
    """Ajoute les en-têtes de cache HTTP"""
    seconds = days * 24 * 60 * 60
    response['Cache-Control'] = f'max-age={seconds}, public'
    response['Expires'] = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime('%a, %d %b %Y %H:%M:%S GMT')

def generate_default_avatar(user):
    """
    Génère une image avatar par défaut avec les initiales de l'utilisateur
    """
    from PIL import ImageDraw, ImageFont
    import random
    
    # Couleur de fond aléatoire basée sur le nom
    colors = [
        '#1a237e', '#0d47a1', '#01579b', '#006064', 
        '#004d40', '#1b5e20', '#33691e', '#827717'
    ]
    bg_color = colors[hash(user.nom) % len(colors)]
    
    # Création de l'image
    img = Image.new('RGB', (200, 200), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Initiales (2 premières lettres)
    initials = (user.nom[0] + user.prenom[0]).upper() if user.prenom else user.nom[0].upper()
    
    # Police (taille adaptative)
    try:
        font_size = 80
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Calcul position texte
    text_width, text_height = draw.textsize(initials, font=font)
    position = ((200 - text_width) // 2, (200 - text_height) // 2)
    
    # Dessin du texte
    draw.text(position, initials, fill="white", font=font)
    
    # Conversion en réponse HTTP
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='image/png')
    response['Cache-Control'] = 'max-age=86400'  # Cache 1 jour
    return response


########################################################################################################

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import CustomUser
from .forms import CustomUserForm  # Assurez-vous d'avoir créé ce formulaire

def user_detail(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    return render(request, 'login/user_detail.html', {'user': user})


from django.shortcuts import render, get_object_or_404, redirect
from .models import CustomUser
from .forms import CustomUserForm  # Crée un ModelForm si ce n'est pas déjà fait

def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = CustomUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users')
    else:
        form = CustomUserForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'login/edit_user.html', context)


def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        user.delete()
        return redirect('users')
    
    context = {
        'user': user
    }
    return render(request, 'login/delete_user.html', context)

#########################################################################################################

def delete_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, "L'utilisateur a été supprimé avec succès.")
        return redirect('users')  # Redirige vers la liste des utilisateurs
    
    return render(request, 'login/confirm_delete.html', {'user': user})

########################################################################################################

def generate_user_card_pdf(request):
    # ton code ici
    pass

########################################################################################################
# views.py
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.shortcuts import redirect, render
import random
import string

from django.contrib.auth.decorators import login_required

@login_required
def settings_view(request):
    user_level = getattr(request.user, 'level', '').upper()
    dashboard_routes = {
    'PRESIDENT_NATIONAL':'Président National',
    'PRESIDENT_PROVINCIAL': 'Président Provincial',
    'SECRETAIRE_GENERAL': 'Secrétaire Général',
    'OPERATEUR': 'Opérateur(trice)',
    'ADMIN_SYSTEME':  'Administrateur Système',
    }
    context = {
        'user_dashboard_url': dashboard_routes.get(user_level, 'home'),  # 'home' est une route par défaut si aucun rôle n'est trouvé
    }
    return render(request, 'dashboard/settings.html', context)


#######################################################################################################
def update_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        user = request.user
        user.photo = request.FILES['photo']
        user.save()
        messages.success(request, 'Photo de profil mise à jour avec succès!')
    return redirect('settings_view')
#########################################################################################################
def change_password(request):
    if request.method == 'POST':
        user = request.user

        # Mise à jour de l'e-mail et du téléphone
        user.email = request.POST.get('email')
        user.telephone = request.POST.get('telephone')
        user.save()
        messages.success(request, 'Profil mis à jour avec succès!')

        # Changement de mot de passe
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Évite la déconnexion après changement du mot de passe
            messages.success(request, 'Votre mot de passe a été changé avec succès!')
            return redirect('settings_view')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            return redirect('settings_view')  # Rediriger même en cas d'erreurs de mot de passe
    else:
        return redirect('login')


##################################################################################################
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.core.exceptions import PermissionDenied


def admin_reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
            # Générer un mot de passe aléatoire
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            user.set_password(new_password)
            user.save()
            
            # Envoyer l'email avec le nouveau mot de passe
            send_mail(
                'Réinitialisation de votre mot de passe - RENEMICO',
                f'Bonjour,\n\n'
                f'Votre mot de passe a été réinitialisé par l\'un des administrateurs.\n'
                f'Votre nouveau mot de passe est: {new_password}\n\n'
                f'Nous vous recommandons de le changer après votre première connexion.\n\n'
                f'Cordialement,\n'
                f'L\'équipe technique',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, f'Un nouveau mot de passe a été envoyé à {email}')
        except User.DoesNotExist:
            messages.error(request, f"Aucun utilisateur trouvé avec l'email {email}")
    
    return redirect('admin_systeme_dashboard')

#####################################################################################################################