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
from rest_framework.pagination import PageNumberPagination

from django.contrib.gis.geos import Point
import operator
from functools import reduce
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
import io, time, os, glob, pprint, json, re
from django.apps import apps
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from . import models
from . import serializers

# https://docs.djangoproject.com/en/4.2/ref/contrib/gis/geoquerysets/
class IntersectsInBBoxFilter(InBBoxFilter):
    def filter_queryset(self, request, queryset, view):
        geoDjango_filter = 'intersects'

        filter_field = getattr(view, 'bbox_filter_field', None)
        if not filter_field:
            return queryset

        bbox = self.get_filter_bbox(request)
        if not bbox:
            return queryset
        return queryset.filter(Q(**{'%s__%s' % (filter_field, geoDjango_filter): bbox}))

class IntersectsInBBoxIndexedFilter(InBBoxFilter):
    def filter_queryset(self, request, queryset, view):
        print('IntersectsInBBoxIndexedFilter filter_queryset')
        geoDjango_filter = 'intersects'

        filter_field = getattr(view, 'bbox_filter_field', None)
        if not filter_field:
            return queryset

        bbox = self.get_filter_bbox(request)
        if not bbox:
            return queryset

        return queryset.indexed_bbox_filter(bbox)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

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
    bbox_filter_field = 'bbox'
    filter_backends = (IntersectsInBBoxIndexedFilter, )
    pagination_class = StandardResultsSetPagination
    # filterset_fields = ['has_regits']
    bbox_filter_include_overlapping = False # Optional

    def list(self, request):

        in_bbox = self.request.query_params.get('in_bbox', None)
        if not in_bbox:
            return Response({
                "count": 0,
                "next": None,
                "previous": None,
                "results": {
                    "type": "FeatureCollection",
                    "features": []
                }
            })
        return super().list(request)

class CoreViewSet(BaseViewSet):
    serializer_class = serializers.CoreSerializer
    queryset = models.Core.objects.all()

