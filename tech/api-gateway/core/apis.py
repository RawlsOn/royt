from django.conf import settings
from dotenv import load_dotenv
load_dotenv(verbose=True)

import rest_framework
from rest_framework.views import APIView
from rest_framework import serializers, viewsets, status, filters, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny

from django_filters.rest_framework import DjangoFilterBackend
import coreapi
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from common.util.logger import RoLogger
logger = RoLogger(another_output_file= settings.LOG_FILE)
from common.util import api_util, str_util
import requests, urllib

import core.models as core_models
import core.serializers as core_serializers
import base.models as base_models

from common.util.slack import fire

class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)

class 토지매물ViewSet(BaseViewSet):
    filter_backends = (DjangoFilterBackend,)
    serializer_class = core_serializers.토지매물Serializer
    queryset = core_models.토지매물.objects.all().order_by('created_at')
    filterset_fields = {
        '토지__geo_unit_id': ['in', 'exact',],
        '토지__토지면적_제곱미터': ['gte', 'lte'],
        '토지__토지면적_평': ['gte', 'lte'],
        '토지__용도지역': ['in', 'exact',],
        '토지__지목': ['in', 'exact'],
        '매매가': ['gte', 'lte'],
        '평당가격': ['gte', 'lte'],
        '제곱미터당가격': ['gte', 'lte'],
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not self.request.query_params.get('토지__geo_unit_id__in'):
            queryset = []

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

class 건물매물ViewSet(BaseViewSet):
    filter_backends = (DjangoFilterBackend,)
    serializer_class = core_serializers.건물매물Serializer
    queryset = core_models.건물매물.objects.all().order_by('created_at')
    filterset_fields = {
        '건물__geo_unit_id': ['in', 'exact',],
        '건물__용도지역': ['in', 'exact',],
        '건물__지목': ['in', 'exact'],
        '건물__토지면적_제곱미터': ['gte', 'lte'],
        '건물__토지면적_평': ['gte', 'lte'],
        '건물__건물용도': ['in', 'exact'],
        '건물__연면적_제곱미터': ['gte', 'lte'],
        '건물__연면적_평': ['gte', 'lte'],
        '건물__층_최저': ['in', 'exact'],
        '건물__층_최고': ['in', 'exact'],
        '건물__엘리베이터': ['in', 'exact'],
        '건물__준공년도': ['gte', 'lte', 'isnull'],
        '토지평당가격': ['gte', 'lte'],
        '토지제곱미터당가격': ['gte', 'lte'],
        '매매가': ['gte', 'lte'],
        '건물전체_보증금': ['gte', 'lte'],
        '건물전체_임대료': ['gte', 'lte'],
        '연면적_평당_임대료': ['gte', 'lte'],
        '연면적_제곱미터당_임대료': ['gte', 'lte'],
        '수익률': ['gte', 'lte'],
        '공용평당_관리비_원': ['gte', 'lte'],
        '공용제곱미터당_관리비_원': ['gte', 'lte'],
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not self.request.query_params.get('건물__geo_unit_id__in'):
            queryset = []

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

class 상가매물ViewSet(BaseViewSet):
    filter_backends = (DjangoFilterBackend,)
    serializer_class = core_serializers.상가매물Serializer
    queryset = core_models.상가매물.objects.all().order_by('created_at')
    filterset_fields = {
        '상가__geo_unit_id': ['in', 'exact',],
        '상가__전용면적_제곱미터': ['gte', 'lte'],
        '상가__전용면적_평': ['gte', 'lte'],
        '상가__노출도': ['in', 'exact'],
        '상가__층': ['in', 'exact'],
        '상가__엘리베이터': ['exact'],
        '상가__준공년도': ['gte', 'lte'],
        '업종': ['in'],
        '매매가': ['gte', 'lte'],
        '보증금': ['gte', 'lte'],
        '임대료': ['gte', 'lte'],
        '권리금': ['gte', 'lte'],
        '공용평당_관리비_원': ['gte', 'lte'],
        '공용제곱미터당_관리비_원': ['gte', 'lte'],
        '수익률': ['gte', 'lte'],
        '평당_임대료': ['gte', 'lte'],
        '제곱미터당_임대료': ['gte', 'lte'],
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not self.request.query_params.get('상가__geo_unit_id__in'):
            queryset = []
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)