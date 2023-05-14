import json
from yookassa import Configuration,Payment, Refund
import uuid
import cfg
Configuration.account_id = cfg.ShopID
Configuration.secret_key = cfg.PaymentAPI_key
class payment():
    def check_pay(self,payment_id):
        payment = json.loads((Payment.find_one(payment_id)).json()) #Делаем запрос о статусе платежа
        if payment['status'] == 'pending':
            return False
        elif payment['status'] =='succeeded':
            return True
    def create_pay_url(self,sum,description,email):
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