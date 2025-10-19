import io, time, os, glob, pprint, json, re, shutil, ntpath
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
from django.utils import timezone

import rest_framework
from django.conf import settings
from rest_framework.response import Response
from rest_framework import generics, status, views
from django.shortcuts import get_object_or_404
from django.http import (
    Http404, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect, JsonResponse
)
import urllib.parse

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from django.shortcuts import redirect

from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from common.util import datetime_util

import user.owner_viewsets as user_owner_viewsets

from common.custom.PlainTextParser import PlainTextParser

from django.contrib.auth.models import update_last_login
import user.serializers as user_serializers
import user.models as user_models

from roemail import models as roemail_models

class Loginjoin(generics.CreateAPIView):
    throttle_scope = 'loginjoin'
    permission_classes = [rest_framework.permissions.AllowAny]
    allowed_methods = ('POST',)
    serializer_class = user_serializers.RegistrateUserSerializer
    queryset = user_models.CustomUser.objects.all()

    def post(self, request, *args, **kwargs):
        print('--------------- LoginJoin', request.data)

        code = request.data.get('code', None)
        email = request.data.get('email', None)

        if not code or not email:
            return Response({
                'detail': 'ng',
                'msg': 'code, email'
            })

        code = code[:3] + ' ' + code[3:]

        found = roemail_models.EmailLoginjoinCode.objects.filter(
            email=email,
            code= code,
            loginjoin_at__isnull= True,
            created_at__gte= datetime_util.minutes_ago(5)
        )
        if found.count() == 0:
            return Response({
                'detail': 'ng',
                'msg_type': 'warning',
                'msg': '유효하지 않은 코드입니다.'
            })

        email_code = found.last()

        pp.pprint(email_code.__dict__)
        user = None
        users = user_models.CustomUser.objects.filter(
            email= email
        )
        if users.count() == 0:
            users = user_models.CustomUser.objects.filter(
                secondary_email= email
            )
        if users.count() == 0:
            user = user_models.CustomUser.objects.create_user(
                email= email,
            )
        if users.count() > 1:
            raise Exception(f'user count > 1 / email: {email}')

        if user is None:
            user = users.first()

        refresh = RefreshToken.for_user(user)
        email_code.loginjoin_at = datetime_util.now()
        email_code.save()
        update_last_login(None, user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_200_OK)


        # serializer = self.get_serializer(data=request.data)

        # if not serializer.is_valid():
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = user_models.CustomUser.objects.create_user(
            email= serializer.data['email'],
        )
        refresh = RefreshToken.for_user(user)
        if settings.SIMPLE_JWT['UPDATE_LAST_LOGIN']:
            update_last_login(None, user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_200_OK)

class UpdateMyProfile(generics.UpdateAPIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    allowed_methods = ('PATCH',)
    filter_backends = [DjangoFilterBackend,]
    serializer_class = user_serializers.UserProfileSerializer
    queryset = user_models.UserProfile.objects.all()
    lookup_field = 'id'

    def patch(self, request, id, *args, **kwargs):
        # serializer로 validation 하려고 했으나 귀찮은 게 많음
        # mutable 작업도 해야 하고, 막상 했더니
        # ['user profile with this user already exists.'
        # 이런 에러도 뜸
        user = get_object_or_404(user_models.CustomUser, id= id)
        if request.user != user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_profile = get_object_or_404(user_models.UserProfile, user_id= id)

        if 'image' in request.data:
            user_profile.userimage = request.data['image']
        # 유저 max_length=16인데 이거 보고 함
        # validation을 자동화해야 하는데 이게 귀찮음
        if 'nickname' in request.data:
            user_profile.nickname = request.data['nickname'][:16]

        if 'bio' in request.data:
            user_profile.bio = request.data['bio']

        user_profile.save()

        return Response(status=status.HTTP_200_OK)

class UpdateMyCustom(generics.UpdateAPIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    allowed_methods = ('PATCH',)
    filter_backends = [DjangoFilterBackend,]
    serializer_class = user_serializers.UserCustomSerializer
    queryset = user_models.UserCustom.objects.all()
    lookup_field = 'id'

    def patch(self, request, id, *args, **kwargs):
        print(request.data)
        user = get_object_or_404(user_models.CustomUser, id= id)
        if request.user != user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_custom = get_object_or_404(user_models.UserCustom, user_id= id)

        if 'theme_colors_json' in request.data:
            user_custom.theme_colors_json = request.data['theme_colors_json']

        # # 유저 max_length=16인데 이거 보고 함
        # # validation을 자동화해야 하는데 이게 귀찮음
        # if 'nickname' in request.data:
        #     user_custom.nickname = request.data['nickname'][:16]

        if 'usercss' in request.data:
            user_custom.usercss = request.data['usercss']

        user_custom.save()

        return Response(status=status.HTTP_200_OK)

class EditUserSetting(generics.UpdateAPIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    allowed_methods = ('PATCH',)
    filter_backends = [DjangoFilterBackend,]
    serializer_class = user_serializers.UserProfileSerializer
    queryset = user_models.UserProfile.objects.all()
    lookup_field = 'id'

    def patch(self, request, id, *args, **kwargs):
        user = get_object_or_404(user_models.CustomUser, id= id)
        if request.user != user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_setting = get_object_or_404(user_models.UserSetting, user_id= id)

        # 이부분은 훨씬 정교하게 바꿔야 함
        # 로그도 다 남기고..
        user.email = request.data['email']
        user.save()

        user_setting.phone_number = request.data['phone_number']
        user_setting.save()

        return Response(status=status.HTTP_200_OK)


class CustomCss(generics.RetrieveAPIView):
    # permission_classes = [rest_framework.permissions.IsAuthenticated]
    queryset = user_models.UserCustom.objects.all()
    parser_classes = [PlainTextParser]
    def retrieve(self, request, id, *args, **kwargs):
        user = get_object_or_404(user_models.CustomUser, id= id)
        # if request.user != user:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)

        user_custom = get_object_or_404(user_models.UserCustom, user_id= id)
        print(user_custom.custom_json)

        # return user_custom.custom_json

        content = """
body { background-color: #5d4037; }
"""
        return HttpResponse(content, content_type='text/plain')

















class RegistrateUser(generics.CreateAPIView):
    permission_classes = [rest_framework.permissions.AllowAny]
    allowed_methods = ('POST',)
    filter_backends = [DjangoFilterBackend,]
    serializer_class = user_serializers.RegistrateUserSerializer
    queryset = user_models.CustomUser.objects.all()

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = user_models.CustomUser.objects.create_user(
            email= serializer.data['email'],
            password= serializer.data['password']
        )
        refresh = RefreshToken.for_user(user)
        if settings.SIMPLE_JWT['UPDATE_LAST_LOGIN']:
            update_last_login(None, user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_200_OK)

class IsRegisteredCode(generics.GenericAPIView):
    serializer_class = rest_framework.serializers.Serializer
    permission_classes = [rest_framework.permissions.AllowAny]
    allowed_methods = ('GET',)
    def get(self, request, format=None):
        email = request.GET.get('email', None)
        false_resp = Response({
            'is_registered_code': False,
        }, status=status.HTTP_200_OK)
        if not email: return false_resp


        user = user_models.CustomUser.objects.filter(email= email).first()
        if user is None: return false_resp

        code = request.GET.get('code', None)
        if code is None or code.strip() == '': return false_resp

        if code != user.usersysteminfo_obj['registered_code']: return false_resp

        return Response({
            'is_registered_code': True,
        }, status=status.HTTP_200_OK)


# # curl -X GET "http://localhost:8088/api/v1/get-user/a47a0193-c628-4b23-b7a6-d76c7112aea3/" -H  "accept: application/json" -H  "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjQwOTU4MTY4LCJqdGkiOiJkOGU0MDhhM2Q3YWI0OTMxYThjZDgwMGE0OTZkZDBlOCIsImVtYWlsIjoiYWRtaW5AYWRtaW4uY29tIn0._Rn5UtRRFhyOWU7rDdQkemdgaxHFci8uaaWiOzBqkUI"

# curl -X POST http://localhost:3111/api/user/kakao/callback/?code=cDieiJ0XLXouEBQf4U-dH5jSfmxu93AOJDKP0Oj8Q8Lu520z0_B1lic-JZzhr4Jw6z2zWQoqJZAAAAGHusO39Q
class LoginByKakaoView(views.APIView):
    permission_classes = [rest_framework.permissions.AllowAny]

    def post(self, request):
        try:
            print('--------------- LoginByKakaoView')
            pp.pprint(request.data)
            kakao_id = request.data['kakao_id']
            if not kakao_id:
                return Response(
                    {'kakao_id': '필수 항목입니다.'},
                    status= status.HTTP_400_BAD_REQUEST
                )

            user = None
            refresh = None
            user_system_info = user_models.UserSystemInfo.objects.filter(kakao_id= kakao_id).first()
            if not user_system_info:
                refresh, user = self.registrate_user(request.data)
            else:
                refresh, user = self.login_user(request.data)

            print('user', user)
            print('nickname', user.userprofile.nickname)
            print('image', user.userprofile.image)

        except Exception as e:
            # raise e
            print(e)
            return Response(
                {'msg': str(e)},
                status= status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'user_nickname': user.userprofile.nickname,
            'user_image': user.userprofile.image
        }, status=status.HTTP_200_OK)

    def registrate_user(self, payload):
        print('registrate_user', payload)
        kakao_account = payload['datum']['kakao_account']
        email = ''
        if kakao_account['has_email']:
            email = kakao_account['email']
        else:
            email = 'cstem' + payload['kakao_id'] + '@' + settings.DOMAIN

        user = user_models.CustomUser.objects.create_user(
            email= email
        )

        # save kakao data
        user.userprofile.nickname = payload['datum']['properties']['nickname']
        user.userprofile.image = payload['datum']['properties']['profile_image']
        user.userprofile.save()

        # 전화번호 가져오는 것은 나중에 넣기
        # user.usersetting.phone_number = payload['datum']['kakao_account']['phone_number']
        user.usersetting.save()

        user.usersysteminfo.kakao_id = payload['kakao_id']
        user.usersysteminfo.kakao_datum = payload['datum']
        user.usersysteminfo.is_kakao_authed = True
        user.usersysteminfo.kakao_verified_at = timezone.now()
        user.usersysteminfo.save()

        refresh = RefreshToken.for_user(user)
        update_last_login(None, user)
        return refresh, user

    def login_user(self, payload):
        print('login_user', payload)
        user = user_models.UserSystemInfo.objects.get(kakao_id= payload['kakao_id']).user
        refresh = RefreshToken.for_user(user)
        update_last_login(None, user)
        return refresh, user


class GetMy(generics.RetrieveAPIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    allowed_methods = ('GET',)
    filter_backends = [DjangoFilterBackend,]
    serializer_class = user_serializers.CustomUserSerializer
    queryset = user_models.CustomUser.objects.all()
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class GetUserPublic(generics.RetrieveAPIView):
    permission_classes = [rest_framework.permissions.AllowAny]
    allowed_methods = ('GET',)
    filter_backends = [DjangoFilterBackend,]
    serializer_class = user_serializers.CustomPublicUserSerializer
    queryset = user_models.CustomUser.objects.all()
    lookup_field = 'id'

















class ChangeUserPassword(generics.GenericAPIView):
    serializer_class = rest_framework.serializers.Serializer
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    allowed_methods = ('PATCH',)
    def patch(self, request, format=None):
        old_pw = request.data.get('password', None)
        new_pw = request.data.get('password_to_change', None)
        user = request.user
        if not user.check_password(old_pw):
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_pw)
        user.save()

        return Response(
            status=status.HTTP_200_OK
        )

class ForgotPassword(generics.GenericAPIView):
    serializer_class = rest_framework.serializers.Serializer
    permission_classes = [rest_framework.permissions.AllowAny]
    allowed_methods = ('GET',)
    def get(self, request, format=None):
        email = request.GET.get('email', None)
        if not email:
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

        user = user_models.CustomUser.objects.filter(email= email).first()
        if user is None:
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

        password = user_models.CustomUser.objects.make_random_password()
        user.set_password(password)
        user.save()

        return Response(
            status=status.HTTP_200_OK
        )


# redirect_uri = settings.BE_URL + "/api/v1/google-signin-callback/"
# state = 'whatever'

# class GoogleSignInBackend(TokenViewBase):
#     throttle_scope = 'signin'
#     permission_classes = [rest_framework.permissions.AllowAny]
#     serializer_class = user_serializers.GoogleSignInSerializer

#     def get(self, request, *args, **kwargs):
#         app_key = settings.GOOGLE_AUTH_CLIENT_ID
#         scope = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"

#         google_auth_api = "https://accounts.google.com/o/oauth2/v2/auth"

#         response = redirect( f"{google_auth_api}?client_id={app_key}&response_type=code&redirect_uri={redirect_uri}&scope={scope}" )

#         return response

# class GoogleSignInCallback(generics.GenericAPIView):
#     throttle_scope = 'signin'
#     permission_classes = [rest_framework.permissions.AllowAny]
#     serializer_class = user_serializers.GoogleSignInSerializer

#     def get(self, request, *args, **kwargs):
#         print('--------- GoogleSignInCallback --------------')
#         code = request.GET.get('code')
#         to_next = request.GET.get('next')
#         print('to_next', to_next)
#         token_resp = requests.post(
#             f"https://oauth2.googleapis.com/token?client_id={settings.GOOGLE_AUTH_CLIENT_ID}&client_secret={settings.GOOGLE_AUTH_SECRET}&code={code}&grant_type=authorization_code&redirect_uri={redirect_uri}&state={state}")
#         print('--------- token_resp --------------')
#         if not token_resp.ok:
#             raise ValidationError('invalid google token')

#         access_token = token_resp.json().get('access_token')

#         user_info_resp = requests.get(
#             "https://www.googleapis.com/oauth2/v3/userinfo",
#             params= { 'access_token': access_token }
#         )
#         print('--------- user_info_resp --------------')
#         if not user_info_resp.ok:
#             raise ValidationError('user info from google failed')

#         user_data = user_info_resp.json()

#         profile_data = {
#             'email': user_data['email'],
#             'first_name': user_data.get('given_name', ''),
#             'last_name': user_data.get('family_name', ''),
#             'nickname': user_data.get('nickname', ''),
#             'name': user_data.get('name', ''),
#             'image': user_data.get('picture', None)
#         }

#         user = user_models.CustomUser.objects.filter(
#             Q(google_login_email= profile_data['email'])|Q(email= profile_data['email'])
#         ).first()

#         # 첫 구글 로그인
#         if user is None:
#             # 가입시키고 jwt 토큰 발급
#             user = user_models.CustomUser.objects.create(
#                 email= profile_data['email'],
#                 google_login_email= profile_data['email'],
#             )
#             user_profile = user_models.UserProfile.objects.get(user_id= user.id)
#             user_system_info = user_models.UserSystemInfo.objects.get(user_id= user.id)
#             user_profile.first_name = profile_data['first_name']
#             user_profile.last_name = profile_data['last_name']
#             user_profile.image = profile_data['image']
#             user_profile.nickname = user_profile.first_name + ' ' + user_profile.last_name
#             user_profile.save()

#             user_system_info.is_google_authed = True
#             user_system_info.save()

#             refresh = RefreshToken.for_user(user)
#             if settings.SIMPLE_JWT['UPDATE_LAST_LOGIN']:
#                 update_last_login(None, user)

#             params = urllib.parse.urlencode({
#                 'refresh': refresh,
#                 'access': refresh.access_token,
#                 'user_id': user.id,
#                 'image': user_profile.image,
#                 'nickname': user_profile.nickname
#             })
#             return HttpResponseRedirect(settings.FE_URL + '/google-auth-arrival/' + "?%s" % params)

#         user_profile = user_models.UserProfile.objects.get(user_id= user.id)
#         user_system_info = user_models.UserSystemInfo.objects.get(user_id= user.id)
#         user_system_info.is_google_authed = True

#         # 기타 프로필 정보가 None 인 경우
#         if user_profile.first_name is None:
#             user_profile.first_name = profile_data['first_name']
#         if user_profile.last_name is None:
#             user_profile.last_name = profile_data['last_name']
#         if user_profile.nickname is None:
#             user_profile.nickname = user_profile.first_name + ' ' + user_profile.last_name
#         if user_profile.image is None:
#             user_profile.image = profile_data['image']

#         user_profile.save()

#         if settings.SIMPLE_JWT['UPDATE_LAST_LOGIN']:
#             update_last_login(None, user)

#         refresh = RefreshToken.for_user(user)
#         params = urllib.parse.urlencode({
#             'refresh': refresh,
#             'access': refresh.access_token,
#             'user_id': user.id,
#             'image': user_profile.image,
#             'nickname': user_profile.nickname
#         })
#         return HttpResponseRedirect(settings.FE_URL + '/google-auth-arrival/' + "?%s" % params)




#         # user, _ = user_get_or_create(**profile_data)

#         # response = redirect(settings.BASE_FRONTEND_URL)
#         # response = jwt_login(response=response, user=user)

#         # return Response({'detail': 'failed'},status=status.HTTP_400_BAD_REQUEST)

# class GoogleSignIn(TokenViewBase):
#     throttle_scope = 'signin'
#     permission_classes = [rest_framework.permissions.AllowAny]
#     serializer_class = user_serializers.GoogleSignInSerializer

#     def post(self, request, *args, **kwargs):

#         serializer = self.get_serializer(data=request.data)

#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         if settings.RUNNING_ENV == 'test':
#             pass
#         else:
#             google_req = requests.get(
#             f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={request.data['access_token']}")
#             if google_req.status_code != 200:
#                 return Response({'detail': 'failed'},status=status.HTTP_400_BAD_REQUEST)

#         user = user_models.CustomUser.objects.filter(
#             Q(google_login_email= request.data['email'])|Q(email= request.data['email'])
#         ).first()

#         # 첫 구글 로그인
#         if user is None:
#             # 가입시키고 jwt 토큰 발급
#             user = user_models.CustomUser.objects.create(
#                 email= request.data['email'],
#                 google_login_email= request.data['email'],
#             )
#             user_profile = user_models.UserProfile.objects.get(user_id= user.id)
#             user_system_info = user_models.UserSystemInfo.objects.get(user_id= user.id)
#             user_profile.first_name = request.data['givenName']
#             user_profile.last_name = request.data['familyName']
#             user_profile.image = request.data['image']
#             user_profile.nickname = user_profile.first_name + ' ' + user_profile.last_name
#             user_profile.save()

#             user_system_info.is_google_authed = True
#             user_system_info.save()

#             refresh = RefreshToken.for_user(user)
#             if settings.SIMPLE_JWT['UPDATE_LAST_LOGIN']:
#                 update_last_login(None, user)

#             return Response({
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#                 'user_id': user.id
#             }, status=status.HTTP_200_OK)

#         user_profile = user_models.UserProfile.objects.get(user_id= user.id)
#         user_system_info = user_models.UserSystemInfo.objects.get(user_id= user.id)
#         user_system_info.is_google_authed = True

#         # 기타 프로필 정보가 None 인 경우
#         if user_profile.first_name is None:
#             user_profile.first_name = request.data['givenName']
#         if user_profile.last_name is None:
#             user_profile.last_name = request.data['familyName']
#         if user_profile.nickname is None:
#             user_profile.nickname = user_profile.first_name + ' ' + user_profile.last_name
#         if user_profile.image is None:
#             user_profile.image = request.data['image']

#         user_profile.save()

#         if settings.SIMPLE_JWT['UPDATE_LAST_LOGIN']:
#             update_last_login(None, user)

#         refresh = RefreshToken.for_user(user)
#         return Response({
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#             'user_id': user.id
#         }, status=status.HTTP_200_OK)