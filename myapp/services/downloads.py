import requests
from bs4 import BeautifulSoup
cookies = {

    'PHPSESSID': '5cc2f9c83d91369fa38ef5fbeb5c0ae7',

    'pref_lng': 'en',

}

from datetime import datetime

headers = {

    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',

}

data = {
    'place': '3',
    'place_details': '',
    'returndiff': '0',
    'placereturn': '0',
    'date_from': '2024/06/16',
    'time_from': '10:00',
    'date_till': '2024/06/20',
    'time_till': '10:00',
    'carid': '0',
}

# Parse the dates in "dd-mm-yyyy" format
start_date_obj = datetime.strptime("16-06-2024", '%d-%m-%Y')
end_date_obj = datetime.strptime("20-06-2024", '%d-%m-%Y')


# Convert the dates to "yyyy/mm/dd" format
start_date_formatted = start_date_obj.strftime('%Y/%m/%d')
end_date_formatted = end_date_obj.strftime('%Y/%m/%d')


print(start_date_formatted)
print(end_date_formatted)
response = requests.post('https://www.rentalcar-tenerife.com/en/rent/', cookies=cookies, headers=headers, data=data)

soup = BeautifulSoup(response.text, 'html.parser')
cars_data = []
cars = soup.find_all('div',class_='row offer-item car-item')
print(len(cars))