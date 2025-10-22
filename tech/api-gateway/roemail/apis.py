from django.conf import settings

import rest_framework
from rest_framework.views import APIView
from rest_framework import serializers, viewsets, status, filters, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny

from django_filters.rest_framework import DjangoFilterBackend
import coreapi
from django.shortcuts import get_object_or_404

from rest_framework_gis.filters import InBBoxFilter

from rest_framework_gis.pagination import GeoJsonPagination
from main.pagination import VeryLargeResultsSetPagination
from django.contrib.gis.geos import Point
import operator
from functools import reduce
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
import io, time, os, glob, pprint, json, re
from django.apps import apps
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from common.util import datetime_util

from roemail import models as roemail_models
from user import models as user_models
from . import serializers as roemail_serializers

from roemail.workers.SendLoginjoinCodeRoMailer import SendLoginjoinCodeRoMailer

class InvitationViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    serializer_class = roemail_serializers.InvitationSerializer
    queryset = roemail_models.Invitation.objects.all()
    filterset_fields = {
        # '토지__geo_unit_id': ['in', 'exact',],
    }

# class IsInvited(generics.RetrieveAPIView):
#     lookup_field = 'invitee_email'
#     permission_classes = (AllowAny,)
#     serializer_class = roemail_serializers.InvitationSerializer
#     allowed_methods = ('GET',)
#     queryset = models.Invitation.objects.all()

#     def retrieve(self, request, *args, **kwargs):
#         print('----------------', request)
#         instance = self.get_object()
#         # serializer = self.get_serializer(instance)
#         return Response({'detail': 'ok'})

class SendLoginjoinCode(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.Serializer
    allowed_methods = ('POST',)
    queryset = roemail_models.Invitation.objects.all()

    def create(self, request, email, *args, **kwargs):
        print('----------------', request, email)
        found = user_models.CustomUser.objects.filter(email=email)
        if found.count() == 0:
            found = user_models.CustomUser.objects.filter(secondary_email=email)
        if found.count () > 1:
            raise Exception(f'중복된 이메일이 있습니다. {email}')

        user = found.first()
        if user and not user.usersystem.is_active:
            return Response({'detail': 'not found'})

        if found.count() == 0:
            found = roemail_models.Invitation.objects.filter(invitee_email=email)
        if found.count() == 0:
            return Response({'detail': 'not found'})

        SendLoginjoinCodeRoMailer({
            'email': email
        }).run()

        return Response({'detail': 'ok'})

class VerifyLoginjoinCode(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.Serializer
    allowed_methods = ('GET',)
    queryset = roemail_models.EmailLoginjoinCode.objects.all()

    def get(self, request, email, code, *args, **kwargs):
        found = roemail_models.EmailLoginjoinCode.objects.filter(
            email=email,
            code= code,
            loginjoin_at__isnull= True,
            created_at__lte= datetime_util.minutes_ago(5)
        )
        if not found:
            return Response({
                'detail': 'ng',
                'msg_type': 'warning',
                'msg': '유효하지 않은 코드입니다.'
            })

        got = found.last()

        return Response({'detail': 'ok'})

# class BaseViewSet(viewsets.ModelViewSet):
#     permission_classes = (AllowAny,)
#     bbox_filter_field = 'geom'
#     filter_backends = (IntersectsInBBoxFilter, )
#     pagination_class = VeryLargeResultsSetPagination
#     # filterset_fields = ['has_regits']
#     bbox_filter_include_overlapping = False # Optional

#     def list(self, request):

#         in_bbox = self.request.query_params.get('in_bbox', None)
#         if not in_bbox:
#             return Response({
#                 "count": 0,
#                 "next": None,
#                 "previous": None,
#                 "results": {
#                     "type": "FeatureCollection",
#                     "features": []
#                 }
#             })
#         return super().list(request)

# class ProtoViewSet(BaseViewSet):
#     serializer_class = serializers.ProtoSerializer
#     queryset = roemail_models.Proto.objects.all()

