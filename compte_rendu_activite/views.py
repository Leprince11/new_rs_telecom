from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.shortcuts import get_object_or_404
import calendar
import os
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.templatetags.static import static

from jours_feries_france import JoursFeries
from datetime import datetime,timedelta
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from compte_rendu_activite.models import CRA,Users,Mission
from pulls import utils


# Create your views here.

def getMonth(month):
    months = {
    1: 'Janvier',
    2: 'Février',
    3: 'Mars',
    4: 'Avril',
    5: 'Mai',
    6: 'Juin',
    7: 'Juillet',
    8: 'Août',
    9: 'Septembre',
    10: 'Octobre',
    11: 'Novembre',
    12: 'Décembre'
}
    
    if month < 1 or month > 12:
        return "Numéro de mois invalide. Veuillez saisir un nombre compris entre 1 et 12."
    month_name = months.get(month)
    
    return month_name


@utils.login_required_connect
def getcra(request):
    user=request.user
    context={}
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    pin = request.session.get('user_id')
    user= Users.objects.get(pk=pin)
    exit=CRA.objects.filter(user=user,start_date__month=current_date.month).exists
    current_month_year=f"{getMonth(current_month)} {current_year}"
    context = {
        'user':user,
        'exit':exit,
        'Annee':current_month_year,
        'userId':user.id_user
    }
    return render(request,'pages/gestion_cra/cra.html',context)

def getClassForCategorie(categorie,hours):
    if categorie == "Mission" and str(hours) != '13':
        return 'bg-success'
    elif categorie == "Absence" and str(hours) != '13':
        return 'bg-danger'
    elif categorie == "Ferie":
        return 'bg-primary'
    return 'bg-warning' 

def initcra(request):
    if request.method=="GET":
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        pin = request.session.get('user_id')
        user= Users.objects.get(pk=pin)
        cras = CRA.objects.filter(start_date__year=current_year, start_date__month=current_month,user=user)

        events = []
        for cra in cras:
            event = {
                'id': cra.id_cra,
                'title': cra.categorie,
                'start': cra.start_date.strftime('%Y-%m-%dT%H:%M:%S'),
                'end': cra.end_date.strftime('%Y-%m-%dT%H:%M:%S'),
                'className': getClassForCategorie(cra.categorie,cra.end_date.hour)
            }
            events.append(event)
        return JsonResponse(events ,safe=False)


def get_weekends(year, month):
    weekends = []
    date = datetime(year, month, 1)
    while date.month == month:
        if date.weekday() in (5, 6):
            weekends.append(date)
        date += timedelta(days=1)
    return weekends

@utils.login_required_connect
def created_cra_datetime(request):
    if request.method == 'POST':
        datetime_str = request.POST.get('datetime')
        mess=""
        try:
            dt = datetime.strptime(datetime_str, '%Y-%m-%d')
            year, month = dt.year, dt.month
            first_day = datetime(year, month, 1)
            if month == 12:
                last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = datetime(year, month + 1, 1) - timedelta(days=1)
            weekends = get_weekends(year, month)
            local_tz = timezone.get_current_timezone()
            weekends_str = [weekend.strftime('%Y-%m-%d') for weekend in weekends]
            current_day = first_day
            jours_feries = JoursFeries.for_year(first_day.year)
            pin = request.session.get('user_id')
            user= Users.objects.get(pk=pin)
            while current_day <= last_day:
                current_day_str = current_day.strftime('%Y-%m-%d')
                local_tz = timezone.get_current_timezone()
                start_time = timezone.make_aware(current_day.replace(hour=9, minute=0, second=0, microsecond=0), local_tz)
                end_time = timezone.make_aware(current_day.replace(hour=18, minute=0, second=0, microsecond=0), local_tz)

                if current_day_str in weekends_str:
                    pass
                else:
                    categorie = dict(CRA.choose_categorie)[1]
                    for nom_jour_ferie, date_jour_ferie in jours_feries.items():
                        if current_day.date() == date_jour_ferie:
                            categorie = dict(CRA.choose_categorie)[3] 
                            break
                    try :
                        existing_cra = CRA.objects.filter(
                            user=user,
                            start_date__date=start_time.date(),
                        ).exists()
                        cra = CRA.objects.filter(
                            user=user,
                            start_date__date=start_time.date(),
                        ).first()
                        if existing_cra:
                            response_data = {
                                'success':True,
                                'message': 'Un CRA existe déjà pour ce mois',
                            }
                            return JsonResponse(response_data)
                        
                        cra = CRA(
                            user=user,
                            start_date=start_time,
                            end_date=end_time,
                            categorie=categorie 
                        )
                        cra.save()
                    except Exception as e:
                        print(e)  
                current_day += timedelta(days=1)

            response_data = {
                    'success':True,
                    'message': "Felecitation votres Compte rendu d'activite"
            }
            return JsonResponse(response_data)
        except ValueError:
            response_data = {
                    'success':False,
                    'message': "Invalid datetime format. Use YYYY-MM-DD."
            }
            return JsonResponse(response_data, status=400)
    else:
        response_data = {
                'success':False,
                'message': "Invalid request"
        }
        return JsonResponse(response_data, status=400)
    
def parse_custom_datetime(date_str):
    try:
        # Définissez le format de date attendu
        return datetime.strptime(date_str, '%a %b %d %Y %H:%M:%S GMT%z (%Z)')
    except ValueError:
        return None
    
@utils.login_required_connect
@utils.utilisateur_autorise(types_autorises=["Consultant","Freelance","Ressources humaines","Direction"])
def manage_cra(request, id_cra=None):
    if request.method == 'POST':
        title = request.POST.get('category-mission')
        # start = request.POST.get('start')
        end = request.POST.get('end')
        categoryTemps = request.POST.get('category-temps')

        user=request.user

        print(title, end,categoryTemps)
        if not all([title, end, categoryTemps]):
            return JsonResponse({'status': 'failed', 'message': 'Missing required fields.'}, status=400)

        # Parsing start and end dates
        try:
            dt = datetime.strptime(end, '%Y-%m-%d')
            
            end_date = parse_custom_datetime(end)
        except Exception as e:
            print({'message:',e})

        

        category_mapping = {
            "Mission": 1,
            "Absence": 2,
            "Ferie": 3
        }
        category_number = category_mapping.get(title, 1)  

        
        if categoryTemps == 'half-day':
            end_date = dt.replace(hour=13, minute=0, second=0, microsecond=0)
        else:
            end_date = dt.replace(hour=18, minute=00, second=00, microsecond=0)
        


        if id_cra:
            
            event = get_object_or_404(CRA, id_cra=id_cra)
            event.end_date = end_date
            event.categorie = dict(CRA.choose_categorie)[category_number] 
            event.save()
            return JsonResponse({'status': 'success'})
        else:
            # Check if an event already exists for the day
            if CRA.objects.filter(user=user).exists():
                return JsonResponse({'status': 'failed', 'message': 'Un événement existe déjà pour ce jour.'}, status=400)
            
            # Create a new event
            event = CRA.objects.create(
                categorie=dict(CRA.choose_categorie)[category_number],
                end_date=end_date,
                user=user
            )
            return JsonResponse({'status': 'success', 'event_id': event.id})
    
    return JsonResponse({'status': 'failed'}, status=400)



def fetch_cra_data(user):
    now = datetime.now()
    current_month = now.strftime('%m/%Y')
    report_date = now.strftime('%d/%m/%Y')
    
    cra_entries = CRA.objects.filter(user=user, start_date__year=now.year, start_date__month=now.month)
    
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    days = []
    total_hours = 0
    days_map = {
        'Mon': 'L',
        'Tue': 'M',
        'Wed': 'M',
        'Thu': 'J',
        'Fri': 'V',
        'Sat': 'S',
        'Sun': 'D'
    }
    
    for day in range(1, days_in_month + 1): 
        date = datetime(now.year, now.month, day)
        hours = 0
        for entry in cra_entries:
            if entry.start_date.day == day:
                if int((entry.end_date - entry.start_date).seconds / 3600)==9:
                    hours += 1
                elif int((entry.end_date - entry.start_date).seconds / 3600)==4:
                    hours += 0.5
                
            
        
        short_weekday = days_map[date.strftime('%a')]
        days.append({
            'day': day,
            'short_weekday': short_weekday,
            'hours': hours if hours > 0 else '  '
        })
        total_hours += hours
    
    return {
        'user_name': f"{user.users_name} {user.users_fname}",
        'current_month': current_month,
        'report_date': report_date,
        'days': days,
        'total_hours': total_hours
    }

def generate_cra_pdf(request, user_id):
    user = get_object_or_404(Users, id_user=user_id)
    mission= get_object_or_404(Mission,id_mission=user.id_mission)
    data = fetch_cra_data(user)
    data['logo_url'] = request.build_absolute_uri(static('images/logo.png'))
    data['mission']=mission
    
    html_content = render_to_string('pages/gestion_conge/cra_rapport.html', data)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="CRA_{user.users_name}_{data["current_month"]}.pdf"'
    
    pdf_status = pisa.CreatePDF(
        html_content,
        dest=response,
        encoding='utf-8'
    )
    
    if pdf_status.err:
        return HttpResponse(f'Nous avons rencontré des erreurs <pre>{html_content}</pre>')
    
    return response


def rapport(request):
    return render(request,'pages/gestion_conge/cra_rapport.html')