import json
import uuid
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from datetime import datetime,timedelta
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.hashers import make_password,check_password
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.dateparse import parse_datetime
import os
from django.core.files.storage import FileSystemStorage

from pulls.tokens import AccountActivationTokenGenerator
from .models import Clients, Groups, Mission, Users,UserTwoFactorAuthData
from .form import SignupForm,LoginForm,TwoFactorAuthForm
from . import tasks, utils

# Create your views here.
def login(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            try:
                user = Users.objects.get(users_mail=username,delete_date__isnull=True)
                if check_password(password,user.users_password):
                    if user is not None:
                        if user.users_is_active:
                            try :
                                two_factor_auth_data=UserTwoFactorAuthData.objects.get(user_id=user.id_user,is_active=True)
                                request.session['user_id'] = str(user.id_user)
                                return JsonResponse({
                                                    "success": True,
                                                    "opt":'activate',
                                                    "msg": "Connexion réussie!",
                                                })
                            except UserTwoFactorAuthData.DoesNotExist :
                                request.session['user_id'] = str(user.id_user)
                                return JsonResponse({
                                                    "success": True,
                                                    'opt':'deactivate',
                                                    "msg": "Connexion réussie!",
                                                })
                        else:
                            return JsonResponse({
                                            "success": False,
                                            "msg": f"Connexion échouée! Votre compte n'a pas été activé. Activez votre compte depuis votre compte electronique",
                                            })
                    else:
                        return JsonResponse({
                                            "success": False,
                                            "msg": "Aucun utilisateur avec les informations fournies n'existe dans notre système.",
                                            })
                else:
                    return JsonResponse({"success": False,
                                        "msg": "Aucun utilisateur avec les informations fournies n'existe dans notre système.",
                                        })
            
            except Users.DoesNotExist:
                return JsonResponse({"success": False,
                                        "msg": "Aucun utilisateur avec les informations fournies n'existe dans notre système.",
                                        })
            except Exception as e:
                return JsonResponse({"success": False,
                                        "msg": "Serveur momentanement indisponible.",
                                        })
        
    form = LoginForm()
    return render(request, 'pages/auth/login.html',{'form': form})

def register(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST':
        post_data = request.POST.copy()
        lname = post_data.get("lname")
        fname = post_data.get("fname")
        email = post_data.get("email")
        password = post_data.get("password")
        accept_terms=post_data.get("accept_terms")

       
        
        if(accept_terms=='on'):
            if(utils.is_valid_email(email)['success']):
                try:
                    users = Users.objects.create(users_mail=email)
                    token_generator = AccountActivationTokenGenerator()
                    token = token_generator.make_token(users)
                    subject = "Veuillez activer votre compte par mail"
                    ctx = {
                            "fullname": f"{fname} {lname}",
                            "domain": str(get_current_site(request)),
                            "uid": urlsafe_base64_encode(force_bytes(users.pk)),
                            "token": token
                        }

                    if utils.is_valid_password(password, users):
                        
                        users.users_password=make_password(password)
                        users.users_name=lname
                        users.users_fname=fname
                        users.users_type="default"
                        users.users_is_active=False
                        users.users_preavis=False
                        users.save()

                        if settings.DEBUG:
                            tasks.send_email_message(
                                subject=subject,
                                header_from="Validation de votre adresse email",
                                template_name="pages/settings/activation_request.txt",
                                user_id=users.id_user,
                                ctx=ctx,
                                simple=True
                            )
                        else:
                            tasks.send_email_message(
                                subject=subject,
                                template_name="pages/settings/activation_request.html",
                                user_id=users.id_user,
                                ctx=ctx,
                                simple=True
                            )

                        return JsonResponse(
                                {
                                    "success": True,
                                    "msg": "Votre compte a été créé! Vous devez vérifier votre adresse e-mail pour pouvoir vous connecter.",
                                }
                            )
                    else:
                        return JsonResponse({'success': False, 'msg': 'Le format est incorrect : le mot de passe doit comporter au moins 8 caractères, incluant une lettre majuscule, une lettre minuscule et un caractère spécial.'})
            
                    
                except Exception as e :
                    print(e)
                    return JsonResponse({'success': False, 'msg': 'Envoie du courier est momentanement indisponible, Merci de reesseyer ulterierement.'}) 
                    
            else:
                return JsonResponse(
                        {
                            "success": False,
                            "msg": f"{utils.is_valid_email(email)['reason']}",
                        })
        else :
            return JsonResponse(
                        {
                            "success": False,
                            "msg": "Veuillez accepter les termes du contrat et les conditions. Merci",
                        })
    else:
        form = SignupForm()
    
    return render(request, 'pages/auth/register.html', {'form': form})


def forget(request):
    return render(request, 'pages/auth/forget.html')

def logout(request):
    if request.session.get('user_id'):
        request.session.flush()
        messages.success(request, 'Déconnexion réussie.')
        return render(request,'pages/auth/logout.html')
    return redirect("login")



@utils.login_required_connect 
def home(request):
    pin = request.session.get('user_id')
    user=request.user
    context=utils.recup_infos_users(user)
    user_type=""
    match user.users_type:
        case 'paie':
            users_all=Users.objects.filter(delete_date=None).order_by('-created_date')[:5]
            count_users=Users.objects.filter(delete_date=None).count()
            stt=Users.objects.filter(users_type='stt',delete_date=None).count()
            con=Users.objects.filter(users_type='con',delete_date=None).count()

            last_month_start= datetime.now().replace(day=1) - timedelta(days=1)
            last_month_start = last_month_start.replace(day=1)
            current_month_start = datetime.now().replace(day=1)

            user_last_month = Users.objects.filter(created_date__gte=last_month_start, created_date__lt=current_month_start).count()
            user_current_month = Users.objects.filter(created_date__gte=current_month_start).count()
               
            def croissance(y2,y1):
                if y1!=0:
                    return ((y2 - y1) / y1)*100
                else :
                    return 0
            user_type ="Ressources humaines"
                
            context.update({
                'users_all':users_all,
                'count_users':count_users,
                'colab_users':(stt+con),
                'croissance':croissance(user_current_month,user_last_month),
            })

        case 'admin':
            pass
        case 'stt':
            pass
        case 'con':
            dt = datetime.now()
            year, month = dt.year, dt.month
            first_day = datetime(year, month, 1)
            if month == 12:
                last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = datetime(year, month + 1, 1) - timedelta(days=1)
            context['date_cra']=datetime(year, month, 27)
            context['date_salaire']=datetime(year, month+1, 5) if month != 12 else (year+1, 1, 5)
            context['date_paie']=datetime(year, month+1, 6) if month != 12 else (year+1, 1, 6)
        case 'com':
            pass
        case 'sup':
                pass
        case _:
            pass
        
    return render(request,'pages/admin/home.html',context)


@utils.login_required_connect
def delete_user(request, user_id):
    if request.method == 'DELETE':
        try:
            user = Users.objects.get(pk=user_id)
            user.delete_date = now()
            user.save()
            return JsonResponse({'success': True, 'message': 'Utilisateur supprimé avec succès.'})
        except Users.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Utilisateur non trouvé.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'}, status=405)

@utils.login_required_connect
def profil(request, user_id=None):
    context = {}
    if user_id:
        # Utilisateur connecté
        user = request.user
        context = utils.recup_infos_users(user)

        # Récupérer l'utilisateur spécifié par user_id
        user_info = get_object_or_404(Users, id_user=user_id)

        context['user_info'] = user_info
        context['type_user_info'] = utils.recup_infos_users(user_info)
        
        # Vérifie le type d'utilisateur et ajuste le contexte en conséquence
        if user_info.users_type in ['con', 'stt']:
            context['is_consultant_or_freelance'] = True
        
        # Pour les administrateurs et RH, afficher tous les clients
        if user.users_type in ['paie', 'admin', 'sup']:
            context['is_admin_or_rh'] = True
            context['clients'] = Clients.objects.all()
        
        # Pour les consultants ou freelances, récupérer la mission actuelle
        if context.get('is_consultant_or_freelance'):
            current_mission = get_current_mission(user_info)
            context['current_mission'] = current_mission
        
        if user_info.client:
            current_client = get_object_or_404(Clients, id_client=user_info.client.id_client)
            context['current_client'] = current_client
        
        # Obtenez la liste des clients
        clients = Clients.objects.all()

        # Grouper les clients par leur nom
        grouped_companies = {}
        for client in clients:
            if client.client_name not in grouped_companies:
                grouped_companies[client.client_name] = []
            grouped_companies[client.client_name].append(client)
        
        context['grouped_companies'] = grouped_companies

        # Inclure les types d'utilisateur et les groupes dans le contexte
        context['user_type'] = Users.USER_TYPES[:-2]
        context['groups'] = Groups.objects.all()
        context['managers'] = Users.objects.filter(users_type='admin', delete_date__isnull=True)
        try:
            # Vérifier l'état de l'authentification à deux facteurs
            try:
                user_two_factor = UserTwoFactorAuthData.objects.get(id=user_info.id_user)
                context['activate'] = user_two_factor.is_active
            except UserTwoFactorAuthData.DoesNotExist:
                context['activate'] = False
            
        except Exception as e:
            print('Message erreur:', e)

    else:
        # Utilisateur connecté
        user = request.user
        context = utils.recup_infos_users(user)
        context['clients'] = Clients.objects.all()
        
        if user.users_type in ['con', 'stt']:
            context['is_consultant_or_freelance'] = True
        
        # Pour les consultants ou freelances, récupérer la mission actuelle
        if context.get('is_consultant_or_freelance'):
            current_mission = get_current_mission(user)
            context['current_mission'] = current_mission
        
        # Récupérer le client associé si disponible
        if user.client:
            context['current_client'] = get_object_or_404(Clients, id_client=user.client.id_client)

        try:
            # Vérifier l'état de l'authentification à deux facteurs
            try:
                user_two_factor = UserTwoFactorAuthData.objects.get(id=user.id_user)
                context['activate'] = user_two_factor.is_active
            except UserTwoFactorAuthData.DoesNotExist:
                context['activate'] = False
            
        except Exception as e:
            print('Message erreur:', e)

    return render(request, 'pages/clients/profil.html', context)

def add_group(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            group_name = data.get('group_name')
            if group_name:
                new_group = Groups(group_name=group_name)
                new_group.save()
                return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def update_user_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        user_types = data.get('user_type')
        manager_id = data.get('manager_id')
        group_ids = data.get('group_ids', [])
        
        # Récupérer l'utilisateur
        user_info = Users.objects.get(pk=user_id)
        # Mettre à jour les types d'utilisateur
        print('Type de users',user_types)
        user_info.users_type=user_types
        # Mettre à jour le manager
        user_info.users_manager = manager_id
        # Mettre à jour les groupes
        user_info.groups.set(group_ids)
        user_info.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)

def parse_date(date_str, date_format='%m/%d/%Y'):
    try:
        print(date_str)
        print(type(date_str))
        return datetime.strptime(date_str, date_format)
    except ValueError as e:
        print(e)
        return None
    

def get_current_mission(user):
    # Exemple de code, adaptez-le à votre modèle
    return Mission.objects.filter(id_mission=user.mission_id).last()

@utils.login_required_connect  # decorateur pour verifier si l'utilisateur est connecter ou pas
def update_profile_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode de requête invalide'}, status=405)
    
    try:
        user = request.user
        user_id = request.POST.get('user_info_id') or request.POST.get('user_id')

        if not user_id:
            return JsonResponse({'success': False, 'message': 'ID utilisateur requis'}, status=400)

        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'ID utilisateur invalide'}, status=400)

        user_to_update = get_object_or_404(Users, id_user=user_uuid)
        
        # Vérification de l'identité de l'utilisateur
        if user.id_user != user_uuid:
            # Vérifier le type d'utilisateur
            is_consultant_or_freelance = user_to_update.users_type in ['con', 'stt']
           
            # Mise à jour des informations client
            client_option = request.POST.get('client_id')
            client_location = request.POST.get('cwebsite')
            
            if client_option == 'other':
                client_name = request.POST.get('client_name')

                if not client_name or not client_location:
                    return JsonResponse({'success': False, 'message': 'Nom et localisation du client requis'}, status=400)
                
                client, created = Clients.objects.get_or_create(client_name=client_name, client_location=client_location)
                if not created:
                    return JsonResponse({'success': False, 'message': 'Ce client est déjà listé. Merci de mettre à jour sa localisation.'}, status=400)
                
                user_to_update.client = client
            elif client_option:
                client = get_object_or_404(Clients, id_client=client_option)
                if client_location:
                    client.client_location = client_location
                    client.save()
                user_to_update.client = client

            if is_consultant_or_freelance:
                # Mise à jour des informations de mission
                mission_id = request.POST.get('mission_id')
                mission_name = request.POST.get('mission_name_')
                mission_manager = request.POST.get('mission_manager_')
                mission_start_str = request.POST.get('mission_start_')
                mission_end_str = request.POST.get('mission_end_')
                mission_description = request.POST.get('mission_desc')

                if mission_start_str and mission_end_str:
                    mission_start = parse_date(mission_start_str)
                    mission_end = parse_date(mission_end_str)
                    if not mission_start or not mission_end:
                        return JsonResponse({'success': False, 'message': 'Format de date invalide'}, status=400)
                else:
                    return JsonResponse({'success': False, 'message': 'Les dates de début et de fin de mission sont requises'}, status=400)

                if mission_id:
                    mission_to_update = get_object_or_404(Mission, id_mission=mission_id)
                    mission_to_update.mission_name = mission_name or mission_to_update.mission_name
                    mission_to_update.mission_manager = mission_manager or mission_to_update.mission_manager
                    mission_to_update.mission_start = mission_start
                    mission_to_update.mission_end = mission_end
                    mission_to_update.mission_description = mission_description or mission_to_update.mission_description
                    mission_to_update.save()
                    user_to_update.mission = mission_to_update
                else:
                    if not all([mission_name, mission_manager, mission_description]):
                        return JsonResponse({'success': False, 'message': 'Tous les champs de la mission sont requis pour créer une nouvelle mission'}, status=400)
                    
                    new_mission = Mission(
                        mission_name=mission_name,
                        mission_manager=mission_manager,
                        mission_start=mission_start,
                        mission_end=mission_end,
                        mission_description=mission_description
                    )
                    new_mission.save()
                    user_to_update.mission = new_mission
       
        # Mise à jour des informations personnelles
        user_to_update.users_name = request.POST.get('users_name', user_to_update.users_name)
        user_to_update.users_fname = request.POST.get('users_fname', user_to_update.users_fname)
        user_to_update.users_address = request.POST.get('location', user_to_update.users_address)
        user_to_update.users_phone = request.POST.get('phone_number', user_to_update.users_phone)
        user_to_update.users_region = request.POST.get('city', user_to_update.users_region)
        user_to_update.users_postal = request.POST.get('postal_code', user_to_update.users_postal)
        user_to_update.save()

        return JsonResponse({'success': True, 'message': 'Profil mis à jour avec succès'})
    except Exception as e:
        print(f'Unexpected error: {str(e)}')
        return JsonResponse({'success': False, 'message': 'Une erreur est survenue lors de la mise à jour du profil'}, status=500)
    

@utils.login_required_connect     
def change_profile_picture(request):
    user = request.user
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        profile_picture = request.FILES['profile_picture']
        
        new_filename = str(uuid.uuid4()) + '.' + profile_picture.name.split('.')[-1]
        # Enregistrer le fichier dans le dossier photos_profil
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, f'photos_profil/{new_filename[:2]}'))
        filename = fs.save(new_filename, profile_picture) 
        
        # Mettre à jour l'utilisateur avec le nouveau chemin de fichier
        user.profile_photo = new_filename
        user.url_photo_profile= f'{new_filename[:2]}/' + new_filename
        user.save()
        
        response = {
            'new_profile_photo_url': fs.url(os.path.join( f'photos_profil/{new_filename[:2]}',filename))
        }
        
        return JsonResponse(response)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def get_clients_data(request):
    if request.method == 'GET':
        clients = Clients.objects.all().values('id_client', 'client_location')
        client_data = {str(client['id_client']): client['client_location'] for client in clients}
        return JsonResponse(client_data)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def verification(request):
    pin=request.session.get('user_id')
    mdp = request.POST.get('password')
    opt_value = request.POST.get('otp')
    if(pin):
        try:
            user = Users.objects.get(pk=pin)
            if(request.method=='POST'):
                if(check_password(mdp,user.users_password)):
                    try:
                        two_factor_auth_data=UserTwoFactorAuthData.objects.get(user_id=user.id_user)
                        context={
                            'otp_secret':two_factor_auth_data.otp_secret,
                            'qr_code':request.session.get('qr_code')
                        }
                        return JsonResponse({
                            'status':True,
                            'message': context
                        })
                    except UserTwoFactorAuthData.DoesNotExist:
                        context=utils.AdminSetupTwoFactorAuthView(user)
                        two_factor_auth_data=UserTwoFactorAuthData.objects.get(user_id=user.id_user)
                        two_factor_auth_data.qr_code=context['qr_code']
                        two_factor_auth_data.save()
                        request.session['qr_code'] = context['qr_code']
                        context['json_id']=user.id_user
                        return JsonResponse({
                            'status':True,
                            'message': context
                        })
                elif (opt_value):
                    two_factor_auth_data = UserTwoFactorAuthData.objects.filter(user=user).first()
                    form = TwoFactorAuthForm(user, request.POST)
                    print(form)
                    if form.is_valid():
                        two_factor_auth_data.rotate_session_identifier()
                        request.session['2fa_token'] = str(two_factor_auth_data.session_identifier)
                        two_factor_auth_data.is_active=True
                        two_factor_auth_data.save()
                        return JsonResponse({'status': True,})
                    else:
                        return JsonResponse({'status': False, 'message': 'Mot de passe expiré'})
                else:
                    return JsonResponse({
                        'status':False,
                        'message':'Tres bien'
                    })
        except Exception as e:
            print('erreur', e)

def opt(request):
    pin=request.session.get('user_id')
    if pin:
        return render(request,'pages/settings/opt.html')
    return redirect('login')
@utils.login_required_connect 
def getcra(request):
    user=request.user
    context=utils.recup_infos_users(user)
    return render(request,'pages/admin/gestion_cra/cra.html',context)
    

def conge(request):
    pin=request.session.get('user_id')
    context={}
    if pin:
        user= Users.objects.get(pk=pin)
        users_type=""
        match user.users_type:
            case 'paie':
                users_type ="Ressources humaines"
            case 'admin':
                users_type ="Direction"
            case 'stt':
                users_type ="Freelance"
            case 'con':
                users_type ="Consultant"
            case 'com':
                users_type ="Commercial"
            case 'sup':
                users_type ="Super admin"
            case _:
                users_type="Inconue"
        context={
            'user':user,
            'users_type':users_type
        }
        return render(request,'pages/admin/gestion_conge/conge.html',context)
    else:
        return redirect('login')


def change_password(request):
    pin = request.session.get('user_id')
    if (pin):
        if request.method == 'POST':
            user=Users.objects.get(pk=pin)
            old_password = request.POST.get('password')
            new_password = request.POST.get('new_password')
            con_password = request.POST.get('con_password')
            if (old_password):
                if check_password(old_password, user.users_password):
                    return JsonResponse({'reponse':'succes'})
                else :
                    return JsonResponse({'reponse':'error','message':'Le mot de passe est incorrect, veuillez réessayer'})

            if(new_password and con_password):
                if(new_password == con_password):
                    if(check_password(new_password,user.users_password)):
                        return JsonResponse({'reponse':'error','message':'Le mot de passe dois etre different que l\'ancien, merci'})
                    else:
                        new_password=make_password(new_password)
                        user.users_password=new_password
                        user.save()
                        return JsonResponse({'reponse':'succes','message':'Mot de passe changer avec success'})
                else:
                    return JsonResponse({'reponse':'error','message':'Les mot de passe sont different'})
            else:
                return JsonResponse({'reponse':'error','message':'Champs obligatoires'})
    else:
        return JsonResponse({'reponse':'error','message':'Vous etes pas autorisé a effectuer cette requete'})

def recup_type_format(user_type):
    match user_type :
        case 'admin':
            return 'Direction'
        case 'paie':
            return 'Ressources humaines'
        case 'con':
            return 'Consultant'
        case 'com':
            return 'Commercial'
        case 'stt':
            return 'Freelance'
        case _:
            return 'Invite'

@utils.login_required_connect
@utils.utilisateur_autorise(types_autorises=["Direction", "Super admin", "Ressources humaines"])
def fiche_paie(request):
    user=request.user
    context= utils.recup_infos_users(user)
        
    if user.users_type == 'paie':
        users = list(Users.objects.filter(users_is_active=True, delete_date__isnull=True).values(
            'id_user','users_name', 'users_fname', 'users_phone','users_type', 'users_mail', 'users_region', 'created_date', 'users_is_active', 'profile_photo','url_photo_profile'
        ))
    else:
        users = list(Users.objects.values(
            'id_user','users_name', 'users_fname', 'users_phone', 'users_type' ,'users_mail', 'users_region', 'created_date', 'users_is_active', 'profile_photo','url_photo_profile'
        ))

    liste=[]

    for u in users :
        liste.append(recup_type_format(u['users_type']))
    print(liste)
              
    context.update({
        'users':zip(users,liste)
    })
    print(context)
    return render(request,'pages/admin/gestion_users/user_all.html',context)

@utils.login_required_connect
@utils.utilisateur_autorise(types_autorises=["Direction", "Super admin", "Ressources humaines"])
def getEmploye(request):
    if request.method == 'GET':
        
        if request.user.users_type == 'paie':
            users = list(Users.objects.filter(users_is_active=True, delete_date__isnull=True).values(
                'users_name', 'users_fname', 'users_phone', 'users_mail', 'users_region', 'created_date', 'users_is_active', 'profile_photo'
            ))
        else:
            users = list(Users.objects.values(
                'users_name', 'users_fname', 'users_phone', 'users_mail', 'users_region', 'created_date', 'users_is_active', 'profile_photo'
            ))
        return JsonResponse(users, safe=False)
    else:
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)

    

def send_confirmation(request,client_id):
    context={}
    if(int(client_id)==12):
        context={
            'email':'lmbaasseko@gmail.com',
            'message':'activer votre compte'
        }
    return render(request,'pages/auth/confirm-mail.html',context)

def activate(request, uidb64, token):
    token_generator = AccountActivationTokenGenerator()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        users = Users.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError):
        users = None
    # checking if the user exists, if the token is valid.
    if users is not None and token_generator.check_token(users, token):
        # if valid set active true
        users.users_is_active = True
        users.save()
        messages.success(
            request, f"Votre email ({users.users_mail}) a été vérifié avec succès ! Vous pouvez désormais vous connecter."
        )
        return redirect("login")
    else:
        return JsonResponse({'message':'site n\'est plus valide'})

def admin_confirm_two_factor_auth(request):
    user_id = request.session.get('user_id', None)
    user = get_object_or_404(Users, id_user=user_id)
    two_factor_auth_data = UserTwoFactorAuthData.objects.filter(user=user).first()
    if request.method == 'POST':
        form = TwoFactorAuthForm(user, request.POST)
        if form.is_valid():
            if two_factor_auth_data:
                two_factor_auth_data.rotate_session_identifier()
                request.session['2fa_token'] = str(two_factor_auth_data.session_identifier)
                user.save()
                return JsonResponse({'success': True,'message': 'Autorisé'})
            else:
                return JsonResponse({'success': True,'message': 'Autorisé'})
        else:
            return JsonResponse({'success': False, 'message': 'Mot de passe expiré'})
    else:
        return JsonResponse({'success': False, 'message': 'Mot de passe expiré'})
    
def anonymise(request):
    return render(request,'pages/settings/anonymise.html')
