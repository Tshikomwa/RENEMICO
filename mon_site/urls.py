from django.urls import path
from . import views
from .views import (
    home_view,
    about_view,
    services_view,
    members_view,
    news_view,
    contact_view,
    join_view,

)
from .views import custom_logout
from .views import generate_user_card_pdf


urlpatterns = [
    # Page d'accueil
    path('', home_view, name='home'),
    # path('', HomeView.as_view(), name='home'),  # Alternative avec vue classe
    
    # Autres pages
    path('a-propos/', about_view, name='about'),
    path('services/', services_view, name='services'),
    path('membres/', members_view, name='members'),
    path('actualites/', news_view, name='news'),
    path('contact/', contact_view, name='contact'),
    path('devenir-membre/', join_view, name='join'),

    # Provinces
    path('province/', views.province, name='province'),
    # Provinces
    path('province/bas-uele/', views.province_bas_uele, name='bas_uele'),
    path('province/equateur/', views.province_equateur, name='equateur'),
    path('province/haut-katanga/', views.province_haut_katanga, name='haut_katanga'),
    path('province/haut-lomami/', views.province_haut_lomami, name='haut_lomami'),
    path('province/haut-uele/', views.province_haut_uele, name='haut_uele'),
    path('province/ituri/', views.province_ituri, name='ituri'),
    path('province/kasai/', views.province_kasai, name='kasai'),
    path('province/kasai-central/', views.province_kasai_central, name='kasai_central'),
    path('province/kasai-oriental/', views.province_kasai_oriental, name='kasai_oriental'),
    path('province/kinshasa/', views.province_kinshasa, name='kinshasa'),
    path('province/kongo-central/', views.province_kongo_central, name='kongo_central'),
    path('province/lomami/', views.province_lomami, name='lomami'),
    path('province/lualaba/', views.province_lualaba, name='lualaba'),
    path('province/mai-ndombe/', views.province_mai_ndombe, name='mai_ndombe'),
    path('province/maniema/', views.province_maniema, name='maniema'),
    path('province/mongala/', views.province_mongala, name='mongala'),
    path('province/nord-kivu/', views.province_nord_kivu, name='nord_kivu'),
    path('province/nord-ubangi/', views.province_nord_ubangi, name='nord_ubangi'),
    path('province/sankuru/', views.province_sankuru, name='sankuru'),
    path('province/sud-kivu/', views.province_sud_kivu, name='sud_kivu'),
    path('province/sud-ubangi/', views.province_sud_ubangi, name='sud_ubangi'),
    path('province/tanganyika/', views.province_tanganyika, name='tanganyika'),
    path('province/tshopo/', views.province_tshopo, name='tshopo'),
    path('province/tshuapa/', views.province_tshuapa, name='tshuapa'),
    path('province/Kwango/', views.province_kwango, name='kwango'),
    path('province/Kwilu/', views.province_kwilu, name='kwilu'),



    # Authentification
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', custom_logout, name='logout'),

    ################################################################################################

    # admin
    path('admin-systeme/dashboard/', views.admin_systeme_dashboard, name='admin_systeme_dashboard'),
    path('operateur/dashboard/', views.operateur_dashboard, name='operateur_dashboard'),
    path('dashboard/president-national/', views.president_national_dashboard, name='president_national_dashboard'),
    path('dashboard/president-provincial/', views.president_provincial_dashboard, name='president_provincial_dashboard'),
    path('dashboard/secretaire-general/', views.secretaire_general_dashboard, name='secretaire_general_dashboard'),
    #################################################################################################
    path('users/', views.users, name='users'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    #################################################################################################


    path('get_image/<int:user_id>/<str:field_name>/', views.get_image, name='get_image'),
    ##################################################################################################
    # ... vos autres URLs ...
    path('user/<int:pk>/', views.user_detail, name='user_detail'),
    path('user/delete/<int:pk>/', views.delete_user, name='delete_user'),

    path('user/<int:user_id>/card/', generate_user_card_pdf, name='user_card_pdf'),
    ###############################################################################################
    path('settings/', views.settings_view, name='settings_view'),
    path('update_profile_picture/', views.update_profile_picture, name='update_profile_picture'),
    path('change_password/', views.change_password, name='change_password'),
    path('admin_reset_password/', views.admin_reset_password, name='admin_reset_password'),

]