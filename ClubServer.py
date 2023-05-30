from flask import Flask
from flask_restful import Api, Resource
from flask import request

import requests

import cfg

import os

#Создание объектов RestFull_API
##################################################################################
app = Flask(__name__)
api = Api()
##################################################################################

#Классы обработчики
##################################################################################
class IamLife(Resource):
    def get(self,Token):
        if Token == cfg.DataFrameAPI_Token:
            os.system('shutdown -s — t 300 -m \\'+ request.remote_addr)
            return request.remote_addr
##################################################################################

#Привязка URL к кассу обработчику
##################################################################################
api.add_resource(IamLife,"/iamlife/<string:Token>") #Логирования пользователя в систем
api.init_app(app)
##################################################################################

app.run(debug=True, port=1502, host="0.0.0.0")