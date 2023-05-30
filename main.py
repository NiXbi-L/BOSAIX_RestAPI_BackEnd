from flask import Flask, request
from flask_restful import Api, Resource

import requests

from payment import payment

import cfg

from SendMail import mail

#Создание объектов RestFull_API
##################################################################################
app = Flask(__name__)
api = Api()
##################################################################################

names = {} #Словарь {"польвователь" : [Ссылка на оплату,ID-операции]}
codes = {}#Словарь {"польвователь" : "Код верификации"}

#Классы обработчики
##################################################################################
class pay(Resource): #Создание платежа /pay/<Token>/<Имя пользователя>/<Сумма>
    def get(self): #обработка GET запросов
        name = request.args.get('name')
        Token = request.args.get('Token')
        sum = request.args.get('sum')
        myToken = requests.get(cfg.databaseurl+"Token",
                               {'TokenDB':cfg.DataFrameAPI_Token,
                                'Token':Token}
                               ).json()['Token']
        if myToken:
            try: #Попытка проверки платежа
                if payment.check_pay(names[name][0]) == False: #Если платеж нашелся, но не оплачен
                    return {"payurl": names[name][1], "payid": names[name][0]} #Возвращаем уже созданый платеж
                else: #Если платеж нашелся но он оплачен
                    pay = payment.create_pay_url(sum,"Тест","rspinko965@gmail.com")
                    pay.append(str(sum))
                    names[name] = pay
                    return {"payurl":pay[1],"payid": pay [0]} #Создаем новый платеж и возвращаем его
            except: #Если пользователь 1 раз обратился к системе
                pay = payment.create_pay_url(sum, "Тест", "rspinko965@gmail.com")
                pay.append(str(sum))
                names[name] = pay
                return {"payurl": pay[1], "payid": pay[0]} #Создаем новый платеж и возвращаем его
class checkpay(Resource): #Проверка платежей /chekpay/<Token>/<Имя пользователя>
    def get(self,Token,name): #обработка GET запросов
        myToken = requests.get(cfg.databaseurl + "Token",
                               {'TokenDB': cfg.DataFrameAPI_Token,
                                'Token': Token}
                               ).json()['Token']
        if myToken:
            try:
                return {
                    'paystatus':str(payment.check_pay(names[name][0])),
                    'amount':str(names[name][2])
                        } #Возвращаем статус платежа и оплаченую сумму
            except:
                return {'paystatus': "NotFound"} #Возвращаем ошибку "Платеж не найден"
class registerFirst(Resource): #Регистрация /reg
    def get(self): #обработка GET запросов
        global codes
        Token = request.args.get('Token')
        login = request.args.get('login')
        password = request.args.get('password')
        email = request.args.get('email')
        acounttype = request.args.get('acounttype')
        print(Token, login, password,email,  acounttype)
        myToken = requests.get(cfg.databaseurl + "Token",
                               {'TokenDB': cfg.DataFrameAPI_Token,
                                'Token': Token}
                               ).json()['Token']
        if myToken or Token == cfg.DataFrameAPI_Token:
            if acounttype == 'gamer' or acounttype == 'buisnes': #Проверка правильности ввода типа аккаунта
                codes[login] = [mail.CheckValidEmail(email),password,email,acounttype] #Проверка действительности Email
                print(codes)
                return {'status': 'Code sended'}
            else:
                return {'status':'acounttype not corrected'} #Ошибка Типа аккаунт
        else:
            return {'status': 'acounttype not corrected or Token not searching'}  # Ошибка Типа аккаунта
class registerSecond(Resource): #Регистрация 2 этап /reg/code
    def get(self):
        global codes
        Token = request.args.get('Token')
        login = request.args.get('login')
        code = request.args.get('code')
        print(code)
        myToken = requests.get(cfg.databaseurl + "Token",
                               {'TokenDB': cfg.DataFrameAPI_Token,
                                'Token': Token}
                               ).json()['Token']
        if myToken or Token == cfg.DataFrameAPI_Token:
            password = codes[login][1]
            email = codes[login][2]
            acounttype = codes[login][3]
            if int(code) == int(codes[login][0]):
                return requests.get(
                    cfg.databaseurl+"reg",
                    {'Token':cfg.DataFrameAPI_Token,
                     'login':login,
                     'password':password,
                     'email':email,
                     'acounttype':acounttype}
                ).json()  # Возврат ответа от БД
            else:
                return {'status':'Code not corrected'}
class loginFirst(Resource): #Логирование в системе /log/<Token>/<Логин>/<Пароль>/<Тип аккаунта gamer || buisnes>
    def get(self): #обработка GET запросов
        Token = request.args.get('Token')
        login = request.args.get('login')
        password = request.args.get('password')
        acounttype = request.args.get('acounttype')
        myToken = requests.get(cfg.databaseurl + "Token",
                               {'TokenDB': cfg.DataFrameAPI_Token,
                                'Token': Token}
                               ).json()['Token']
        if myToken and Token == cfg.DataFrameAPI_Token:
            if acounttype == 'gamer' or acounttype == 'buisnes': #Проверка правильности ввода типа аккаунта
                email = requests.get(cfg.databaseurl+"search",
                                     {'Token':cfg.DataFrameAPI_Token,
                                      'login':login,
                                      'acounttype':acounttype}
                                     ).json()['email']
                codes[login] = [mail.CheckValidEmail(email), password, acounttype]
                return {'status': 'Code sended'}
            else:
                return {'status':'acounttype not corrected'} #Ошибка Типа аккаунта
class loginSecond(Resource): #Логирование в системе 2 этап /log/code
    def get(self):
        Token = request.args.get('Token')
        login = request.args.get('login')
        code = request.args.get('code')
        myToken = requests.get(cfg.databaseurl + "Token",
                               {'TokenDB': cfg.DataFrameAPI_Token,
                                'Token': Token}
                               ).json()['Token']
        if myToken or Token == cfg.DataFrameAPI_Token:
            password = codes[login][1]
            acounttype = codes[login][2]
            if code == int(codes[login][0]):
                return requests.get(cfg.databaseurl+'log',
                                    {'Token':cfg.DataFrameAPI_Token,
                                     'login':login,
                                     'password':password,
                                     'acounttype':acounttype}
                                    ).json() #Возврат ответа от БД
            else:
                return {'status': 'Code not corrected'}
class GetToken(Resource): #Запрос API токена /gettoken/<Логин>/<Пароль>
    def get(self):
        password = request.args.get('password')
        login = request.args.get('login')
        return requests.get(cfg.databaseurl+"gettoken",
                            {'Token':cfg.DataFrameAPI_Token,
                             'login':login,
                             'password':password}
                            ).json()
##################################################################################

#Привязка URL к кассу обработчику
##################################################################################
api.add_resource(pay,"/pay") #Создание ссылки на оплату
api.add_resource(checkpay,"/chekpay>") #проверка оплаты

api.add_resource(registerFirst,"/reg") #Регистрация пользователя 1 этап
api.add_resource(registerSecond,"/reg/code") #Регистрация пользователя  2 этап

api.add_resource(loginFirst,"/log") #Логирования пользователя в системе 1 этап
api.add_resource(loginSecond,"/log/code") #Логирования пользователя в систем 2 этап

api.add_resource(GetToken,"/gettoken") #Логирования пользователя в систем
api.init_app(app)
##################################################################################
if __name__ == "__main__":
    app.run(debug=True,port=1500,host="0.0.0.0")

