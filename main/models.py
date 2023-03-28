from django.db import models
from django.contrib.auth.models import User
from twilio.rest import Client
import datetime
from functools import reduce
# Create your models here.



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
           if self.passed ==True:
               pass
           else:
                self.ads_start_date_time=datetime.datetime.now()
                self.ads_end_date_time= datetime.datetime.now() + datetime.timedelta(days=self.duration)
        else:
            pass
        
        super().save(*args,**kwargs)




class Packages(models.Model):
    name=models.CharField(max_length=100,null=True,blank=True)
    price=models.PositiveIntegerField(null=True,blank=True)
    duration=models.IntegerField(null=True,blank=True,default=0)
    date_added=models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.name}'


class CartedEvent(models.Model):
    user=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE)
    packages=models.ForeignKey(Packages,null=True,blank=True,on_delete=models.CASCADE,related_name='packages')
    events=models.ManyToManyField(Events,blank=True,related_name='carted_event')
    paid=models.BooleanField(default=False)
    otp_code=models.CharField(max_length=500,null=True,blank=True)
    txref_id=models.CharField(max_length=500,null=True,blank=True)


    @property
    def total_price(self):
        events=self.events.all()

        total_amount=reduce(lambda p1,p2: p1.price + p2.price, events)
        return total_amount

    




class PayedEvents(models.Model):
    carted_event=models.ForeignKey(CartedEvent,null=True,blank=True,on_delete=models.CASCADE)
    txref_id=models.CharField(max_length=500,null=True,blank=True)
    paid=models.BooleanField(default=False)