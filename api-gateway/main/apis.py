from django.conf import settings

import rest_framework
from rest_framework.views import APIView
from rest_framework import serializers, viewsets, status, filters, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from common.util.logger import RoLogger
logger = RoLogger(another_output_file= settings.LOG_FILE)
from common.util import api_util, str_util

import main.models as main_models
# import core.models as core_models
import main.serializers as main_serializers
import base.models as base_models

class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)

# localhost:3111/api/main/매물노트/?geo_unit_ids=1,2,5,7,18,24,36,37,38,39,54,55,110,219,220,221,223,246,252,254,261,278,294,295,306,308,309,316,321,322,323,324,346,350,352,353,354,355
# class 매물노트(generics.GenericAPIView):
#     permission_classes = (AllowAny,)
#     filter_backends = (DjangoFilterBackend,)

#     def get_queryset(self):
#         return None

#     def none_response(self):
#         return Response({
#             "count": 0,
#             "next": None,
#             "previous": None,
#             "results": []
#         })

#     def get(self, request, *args, **kwargs):
#         self.queryset = self.filter_queryset(self.get_queryset())
#         geo_unit_ids = self.request.query_params.get('geo_unit_ids')
#         if not geo_unit_ids:
#             return self.none_response()
#         geo_unit_ids = [int(x) for x in geo_unit_ids.split(',')]

#         print(geo_unit_ids)

#         ret = {}

#         토지s = core_models.토지.objects.filter(geo_unit_id__in=geo_unit_ids)
#         토지매물s = core_models.토지매물.objects.filter(토지__in= 토지s)
#         토지매물_ids = [x.id for x in 토지매물s]
#         토지매물노트s = main_models.토지매물노트.objects.filter(토지매물_id__in= 토지매물_ids)
#         토지serializer = main_serializers.토지매물노트Serializer(토지매물노트s, many=True)
#         ret['토지매물노트'] = 토지serializer.data

#         건물s = core_models.건물.objects.filter(geo_unit_id__in=geo_unit_ids)
#         건물매물s = core_models.건물매물.objects.filter(건물__in= 건물s)
#         건물매물_ids = [x.id for x in 건물매물s]
#         건물매물노트s = main_models.건물매물노트.objects.filter(건물매물_id__in= 건물매물_ids)
#         건물serializer = main_serializers.건물매물노트Serializer(건물매물노트s, many=True)
#         ret['건물매물노트'] = 건물serializer.data

#         상가s = core_models.상가.objects.filter(geo_unit_id__in=geo_unit_ids)
#         상가매물s = core_models.상가매물.objects.filter(상가__in= 상가s)
#         상가매물_ids = [x.id for x in 상가매물s]
#         상가매물노트s = main_models.상가매물노트.objects.filter(상가매물_id__in= 상가매물_ids)
#         상가serializer = main_serializers.상가매물노트Serializer(상가매물노트s, many=True)
#         ret['상가매물노트'] = 상가serializer.data

#         return Response({
#             "count": None,
#             "next": None,
#             "previous": None,
#             "results": ret
#         })
