import sqlite3
import json


class UserTempData:
	def __init__(self):
		super(UserTempData, self).__init__()

	def getData(self):
		# Получаем данные из файла
		with open('databases/user_temp_data.json') as f:
			data = json.load(f)
		return data

	def writeData(self, data):
		# Записываем данные в файл
		with open('databases/user_temp_data.json', 'w') as f:
			json.dump(data, f)

	def search(self, id):
		data = self.getData()
		data_id = 0
		# Поиск данных пользователя
		for user in data['users']:
			if user[0] == id:
				return data_id
			data_id += 1
		return None
	
	def add(self, id, user):
		data = self.getData()
		data_id = self.search(id)
		new_data = [id, user[0], user[1]]
		# Проверяем наличие данных
		if data_id == None:
			# Добавляем новые данные пользователя
			data['users'].append(new_data)
			self.writeData(data)
		else:
			data['users'][data_id] = new_data
			self.writeData(data)

	def delete(self, data_id):
		data = self.getData()
		# Удаляем данные пользователя
		data['users'].pop(data_id)
		self.writeData(data)

def readDatabase():
	# Подключаемся к базе данных
	connection = sqlite3.connect("databases/db_easy_school.sqlite")
	cursor = connection.cursor()
	# Делаем sql запрос
	sql_questions = 'SELECT * FROM ES_base'
	cursor.execute(sql_questions)
	# Получаем данные из базы
	questions = cursor.fetchall()
	return questions

def searchName(id, name):
	questions = readDatabase()
	# Проверяем наличие ФИО в базе
	for user in questions:
		if user[0] == name.lower():
			userTempData = UserTempData()
			userTempData.add(id, user)
			return True
	return False

def searchAccount(id, account):
	userTempData = UserTempData()
	data = userTempData.getData()
	data_id = userTempData.search(id)
	# Проверяем ЛС пользователя
	if data_id != None:
		if data['users'][data_id][2] == account:
			userTempData.delete(data_id)
			return True
		else:
			return False
	else:
		return False

def deleteTempData(id):
	userTempData = UserTempData()
	data_id = userTempData.search(id)
	if data_id != None:
		userTempData.delete(data_id)