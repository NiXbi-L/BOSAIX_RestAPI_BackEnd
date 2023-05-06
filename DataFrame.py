from flask import Flask
from flask_restful import Api, Resource
import requests

import pandas as pd

#Чтение таблиц Exel
##################################################################################
userdata = pd.read_excel('DataBase/Sheets/UserData.xlsx',usecols=[1,2,3,4,5]).to_dict('list')
userdataBuisnes = pd.read_excel('DataBase/Sheets/UserDataBuisnes.xlsx',usecols=[1,2,3,4]).to_dict('list')
##################################################################################

#Создание объектов RestFull_API
##################################################################################
app = Flask(__name__)
api = Api()
##################################################################################

#Иные функции
##################################################################################
def DBadd(dictt,namesarr,inputarr): #Добавление данных в бд (словарь,список имен,список данных)
    assert len(namesarr) == len(inputarr) #Если оба списки равны
    for i in range(len(namesarr)):
        dictt[namesarr[i]].append(inputarr[i])
    return dictt #Возвращаем копию словаря уже с внесенными данными
##################################################################################

#Классы обработчики
##################################################################################
class addDataFrame(Resource): #Запрос на добавление в базу данных /<Логин>/<Пароль>/<Эл. почта>/<Тип аккаунта gamer || buisnes>
    def put(self,login,password,email,acounttype): #Обработка PUT запросов
        global userdata,userdataBuisnes #Обозначаем работу с глобальными переменными
        if acounttype == 'gamer': #Если передаваемый тип аккаунта 'gemer'
            if login in userdata['UserName']: #Проверка наличия пользователя в БД
                return {'status': 'UserInDataBase'} #Возврат статуса операции
            else:
                userdata = DBadd(userdata,[
                    'UserName',
                    'UserPass',
                    'email',
                    'Balance',
                    'GameTime'
                ],[
                    login,
                    password,
                    email,
                    0.0,
                    "00:00:00"
                ]) #Добавление данных в БД
                pd.DataFrame(userdata).to_excel('DataBase/Sheets/UserData.xlsx') #Сохранение в постоянную память
                return {'status': 'UserAdded'} #Возврат статуса операции
        elif acounttype == 'buisnes': #Если передаваемый тип аккаунта 'buisnes'
            if login in userdataBuisnes['UserName']: #Проверка наличия пользователя в БД
                return {'status': 'UserInDataBase'} #Возврат статуса операции
            else:
                userdataBuisnes = DBadd(userdataBuisnes,
                                        [
                                        'UserName',
                                        'UserPass',
                                        'email',
                                        'Balance',
                                        ],[
                                        login,
                                        password,
                                        email,
                                        0.0,
                                        ]) #Добавление данных в БД
                pd.DataFrame(userdataBuisnes).to_excel('DataBase/Sheets/UserDataBuisnes.xlsx') #Сохранение в постоянную память
                return {'status': 'UserAdded'} #Возврат статуса операции
class logDataFrame(Resource): #Запрос на правильность введеных данных для логирования /<Логин>/<Пароль>/<Тип аккаунта gamer || buisnes>
    def get(self,login,password,acounttype): #Обработка GET запросов
        if acounttype == 'gamer': #Если передаваемый тип аккаунта 'gemer'
            if login in userdata['UserName'] and userdata['UserPass'][
                userdata['UserName'].index(login)
            ] == password: #Проверка правильности введеных данных для логирования
                return {'status': 'OK'} #Возврат статуса операции
            else:
                return {'status': 'NotFound'} #Возврат статуса операции
        elif acounttype == 'buisnes': #Если передаваемый тип аккаунта 'buisnes'
            if login in userdataBuisnes['UserName'] and userdataBuisnes['UserPass'][
                userdataBuisnes['UserName'].index(login)
            ] == password: #Проверка правильности введеных данных для логирования
                return {'status': 'OK'} #Возврат статуса операции
            else:
                return {'status': 'NotFound'} #Возврат статуса операции
##################################################################################

#Привязка URL к кассу обработчику
##################################################################################
api.add_resource(addDataFrame,"/<string:login>/<string:password>/<string:email>/<string:acounttype>")  #Запрос на добавление в базу данных
api.add_resource(logDataFrame,"/<string:login>/<string:password>/<string:acounttype>") #Запрос на правильность введеных данных для логирования
api.init_app(app)
##################################################################################

app.run(debug=True,port=1501,host="0.0.0.0")