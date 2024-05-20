from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.http import JsonResponse   
from urllib.parse import urljoin
import json
from bs4 import BeautifulSoup

cookies = {

    'PHPSESSID': '5cc2f9c83d91369fa38ef5fbeb5c0ae7',

    'pref_lng': 'en',

}

 

headers = {

    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',

}


def get_cars(request):
    return render(request, 'your_template.html')

def get_details(request,start_date,end_date):
    from datetime import datetime
    print(start_date)
    print(end_date)
    start_date_obj = datetime.strptime(start_date, '%d-%m-%Y')
    end_date_obj = datetime.strptime(end_date, '%d-%m-%Y')
    # Convert the dates to "yyyy/mm/dd" format
    start_date_formatted = start_date_obj.strftime('%Y/%m/%d')
    end_date_formatted = end_date_obj.strftime('%Y/%m/%d')
    print(start_date_formatted)
    print(end_date_formatted)

    data = {
    'place': '3',
    'place_details': '',
    'returndiff': '0',
    'placereturn': '0',
    'date_from': start_date_formatted,
    'time_from': '10:00',
    'date_till': end_date_formatted,
    'time_till': '10:00',
    'carid': '0',
}
    response = requests.post('https://www.rentalcar-tenerife.com/en/rent/', cookies=cookies, headers=headers, data=data)
    print(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')
    cars_data = []
    cars = soup.find_all('div',class_='row offer-item car-item')
    base_url = "https://www.rentalcar-tenerife.com"
    for car in cars:
        relative_src = car.find("img")['src']
        src_img = urljoin(base_url, relative_src)
        title = car.find("h2").text
        style = car.find("h5").text
        description = car.find("p").text
        amount = car.find("p",class_="offer-price").find("span").text
        tt = car.find("p",class_="offer-price").find("span").text
        offer_price = car.find("p",class_="offer-price").text.replace(tt,"")
        car_data = {
        "src_img": src_img,
        "title": title,
        "style": style,
        "description": description,
        "amount": amount,
        "offer_price": offer_price
            }
    
        cars_data.append(car_data)
    json_data = json.dumps(cars_data)

    # Create a JsonResponse object with the JSON data

    data = {
        "message": cars_data,
        "status": "success"
    }

    response = JsonResponse(data)

    # Add custom headers to the response
    response['X-Custom-Header'] = 'Custom Value'

    return response

def details(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        start_hour = request.POST.get('start_hour_hour') + ':' + request.POST.get('start_minute')
        end_date = request.POST.get('end_date')
        end_hour = request.POST.get('end_hour_hour') + ':' + request.POST.get('end_minute')
        print(start_date)
        print(start_hour)
        print(end_date)
        print(end_hour)
        data = {
                    'need_place_details': '0',
                    'place': '4',
                    'place_details': '',
                    'placereturn': '3',
                    'date_from': start_date,
                    'time_from': start_hour,
                    'date_till': end_date,
                    'time_till': end_hour,
                }
        
        response = requests.post('https://www.rentalcar-tenerife.com/en/rent/', cookies=cookies, headers=headers, data=data,stream=True)
        if response.ok:
            
            soup = BeautifulSoup(response.text, 'html.parser')
            cars_data = []
            cars = soup.find_all('div',class_='row offer-item car-item')
            base_url = "https://www.rentalcar-tenerife.com"
            for car in cars:
                relative_src = car.find("img")['src']
                src_img = urljoin(base_url, relative_src)
                title = car.find("h2").text
                style = car.find("h5").text
                description = car.find("p").text
                amount = car.find("p",class_="offer-price").find("span").text
                tt = car.find("p",class_="offer-price").find("span").text
                offer_price = car.find("p",class_="offer-price").text.replace(tt,"")
                car_data = {
                "src_img": src_img,
                "title": title,
                "style": style,
                "description": description,
                "amount": amount,
                "offer_price": offer_price
                    }
            
                cars_data.append(car_data)
            json_data = json.dumps(cars_data)

            print(cars_data)
            print(len(cars))

        else:

            # Handle errors or unexpected responses

            print(f"Error: {response.status_code}")

        # Similarly, get other form data
        # Process the form data as needed
    else:
        # Handle GET request or render initial form
        pass  
    return render(request, 'details.html',{
            'start_date': start_date,
            'start_hour': start_hour,
            'end_date': end_date,
            'end_hour': end_hour,
            'cars_data': cars_data,
            'result': len(cars)
        })

def download_fb_video(request):
    url = request.GET.get('url_param')
    download.url = str(url).replace("ẞ",'&') 
    #print(url)  
    # Create a dictionary representing your JSON data
    response = download.facebook()
    if response['status_code'] == 200:
        data = response
    else:
        data = {
            "message": response['message'],
            "status": "failed"
        }

    # Create a JsonResponse object with the JSON data
    response = JsonResponse(data)

    # Add custom headers to the response
    response['X-Custom-Header'] = 'Custom Value'

    return response




def hello_world(request):
    # Create a dictionary representing your JSON data
    data = {
        "message": "hello pages ",
        "status": "success"
    }

    # Create a JsonResponse object with the JSON data
    response = JsonResponse(data)

    # Add custom headers to the response
    response['X-Custom-Header'] = 'Custom Value'

    return response

def home_view(request):
    return HttpResponse("Hello!")
