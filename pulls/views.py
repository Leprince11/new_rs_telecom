from django.conf import settings
from django.contrib import messages
from django.shortcuts import render,redirect
from datetime import datetime,timedelta
from django.http import JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.hashers import make_password,check_password
from django.urls.base import reverse
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from pulls.tokens import AccountActivationTokenGenerator
from .models import User
from .form import SignupForm,LoginForm
from . import tasks, utils

# Create your views here.
def login(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            try:
                user = User.objects.get(users_mail=username)
                if check_password(password,user.users_password):
                    if user is not None:
                        if user.users_is_active:
                            request.session['user_id'] = str(user.id_user)
                            return JsonResponse({
                                                    "success": True,
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
            except User.DoesNotExist:
                return JsonResponse({
                                "success": False,
                                "msg": "Aucun utilisateur avec les informations fournies n'existe dans notre système.",
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
                users = User.objects.create(users_mail=email)
                if utils.is_valid_password(password, users):
                    users.users_password=make_password(password)
                    users.users_name=lname
                    users.users_fname=fname
                    users.users_mail=email
                    users.created_date=datetime.today()
                    users.users_type="default"
                    users.users_is_active=False
                    users.users_preavis=False
                    users.save()
                    subject = "Veuillez activer votre compte par mail"
                    token_generator = AccountActivationTokenGenerator()
                    token = token_generator.make_token(users)
                    ctx = {
                        "fullname": f"{fname} {lname}",
                        "domain": str(get_current_site(request)),
                        "uid": urlsafe_base64_encode(force_bytes(users.pk)),
                        "token": token
                    }

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
                            header_from="Validation de votre adresse email",
                            template_name="pages/settings/activation_request.html",
                            user_id=users.id_user,
                            ctx=ctx,
                            simple=True
                        )
                        # raw_password = password

                    return JsonResponse(
                        {
                            "success": True,
                            "msg": "Votre compte a été créé! Vous devez vérifier votre adresse e-mail pour pouvoir vous connecter.",
                        }
                    )
                else:
                    return JsonResponse({'success': False, 'errors': form.errors.as_ul()})
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

def home(request):
    pin = request.session.get('user_id')
    context={}
    if pin:
        user= User.objects.get(pk=pin)
        user_type=""
        match user.users_type:
            case 'paie':
                users_all=User.objects.filter(delete_date=None).order_by('-id_user')[:5]
                count_users=User.objects.filter(delete_date=None).count()
                stt=User.objects.filter(users_type='stt',delete_date=None).count()
                con=User.objects.filter(users_type='con',delete_date=None).count()

                last_month_start= datetime.now().replace(day=1) - timedelta(days=1)
                last_month_start = last_month_start.replace(day=1)
                current_month_start = datetime.now().replace(day=1)

                user_last_month = User.objects.filter(created_date__gte=last_month_start, created_date__lt=current_month_start).count()
                user_current_month = User.objects.filter(created_date__gte=current_month_start).count()
                def croissance(y2,y1):
                    if y1!=0:
                        return ((y2 - y1) / y1)*100
                    else :
                        return 0
                user_type ="Ressources humaines"
                context={
                    'user':user,
                    'users_type':user_type,
                    'users_all':users_all,
                    'count_users':count_users,
                    'colab_users':(stt+con),
                    'croissance':croissance(user_current_month,user_last_month),
                }
            case 'admin':
                users_type ="Direction"
            case 'stt':
                users_type ="Freelance"
            case 'con':
                users_type ="Consultant"
            case 'com':
                users_type ="Commerciaux"
            case 'sup':
                users_type ="Super admin"
            case _:
                users_type="Inconue"
        
        return render(request,'pages/admin/home.html',context)
    return redirect('login')


def getcra(request):
    context={}
    pin=request.session.get('user_id')
    if pin:
        user= User.objects.get(pk=pin)
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
            case 'sup':
                users_type ="Commerciaux"
            case 'sup':
                users_type ="Super admin"
            case _:
                users_type="Inconue"
        context={
            'user':user,
            'users_type':users_type
        }
        return render(request,'pages/admin/gestion_cra/cra.html',context)
    else:
        return redirect('login')

def conge(request):
    pin=request.session.get('user_id')
    context={}
    if pin:
        user= User.objects.get(pk=pin)
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
            case 'sup':
                users_type ="Commerciaux"
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




def fiche_paie(request):
    pin=request.session.get('user_id')
    if pin:
        return render(request,'pages/admin/gestion_paie/fiche_de_paie.html')
    else:
        return redirect('login')

def note_frais(request):
    pin=request.session.get('user_id')
    if pin:
        return render(request,'pages/admin/gestion_note/note_de_frais.html')
    else:
        return redirect('login')
    

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
        users = User.objects.get(pk=uid)
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
