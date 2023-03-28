from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
import datetime
from rest_framework.permissions import AllowAny,IsAuthenticated


from django.utils import timezone
# Create your views here.


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

        