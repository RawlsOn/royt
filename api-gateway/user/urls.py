from rest_framework.routers import DefaultRouter

from django.urls import re_path, path, include

from . import apis

from common.custom.jwt_views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
# router.register('user-profile', apis.UserProfileViewSet)


urlpatterns = [

    path('user/', include(router.urls)),

    # path(
    #     'v1/google-signin/',
    #     apis.GoogleSignIn.as_view(),
    #     name="GoogleSignIn"
    # ),
    # path(
    #     'v1/google-signin-be/',
    #     apis.GoogleSignInBackend.as_view(),
    #     name="GoogleSignInBackend"
    # ),
    # path(
    #     'v1/google-signin-callback/',
    #     apis.GoogleSignInCallback.as_view(),
    #     name="GoogleSignInCallback"
    # ),
    path('user/loginjoin/', apis.Loginjoin.as_view(), name='loginjoin'),
    path('user/get-my/<str:id>/', apis.GetMy.as_view(), name="get-my"),
    path('user/update-my-profile/<str:id>/', apis.UpdateMyProfile.as_view(), name="update-my-profile"),
    path('user/update-my-custom/<str:id>/', apis.UpdateMyCustom.as_view(), name="update-my-custom"),

    path('user/custom-css/<str:id>.css', apis.CustomCss.as_view(), name="custom-css"),









    path('user/join/', apis.RegistrateUser.as_view(), name='registrate_user'),

    path('user/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('user/login-by-kakao/', apis.LoginByKakaoView.as_view(), name='login_by_kakao'),

    path(
        'user/change-password/',
        apis.ChangeUserPassword.as_view(),
        name="ChangeUserPassword"
    ),

    path(
        'user/forgot-password/',
        apis.ForgotPassword.as_view(),
        name="ForgotPassword"
    ),

    path(
        'user/get-user-public/<str:id>/',
        apis.GetUserPublic.as_view(),
        name="GetUserPUblic"
    ),
    path(
        'user/edit-user-setting/<str:id>/',
        apis.EditUserSetting.as_view(),
        name="EditUserSetting"
    ),
    path('user/', include(router.urls)),
]
