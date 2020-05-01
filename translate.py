import urllib.request
from bs4 import BeautifulSoup
import requests

URL = "https://translate.yandex.net/api/v1.5/tr.json/translate"
KEY = "trnsl.1.1.20191018T053625Z.94f9b7c48e3a3d90.adfa6a649a24aba190fe7bf885a1ac024deaa7b1"

def translate(text):
	params = {
		"key": KEY,     
		"text": text,
		"lang": 'ru-en'
		}
	# Делаем запрос на перевод
	response = requests.get(URL ,params=params)
	# Получаем ответ
	json = response.json()
	translated_text = json['text'][0]
	return translated_text