from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import AllowAny,IsAuthenticated
from .serializers import *
# from main.serializers import 
from rest_framework.pagination import LimitOffsetPagination
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password,check_password
import json
from django.contrib.auth.models import User
from knox.auth import AuthToken
from django.contrib.auth import login,logout,authenticate
from rest_framework import status

from social_django.utils import psa
from knox.auth import TokenAuthentication

from requests.exceptions import HTTPError
from django.conf import settings
from knox.auth import AuthToken
from rest_framework.decorators import api_view, permission_classes
# from appauth.decorators import *
from main.models import *
# from main.serializers import *
import string

from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.

def generated_token():
    alph='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    num='0123456789'
    ualph=alph.lower()
    unum=alph.lower()
    value=''
    ini_code=alph+num+ualph+unum


    while len(value) < 7:
        code=str(random.choice(ini_code))
        value+=code
    return value



def password_resToken(length):

    return ''.join(random.choices( string.digits,k=length))


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegistrationView(APIView):
    permission_classes=[AllowAny,]
    serializer_class=UserSerializer
    

    def get(self,request):
        
        try:
            token=str(request.GET.get('token'))
            profile=Profile.objects.all()
            for user_profile in profile:

                if check_password(token,user_profile.activation_token):
                    # print(user_profile.user.is_active)
                    user=User.objects.get(id=user_profile.user.id)

                    user.is_active=True
                    user.save()

                    return Response({
                        'message':'account activated',
                        'active':True
                    })
                else:
                    return Response('token not reconized for registered user')
        except ObjectDoesNotExist:
            return Response('no profile data found')


    def post(self,request):
        
        
        try:
            user=User.objects.get(email=str(request.data['email']).lower())
            return Response({
                'message':'user with email already exist',
                'payload': UserSerializer(user,many=False).data,
                'signed_in':False
            })

        
        except ObjectDoesNotExist:
            serializer=UserSerializer(data=request.data)
            
            if serializer.is_valid():
               
                serializer.save()
                
                user=serializer.instance
    
                activation_token=generated_token()
                profile=Profile.objects.get(user=user)
                
                profile.activation_token=make_password(activation_token)
                profile.save()

             
                
                send_mail(
                'Soundr account verification',
                f'click this link to verify you account http://127.0.0.1:8000/auth/register?token={activation_token}',
                'from soundr@gmail.com',
                [user.email],
                
                )
                serialiized_data=UserSerializer(user).data

                return Response({
                    'user':serialiized_data,
                    'profile':ProfileSerializer(profile,many=False).data,
                    'signed_in':True
                })



class LoginView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (BasicAuthentication,)
    serializer_class = UserSerializer

    
    def get(self,request):
        return Response({
            'g_client_id':settings.GOOGLE_CLIENT_ID,
            'g_client_secret':settings.GOOGLE_CLIENT_SECRET
        })
    def post(self,request):
        
        try:
            password=request.data.get('password')
            user=User.objects.get(email=str(request.data['email']).lower())
        

            if check_password(password,user.password):
                if user.is_active == True:

                
                    serialized_data = UserSerializer(user)
                    token=get_tokens_for_user(user)
                    # login(request,user)

                    return Response({
                        'token':token,
                        'user':serialized_data.data,
                        'status':status.HTTP_202_ACCEPTED
                    },status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({
                        'message':'this users account is not active, activate through you mail'
                    })
            else:
                return Response({"wrong_credentials": True,'status':status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({
                'user_exist':False,
                'status':status.HTTP_400_BAD_REQUEST
            },status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([AllowAny])
@psa()
def register_by_access_token(request, backend):
    token = request.data.get('access_token')
    # user = backend.do_auth(token)
    user = request.backend.do_auth(token)
    print(token)

    # print(request)
    if user:
        # new_user=User.objects.get(user=user)
        profile=Profile.objects.get_or_create(
            user=user,
            first_name=user.first_name,
            second_name=user.last_name,
            email=user.email

            )
        token =get_tokens_for_user(user)
        # package=Package.objects.get(name='bronze')
        # UserPackage.objects.create(
        #     user=user,
        #     package=package
        # )
        return Response(
            {
                'token': token[1],
                'profile':ProfileSerializer(profile,many=False).data
            },
            status=status.HTTP_200_OK,
            )
    else:
        return Response(
            {
                'errors': {
                    'token': 'Invalid token'
                    }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )




class LogoutView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]

    
    def post(self, request):
        token=AuthToken.objects.filter(user=request.user).delete()
        logout(request)

        return Response({
            'message': 'user succesfully logged out',
            'logged_out':True
        })
    

class ChangePassWordView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def post(self,request):
        current_pw=request.data['current_pw']
        user=User.objects.get(id=request.user.id)
        if check_password(current_pw,user.password):
            user.set_password(request.data['new_pw'])
            user.save()
            return Response({
                'message':'password successfully changed',
                'status':'success'
            })
   
        
        else:
            return Response({
                'message':'current password don\'t match',
                'status':'failed'
            })


class RequestPasswordResetView(APIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = ()
    permission_classes = ()
    def post(self,request):
        profiles=Profile.objects.all()
        try:
            profile=Profile.objects.get(user__email=request.data.get('email'))
            token=password_resToken(5)
            # for user_profile in profiles:
            #     if check_password(token,user_profile.security_token):
            #         return Response({
            #             'message':'a similar token have been generated'
            #         })
                    
            #     else:

            profile.security_token=make_password(token)

            message = """<p>Hi there!, <br> <br>You have requested to change your password. <br> <br>
            <b>Use """ + token + """ as your verification code</b></p>"""
            subject = 'Password Change Request'
            data = {'status':'success','6_digits':token}

            send_mail(
            subject,
            message,
            'from soundr@gmail.com',
            [profile.user.email],
            
            )

            return({
                'message':data,
                'status':status.HTTP_202_ACCEPTED
            })


        
        except ObjectDoesNotExist:
            return Response({
                'message':'incorrect email',
                'status':status.HTTP_404_NOT_FOUND
            })


class VerifyPasswordResetVerify(APIView):
    def post(self,request):
        email=request.data.get('email')
        token=request.data.get('token')
        try:
            user=User.objects.get(email=email)

            try:
                profile=Profile.objects.get(user=user)
                if check_password(token,profile.security_token):
                    user.set_password(request.data.get('new_pw'))
                    user.save()
                    data = {'success':True}
                    profile.security_token=''
                    profile.save()
                else:
                    data= {'invalid_code':True}
                return Response(data,status=status.HTTP_202_ACCEPTED)

            
            except ObjectDoesNotExist:
                return Response({
                    'message':'user have no profile status',
                    'invalid_profile':True 
                })



        except ObjectDoesNotExist:
            return Response({
                'message':'user dont\' exist',
                'status':False
            })
