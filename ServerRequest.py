import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

class Requests:
    baseUrl=os.getenv('homeaddress', "")

    def getFinance(self):
        r = requests.get(self.baseUrl+'/getFinances')
        return r.json()['dataToSend']

    def getTransactions(self):
        r = requests.get(self.baseUrl+'/getTransactions')
        return r.json()['dataToSend']

    def dropTransactions(self, msg):
        r = requests.post(self.baseUrl+'/dropTransactions', json={"password": os.getenv('serverdroppw', ""), "message": msg})
        return r.json()

    def serverIsRunning(self):
        r = requests.get(self.baseUrl)
        return (r.status_code==200)

class Notifications:
    baseUrl=os.getenv('notification_address', "")

    def sendEmail(self, title, message):
        r = requests.post(self.baseUrl, json={"token": os.getenv('token', ""), 
                                              "user": os.getenv('user', ""),
                                              "title": title,
                                              "message": message,
                                              "html": 1})
        return r.json()