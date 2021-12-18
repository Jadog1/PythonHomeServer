import requests
import json
import os, shutil
from dotenv import load_dotenv
import fitz
load_dotenv()

def clearTempStorage():
    folder = 'C:\\Temp'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

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

    def sendEmailAttachment(self, title, message, file):
        doc=fitz.open('C:\\Temp\\'+file)
        page=doc.loadPage(0)
        pix=page.get_pixmap()
        pix.save('C:\\Temp\\temp.jpg')
        r = requests.post(self.baseUrl, data={"token": os.getenv('token', ""), 
                                              "user": os.getenv('user', ""),
                                              "title": title,
                                              "message": message,
                                              "html": 1},
                                             files={"attachment": ("image.jpg", open("C:\\Temp\\temp.jpg", "rb"), "image/jpeg")})
        clearTempStorage()
        return r.json()