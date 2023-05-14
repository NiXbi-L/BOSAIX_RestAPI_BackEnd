import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import cfg
from random import randrange
class mail():
    def sendEmailMsg(self,to_email,message): #Функция отправки сообщений на Email
        msg = MIMEMultipart()
        msg.attach (MIMEText (message, 'plain'))
        server = smtplib.SMTP('smtp.mail.ru: 25')
        server.starttls()
        server.login (cfg.from_email, cfg.password)
        server.sendmail (cfg.from_email, to_email, msg.as_string())
        server.quit()
    def CheckValidEmail(self,email):
        code = str(randrange(100000,1000000))
        mail.sendEmailMsg(email,"Ваш код верификации: "+code)
        return code