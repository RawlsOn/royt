

from rest_framework import status, filters, generics
from rest_framework.response import Response

from rest_framework.permissions import AllowAny

from config.models import *
from config.serializers import *

from common.util.api_util import validate_param_exists
from common.util.finance_util import get_score_from

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

# 뒤에다가 API를 다 붙이는 게 좋을 듯.
# 그래야 모델 이름과 안 겹침.

class SEO(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SEOSerializer
    allowed_methods = ('GET',)
    queryset = SEO.objects.all()

class BaseSetting(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = BaseSettingSerializer
    allowed_methods = ('GET',)
    queryset = BaseSetting.objects.all()
