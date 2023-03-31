from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
import datetime
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status

from django.utils import timezone
import random
from django.contrib.auth.hashers import make_password,check_password
# Create your views here.


def generate_otp():
    nums='0123456789'
    otp_token=''
    while len(otp_token)<6:
        
        otp_token+=random.choice(nums)
    return otp_token


def allEventsObjects(request,*args,**kwargs):
    allObjects={}
    try:
        events=Events.objects.filter(user=request.user).order_by('-date_added')
        allObjects['events']=EventsSerializer(events,many=True).data
    except ObjectDoesNotExist:
        allObjects['events']=[]
    
    try:
        upcoming=Events.objects.filter(user=request.user,passed=False)
        allObjects['upcoming']=EventsSerializer(upcoming,many=True).data
    except ObjectDoesNotExist:
        allObjects['upcoming']=[]
    
    try:
        passed=Events.objects.filter(user=request.user,passed=True)
        allObjects['passed']=EventsSerializer(passed,many=True).data
    except ObjectDoesNotExist:
        allObjects['passed']=[]
    return allObjects


def SetEventEndDate(event_start_date_time,day=0,hour=0,minute=0):
    # end_date=event_start_date+datetime.timedelta(days=day)
    end_date_time=event_start_date_time+datetime.timedelta(days=day,hours=hour,minutes=minute)

    return end_date_time
    


class EventsView(APIView):
    authentication_classes=[JWTAuthentication,]
    permission_classes=[IsAuthenticated]
    def get(self,request,*args,**kwargs):
        
        all_events=Events.objects.filter(user=request.user).order_by('-date_added')
        passed_events=list(filter(lambda x: x.end_date_time < timezone.now(),all_events))
       
        for event in all_events:
            if event in passed_events:
                print(event)
                if event.passed== True:
                    pass
                else:
                    event.passed=True
                event.save()
        objects=allEventsObjects(request)

        return Response({
            'events':objects
        })
    

    def post(self,request,*args,**kwargs):
        serializer=EventsSerializer(data=request.data)
        event_start_date=str(request.data.get('start_date')).split('-')
        event_start_time=str(request.data['start_time']).split(':')

        day_duration=int(request.data.get('day_duration',0))
        hourly_duration=int(request.data.get('hr_duration',0))
        min_duration=int(request.data.get('min_duration',0))

        
        start_date_time=datetime.datetime(int(event_start_date[0]),int(event_start_date[1]),
                                int(event_start_date[2]),int(event_start_time[0]),
                                int(event_start_time[1]),int(event_start_time[2]))
        
        end_date_time=SetEventEndDate(start_date_time,day=day_duration,
                                          hour=hourly_duration,minute=min_duration)
        

        if serializer.is_valid():
            serializer.save()
            serializer.instance.user=request.user
            serializer.instance.start_date_time=start_date_time
            serializer.instance.end_date_time=end_date_time
            

            serialized_data=serializer.save()

            return Response({
                'data':EventsSerializer(serialized_data).data
            })

        else:
            return Response({
                'message':'invalid data',
                'payload':request.data
            })



class PackagesView(APIView):
    authentication_classes=[JWTAuthentication,]
    permission_classes=[IsAuthenticated]
    def get(self,request,*args,**kwargs):
        pass

    def post(self,request,*args,**kwargs):
        serializer=PackagesSerializer(data=request)

        if serializer.is_valid():
            serializer.save()

            return Response({
                'message':'package added',
                'created':True
            })
        


        

class SelectPackageForEvent(APIView):
    authentication_classes=[JWTAuthentication,]
    permission_classes=[IsAuthenticated]
    def get(self,request,*args,**kwargs):
        all_events=Events.objects.filter(user=request.user).order_by('-date_added')
        packages=Packages.objects.all()


        return Response({
            'events':EventsSerializer(all_events,many=True).data,
            'packages':PackagesSerializer(packages,many=True).data
        }) 
    

    
    def post(self,request,*args,**kwargs):
        event_id=request.GET.get('event_id')
        package_id=request.GET.get('package_id')


        try:
            event=Events.objects.get(id=event_id,user=request.user)
        except ObjectDoesNotExist:
            return Response({
                'message':'user event don\'t exist',
                'status': status.HTTP_404_NOT_FOUND,
                'event_found':False
            })
        package=Packages.objects.get(id=package_id)

        # cart,created=CartedEvent.objects.get_or_create(
        #     user=request.user,
        #     packages=package,
        #     paid=False
        # )
        carted_event=CartedEvent.objects.filter(user=request.user,paid=False)
    
        if carted_event.exists():
            
            cart=carted_event.first()
            if event in cart.events.all():
                 return Response({
                'message':'event already added to cart',
                'added':True,
                'status':status.HTTP_202_ACCEPTED
            })

            else:
                cart.events.add(event)
                cart.save()
                # PayedEvents.objects.create(
                #     user=request.user,
                #     carted_event=cart,
                #     # otp_code=make_password(generate_otp)

                # )   
            return Response({
                'message':'succesfully added cart',
                'added':True,
                'status':status.HTTP_202_ACCEPTED
            })
        else:
            cart=CartedEvent.objects.create(user=request.user,packages=package,
                                            paid=False
                                        )
            cart.events.add(event)
            cart.save()
            return Response({
                'message':'succesfully added cart',
                'added':True,
                'status':status.HTTP_202_ACCEPTED
            })
        

class IncreaseDecreaseDurationView(APIView):
    authentication_classes=[JWTAuthentication,]
    permission_classes=[IsAuthenticated]
    def get(self,*args,**kwargs):
        event_id=self.request.GET.get('event_id')
        action=str(self.request.data['action']).lower()

        cart_event=CartedEvent.objects.filter(user=self.request.user,paid=False)
        try:
            event=Events.objects.get(id=event_id,user=self.request.user)
        except ObjectDoesNotExist:
            return Response({
                'message':'event not found',
                'status':status.HTTP_404_NOT_FOUND
            })
        if cart_event.exists():
            cart=cart_event.first()
            if event in cart.events.all():
                if action == 'increase':
                    event.duration+=1
                    
                else:
                    if event.duration > 0:
                        event.duration-=1
                    else:
                        event.duration=0
                event.save()
                cart.save()
                return Response({'duration_altered':True,'status':status.HTTP_200_OK})
            
            else:
                return Response({'message':'event not in cart','status':status.HTTP_404_NOT_FOUND})
        
        else:
            return Response({'message':'no cart ','status':status.HTTP_404_NOT_FOUND})
        



class OTPPaymentVerification(APIView):
    authentication_classes=[JWTAuthentication,]
    permission_classes=[IsAuthenticated]

    def get(self,request,*args,**kwargs):
        cart=CartedEvent.objects.filter(user=request.user,paid=False).first()
        events=PayedEvents.objects.create(
                user=request.user,
                carted_event=cart,
                # otp_code=make_password(generate_otp)

            )
        
        return Response({
            'events':EventsSerializer(events,many=True).data,
            'otp_generated':True
        })
    

    def post(self,request,*args,**kwargs):
        otp_code=request.data['otp']
        event=PayedEvents.objects.filter(user=request.user,paid=False).first()

        if check_password(otp_code,event.otp_code):
            return Response({
                'verified':True,
                'event':PayedEventSerializer(event,many=False).data
            })




        