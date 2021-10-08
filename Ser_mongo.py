# Внесение в базу данных и проверка на дубликаты встроенна непосредственно в парсер и работают автоматически с его запуском.
#база размещена на внешнем сервере https://cloud.mongodb.com/v2/6159636eb0b05966e26cc609#security/network/accessList(есть урезанный бесплатный вариант) настроена на вход с любого IP (0.0.0.0/0) проблем быть не должно.
#возможные лаги, у pymongo возможны проблемы с зависимостями, также могут быть проблемы с настройкой политики сертификатов безопасности
#при соеденениии  с базой данных.
from pymongo import MongoClient
import bs4
from bs4 import BeautifulSoup
import requests

cluster = MongoClient(
    "mongodb+srv://A-WWW:32125M32125@cluster0.0b6py.mongodb.net/Testdata1?retryWrites=true&w=majority")
db = cluster["Testdata1"]
collection = db["Testcol1"]

URL = 'https://electrica-shop.com.ua/c74-rozetki_i_viklyuchateli/filter/494p-1228.m-5/page/2'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36',
    'accept': '*/*'}


def get(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r

def parse():
    html = get(URL)
    if html.status_code == 200:
        print('ok we have 200')
        get_cont(html.text)
    else:
        print("что то пошло не так")

def get_cont(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all(class_='products-txt-block')
    prod = []
    presence = []
    for item in items:
        prod.append({'Изделие': item.find(class_='products-name').get_text(strip=True),
                     'Наличие': item.find(class_='products-quantity instock').get_text(strip=True)})
    print(f'Получено {len(prod)} товарных едениц')
    for value in prod:
        # print(value)
#обычно использается подход с поиском скертефекатов уже в базе денных (агрегация,distinct,deleteMany ,в различных вариациях) но
#учитывая характер спарсенных данных проще отлавливать их на перед внесением в базу данных.
        if len(list(collection.find(value))) == 0:
            collection.insert_one(value)
parse()

# collection.remove( {} )
#collection.delete_many({})
# f = list(collection.distinct('Изделие'))

print('В колекции находится', collection.count_documents({}), "документов")
for i in list(collection.find({})):
    print(i[ 'Изделие'], i ['Наличие'])

