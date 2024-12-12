from .models import Car  , Moteurs , Radios , Booking , Client , Accessoire , Taux , Detail_accessoire  , Contactclient
from .serializers import UserSerializer
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail , get_connection
from django.http import HttpResponse, JsonResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from urllib.parse import urljoin
import cloudscraper
import json
import random
import requests

class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


def get_all_contacts(request):
    contacts = Contactclient.objects.all().values()
    return JsonResponse({'contacts': list(contacts)}, safe=False)


@csrf_exempt  # This is needed to bypass CSRF validation for simplicity; consider more secure methods in production.
def contact_view(request):
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            print(name)
            email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')
            current_date = datetime.now()
            contact_created = current_date.strftime('%Y-%m-%d')

            contact_details = {
                'name': name,
                'email':email ,
                'subject':subject,
                'message':message,
                'contact_created':contact_created
            }

            # Save to the Ahh model
            contact = Contactclient(name=name, email=email, subject=subject, 
                                    message=message , date_created = contact_created )
            contact.save()
            from_email = 'eliterentacartenerifer@gmail.com'
            message_ad_html = render_to_string('contact_email_template.html', contact_details)
            email_admin = EmailMultiAlternatives(
                f"New Contact Form Submission {contact_created}",
                message_ad_html,  # plain text version
                from_email,
                [from_email],
                connection=connection
            )
            email_admin.attach_alternative(message_ad_html, "text/html")
            send_mail(subject, message, email, [''], fail_silently=False)
            try:
                email_admin.send()
                return JsonResponse({'status': 'success', 'message': 'Form submitted successfully.'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def logout_view(request):
    from django.contrib.auth import logout
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logged out successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    


def get_owner_cars(nbr_j , taux):
    # Filter cars where is_owner_car is True
    owner_cars = Car.objects.filter(is_owner_car=True)
    dd = []
    for car in owner_cars:
        ##print(car.id_car)
        price = float(car.price) * nbr_j
        price = price + price * taux 
        counter = 0
        counter = counter + 1 if car.air_condition else counter
        counter = counter + 1 if car.power_steering else counter
        counter = counter + 1 if car.radio else counter
        counter = counter + 1 if car.central_locking else counter
        data_car = {
            'id': car.id,
            'title': car.title,
            'category': car.category,  # Make sure this matches your model field
            'price': price ,
            'image': car.image.url,
            'is_active': car.is_active,
            'air_condition': car.air_condition,
            'radio': car.radio,
            'power_steering': car.power_steering,
            'central_locking': car.central_locking,
            'number_doors': car.doors,
            'moteur': car.moteur,
            'is_owner_car': car.is_owner_car,
            'passengers': car.passengers,
            'car_model': car.car_model,
            'is_auto': car.is_auto,
            'counter':counter,
        }
        dd.append(data_car)
    return dd
        
def check_and_get_car_by_style(id_car,price,taux):
    try:
        ###print('check and get ')
        car_data = {}
        # Check if the car with the given style exists
        car = Car.objects.get(id_car=id_car)
       ###print(f"{car} exists. Details: {car.title}, {car.price}, {car.category}, {car.doors} doors, Active: {car.is_active}.")
        # If exists, return the car details
        price = float(price) + float(price) * taux
        counter = 0
        counter = counter + 1 if car.air_condition else counter
        counter = counter + 1 if car.power_steering else counter
        counter = counter + 1 if car.radio else counter
        counter = counter + 1 if car.central_locking else counter
        car_data = {
                'id': car.id,
                'title': car.title,
                'category': car.category,
                'price': price,
                'image': car.image.url if car.image else None,
                    'number_doors': car.doors,
                    'air_condition': car.air_condition,
                    'radio': car.radio,
                    'moteur': car.moteur,
                    'is_active': car.is_active,
                    "central_locking": car.central_locking,
                    'power_steering': car.power_steering,
                    'passengers': car.passengers,
                    'car_model': car.car_model,
                    'is_auto': car.is_auto,
                    'counter':counter

            }
        
        ###print(car_data)
        


    except Car.DoesNotExist:
        pass
        # If the car does not exist, return an appropriate message

    return car_data


def car_is_existe(id_car):
    car_styles_to_check = [id_car]
    # Récupérer les voitures dont le style est dans la liste car_styles
    existing_cars = Car.objects.filter(id_car__in=car_styles_to_check)
    
    # Extraire les styles des voitures existantes
    existing_styles = set(existing_cars.values_list('id_car', flat=True))
    return True if existing_styles else False


@csrf_exempt
def activation_car(request,car_id):
    if request.method == 'POST':
        car = get_object_or_404(Car, id=car_id)
        car.is_active = True if request.POST['is_active'] == 'true'  else False

        car.save()
        msg = {
            'message': 'ok'
        }
        return JsonResponse(msg)
    else :
        return JsonResponse({'error': 'Invalid request method'}, status=400)
# 



#@api_view(['POST'])
@csrf_exempt #@permission_classes([IsAuthenticated])
def update_taux(request):
    print('update taux')
    if 'taux' in request.POST:
        taux = Taux.objects.first()
        print('taux bd is ' , taux.taux_buy )
        taux.taux_buy = float(request.POST.get('taux'))
        taux.save()
        return JsonResponse({'message': 'okey', 'status': '200'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
@csrf_exempt
def get_taux(request):
    if request.method == 'GET':
        ##print("update car")
        taux =  Taux.objects.first()
        updated_data = {
            'taux': taux.taux_buy,
            'status': "200"
        }
        ##print(updated_data)
        return JsonResponse(updated_data)
    else :
        return JsonResponse({'error': 'Invalid request method'}, status=400)

#@api_view(['POST'])
@csrf_exempt #@permission_classes([IsAuthenticated])
def update_acc(request,id):

    acc =  acc = Accessoire.objects.get(id=id)
    acc.name = request.POST.get('name')
    acc.is_per_day = True if request.POST['is_per_day'] == 'true'  else False
    acc.price  = float(request.POST.get('price'))
    acc.description  = request.POST.get('description')
    acc.is_multiple  = True if request.POST['is_multiple'] == 'true'  else False
    acc.nbr_choices = int(request.POST['nbr_choices'])
    acc.save()
    updated_data = {
        'message': "okey",
        'status': "200"
    }
    ##print(updated_data)
    return JsonResponse(updated_data)

# Fetch car details based on start and end dates



#@api_view(['POST'])
@csrf_exempt #@permission_classes([IsAuthenticated])
def update_car(request,car_id):
    print("update car" , car_id)
    car = get_object_or_404(Car, id=car_id)
    ##print(request.POST.get('title'))
    ##print(request.POST.get('category'))
    ##print(request.POST.get('moteur'))
    if 'is_active' in request.POST:
        car.is_active = request.POST.get('is_active') == 'true'
    if 'title' in request.POST:
        car.title = request.POST['title']
    if 'category' in request.POST:
        car.category = request.POST['category']
    if 'car_model' in request.POST:
        car.car_model = request.POST['car_model']
    if 'moteur' in request.POST:
        car.moteur = request.POST['moteur']
    if 'price' in request.POST:
        car.price = request.POST['price']
    if 'air_condition' in request.POST:
        car.air_condition = request.POST.get('air_condition') == 'true'
    if 'radio' in request.POST:
        car.radio = request.POST.get('radio') == 'true'
    if 'power_steering' in request.POST:
        car.power_steering = request.POST.get('power_steering') == 'true'
    if 'central_locking' in request.POST:
        car.central_locking = request.POST['central_locking']
    if 'doors' in request.POST:
        car.doors = request.POST['doors']
    if 'passengers' in request.POST:
        car.passengers = request.POST['passengers']
    if 'is_auto' in request.POST:
        car.is_auto = request.POST.get('is_auto') == 'true'
    if 'image' in request.FILES:
        if request.FILES['image'] :
            car.delete_img()
            car.image = request.FILES['image']
    car.save()
    updated_data = {
        'title': car.title,
        'category': car.category,
        'price': car.price,
        'image': car.image.url if car.image else None
    }
    ##print(updated_data)
    return JsonResponse(updated_data)

# Fetch car details based on start and end dates


@csrf_exempt
def update_book(request,id_book):
    if request.method == 'POST':
        ##print("update car")
        car = get_object_or_404(Booking, id=id_book)
        if 'is_confirmed' in request.POST:
            car.is_confirmed = True
            car.is_canceled = False
        else:
            car.is_confirmed =  False
            car.is_canceled = True            
 
        car.save()
        updated_data = {
            'msg': 'success'
        }
        ##print(updated_data)
        return JsonResponse(updated_data)
    else :
        return JsonResponse({'error': 'Invalid request method'}, status=400)
# Fetch car details based on start and end dates



@csrf_exempt
def get_client(request, id):
    if request.method == 'GET':
        car = get_object_or_404(Client, id=id)
        data = {
                'id': car.id,
                'title': car.title,
                'category': car.category,
                'image': car.image.url if car.image else None,
                    'doors': car.doors,
                    'air_condition': car.air_condition,
                    'radio': car.radio,
                    'moteur': car.moteur,
                    "central_locking": car.central_locking,
                    'power_steering': car.power_steering ,
                    'passengers': car.passengers,
                    'car_model':car.car_model,
                    'is_auto':car.is_auto,
                    'is_owner_car':car.is_owner_car,
                    'price': car.price,
                    'is_active': car.is_active
            }
        return JsonResponse(data)

    else :
        return JsonResponse({'error': 'Invalid request method'}, status=400)
# Fetch car details based on start and end dates




@csrf_exempt
def get_car(request, car_id):
    if request.method == 'GET':
        car = get_object_or_404(Car, id=car_id)
        data = {
                'id': car.id,
                'title': car.title,
                'category': car.category,
                'image': car.image.url if car.image else None,
                    'doors': car.doors,
                    'air_condition': car.air_condition,
                    'radio': car.radio,
                    'moteur': car.moteur,
                    "central_locking": car.central_locking,
                    'power_steering': car.power_steering ,
                    'passengers': car.passengers,
                    'car_model':car.car_model,
                    'is_auto':car.is_auto,
                    'is_owner_car':car.is_owner_car,
                    'price': car.price,
                    'is_active': car.is_active
            }
        return JsonResponse(data)

    else :
        return JsonResponse({'error': 'Invalid request method'}, status=400)
# Fetch car details based on start and end dates

def insert_into(id_car,title,category,price,image_url,is_active,doors,air_condition,radio,power_steering,central_locking,moteur, passengers,car_model ,is_auto):
    ##print('inserting ...',id_car)
    import logging
    logger = logging.getLogger('myapp')
    response = requests.get(image_url)
    image_name = image_url.split('/')[-1]
    image_content = ContentFile(response.content)
    file_path = default_storage.save(f'cars/{image_name}', image_content)
    #style_obj = Styles.objects.filter(name__in=['default']).first()
    #moteur_obj = Moteurs.objects.filter(name__in=['default']).first()
    #radio_obj = Radios.objects.filter(name__in=['default']).first()
    car = Car( id_car=id_car,title=title,category=category,
            price=price,image=file_path,is_active = is_active,doors=doors,air_condition = air_condition
            ,radio = radio,power_steering = power_steering,
            central_locking = central_locking,moteur = moteur , passengers = passengers , car_model = car_model , is_auto = is_auto
        )
    car.save()
    cart_details = {'car' : car,
        'link':f'https://eliterent-car.onrender.com/sysadmin/update/{car.id}'
    }
    from_email = 'eliterentacartenerifer@gmail.com'
    message_ad_html = render_to_string('car_created_email.html', cart_details)
    email_admin = EmailMultiAlternatives(
        f"New Cars Was Added {cart_details}",
        message_ad_html,  # plain text version
        from_email,
        [from_email],
        connection=connection
    )
    email_admin.attach_alternative(message_ad_html, "text/html")
    send_mail("New Car Was Added !!!", message_ad_html, "ayoubelbahti79@gmail.com", [''], fail_silently=False)
    try:
        email_admin.send()
        logger.debug(f'new car added at {datetime.now()}')
    except Exception as e:
        print('error ! ', str(e))


def get_time_zones(start_datetime_string,end_datetime_string):
    import pytz

    # Define the date-time strings
    #start_datetime_string = "05/07/2024 15:30"
    #end_datetime_string = "10/07/2024 14:15"

    # Parse the date-time strings into datetime objects
    start_datetime_object = datetime.strptime(start_datetime_string, "%Y/%m/%d %H:%M")
    end_datetime_object = datetime.strptime(end_datetime_string, "%Y/%m/%d %H:%M")

    # Define the time zone (adjust according to your requirements)
    timezone = pytz.timezone('UTC')

    # Localize the datetime objects to the specified time zone
    start_datetime_object = timezone.localize(start_datetime_object)
    end_datetime_object = timezone.localize(end_datetime_object)

    # Convert the datetime objects to Unix timestamps
    start_unix_timestamp = int(start_datetime_object.timestamp())
    end_unix_timestamp = int(end_datetime_object.timestamp())

    print("start_time =", start_unix_timestamp)
    print("end_time =", end_unix_timestamp)
    return start_unix_timestamp , end_unix_timestamp



def get_scrap_data_car(car , start_date , end_date):
    import requests
    print("start_date : " , start_date)
    print("end_date  : " , end_date)
    cookies = {
        'lang': 'en',
        'PHPSESSID': 'v8js2ct4cvd5e4eabvrk526b46',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.5',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        # 'Cookie': 'lang=en; PHPSESSID=v8js2ct4cvd5e4eabvrk526b46',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Brave";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'step': 'popup',
        'car': car,
        'start_time': start_date,
        'end_time': end_date,
    }

    response = requests.get('https://www.pluscar-tenerife.com/booking.php', params=params, cookies=cookies, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extracting features
    features_div = soup.find('div', class_='pop-intern-feat-list')

    features = features_div.decode_contents().split('<br/>')
    # Extracting image source
    image_src = soup.find('div', class_='pop-intern-img').find('img')['src']
    doors = 0
    air_condition = False
    radio = False
    power_steering = False
    central_locking = ''
    moteur = ''

    # Assigning values to feature variables based on extracted features
    for feature in features:
        if 'doors' in feature.lower():
            doors = int(feature.lower().replace('doors','').replace(' ',''))
        elif 'air' in feature.lower():
            air_condition = True
        elif 'radio' in feature.lower():
            radio = True
        elif 'power' in feature.lower():
            power_steering = True
        #elif 'auto' in feature.lower():
        #    is_auto = True      avoir de tels ort inserer car_model
        elif 'lock' in feature.lower():
            central_locking = feature.lower()
        elif 'diesel' in feature.lower():
            moteur = feature.lower()

    return image_src,doors,air_condition,radio,power_steering,central_locking,moteur



def import_cars(request):
    current_date = datetime.now()


    # Format current date as '%d-%m-%Y'
    formatted_current_date = current_date.strftime('%Y/%m/%d')

    # Add 1 day to current date
    next_day_date = current_date + timedelta(days=1)
    next_day_date = next_day_date.strftime('%Y/%m/%d')
    print(formatted_current_date)
    print(next_day_date)

    cookies = {
        'lang': 'en',
        'PHPSESSID': 'v8js2ct4cvd5e4eabvrk526b46',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.5',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        # 'Cookie': 'lang=en; PHPSESSID=v8js2ct4cvd5e4eabvrk526b46',
        'Origin': 'https://www.pluscar-tenerife.com',
        'Referer': 'https://www.pluscar-tenerife.com/booking.php?lang=en',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Brave";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'lang': 'en',
    }

    data = {
        'step': 'step_1',
        'substep': 'search',
        'start_date': formatted_current_date,
        'start_hour_hour': "00",
        'start_minute': "00",
        'end_date':next_day_date,
        'end_hour_hour': "00",
        'end_minute': "00",
        'SUBMIT': 'Show cars and prices',
    }

    scraper = cloudscraper.create_scraper()

    response = scraper.post('https://www.pluscar-tenerife.com/booking.php', params=params, cookies=cookies, headers=headers, data=data)
    response_text = response.text  # Keep the text as it is without encoding/decoding

    # Use the right encoding to decode the response if needed
    response_text = response_text.encode(response.encoding).decode('utf-8')
    
    soup = BeautifulSoup(response_text, 'html.parser')
    cars_data = []

    cars = soup.find_all('div', class_='cars panel')
    base_url = "https://www.pluscar-tenerife.com"
    print(len(cars))
    import logging
    logger = logging.getLogger('myapp')
    logger.debug(f'{len(cars)} cars at {datetime.now()}')

    for car in cars:
        title = car.find('div', class_='cars_name').text
        id_car = title.replace(" ","_")
        if not car_is_existe(id_car):
            print(id_car , " is not eixiste ")
            start_timestamp , end_timestamp = get_time_zones(f'{formatted_current_date} 00:00' , f'{next_day_date} 00:00')
            relative_src,doors,air_condition,radio,power_steering,central_locking,moteur = get_scrap_data_car(title , start_timestamp , end_timestamp)
            src_img = urljoin(base_url, relative_src)
            styles = ['Mini', 'Economic', 'Standard', 'People Carriers', 'Luxury','SUVs'];
            category = random.choices(styles)[0]
            amount = car.find('div', class_='cars_price').text
            amount = amount.replace("€",'')
            amount = amount.replace(" ",'')
            is_actives = [True,False]
            is_autos = [True,False]
            is_active = random.choices(is_actives)
            is_auto = random.choices(is_autos)[0]
            cars_data.append(category)
            car_models = ['AUDI', 'MERCEDES', 'BMW', 'PORSCHE', 'VW', 'FERRARI', 'LAMBORGHINI', 'LEXUS', 'FORD MUSTANG', 'CHEVROLET CAMARO', 'TOYOTA', 'RENAULT', 'FIAT', 'SMART', 'PEUGEOT', 'MINI COOPER', 'SPECIAL OFFERS', 'TESLA', 'ŠKODA', 'BENTLEY', 'RANGE ROVER', 'HYUNDAI'];
            car_model = random.choices(car_models)[0]
            moteurs = ['gasoline', 'DIESEL', 'electric'];
            moteur = random.choices(moteurs)[0]
            passengers = [1 ,2 , 4 ]
            passen = random.choices(passengers)[0]
            insert_into(id_car,title,category,amount,src_img,is_active[0],doors,air_condition,radio,power_steering,central_locking,moteur
                         , passen, car_model , is_auto)

    ###print(cars_data)
    data = {
        "message": f'{len(cars_data)} cars imported ',
        "status": "success"
    }

    response = JsonResponse(data)
    response['X-Custom-Header'] = 'Custom Value'
    return response


@csrf_exempt
def delete_car(request, car_id):
    try:
        car = Car.objects.get(pk=car_id)
        car.delete()
        return JsonResponse({'message': 'Car deleted successfully'}, status=204)
    except Car.DoesNotExist:
        return JsonResponse({'error': 'Car not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Simple HTTP response example
def home_view(request):
    return HttpResponse("Hello!")
@csrf_exempt
def get_cars_from_db(request):
    try:
        # Fetch all cars from the database
        if request.method == 'GET':
            cars = Car.objects.all()
            taux = Taux.objects.first()
            #print(taux.taux_buy)
            # Serialize car data into JSON format
            cars_data = []
            for car in cars:
                counter = 0
                counter = counter + 1 if car.air_condition else counter
                counter = counter + 1 if car.power_steering else counter
                counter = counter + 1 if car.radio else counter
                counter = counter + 1 if car.central_locking else counter
                price = float(car.price) + float(car.price) * float(taux.taux_buy)
                car_data = {
                    'id': car.id,
                    'id_car': car.id_car,
                    'title': car.title,
                    'category': car.category,
                    'price': car.price,
                    'price_with_taux': price,
                    'image': car.image.url if car.image else None ,
                    'is_active': car.is_active,
                    'air_condition': car.air_condition,
                    'radio': car.radio,
                    'power_steering': car.power_steering,
                    'central_locking': car.central_locking,
                    'number_doors': car.doors,
                    'moteur ': car.moteur,
                    'passengers ': car.passengers,
                    'car_model ': car.car_model,
                    'is_auto ': car.is_auto,
                    'counter':counter
                    }
                ##print(car_data)
                cars_data.append(car_data)
            
            # Return JSON response with car data
            return JsonResponse(cars_data, safe=False)
        else:
            return JsonResponse({'error': 'bad request'}, status=500)
    except Exception as e:
        # Return error response if something goes wrong
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def get_cars_from_db_actives(request):
    try:
        # Fetch all cars from the database
        if request.method == 'GET':
            cars = Car.objects.filter(is_active=True)
            taux = Taux.objects.first()
            #print(taux.taux_buy)
            # Serialize car data into JSON format
            cars_data = []
            for car in cars:
                counter = 0
                counter = counter + 1 if car.air_condition else counter
                counter = counter + 1 if car.power_steering else counter
                counter = counter + 1 if car.radio else counter
                counter = counter + 1 if car.central_locking else counter
                price = float(car.price) + float(car.price) * float(taux.taux_buy)
                car_data = {
                    'id': car.id,
                    'id_car': car.id_car,
                    'title': car.title,
                    'category': car.category,
                    'price': car.price,
                    'price_with_taux': price,
                    'image': car.image.url if car.image else None ,
                    'is_active': car.is_active,
                    'air_condition': car.air_condition,
                    'radio': car.radio,
                    'power_steering': car.power_steering,
                    'central_locking': car.central_locking,
                    'number_doors': car.doors,
                    'moteur ': car.moteur,
                    'passengers ': car.passengers,
                    'car_model ': car.car_model,
                    'is_auto ': car.is_auto,
                    'counter':counter
                    }
                ##print(car_data)
                cars_data.append(car_data)
            
            # Return JSON response with car data
            return JsonResponse(cars_data, safe=False)
        else:
            return JsonResponse({'error': 'bad request'}, status=500)
    except Exception as e:
        # Return error response if something goes wrong
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt

def get_all_cars(request):
    try:
        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            start_hour = request.POST.get('start_hour')
            start_minute = request.POST.get('start_minute')
            end_hour = request.POST.get('end_hour')
            end_minute = request.POST.get('end_minute')
            nbr_jour = request.POST.get('nbr_jour')
            ##print(start_date)
            ##print(start_hour)
            ##print(start_minute)
            ##print(end_date)
            ##print(end_hour)
            ##print("end_minute" + end_minute)

            cookies = {
                'lang': 'en',
                'PHPSESSID': 'v8js2ct4cvd5e4eabvrk526b46',
            }

            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.5',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                # 'Cookie': 'lang=en; PHPSESSID=v8js2ct4cvd5e4eabvrk526b46',
                'Origin': 'https://www.pluscar-tenerife.com',
                'Referer': 'https://www.pluscar-tenerife.com/booking.php?lang=en',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Sec-GPC': '1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Brave";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            params = {
                'lang': 'en',
            }

            data = {
                'step': 'step_1',
                'substep': 'search',
                'start_date': start_date,
                'start_hour_hour': start_hour,
                'start_minute': start_minute,
                'end_date': end_date,
                'end_hour_hour': end_hour,
                'end_minute': end_minute,
                'SUBMIT': 'Show cars and prices',
            }

            scraper = cloudscraper.create_scraper()

            response = scraper.post('https://www.pluscar-tenerife.com/booking.php', params=params, cookies=cookies, headers=headers, data=data)
            response_text = response.text  # Keep the text as it is without encoding/decoding

            # Use the right encoding to decode the response if needed
            response_text = response_text.encode(response.encoding).decode('utf-8')
            
            soup = BeautifulSoup(response_text, 'html.parser')
            cars_data = []
            try:
        # Convert to decimal, will raise ValueError if not a valid number
                nbr_jour = float(nbr_jour)
                if nbr_jour != nbr_jour:  # This checks for NaN since NaN is not equal to itself
                    nbr_jour = 0
            except ValueError:
        # Handle the error appropriately
                nbr_jour = 0
            
            #Taux
            taux = Taux.objects.first()
            #print(taux.taux_buy)
            cars = soup.find_all('div', class_='cars panel')
            ##print(len(cars))
            for car in cars:
                title = car.find('div', class_='cars_name').text
                id_car = title.replace(" ","_")
                ###print(id_car)
                price = car.find('div',class_="cars_price").text
                amount = price.replace("€",'')
                ##print(id_car , " " , amount)
                #amount = float(amount) * nbr_jour
                ###print('nbr_jour ',float(amount) * nbr_jour)
                

               
                car_data = check_and_get_car_by_style(id_car,amount, float(taux.taux_buy))

                if car_data and car_data['is_active']:
                    cars_data.append(car_data)
            
            for cc in get_owner_cars(nbr_jour , float(taux.taux_buy)):
                cars_data.append(cc)
            

        else:
            return JsonResponse({'error': "bad request"}, status=500)

        return JsonResponse(cars_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def delete_all_cars(request):
    if request.method == 'POST':
        try:
            cars = Car.objects.all()
            for car in cars:
                car.delete()
            return JsonResponse({'message': 'All cars deleted successfully'}, status=204)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def get_acc(request, book_id):
    if request.method == 'GET':
        book = get_object_or_404(Booking, id=book_id)
        list_data=[]
        for acc_s in book.accessoire.all():
            data = {
                'acc_name': acc_s.acc.name,
                        'is_per_day': acc_s.acc.is_per_day,
                        'acc_price': acc_s.acc.price,
                        'quantity': acc_s.quantity,
                        'nbr_days': book.nbr_days,
                        'id_acc': acc_s.acc.id,
                }
            list_data.append(data)
            
        return JsonResponse(list_data ,safe=False)

    else :
        return JsonResponse({'error': 'Invalid request method'}, status=400)
# Fetch car details based on start and end dates

@csrf_exempt
def get_all_bookings(request):
    if request.method == 'GET':
        try:
            dt = []
            bookings = Booking.objects.all()
            for book in bookings:

                counter = 0
                counter = counter + 1 if book.car.air_condition else counter
                counter = counter + 1 if book.car.power_steering else counter
                counter = counter + 1 if book.car.radio else counter
                counter = counter + 1 if book.car.central_locking else counter

                book_data = {
                        'id':	book.id	,
                        'id_booking':	book.id_booking	,
                        'ass_price':	book.ass_price,
                        'total_price':book.total_price	,
                        'client_name':book.client.name	,
                        'client_surname':book.client.surname	,
                        'client_telephone':book.client.telephone	,
                        'client_email':book.client.email	,
                        'client_date_of_birth':book.client.date_of_birth	,
                        'car_name':book.car.title	,
                        'car_style':book.car.category	,
                        'car_id':book.car.id,
                        'is_confirmed':book.is_confirmed,
                        'is_canceled':book.is_canceled,
                        'taux_buy':book.taux_buy,
                        'car_price': book.car_price,
                        'profit': book.car_price - (book.car_price * book.taux_buy),
                        'date_created':book.date_created,
                        'comment':book.comment,
                        'hoteldropname':book.hoteldropname,
                        'hotelname':book.hotelname,
                        'country':book.client.country	,
                        'Pickupdate':book.client.country	,
                        'pickupdate': book.pickupdate,
                        'dropoffdate': book.dropoffdate,
                        'location': book.location,
                        'selected_return_location': book.selected_return_location,
                        'client_id': book.client.id,
                        'nbr_days':book.nbr_days,
                            'image': book.car.image.url if book.car.image else None,
                            'number_doors': book.car.doors,
                            'air_condition': book.car.air_condition,
                            'radio': book.car.radio,
                            'moteur': book.car.moteur,
                            'is_active': book.car.is_active,
                            "central_locking": book.car.central_locking,
                            'power_steering': book.car.power_steering,
                            'passengers': book.car.passengers,
                            'car_model': book.car.car_model,
                            'is_auto': book.car.is_auto,
                            'counter':counter,



                        }
                dt.append(book_data)

            return JsonResponse(dt, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def get_all_accessorys(request):
    if request.method == 'GET':
        try:
            dt = []
            accs = Accessoire.objects.all()
            for acc in accs:
                acc_data = {
                        'id':	acc.id	,
                        'name':	acc.name,
                        'is_per_day':acc.is_per_day	,
                        'price':acc.price	,
                        'nbr_choices':acc.nbr_choices	,
                        'description':acc.description	,
                        'is_multiple':acc.is_multiple	,

                        }
                dt.append(acc_data)

            return JsonResponse(dt, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def get_all_radios(request):
    if request.method == 'POST':
        try:
            dt = []
            radios = Radios.objects.all()
            for radio in radios:
                data_rad = {
                    'name': radio.name,
                }
                dt.append(data_rad)

            return JsonResponse(dt, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def get_all_moteurs(request):
    if request.method == 'POST':
        try:
            dt = []
            moteurs = Moteurs.objects.all()
            for moteur in moteurs:
                data_mot = {
                    'name': moteur.name,
                }
                dt.append(data_mot)

            return JsonResponse(dt, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


#@api_view(['POST'])
@csrf_exempt #@permission_classes([IsAuthenticated])
def add_car(request):
    title = request.POST.get('title')
    category = request.POST.get('category')
    price = request.POST.get('price')
    image = request.FILES.get('image')
    current_date = datetime.now()
    date_created = current_date.strftime('%Y_%m_%d')
    id_car = request.POST.get('title').replace(' ','_') + date_created
    is_active = request.POST.get('is_active') == 'true'
    air_condition = request.POST.get('air_condition') == 'true'
    radio = request.POST.get('radio') == 'true'
    power_steering = request.POST.get('power_steering') == 'true'
    central_locking = request.POST.get('central_locking')
    doors = request.POST.get('doors')
    moteur = request.POST.get('moteur')
    is_owner_car = True
    passengers = request.POST.get('passengers')
    car_model = request.POST.get('car_model')
    is_auto = request.POST.get('is_auto') == 'true'

    # Validate required fields
    car = Car(
        title=title,
        category=category,  # Assuming you have a typo here; should be 'category'
        price=price,
        image=image,
        id_car=id_car,
        is_active=is_active,
        air_condition=air_condition,
        radio=radio,
        power_steering=power_steering,
        central_locking=central_locking,
        doors=int(doors),
        moteur=moteur,
        is_owner_car=is_owner_car,
        passengers=int(passengers),
        car_model=car_model,
        is_auto=is_auto
    )
    car.save()
    data = {
        'message': 'Car added successfully',
        'status': 'success'
    }
    return JsonResponse(data)



@csrf_exempt
def send_booking_confirmation(recepteur , admin_mail ,booking_details , lang):

    translations = {
    'en': {
        'title': 'Booking Confirmation',
        'dear': 'Dear',
        'front_message': 'Thank you for booking with us!',
        'car_name_label': 'Car Name',
        'car_style_label': 'Car Style',
        'hotel_drop_name_label': 'Hotel Drop Name',
        'hotel_name_label': 'Hotel Name',
        'pickup_date_label': 'Pickup Date',
        'dropoff_date_label': 'Dropoff Date',
        'location_label': 'Location',
        'return_location_label': 'Return Location',
        'number_of_days_label': 'Number of Days',
        'total_price_label': 'Total Price',
        'back_message': 'We look forward to serving you!'
    },
    'es': {
        'title': 'Confirmación de Reserva',
        'dear': 'Estimado',
        'front_message': """Gracias por su reserva.\n
                Hemos recibido su solicitud a los siguientes parámetros:""",
        'car_name_label': 'Nombre del Coche',
        'car_style_label': 'Estilo del Coche',
        'hotel_drop_name_label': 'Nombre del Hotel de Entrega',
        'hotel_name_label': 'Nombre del Hotel',
        'pickup_date_label': 'Fecha de Recogida',
        'dropoff_date_label': 'Fecha de Devolución',
        'location_label': 'Ubicación',
        'return_location_label': 'Lugar de Devolución',
        'number_of_days_label': 'Número de Días',
        'total_price_label': 'Precio Total',
        'back_message': """Comprobaremos la disponibilidad para sus fechas y les enviaremos la confirmación lo antes posible
            \nSaludos, Elite rent a car"""
    },
    'rus': {
        'title': 'Подтверждение бронирования',
        'dear': 'Уважаемый',
        'front_message': """Спасибо за ваше бронирование .
                Мы получили вашу заявку по следующим параметрам : """,
        'car_name_label': 'Название автомобиля',
        'car_style_label': 'Стиль автомобиля',
        'hotel_drop_name_label': 'Название отеля доставки',
        'hotel_name_label': 'Название отеля',
        'pickup_date_label': 'Дата получения',
        'dropoff_date_label': 'Дата возврата',
        'location_label': 'Местоположение',
        'return_location_label': 'Место возврата',
        'number_of_days_label': 'Количество дней',
        'total_price_label': 'Общая цена',
        'back_message': """Мы проверим доступность на ваши даты и и отправим вам всю
            Информацию в ближайшее время.\n
            Спасибо, что выбрали наш сервис ."""
    }
}
    booking_details.update(translations.get(lang, translations['en']))
    from_email = 'eliterentacartenerifer@gmail.com'
    subject = 'Booking Confirmation'
    ad_subject = f'New Booking {booking_details["id_booking"]}'
    message_html = render_to_string('booking_confirmation_email.html', booking_details)
    message_ad_html = render_to_string('admin_notification_email.html', booking_details)
    # Use EmailMultiAlternatives to send both plain text and HTML versions
    email = EmailMultiAlternatives(
        subject,
        message_html,  # plain text version
        from_email,
        [recepteur],
        connection=connection
    )
    email.attach_alternative(message_html, "text/html")

    email_admin = EmailMultiAlternatives(
        ad_subject,
        message_ad_html,  # plain text version
        from_email,
        [admin_mail],
        connection=connection
    )
    email_admin.attach_alternative(message_ad_html, "text/html")

    try:
        email.send()
        email_admin.send()
        return JsonResponse({'status': 'success', 'message': 'Confirmation email sent successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



#@api_view(['POST'])
@csrf_exempt #@permission_classes([IsAuthenticated])
def add_acc(request):
    name = request.POST.get('name')
    price = request.POST.get('price')
    description = request.POST.get('description')
    is_multiple = True if request.POST['is_multiple'] == 'true'  else False
    is_per_day = True if request.POST['is_per_day'] == 'true'  else False
    nbr_choices = request.POST.get('nbr_choices')
    acc = Accessoire(
        name=name,
        is_per_day=is_per_day,  # Assuming you have a typo here; should be 'category'
        price=price,
        description=description,
        is_multiple=is_multiple,
        nbr_choices=nbr_choices
    )
    acc.save()
    data = {
        'message': 'Accessory added successfully',
        'status': 'success'
    }
    return JsonResponse(data)




@csrf_exempt
def add_book(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        telephone = request.POST.get('telephone')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('date_of_birth')
        country = request.POST.get('country')
        hotelname = request.POST.get('hotelname')
        language = request.POST.get('language')
        hoteldropname = request.POST.get('hoteldropname')
        pickupdate = request.POST.get('pickupdate')
        location = request.POST.get('selectedPickLocation')
        dropoffdate = request.POST.get('dropoffdate')
        selected_return_location = request.POST.get('selectedReturnLocation')
        nbr_days = request.POST.get('nbr_days')
        ass_price = request.POST.get('total_acc', '0')
        car_price = request.POST.get('car_price', '0')
        taille = request.POST.get('taille')
        try:
        # Convert to decimal, will raise ValueError if not a valid number
            ass_price = float(ass_price)
            if ass_price != ass_price:  # This checks for NaN since NaN is not equal to itself
                ass_price = 0
        except ValueError:
        # Handle the error appropriately
            ass_price = 0


        
        client = Client(name=name, surname=surname,telephone=telephone, email=email,date_of_birth=date_of_birth , country=country)
        client.save()
        total_price = request.POST.get('total_price')
        try:
        # Convert to decimal, will raise ValueError if not a valid number
            total_price = float(total_price)
            if total_price != total_price:  # This checks for NaN since NaN is not equal to itself
                total_price = 0
        except ValueError:
        # Handle the error appropriately
            total_price = 0
        car_id = request.POST.get('car_id')
        comment = request.POST.get('comment')

        car = Car.objects.filter(id=car_id).first()

        current_date = datetime.now()

        # Format current date as '%d-%m-%Y'
        date_created = current_date.strftime('%Y-%m-%d')
        taux =  Taux.objects.first()
        book = Booking(total_price=total_price, car=car,client=client,ass_price=ass_price , 
                        comment=comment , date_created = date_created 
                        , pickupdate = pickupdate , dropoffdate= dropoffdate , 
                        nbr_days = nbr_days , selected_return_location = selected_return_location , 
                        location = location , taux_buy = taux.taux_buy , car_price = car_price,
                        hoteldropname = hoteldropname , hotelname = hotelname)
        book.save()

        for i in range(0,int(taille)):
            # Access individual accessory properties
            acc_name = request.POST.get(f'accessories[{i}][acc_name]')
        # GET ACCESSOIRE 
            acc_quantity = request.POST.get(f'accessories[{i}][acc_quantity]')
            ac_id = request.POST.get(f'accessories[{i}][ac_id]')
            print(ac_id)
            print(acc_name)
            acc = Accessoire.objects.get(id = ac_id)
        # CREATE ACC DETAIL
            acc_detail = Detail_accessoire(quantity = acc_quantity) 
            acc_detail.acc = acc
            acc_detail.save()
            book.accessoire.add(acc_detail)



        #ADD ACC TO DETAIL 

        # ADD DETAIL TO BOOK
        
        front_message = "Спасибо за ваше бронирование . \n Мы получили вашу заявку по следующим параметрам : "
        back_message = """Мы проверим доступность на ваши даты и и отправим вам всю
                            Информацию в ближайшее время.
                            Спасибо, что выбрали наш сервис .

                            С уважением, elite rent a car"""
        book.save()
        booking_details = {
            'client':name,
            'front_message': front_message,
            'back_message': back_message,
                'total_price': book.total_price,
                'car_name': book.car.title,
                'car_style': book.car.category,
                'hoteldropname': book.hoteldropname,
                'hotelname': book.hotelname,
                'Pickupdate': book.client.country,
                'pickupdate': book.pickupdate,
                'dropoffdate': book.dropoffdate,
                'location': book.location,
                'selected_return_location': book.selected_return_location,
                'nbr_days': book.nbr_days,
                'id_booking': book.id_booking,
                'mark':"Elite",
                'link':"https://eliterent-car.onrender.com/admin/book",
                'image': "image_url"
            }
        
    # Compose email
        send_booking_confirmation(email , "eliterentacartenerifer@gmail.com",booking_details,language)
        data = {
            'message': 'book added successfully',
            'status': 'success'
        }
        return JsonResponse(data)





def ayoub(title):
    print(title)


#@api_view(['POST'])
@csrf_exempt #@permission_classes([IsAuthenticated])
def add_moteur(request):
    title = request.POST.get('title')
    if title:
        moteur = Moteurs(name=title)
        moteur.save()
        data = {
            'message': 'moteur added successfully',
            'status': 'success'
        }
    else:
        data = {
            'message': 'Invalid data',
            'status': 'error'
        }
    return JsonResponse(data)


#@api_view(['POST'])
@csrf_exempt #@permission_classes([IsAuthenticated])
def add_radio(request):
    title = request.POST.get('title')
    if title:
        radio = Radios(name=title)
        radio.save()
        data = {
            'message': 'radio added successfully',
            'status': 'success'
        }
    else:
        data = {
            'message': 'Invalid data',
            'status': 'error'
        }
    return JsonResponse(data)

