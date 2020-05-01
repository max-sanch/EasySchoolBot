import urllib.request
from bs4 import BeautifulSoup


def get_soup(url):
	# Делаем запрос на сайт
	response = urllib.request.urlopen(url)
	# Получаем html страницы
	html = response.read()
	return BeautifulSoup(html)

def pars_centers():
	soup = get_soup("http://e-a-s-y.ru/contacts/")
	centers_list = soup.find('div', class_="contacts__list")
	centers_list = centers_list.find_all('div', class_="contacts-card")
	output = []
	# Добавляем все школы в список
	for center in centers_list:
		name = center.find('h3').text
		adress = center.find_all('p')[0].text
		email = center.find_all('p')[1].text[1:]
		work_time = center.find_all('div', class_="contacts-card__schedule")
		time_list = [time.text for time in work_time]
		output.append({
			'name': name,
			'adress': adress,
			'email': email,
			'time': time_list})
	return output

def pars_events():
	soup = get_soup("http://e-a-s-y.ru/events/")
	events_list = soup.find_all('div', class_="events-list__item")
	output = []
	# Добавляем все мероприятия в список
	for event in events_list:
		link = event.find('a')['href']
		description = event.find('div', class_="card-current__excerpt").text
		age = event.find('small').text
		if age == '':
			age = "0+"
		name = event.find('h3', class_="card-current__title").text
		date = event.find('span').text
		output.append({
			'name': name + " (" + age + ") ",
			'date': date,
			'link': link,
			'description': description})
	return output
