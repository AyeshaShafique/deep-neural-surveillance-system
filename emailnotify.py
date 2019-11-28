

import os
import time
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import COMMASPACE, formatdate




class MailNotify:
    
    def __init__(self):
        self.smtp_server="smtp.gmail.com"
        self.smtp_port=465
        self.username=""
        self.password="@"
        self.send_from="@gmail.com"
        self.send_to="@gmail.com, @gmail.com"
        self._dir = "E:\\Last days Data\\stream-video-browser\\stream-video-browser\\Results\\"
        self.lock = threading.Lock()
        
    
    def send_mail(self):
        while True:
            print("Lock request.")
            time.sleep(60)
            
            with self.lock:
                print("Lock acquire.")
                files = (fle for rt, _, f in os.walk(self._dir) for fle in f if (time.time() - os.stat(
                os.path.join(rt, fle)).st_mtime < 60  and fle.endswith('.jpg')))
                files = list(files)
                
 
            msg = MIMEMultipart()
            msg['From'] = self.send_from
            msg['To'] = COMMASPACE.join(self.send_to.split(','))
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = "Face alert!!" + " (" + files[0][:-4] + ")"
    
            text="Captured face. \nThanks"
            msg.attach(MIMEText(text))
     
             # image attachment
            images_list=[] 
            for f_img in files[:1]:
                fp = open(os.path.join(self._dir, f_img), 'rb')
                image = MIMEImage(fp.read())
                images_list.append(image)
                fp.close()
            msg.attach(images_list[0])

            smtp = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            smtp.ehlo()
            smtp.login(self.username,  self.password)
            smtp.sendmail(self.send_from, self.send_to.split(','), msg.as_string())
            smtp.close()
            print("Lock released!")
