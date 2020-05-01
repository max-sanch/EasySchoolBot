import time
import json

from telebot import types
from telebot import TeleBot
from telebot.types import Message

import message_text
import translate
import database
import parsers

TOKEN = ''
bot = TeleBot(TOKEN)


class MarkupManager:
	def __init__(self):
		super(MarkupManager, self).__init__()
	
	def update(self, message):
		authorization = Authorization()
		translator = Translator()
		# Получаем статус авторизации
		status_auth = authorization.status(message.chat.id)
		# Размечаем кнопки в зависимости от статуса
		if status_auth == 3:
			# Получаем статус переводчика
			isTranslat = translator.status(message.chat.id)
			if isTranslat:
				markup = self.getTranslat()
			else:
				markup = self.getAuth()
		elif status_auth == 0 or status_auth == None:
			markup = self.getUnAuth()
		else:
			markup = self.getGoAuth()
		return markup

	def getTranslat(self):
		# Разметка для переводчика
		markup=types.ReplyKeyboardMarkup()
		markup.row('❌ Выход')
		return markup

	def getGoAuth(self):
		# Разметка для авторизации
		markup=types.ReplyKeyboardMarkup()
		markup.row('❌ Отмена')
		return markup

	def getUnAuth(self):
		# Разметка для неавторизованного
		markup=types.ReplyKeyboardMarkup()
		markup.row('✅ Авторизация')
		markup.row('🎈 Мероприятия', '🏫 Школы')
		markup.row('👨🏼‍💻 Помощь')
		return markup

	def getAuth(self):
		# Разметка для авторизованного
		markup=types.ReplyKeyboardMarkup()
		markup.row('📚 Домашка', '📋 Оценки')
		markup.row('🇬🇧 Переводчик', '🏫 Школы')
		markup.row('🎈 Мероприятия', '❌ Выход')
		markup.row('👨🏼‍💻 Помощь')
		return markup

class StatusUsers:
	def __init__(self):
		super(StatusUsers, self).__init__()

	def getData(self):
		# Получаем данные из файла
		with open('databases/status_users.json') as f:
			data = json.load(f)
		return data

	def search(self, id):
		data = self.getData()
		array = data['users']
		low = 0
		high = len(array)-1
		# Бинарный поиск по id пользователя
		while low <= high:
			mid = (low + high) // 2
			if id < array[mid]['id']:
				high = mid - 1
			elif id > array[mid]['id']:
				low = mid + 1
			else:
				return mid
		return None

	def read(self, id):
		status_id = self.search(id)
		if status_id == None:
			return None
		data = self.getData()
		# Получаем статус пользователя по id
		status_user = data['users'][status_id]
		return status_user

	def change(self, id, key, value):
		data = self.getData()
		# Изменяем значение статуса по ключу
		data['users'][self.search(id)][key] = value
		# Записываем новые данные в файл
		with open('databases/status_users.json', 'w') as f:
			json.dump(data, f)

	def add(self, id):
		data = self.getData()
		status_id = self.search(id)
		new_status = {'id': id, 'Auth': 0, 'Translator': False}
		# Есть ли пользователь в файле
		if status_id == None:
			# Добавляем нового пользователя
			data['users'].append(new_status)
			# Сортируем всех пользователей по id
			data['users'].sort(key=lambda x: x['id'])
		else:
			# Изменяем данные пользователя на новые
			data['users'][status_id] = new_status
		# Записываем новые данные в файл
		with open('databases/status_users.json', 'w') as f:
			json.dump(data, f)

class Translator:
	def __init__(self):
		super(Translator, self).__init__()
		self.statusUsers = StatusUsers()
		self.markupManager = MarkupManager()

	def status(self, id):
		# Получаем данные пользователя
		status_user = self.statusUsers.read(id)
		if status_user == None:
			return None
		# Возвращаем статус переводчика
		return status_user['Translator']

	def start(self, id):
		# Получаем разметку переводчика
		markup = self.markupManager.getTranslat()
		text = 'Переводчик включён!\nПросто введите фразу.'
		bot.send_message(id, text, reply_markup=markup)
		# Изменяем статус переводчика
		self.statusUsers.change(id, 'Translator', True)

	def translat(self, id, text):
		# Отправляем переведённый текст
		bot.send_message(id, translate.translate(text))

	def stop(self, id):
		# Получаем разметку авторизованного
		markup = self.markupManager.getAuth()
		# Изменяем статус переводчика
		self.statusUsers.change(id, 'Translator', False)
		bot.send_message(id, 'Переводчик выключен!',
			reply_markup=markup)

class Authorization:
	def __init__(self):
		super(Authorization, self).__init__()
		self.markupManager = MarkupManager()
		self.statusUsers = StatusUsers()

	def status(self, id):
		# Получаем данные пользователя
		status_user = self.statusUsers.read(id)
		if status_user == None:
			return None
		# Возвращаем статус авторизации
		return status_user['Auth']

	def start(self, id, message):
		# Получаем статус авторизации
		status_id = self.status(id)
		# Обрабатываем в зависимости от статуса
		if status_id == 0:
			# Получаем разметку авторизации
			markup = self.markupManager.getGoAuth()
			bot.send_message(id, 'Введите ФИО',
				reply_markup=markup)
			# Изменяем статус авторизации
			self.statusUsers.change(id, 'Auth', 1)

		elif status_id == 1:
			text = message.text.lower()
			# Проверяем наличие ФИО в базе данных
			isName = database.searchName(id, text)
			if isName:
				bot.send_message(id, 'Введите номер ЛС')
				# Изменяем статус авторизации
				self.statusUsers.change(id, 'Auth', 2)
			else:
				bot.send_message(id, '⚠️ Неверное ФИО')
				bot.send_message(id, 'Введите ФИО')

		elif status_id == 2:
			text = message.text.lower()
			# Проверяем ЛС пользователя
			isAccount = database.searchAccount(id, text)
			if isAccount:
				# Получаем разметку авторизованного
				markup = self.markupManager.getAuth()
				text = '✅ Вы успешно авторизовались!'
				bot.send_message(message.chat.id,
					text, reply_markup=markup)
				# Изменяем статус авторизации
				self.statusUsers.change(id, 'Auth', 3)
			else:
				bot.send_message(id, '⚠️ Неверный ЛС')
				bot.send_message(id, 'Введите номер ЛС')

		elif status_id == 3:
			bot.send_message(message.chat.id,
				'⚠️ Вы уже авторизовались!')

class Handler:
	def __init__(self):
		super(Handler, self).__init__()
		self.markupManager = MarkupManager()
		self.authorization = Authorization()
		self.translator = Translator()
		self.statusUsers = StatusUsers()

	def translate(self, message):
		# Проверяем нажатие кнопки выхода
		if message.text.lower() == '❌ выход':
			self.translator.stop(message.chat.id)
		else:
			self.translator.translat(message.chat.id, message.text)

	def startAuth(self, message):
		# Проверяем нажатие кнопки отмены
		if message.text.lower() == '❌ отмена':
			# Изменяем статус авторизации
			self.statusUsers.change(message.chat.id, 'Auth', 0)
			# Получаем разметку неавторизованного
			markup = self.markupManager.getUnAuth()
			# Удаляем временные данные пользователя
			database.deleteTempData(message.chat.id)
			bot.send_message(message.chat.id,
				'Отмена авторизации!', reply_markup=markup)
		else:
			self.authorization.start(message.chat.id, message)

	def authorized(self, message):
		# Проверяем нажатие кнопки авторизованного
		if message.text.lower() == '📚 домашка':
			bot.send_message(message.chat.id,
				'Эта возможность пока недоступна!')

		elif message.text.lower() == '📋 оценки':
			bot.send_message(message.chat.id,
				'Эта возможность пока недоступна!')

		elif message.text.lower() == '🇬🇧 переводчик':
			self.translator.start(message.chat.id)

		elif message.text.lower() == '❌ выход':
			# Получаем разметку неавторизованного
			markup = self.markupManager.getUnAuth()
			# Изменяем статус авторизации
			self.statusUsers.change(message.chat.id, 'Auth', 0)
			bot.send_message(message.chat.id,
				'Вы успешно вышли!', reply_markup=markup)

		else:
			self.unAuthorized(message)

	def unAuthorized(self, message):
		# Проверяем нажатие кнопки неавторизованного
		if message.text.lower() == '👨🏼‍💻 помощь':
			bot.send_message(message.chat.id, message_text.help())

		elif message.text.lower() == '✅ авторизация':
			self.authorization.start(message.chat.id, message)

		elif message.text.lower() == '🎈 мероприятия':
			# Парсим список мероприятий
			events = parsers.pars_events()
			# Проверяем наличие мероприятий
			if len(events) == 0:
				bot.send_message(message.chat.id,
					'❗️ Мероприятий в ближайшее время нету!')
			else:
				for event in events:
					text = '🎈 %s\n%s\n\nСсылка:\n%s' % (
						event['name'],
						event['date'],
						event['link'])
					bot.send_message(message.chat.id, text)

		elif message.text.lower() == '🏫 школы':
			# Парсим список школ
			centers = parsers.pars_centers()
			for center in centers:
				time_str = ''
				for time in center['time']:
					time_str = time_str + time + '\n'
				text = '🏫 %s\n\nАдрес:\n%s\n\n%s\n%s' % (
					center['name'],
					center['adress'],
					time_str,
					center['email'])
				bot.send_message(message.chat.id, text)

		else:
			# Получаем разметку в зависимости от статуса
			markup = self.markupManager.update(message)
			print('[%s][%s %s][Ошибка]: %s' % (
				message.chat.id,
				message.chat.first_name,
				message.chat.last_name,
				message.text))
			bot.send_message(message.chat.id,
				'⚠️ Ошибка!', reply_markup=markup)

class MessageManager:
	def __init__(self):
		super(MessageManager, self).__init__()
		self.authorization = Authorization()
		self.statusUsers = StatusUsers()
		self.translator = Translator()

	def start(self, message):
		# Получаем статус авторизации
		status_auth = self.authorization.status(message.chat.id)
		if status_auth == None:
			markupManager = MarkupManager()
			# Добавляем новые данные пользователя
			self.statusUsers.add(message.chat.id)
			# Получаем разметку неавторизованного
			markup = markupManager.getUnAuth()
			bot.send_message(message.chat.id,
				message_text.start(), reply_markup=markup)
		else:
			bot.send_message(message.chat.id, '⚠️ Вы уже стартовали!')

	def commands(self, message):
		handler = Handler()
		# Получаем статус авторизации
		status_auth = self.authorization.status(message.chat.id)
		# Обработка в зависимости от статуса
		if status_auth == 3:
			# Получаем статус переводчика
			isTranslat = self.translator.status(message.chat.id)
			if isTranslat:
				handler.translate(message)
			else:
				handler.authorized(message)
		elif status_auth == 0:
			handler.unAuthorized(message)
		elif status_auth == None:
			self.statusUsers.add(message.chat.id)
			handler.unAuthorized(message)
		else:
			handler.startAuth(message)

@bot.message_handler(commands=['start'])
def startHandler(message):
	messageManager = MessageManager()
	messageManager.start(message)
	print('[%s][%s %s][Команда]: @start' % (message.chat.id,
		message.chat.first_name, message.chat.last_name))

@bot.message_handler(content_types=['text'])
def messageHandler(message: Message):
	messageManager = MessageManager()
	messageManager.commands(message)

while True:
	try:
		bot.polling(none_stop=True, interval=0, timeout=20)
	except Exception as E:
		time.sleep(1)