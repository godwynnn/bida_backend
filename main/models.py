from django.db import models
from django.contrib.auth.models import User
from twilio.rest import Client
import datetime
from functools import reduce
import random
from django.contrib.auth.hashers import check_password,make_password
from django.core.mail import send_mail
import math
# Create your models here.
def generate_otp():
    nums='0123456789'
    otp_token=''
    while len(otp_token)<6:
        
        otp_token+=random.choice(nums)
    return otp_token



class Profile(models.Model):
    user=models.OneToOneField(User,null=True,blank=True,on_delete=models.CASCADE,unique=True)
    email=models.EmailField(null=True,blank=True)
    first_name=models.CharField(max_length=100,blank=True, null=True)
    second_name=models.CharField(max_length=100,blank=True, null=True)
    device = models.CharField(max_length=200, null=True, blank=True)
    security_token=models.CharField(max_length=1000, null=True, blank=True)
    phone_no=models.PositiveIntegerField(null=True,blank=True)
    image=models.ImageField(null=True,blank=True,upload_to='image/users_img',default='')
    followers=models.ManyToManyField(User,blank=True,related_name='followers')
    following=models.ManyToManyField(User,blank=True,related_name='following')
    activation_token=models.CharField(max_length=200,null=True, blank=True)
    date_joined=models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.user}'
    # def save(self,*args,**kwargs):
    #     pass

    class Meta:
        ordering= ['-date_joined']

class Events(models.Model):
    user=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE)
    title=models.CharField(max_length=200,null=True,blank=True)
    description=models.TextField(max_length=10000,null=True,blank=True)
    duration=models.IntegerField(null=True,blank=True,default=0)
    start_date_time=models.DateTimeField(null=True,blank=True)
    end_date_time=models.DateTimeField(null=True,blank=True)
    paid=models.BooleanField(default=False)
    passed=models.BooleanField(default=False)
    ads_start_date_time=models.DateTimeField(null=True,blank=True)
    ads_end_date_time=models.DateTimeField(null=True,blank=True)
    date_added=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title}'
    
    def save(self,*args,**kwargs):
        if self.duration >0:
           if self.passed ==True and self.paid==False:
               self.ads_start_date_time=''
               self.ads_end_date_time=''
           elif self.passed ==False and self.paid==True  :
                self.ads_start_date_time=datetime.datetime.now()
                self.ads_end_date_time= datetime.datetime.now() + datetime.timedelta(days=self.duration)
        elif self.duration < 0:
            self.duration=0
        else:
            pass
        
        super().save(*args,**kwargs)




class Packages(models.Model):
    name=models.CharField(max_length=100,null=True,blank=True)
    price=models.PositiveIntegerField(null=True,blank=True)
    date_added=models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.name}'



# class EventItem(models.Model):
#     event=models.OneToOneField(Events,null=True,blank=True,on_delete=models.CASCADE,related_name='event_iten')
#     duration=models.IntegerField(null=True,blank=True,default=0)
#     date_added=models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f'{self.event.title} will last for {str(self.duration)}'
    
    
#     def event_ads_cost(self):
#         return self.duration * self.event.price



class CartedEvent(models.Model):
    user=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE)
    packages=models.ForeignKey(Packages,null=True,blank=True,on_delete=models.CASCADE,related_name='packages')
    events=models.ManyToManyField(Events,blank=True,related_name='carted_event')
    paid=models.BooleanField(default=False)
    # total=models.IntegerField(null=True,blank=True,default=0)
    txref_id=models.CharField(max_length=500,null=True,blank=True)


    @property
    def total_price(self):
        events=self.events.all()
        duration_list=[]
        for event in events:
            duration_list.append(event.duration)
        print(duration_list)
        total_duration=reduce(lambda x,y: x+ y, duration_list)

        total_amount=total_duration*self.packages.price
        return total_amount
    
    # def save(self,*args,**kwargs):
        
    #     self.total= self.total_price
    #     super().save(*args,**kwargs)

    




class PayedEvents(models.Model):
    user=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE)
    carted_event=models.ForeignKey(CartedEvent,null=True,blank=True,on_delete=models.CASCADE)
    txref_id=models.CharField(max_length=500,null=True,blank=True)
    otp_code=models.CharField(max_length=1000,null=True,blank=True)
    paid=models.BooleanField(default=False)

    def save(self,*args,**kwargs):
        if self.paid==False:
            token=generate_otp()
            otp_list=[event.otp_code for event in list(PayedEvents.objects.all())]
            print(otp_list)
            
            if not check_password(token,otp_list):
                self.otp_code=make_password(token)
                send_mail(
                    'Bida payment otp',
                    f'your otp code is {token}',
                    'from Bida@gmail.com',
                    [self.user.email],
                    
                    )


        super().save(*args,**kwargs)

    