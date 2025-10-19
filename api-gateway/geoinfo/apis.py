from django.conf import settings

from rest_framework.views import APIView
from rest_framework import serializers, viewsets, status, filters, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny

from django_filters.rest_framework import DjangoFilterBackend
import coreapi

from rest_framework_gis.filters import InBBoxFilter

from rest_framework_gis.pagination import GeoJsonPagination
from django.contrib.gis.geos import Point
import operator
from functools import reduce
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
import io, time, os, glob, pprint, json, re
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

import geoinfo.models as geoinfo_models
import geoinfo.serializers as geoinfo_serializers

class InBBoxFilterBackend(DjangoFilterBackend):
    # for schema
    # eg: 129.0,35.0796,129.17,35.3796
    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='in_bbox',
                location='query',
                required=True,
                type='string'
            )
        ]

class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)

class GeoUnitViewSet(BaseViewSet):
    bbox_filter_field = 'center'
    filter_backends = (InBBoxFilter, InBBoxFilterBackend, DjangoFilterBackend)
    # filterset_fields = ['has_regits']
    bbox_filter_include_overlapping = False # Optional

    serializer_class = geoinfo_serializers.GeoUnitSerializer
    queryset = geoinfo_models.GeoUnit.objects.all()

# class GeoInfo(generics.ListAPIView):
#     """
#     # BBOX로 필지리스트 얻기
#     """
#     # filter_backends = (UserDetailFilter, )
#     queryset = olive_ui_models.OlivePilji.objects.filter(
#     )
#     permission_classes = (AllowAny,)
#     pagination_class = GeoJsonPagination
#     serializer_class = olive_ui_serializers.PiljiSerializer
#     bbox_filter_field = 'centroid'
#     filter_backends = (InBBoxFilter, InBBoxFilterBackend, DjangoFilterBackend)
#     filterset_fields = ['has_regits']
#     bbox_filter_include_overlapping = False # Optional

# class PiljisByPnusFilterBackend(DjangoFilterBackend):
#     # for schema
#     def get_schema_fields(self, view):
#         return [
#             coreapi.Field(
#                 name='pnus',
#                 location='query',
#                 required=True,
#                 type='string'
#             )
#         ]

# class PiljisByPnus(generics.ListAPIView):
#     permission_classes = (AllowAny,)
#     # pagination_class = GeoJsonPagination
#     # serializer_class = olive_ui_serializers.PiljiSerializer
#     filter_backends = (PiljisByPnusFilterBackend,)

#     def get_queryset(self):
#         return olive_ui_models.OlivePilji.objects.filter(
#             PNU__in=self.query['pnus']
#         )

#     def validate(self, request):
#         self.query = {}
#         body = json.loads(request.body)
#         self.query['pnus'] = body['data'].get('pnus', '').strip()
#         if self.query['pnus'] == '':
#             return False, Response(
#                 {'pnus': '필수 항목입니다.'},
#                 status= status.HTTP_400_BAD_REQUEST
#             )
#         pnus = self.query['pnus'].split(',')

#         self.query['pnus'] = pnus

#         return True, None

#     def post(self, request, format=None):
#         """
#         # PNU 리스트로 필지정보 얻기
#         # get으로 하기에는 url에 pnu가 다 안들어가는 경우가 있어 post로 함
#         """
#         is_valid, resp = self.validate(request)
#         if not is_valid:
#             return resp

#         queryset = self.get_queryset()
#         paginator = GeoJsonPagination()
#         page = paginator.paginate_queryset(queryset, request)
#         serializer = olive_ui_serializers.PiljiSerializer(page, many=True, context={'request': request})

#         # serializer.is_quotip_in = True
#         return paginator.get_paginated_response(serializer.data)

# class PiljisByRegitsFilterBackend(DjangoFilterBackend):
#     # for schema
#     def get_schema_fields(self, view):
#         return [
#             coreapi.Field(
#                 name='regits',
#                 location='query',
#                 required=True,
#                 type='string'
#             )
#         ]

# class PiljisByRegits(generics.ListAPIView):
#     """
#     # 고유번호 리스트로 등기부의 필지정보 얻기
#     """
#     permission_classes = (AllowAny,)
#     # pagination_class = GeoJsonPagination
#     # serializer_class = olive_ui_serializers.PiljiSerializer
#     filter_backends = (PiljisByRegitsFilterBackend,)

#     def get_queryset(self):
#         return olive_ui_models.OlivePilji.objects.filter(
#             reduce(
#                 operator.or_,
#                 (Q(comm_unique_nos__contains=x) for x in self.query['regits'])
#             )
#         )[:30]
#         # 여기서 30개는 임의적임. geo데이터는 30개가 디폴트이므로 거기에 맞춰서..
#         # 아니 애초에 이렇게 하는 게 맞는 것인가 하는 의문이 듬.
#         # 필지정보와 등기부 정보를 연결해야 하나?
#         # 지금 필지는 만들어 두었다. 하지만 등기에서 필지를 찾을 수는 없음
#         # 필지에서 등기를 찾는 것은 쉬우나(애초에 데이터 흐름이 그러므로)
#         # 등기에서 필지는 찾는 것은 등기를 건드려야 하는 불안함이 있음
#         # 최대한 등기는 독립적으로 두고 싶다

#     def validate(self, request):
#         self.query = {}
#         self.query['regits'] = request.query_params.get('regits', '').strip()
#         if self.query['regits'] == '':
#             return False, Response(
#                 {'regits': '필수 항목입니다.'},
#                 status= status.HTTP_400_BAD_REQUEST
#             )
#         regits = self.query['regits'].split(',')

#         self.query['regits'] = regits

#         return True, None

#     def get(self, request, format=None):
#         is_valid, resp = self.validate(request)
#         if not is_valid:
#             return resp

#         queryset = self.get_queryset()
#         results = olive_ui_serializers.PiljiSerializer(
#             queryset,
#             many=True,
#             context={'request': request}
#         ).data

#         # serializer.is_quotip_in = True
#         return Response({
#             "count": len(results['features']),
#             "next": None,
#             "previous": None,
#             "results": results
#         })

# class ContainsShapeFilterBackend(DjangoFilterBackend):
#     # for schema
#     def get_schema_fields(self, view):
#         return [
#             coreapi.Field(
#                 name='contains_shape',
#                 location='query',
#                 required=True,
#                 type='string'
#             )
#         ]

# class PiljiGis(generics.ListAPIView):

#     # curl -X GET 'http://localhost:5001/api/piljis/?contains_shape=129.11214,35.10879'
#     permission_classes = (AllowAny,)
#     # pagination_class = GeoJsonPagination
#     # serializer_class = olive_ui_serializers.PiljiSerializer
#     filter_backends = (ContainsShapeFilterBackend,)

#     def get_queryset(self):
#         return olive_ui_models.OlivePilji.objects.filter(
#             shape__contains=Point(x= self.query['x'], y= self.query['y'])
#         )

#     def validate(self, request):
#         self.query = {}
#         self.query['contains_shape'] = request.query_params.get('contains_shape', '').strip()
#         if self.query['contains_shape'] == '':
#             return False, Response(
#                 {'contains_shape': '필수 항목입니다.'},
#                 status= status.HTTP_400_BAD_REQUEST
#             )
#         splitted = self.query['contains_shape'].split(',')
#         if len(splitted) != 2:
#             return False, Response(
#                 {'contains_shape': 'X, Y의 형태가 필요합니다.'},
#                 status= status.HTTP_400_BAD_REQUEST
#             )

#         self.query['x'] = float(splitted[0])
#         self.query['y'] = float(splitted[1])

#         return True, None

#     def get(self, request, format=None):
#         """
#         # 포인트로 필지정보 얻기. 하나만 오는 게 정상.
#         """
#         is_valid, resp = self.validate(request)
#         if not is_valid:
#             return resp

#         queryset = self.get_queryset()
#         paginator = GeoJsonPagination()
#         page = paginator.paginate_queryset(queryset, request)
#         serializer = olive_ui_serializers.PiljiSerializer(page, many=True, context={'request': request})

#         # serializer.is_quotip_in = True
#         return paginator.get_paginated_response(serializer.data)