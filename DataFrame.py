from flask import Flask, request
from flask_restful import Api, Resource
import requests

import pandas as pd

import random

import cfg

#Чтение таблиц Exel
##################################################################################
userdata = pd.read_excel('DataBase/Sheets/UserData.xlsx',usecols=[1,2,3,4,5]).to_dict('list')
userdataBuisnes = pd.read_excel('DataBase/Sheets/UserDataBuisnes.xlsx',usecols=[1,2,3,4]).to_dict('list')
Tokens = pd.read_excel('DataBase/Sheets/Tokens.xlsx',usecols=[1,2]).to_dict('list')
##################################################################################

#Создание объектов RestFull_API
##################################################################################
app = Flask(__name__)
api = Api()
##################################################################################

#Иные функции
##################################################################################
def DBadd(dictt,inputarr): #Добавление данных в бд (словарь,список имен,список данных)
    assert len(list(dictt)) == len(inputarr)
    j = 0
    for i in list(dictt):
        dictt[i].append(inputarr[j])
        j+=1
    return dictt #Возвращаем копию словаря уже с внесенными данными
def getToken():
    chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    for n in range(1):
        password = ''
        for i in range(64):
            password += random.choice(chars)
    return password
##################################################################################

#Классы обработчики
##################################################################################
class addDataFrame(Resource): #Запрос на добавление в базу данных /<Token>/<Логин>/<Пароль>/<Эл. почта>/<Тип аккаунта gamer || buisnes>
    def get(self): #Обработка GET запросов
        Token = request.args.get('Token')
        login = request.args.get('login')
        password = request.args.get('password')
        email = request.args.get('email')
        acounttype = request.args.get('acounttype')
        if str(Token) == str(cfg.DataFrameAPI_Token):
            global userdata,userdataBuisnes #Обозначаем работу с глобальными переменными
            if acounttype == 'gamer': #Если передаваемый тип аккаунта 'gemer'
                if login in userdata['UserName']: #Проверка наличия пользователя в БД
                    return {'status': 'UserInDataBase'} #Возврат статуса операции
                else:
                    userdata = DBadd(userdata,[
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
                    userdataBuisnes = DBadd(userdataBuisnes,[
                                            login,
                                            password,
                                            email,
                                            0.0,
                                            ]) #Добавление данных в БД
                    pd.DataFrame(userdataBuisnes).to_excel('DataBase/Sheets/UserDataBuisnes.xlsx') #Сохранение в постоянную память
                    return {'status': 'UserAdded'} #Возврат статуса операции
        else:
            return {'Status' : "Доступ закрыт"}
class logDataFrame(Resource): #Запрос на правильность введеных данных для логирования /<Token>/<Логин>/<Пароль>/<Тип аккаунта gamer || buisnes>
    def get(self): #Обработка GET запросов
        Token = request.args.get('Token')
        login = request.args.get('login')
        password = request.args.get('password')
        acounttype = request.args.get('acounttype')
        if Token == cfg.DataFrameAPI_Token:
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
        else:
            return {'Status' : "Доступ закрыт"}
class SearchDataFrame(Resource): #Поисковой запрос по логину пользователя /search/<Token>/<Логин>/<Тип аккаунта gamer || buisnes>
    def get(self):
        Token = request.args.get('Token')
        login = request.args.get('login')
        acounttype = request.args.get('acounttype')
        if Token == cfg.DataFrameAPI_Token:
            if acounttype == 'gamer':
                ret = {}
                index = userdata['UserName'].index(login)
                for i in list(userdata):
                    ret[i] = userdata[i][index]
                return ret
            elif acounttype == 'buises':
                ret = {}
                index = userdataBuisnes['UserName'].index(login)
                for i in list(userdataBuisnes):
                    ret[i] = userdataBuisnes[i][index]
                return ret
        else:
            return {'Status' : "Доступ закрыт"}
class GetToken(Resource): #Запрос на Получение токена /gettoken/<Token>/<Логин>/<Пароль>
    def get(self):
        Token = request.args.get('Token')
        login = request.args.get('login')
        password = request.args.get('password')
        if Token == cfg.DataFrameAPI_Token:
            if login in userdataBuisnes['UserName'] \
            and password == userdataBuisnes['UserPass'][userdataBuisnes['UserName'].index(login)]:
                try:
                    return {'Token': Tokens['Token'][Tokens['UserName'].index(login)]}
                except:
                    retToken = getToken()
                    Tokens['UserName'].append(login)
                    Tokens['Token'].append(retToken)
                    pd.DataFrame(Tokens).to_excel('DataBase/Sheets/Tokens.xlsx')  # Сохранение в постоянную память
                    return {'Token': retToken}
            else:
                return {'Status':"Eror"}
        else:
            return {'Status' : "Доступ закрыт"}
class isTokenEnable(Resource): #Запрос на наличие токена /Token/<Token>/<userToken>
    def get(self):
        Token = request.args.get('TokenDB')
        userToken = request.args.get('Token')
        if Token == cfg.DataFrameAPI_Token:
            if userToken in Tokens['Token']:
                return {'Token':True}
            else:
                return {'Token': False}
        else:
            return {'Status' : "Доступ закрыт"}
##################################################################################

#Привязка URL к кассу обработчику
##################################################################################
api.add_resource(addDataFrame,"/reg")  #Запрос на добавление в базу данных

api.add_resource(logDataFrame,"/log") #Запрос на правильность введеных данных для логирования

api.add_resource(SearchDataFrame,"/search") #Запрос Данных пользователя

api.add_resource(GetToken,"/gettoken") #Запрос Данных пользователя
api.add_resource(isTokenEnable,"/Token") #Запрос Данных пользователя
api.init_app(app)
##################################################################################

app.run(debug=True,port=1501,host="0.0.0.0")