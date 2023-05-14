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
        myToken = requests.get(cfg.databaseurl + "Token/" + cfg.DataFrameAPI_Token + "/" + Token).json()['Token']
        if myToken:
            try:
                return {
                    'paystatus':str(payment.check_pay(names[name][0])),
                    'amount':str(names[name][2])
                        } #Возвращаем статус платежа и оплаченую сумму
            except:
                return {'paystatus': "NotFound"} #Возвращаем ошибку "Платеж не найден"
class registerFirst(Resource): #Регистрация /reg/<Token>/<Логин>/<Пароль>/<Эл. почта>/<Тип аккаунта gamer || buisnes>
    def get(self,Token,login,password,email,acounttype): #обработка GET запросов
        myToken = requests.get(cfg.databaseurl + "Token/" + cfg.DataFrameAPI_Token + "/" + Token).json()['Token']
        if myToken and acounttype == 'gamer':
            if acounttype == 'gamer' or acounttype == 'buisnes': #Проверка правильности ввода типа аккаунта
                codes[login] = [mail.CheckValidEmail(email),password,email,acounttype] #Проверка действительности Email
                return {'status': 'Code sended'}
            else:
                return {'status':'acounttype not corrected'} #Ошибка Типа аккаунта
        elif Token == cfg.DataFrameAPI_Token and acounttype == 'buisnes':
            if acounttype == 'gamer' or acounttype == 'buisnes': #Проверка правильности ввода типа аккаунта
                codes[login] = [mail.CheckValidEmail(email),password,email,acounttype] #Проверка действительности Email
                return {'status': 'Code sended'}
            else:
                return {'status':'acounttype not corrected'} #Ошибка Типа аккаунта
        else:
            return {'status': 'acounttype not corrected or Token not searching'}  # Ошибка Типа аккаунта
class registerSecond(Resource): #Регистрация 2 этап /reg/<Token>/<Логин>/<код верификации>
    def get(self,Token,login,code):
        myToken = requests.get(cfg.databaseurl + "Token/" + cfg.DataFrameAPI_Token + "/" + Token).json()['Token']
        if codes[login][3] == 'gamer':
            if myToken:
                password = codes[login][1]
                email = codes[login][2]
                acounttype = codes[login][3]
                if code == int(codes[login][0]) :
                    return requests.put(
                        cfg.databaseurl +cfg.DataFrameAPI_Token+"/"+ login + "/" + password + "/" + email + "/" + acounttype).json()  # Возврат ответа от БД
                else:
                    return {'status':'Code not corrected'}
        elif codes[login][3] == 'buisnes':
            password = codes[login][1]
            email = codes[login][2]
            acounttype = codes[login][3]
            if code == int(codes[login][0]):
                return requests.put(
                    cfg.databaseurl + cfg.DataFrameAPI_Token + "/" + login + "/" + password + "/" + email + "/" + acounttype).json()  # Возврат ответа от БД
            else:
                return {'status': 'Code not corrected'}
class loginFirst(Resource): #Логирование в системе /log/<Token>/<Логин>/<Пароль>/<Тип аккаунта gamer || buisnes>
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
class loginSecond(Resource): #Логирование в системе 2 этап /log/<Token>/<Логин>/<код верификации>
    def get(self,Token,login,code):
        myToken = requests.get(cfg.databaseurl + "Token/" + cfg.DataFrameAPI_Token + "/" + Token).json()['Token']
        if codes[login][2] == 'gamer':
            if myToken:
                password = codes[login][1]
                acounttype = codes[login][2]
                if code == int(codes[login][0]):
                    return requests.get(cfg.databaseurl+cfg.DataFrameAPI_Token+"/"+login+"/"+password+"/"+acounttype).json() #Возврат ответа от БД
                else:
                    return {'status': 'Code not corrected'}
        elif codes[login][2] == 'buisnes':
            if Token == cfg.DataFrameAPI_Token:
                password = codes[login][1]
                acounttype = codes[login][2]
                if code == int(codes[login][0]):
                    return requests.get(
                        cfg.databaseurl + cfg.DataFrameAPI_Token + "/" + login + "/" + password + "/" + acounttype).json()  # Возврат ответа от БД
                else:
                    return {'status': 'Code not corrected'}
class GetToken(Resource): #Запрос API токена /gettoken/<Логин>/<Пароль>
    def get(self,login,password):
        return requests.get(cfg.databaseurl+"gettoken/"+cfg.DataFrameAPI_Token+"/"+login+"/"+password).json()
##################################################################################

#Привязка URL к кассу обработчику
##################################################################################
api.add_resource(pay,"/pay") #Создание ссылки на оплату
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

