#this signal help us to listen what has been added to database and save it respectively
from django.db.models.signals import pre_save
from django.contrib.auth.models import User

def updateUser(sender,instance,**kwargs):
    # print('Signal Triggered')
    user = instance
    if user.email !='':
        user.username = user.email #we take that username and fill it with the email

pre_save.connect(updateUser,sender=User)
