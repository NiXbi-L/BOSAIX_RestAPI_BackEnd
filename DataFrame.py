from flask import Flask
from flask_restful import Api, Resource
import requests

import pandas as pd

userdata = pd.read_excel('DataBase/Sheets/UserData.xlsx',usecols=[1,2,3,4,5]).to_dict('list')
userdataBuisnes = pd.read_excel('DataBase/Sheets/UserDataBuisnes.xlsx',usecols=[1,2,3,4]).to_dict('list')

app = Flask(__name__)
api = Api()
def DBadd(dictt,namesarr,inputarr):
    assert len(namesarr) == len(inputarr)
    for i in range(len(namesarr)):
        dictt[namesarr[i]].append(inputarr[i])
    return dictt
class addDataFrame(Resource):
    def put(self,login,password,email,acounttype):
        global userdata,userdataBuisnes
        if acounttype == 'gamer':
            if login in userdata['UserName']:
                return {'status': 'UserInDataBase'}
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
                ])
                pd.DataFrame(userdata).to_excel('DataBase/Sheets/UserData.xlsx')
                return {'status': 'UserAdded'}
        elif acounttype == 'buisnes':
            if login in userdataBuisnes['UserName']:
                return {'status': 'UserInDataBase'}
            else:
                userdataBuisnes = DBadd(userdataBuisnes, [
                    'UserName',
                    'UserPass',
                    'email',
                    'Balance',
                ], [
                                     login,
                                     password,
                                     email,
                                     0.0,
                                 ])
                pd.DataFrame(userdataBuisnes).to_excel('DataBase/Sheets/UserDataBuisnes.xlsx')
                return {'status': 'UserAdded'}
class logDataFrame(Resource):
    def get(self,login,password,acounttype):
        if acounttype == 'gamer':
            if login in userdata['UserName'] and userdata['UserPass'][
                userdata['UserName'].index(login)
            ] == password:
                return {'status': 'OK'}
            else:
                return {'status': 'NotFound'}
        elif acounttype == 'buisnes':
            if login in userdataBuisnes['UserName'] and userdataBuisnes['UserPass'][
                userdataBuisnes['UserName'].index(login)
            ] == password:
                return {'status': 'OK'}
            else:
                return {'status': 'NotFound'}


api.add_resource(addDataFrame,"/<string:login>/<string:password>/<string:email>/<string:acounttype>")
api.add_resource(logDataFrame,"/<string:login>/<string:password>/<string:acounttype>")
api.init_app(app)

app.run(debug=True,port=1501,host="0.0.0.0")