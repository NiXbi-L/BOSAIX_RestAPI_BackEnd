from flask import Flask
from flask_restful import Api, Resource
import requests

import json
from yookassa import Configuration,Payment, Refund
import uuid

import cfg

app = Flask(__name__)
api = Api()
#Привязываем платежные данные
Configuration.account_id = cfg.ShopID
Configuration.secret_key = cfg.PaymentAPI_key

def check_pay(payment_id):
    payment = json.loads((Payment.find_one(payment_id)).json())
    print(payment['status'])
    if payment['status'] == 'pending':
        return False
    elif payment['status'] =='succeeded':
        return True
def create_pay_url(sum,description,email):
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": str(sum),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://ya.ru"
        },
        "capture" : True,
        "description": description,
        'receipt': {
            "customer": {
                "email": email
            },
            "items":[{
            'description': description,
            "amount": {
            "value": str(sum),
            "currency": "RUB"
            },
            'quantity': 1,
            'vat_code': 1,
            }]
        }
        }, idempotence_key)
    payment_data = json.loads(payment.json())
    payment_id = payment_data['id']
    payment_url = (payment_data['confirmation'])['confirmation_url']
    return [payment_id, payment_url]

def Get(url):
    resp = requests.get(url)
    return resp.json()

names = {}
class pay(Resource):
    def get(self,name,sum):
        try:
            if check_pay(names[name][0]) == False:
                return {"payurl": names[name][1], "payid": names[name][0]}
            else:
                pay = create_pay_url(sum,"Тест","rspinko965@gmail.com")
                pay.append(str(sum))
                names[name] = pay
                return {"payurl":pay[1],"payid": pay [0]}
        except:
            pay = create_pay_url(sum, "Тест", "rspinko965@gmail.com")
            pay.append(str(sum))
            names[name] = pay
            return {"payurl": pay[1], "payid": pay[0]}
class checkpay(Resource):
    def get(self,name):
        try:
            return {
                'paystatus':str(check_pay(names[name][0])),
                'amount':str(names[name][2])
                    }
        except:
            return {'paystatus': "NotFound"}
class register(Resource):
    def get(self,login,password,email,acounttype):
        if acounttype == 'gamer' or acounttype == 'buisnes':
            return requests.put(cfg.databaseurl+login+"/"+password+"/"+email+"/"+acounttype).json()
        else:
            return {'status':'acounttype not corrected'}
class login(Resource):
    def get(self,login,password,acounttype):
        if acounttype == 'gamer' or acounttype == 'buisnes':
            return Get(cfg.databaseurl+login+"/"+password+"/"+acounttype)
        else:
            return {'status':'acounttype not corrected'}


api.add_resource(pay,"/pay/<string:name>/<int:sum>") #Создание ссылки на оплату
api.add_resource(checkpay,"/chekpay/<string:name>") #проверка оплаты
api.add_resource(register,"/reg/<string:login>/<string:password>/<string:email>/<string:acounttype>") #Регистрация пользователя
api.add_resource(login,"/log/<string:login>/<string:password>/<string:acounttype>") #Логирования пользователя в системе
api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True,port=1500,host="0.0.0.0")

