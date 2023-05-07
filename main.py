from flask import Flask
from flask_restful import Api, Resource
import requests

import json
from yookassa import Configuration,Payment, Refund
import uuid

import cfg

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from random import randrange

#Создание объектов RestFull_API
##################################################################################
app = Flask(__name__)
api = Api()
##################################################################################

#Привязываем платежные данные
##################################################################################
Configuration.account_id = cfg.ShopID
Configuration.secret_key = cfg.PaymentAPI_key
##################################################################################

names = {} #Словарь {"польвователь" : [Ссылка на оплату,ID-операции]}
codes = {}#Словарь {"польвователь" : "Код верификации"}

#Функции работы с Email
##################################################################################
def sendEmailMsg(to_email,message): #Функция отправки сообщений на Email
    msg = MIMEMultipart()
    msg.attach (MIMEText (message, 'plain'))
    server = smtplib.SMTP('smtp.mail.ru: 25')
    server.starttls()
    server.login (cfg.from_email, cfg.password)
    server.sendmail (cfg.from_email, to_email, msg.as_string())
    server.quit()
def CheckValidEmail(email):
    code = str(randrange(100000,1000000))
    sendEmailMsg(email,"Ваш код верификации: "+code)
    return code

##################################################################################

#Функции оплаты
##################################################################################
def check_pay(payment_id):
    payment = json.loads((Payment.find_one(payment_id)).json()) #Делаем запрос о статусе платежа
    if payment['status'] == 'pending':
        return False
    elif payment['status'] =='succeeded':
        return True
def create_pay_url(sum,description,email):
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": str(sum), #Cумма
            "currency": "RUB" #Валюта
        },
        "confirmation": { #переадресация после платежа
            "type": "redirect",
            "return_url": "https://ya.ru"
        },
        "capture" : True, #Установка платежа без доп подтверждения
        "description": description, #Установка описания (передается в функцию параметром description)
        'receipt': { #Формирование чека для отправки в налоговую
            "customer": { #Данные клиента
                "email": email #Установка электронной почты (передается в функцию параметром email)
            },
            "items":[{ #Передача проданых позиций
            'description': description, #Установка описания (передается в функцию параметром description)
            "amount": {
            "value": str(sum), #Cумма (передается в функцию параметром sum)
            "currency": "RUB" #Валюта
            },
            'quantity': 1, #Кол-во товара
            'vat_code': 1, #Код ставки НДС
            }]
        }
        }, idempotence_key) #Делаем запрос для создании платежа возможные параметры значений см. https://yookassa.ru/developers/api#payment
    payment_data = json.loads(payment.json()) #Парсинг Json ответа
    payment_id = payment_data['id'] #Создание объекта payment_id
    payment_url = (payment_data['confirmation'])['confirmation_url'] #Создание объекта payment_url
    return [payment_id, payment_url] #Возварат списка с URL для оплаты и ID платежа
##################################################################################

#Классы обработчики
##################################################################################
class pay(Resource): #Создание платежа /pay/<Имя пользователя>/<Сумма>
    def get(self,Token,name,sum): #обработка GET запросов
        myToken = requests.get(cfg.databaseurl+"Token/"+cfg.DataFrameAPI_Token+"/"+Token).json()['Token']
        if myToken:
            try: #Попытка проверки платежа
                if check_pay(names[name][0]) == False: #Если платеж нашелся, но не оплачен
                    return {"payurl": names[name][1], "payid": names[name][0]} #Возвращаем уже созданый платеж
                else: #Если платеж нашелся но он оплачен
                    pay = create_pay_url(sum,"Тест","rspinko965@gmail.com")
                    pay.append(str(sum))
                    names[name] = pay
                    return {"payurl":pay[1],"payid": pay [0]} #Создаем новый платеж и возвращаем его
            except: #Если пользователь 1 раз обратился к системе
                pay = create_pay_url(sum, "Тест", "rspinko965@gmail.com")
                pay.append(str(sum))
                names[name] = pay
                return {"payurl": pay[1], "payid": pay[0]} #Создаем новый платеж и возвращаем его
class checkpay(Resource): #Проверка платежей /chekpay/<Имя пользователя>
    def get(self,Token,name): #обработка GET запросов
        myToken = requests.get(cfg.databaseurl + "Token/" + cfg.DataFrameAPI_Token + "/" + Token).json()['Token']
        if myToken:
            try:
                return {
                    'paystatus':str(check_pay(names[name][0])),
                    'amount':str(names[name][2])
                        } #Возвращаем статус платежа и оплаченую сумму
            except:
                return {'paystatus': "NotFound"} #Возвращаем ошибку "Платеж не найден"
class registerFirst(Resource): #Регистрация /reg/<Логин>/<Пароль>/<Эл. почта>/<Тип аккаунта gamer || buisnes>
    def get(self,Token,login,password,email,acounttype): #обработка GET запросов
        myToken = requests.get(cfg.databaseurl + "Token/" + cfg.DataFrameAPI_Token + "/" + Token).json()['Token']
        if myToken and acounttype == 'gamer':
            if acounttype == 'gamer' or acounttype == 'buisnes': #Проверка правильности ввода типа аккаунта
                codes[login] = [CheckValidEmail(email),password,email,acounttype] #Проверка действительности Email
                return {'status': 'Code sended'}
            else:
                return {'status':'acounttype not corrected'} #Ошибка Типа аккаунта
        elif Token == cfg.DataFrameAPI_Token and acounttype == 'buisnes':
            if acounttype == 'gamer' or acounttype == 'buisnes': #Проверка правильности ввода типа аккаунта
                codes[login] = [CheckValidEmail(email),password,email,acounttype] #Проверка действительности Email
                return {'status': 'Code sended'}
            else:
                return {'status':'acounttype not corrected'} #Ошибка Типа аккаунта
        else:
            return {'status': 'acounttype not corrected or Token not searching'}  # Ошибка Типа аккаунта
class registerSecond(Resource): #Регистрация 2 этап /reg/<Логин>/<код верификации>
    def get(self,Token,login,code):
        myToken = requests.get(cfg.databaseurl + "Token/" + cfg.DataFrameAPI_Token + "/" + Token).json()['Token']
        if myToken:
            password = codes[login][1]
            email = codes[login][2]
            acounttype = codes[login][3]
            if code == int(codes[login][0]) :
                return requests.put(
                    cfg.databaseurl +cfg.DataFrameAPI_Token+"/"+ login + "/" + password + "/" + email + "/" + acounttype).json()  # Возврат ответа от БД
            else:
                return {'status':'Code not corrected'}
class loginFirst(Resource): #Логирование в системе /log/<Логин>/<Пароль>/<Тип аккаунта gamer || buisnes>
    def get(self,Token,login,password,acounttype): #обработка GET запросов
        myToken = requests.get(cfg.databaseurl + "Token/" + cfg.DataFrameAPI_Token + "/" + Token).json()['Token']
        if myToken and acounttype == 'gamer':
            if acounttype == 'gamer' or acounttype == 'buisnes': #Проверка правильности ввода типа аккаунта
                email = requests.get(cfg.databaseurl+"search/"+cfg.DataFrameAPI_Token+"/"+login+"/"+acounttype).json()['email']
                codes[login] = [CheckValidEmail(email), password, acounttype]
                return {'status': 'Code sended'}
            else:
                return {'status':'acounttype not corrected'} #Ошибка Типа аккаунта
        elif Token == cfg.DataFrameAPI_Token and acounttype == 'buisnes':
            if acounttype == 'gamer' or acounttype == 'buisnes': #Проверка правильности ввода типа аккаунта
                email = requests.get(cfg.databaseurl+"search/"+cfg.DataFrameAPI_Token+"/"+login+"/"+acounttype).json()['email']
                codes[login] = [CheckValidEmail(email), password, acounttype]
                return {'status': 'Code sended'}
            else:
                return {'status':'acounttype not corrected'} #Ошибка Типа аккаунта
        else:
            return {'status': 'acounttype not corrected or Token not searching'}  # Ошибка Типа аккаунта
class loginSecond(Resource): #Логирование в системе /log/<Логин>/<код верификации>
    def get(self,Token,login,code):
        myToken = requests.get(cfg.databaseurl + "Token/" + cfg.DataFrameAPI_Token + "/" + Token).json()['Token']
        if myToken:
            password = codes[login][1]
            acounttype = codes[login][2]
            if code == int(codes[login][0]):
                return requests.get(cfg.databaseurl+cfg.DataFrameAPI_Token+"/"+login+"/"+password+"/"+acounttype).json() #Возврат ответа от БД
            else:
                return {'status': 'Code not corrected'}
class GetToken(Resource): #Логирование в системе /log/<Логин>/<код верификации>
    def get(self,login,password):
        return requests.get(cfg.databaseurl+"gettoken/"+cfg.DataFrameAPI_Token+"/"+login+"/"+password).json()
##################################################################################

#Привязка URL к кассу обработчику
##################################################################################
api.add_resource(pay,"/pay/<string:Token>/<string:name>/<int:sum>") #Создание ссылки на оплату
api.add_resource(checkpay,"/chekpay/<string:Token>/<string:name>") #проверка оплаты

api.add_resource(registerFirst,"/reg/<string:Token>/<string:login>/<string:password>/<string:email>/<string:acounttype>") #Регистрация пользователя 1 этап
api.add_resource(registerSecond,"/reg/<string:Token>/<string:login>/<int:code>") #Регистрация пользователя  2 этап

api.add_resource(loginFirst,"/log/<string:Token>/<string:login>/<string:password>/<string:acounttype>") #Логирования пользователя в системе 1 этап
api.add_resource(loginSecond,"/log/<string:Token>/<string:login>/<int:code>") #Логирования пользователя в систем 2 этап

api.add_resource(GetToken,"/gettoken/<string:login>/<string:password>") #Логирования пользователя в систем
api.init_app(app)
##################################################################################
if __name__ == "__main__":
    app.run(debug=True,port=1500,host="0.0.0.0")

