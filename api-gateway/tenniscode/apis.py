from django.conf import settings
from dotenv import load_dotenv
load_dotenv(verbose=True)

import rest_framework
from rest_framework.views import APIView
from rest_framework import status, filters, generics, serializers, viewsets, mixins, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny

from django_filters.rest_framework import DjangoFilterBackend
import coreapi
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
from dateutil.relativedelta import relativedelta
import io, time, os, glob, pprint, json, re, shutil, ntpath, sys, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()
from common.util.logger import RoLogger
logger = RoLogger(another_output_file= settings.LOG_FILE)
from common.util import api_util, str_util, datetime_util
import requests, urllib

import tenniscode.models as tenniscode_models

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = tenniscode_models.Competition
        fields = '__all__'

class PerformanceSerializer(serializers.ModelSerializer):
    competition = CompetitionSerializer(read_only= True)

    class Meta:
        model = tenniscode_models.Performance
        fields = '__all__'

class PlayerSerializer(serializers.ModelSerializer):
    performances = serializers.SerializerMethodField()
    def get_performances(self, obj):
        return PerformanceSerializer(
            tenniscode_models.Performance.objects.filter(
                player_id= obj.id
            ).filter(
                match_date__gte= obj.기준일 - relativedelta(years=1)
            ).order_by('-point'),
            many=True
        ).data

    class Meta:
        model = tenniscode_models.Player
        fields = '__all__'

class SimplePlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = tenniscode_models.Player
        fields = '__all__'


class ClubSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    players = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    link = serializers.ReadOnlyField()
    link_escaped = serializers.ReadOnlyField()

    def get_profile(self, obj):
        profile = tenniscode_models.ClubProfile.objects.filter(club= obj).first()
        if profile:
            if profile.image is None:
                profile.image = 'https://rawlson-public-seoul.s3.ap-northeast-2.amazonaws.com/LOVE_TENNIS/c/%ED%85%8C%EB%8B%88%EC%8A%A4%EC%BD%94%EB%93%9C.png'
                profile.save()
            return profile.to_obj
        else:
            return tenniscode_models.ClubProfile.objects.create(
                club= obj,
                image= 'https://rawlson-public-seoul.s3.ap-northeast-2.amazonaws.com/LOVE_TENNIS/c/%ED%85%8C%EB%8B%88%EC%8A%A4%EC%BD%94%EB%93%9C.png'
            ).to_obj

    def get_players(self, obj):
        return PlayerSerializer(
            obj.player_set.all().order_by('-full_point'),
            many=True
        ).data

    def get_comments(self, obj):
        return AnonClubCommentSerializer(
            obj.ClubS_comments.filter(
                parent= None,
                is_deleted= False
            ).order_by('created_at'),
            many=True
        ).data

    class Meta:
        model = tenniscode_models.Club
        fields = '__all__'

class SimpleClubSerializer(serializers.ModelSerializer):
    link = serializers.ReadOnlyField()
    link_escaped = serializers.ReadOnlyField()

    class Meta:
        model = tenniscode_models.Club
        fields = '__all__'

# class ClubViewSet(mixins.ListModelMixin, viewsets.ViewSetMixin, generics.GenericAPIView):
#     serializer_class = SimpleClubSerializer
#     queryset = tenniscode_models.Club.objects.all()
#     permission_classes = (AllowAny, )
#     filter_backends = [filters.OrderingFilter]
#     ordering_fields = ['rank', 'challenger_rank']

# class ClubViewSet(mixins.RetrieveModelMixin, viewsets.ViewSetMixin, generics.GenericAPIView):
#     serializer_class = ClubSerializer
#     queryset = tenniscode_models.Club.objects.all()
#     permission_classes = (AllowAny, )

class TenThousandPagination(rest_framework.pagination.PageNumberPagination):
       page_size = 10000

class FetchClubs(generics.ListAPIView):
    permission_classes = [AllowAny]
    allowed_methods = ('GET',)
    filter_backends = [DjangoFilterBackend,]
    pagination_class = TenThousandPagination
    serializer_class = SimpleClubSerializer
    queryset = tenniscode_models.Club.objects.all().order_by('full_rank')
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['full_rank', 'master_rank', 'challenger_rank']

class GetClub(generics.GenericAPIView):
    permission_classes = [AllowAny]
    allowed_methods = ('GET',)
    queryset = tenniscode_models.Club.objects.all()
    serializer_class = ClubSerializer
    lookup_field = 'title'

    def get(self, request, title, format=None):
        got = tenniscode_models.Club.objects.filter(title= title).first()
        if not got:
            return Response(
                data= {'detail': '클럽이 없습니다.'},
                status= status.HTTP_400_BAD_REQUEST
            )

        return Response(
            data= ClubSerializer(got).data
        )

class GetIndexInfo(generics.GenericAPIView):
    permission_classes = [AllowAny]
    allowed_methods = ('GET',)
    queryset = tenniscode_models.Club.objects.all()
    serializer_class = ClubSerializer

    def get(self, request, format=None):
        남자_통합_1위 = tenniscode_models.Club.objects.all().order_by('full_rank').first()
        남자_신인부_1위 = tenniscode_models.Club.objects.all().order_by('challenger_rank').first()
        최다_랭커_보유_클럽 = tenniscode_models.Club.objects.all().order_by('players_count_having_performance', 'full_point').last()

        return Response(
            data= {
                '남자_통합_1위': SimpleClubSerializer(남자_통합_1위).data,
                '남자_신인부_1위': SimpleClubSerializer(남자_신인부_1위).data,
                '최다_랭커_보유_클럽': SimpleClubSerializer(최다_랭커_보유_클럽).data
            }
        )

        # sise = int(self.params['sise'])
        # requested = int(self.params['requested'])
        # return_period = int(self.params['return_period'])

        # if sise == 0:
        #     score = 0
        # else:
        #     score = get_score_from(
        #         ltv= requested / sise * 100,
        #         return_period_month= return_period
        #     )

        # queryset = self.queryset.filter(
        #     Q(score__gte=score)
        # ).order_by('score').first()

        # result = self.get_serializer(result, many=True)
        # result = self.get_serializer(queryset)
        return Response(
            {
                'data': []
            },
            status=status.HTTP_200_OK
        )

class AnonClubChildrenCommentSerializer(serializers.ModelSerializer):
    pretty_created_at = serializers.SerializerMethodField()
    def get_pretty_created_at(self, obj):
        return datetime_util.pretty_date(obj.created_at)

    class Meta:
        model = tenniscode_models.AnonClubComment
        fields = ['id', 'club', 'writer_name', 'content', 'parent', 'pretty_created_at']

class AnonClubCommentSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    def get_children(self, obj):
        return AnonClubChildrenCommentSerializer(
            tenniscode_models.AnonClubComment.objects.filter(
                parent= obj.id
            ).order_by('-created_at'),
            many=True
        ).data

    pretty_created_at = serializers.SerializerMethodField()
    def get_pretty_created_at(self, obj):
        return datetime_util.pretty_date(obj.created_at)

    class Meta:
        model = tenniscode_models.AnonClubComment
        fields = ['id', 'club', 'writer_name', 'content', 'children', 'pretty_created_at', 'created_at']

class PostAnonClubComment(generics.GenericAPIView):
    permission_classes = [AllowAny]
    allowed_methods = ('GET',)
    queryset = tenniscode_models.AnonClubComment.objects.all()
    serializer_class = AnonClubCommentSerializer

    def post(self, request, club_id, *args, **kwargs):
        club = api_util.get_object_or_400(tenniscode_models.Club, id= club_id)
        client_ip = api_util.get_client_ip(request)
        parent_id = request.data.get('parent', None)
        parent = None
        if parent_id:
            parent = tenniscode_models.AnonClubComment.objects.get(id= parent_id)

        writer_name = request.data.get('writer_name', None)
        if not writer_name:
            return Response(
                data= {'detail': '이름을 입력하세요.'},
                status= status.HTTP_400_BAD_REQUEST
            )

        writer_pw = request.data.get('writer_pw', None)
        if not writer_pw:
            return Response(
                data= {'detail': '비밀번호를 입력하세요.'},
                status= status.HTTP_400_BAD_REQUEST
            )

        # if not 8 <= len(writer_pw) <= 16 :
        #     return Response(
        #         data= {'detail': '비밀번호는 8자 이상 16자 이하로 입력하세요.'},
        #         status= status.HTTP_400_BAD_REQUEST
        #     )

        content = request.data.get('content', None)
        if not content:
            return Response(
                data= {'detail': '내용을 입력하세요.'},
                status= status.HTTP_400_BAD_REQUEST
            )

        if len(content) < 5:
            return Response(
                data= {'detail': '내용을 더 입력해 주세요.'},
                status= status.HTTP_400_BAD_REQUEST
            )

        if len(content) > 255:
            return Response(
                data= {'detail': '내용이 너무 많습니다.'},
                status= status.HTTP_400_BAD_REQUEST
            )
        comment = tenniscode_models.AnonClubComment.objects.create(
            club= club,
            parent= parent,
            content= content,
            writer_name= writer_name,
            writer_pw= writer_pw,
            writer_ip= client_ip
        )
        return Response(
            data={'comment': comment.to_obj},
            status=status.HTTP_201_CREATED
        )

class DeleteAnonClubComment(generics.GenericAPIView):
    permission_classes = [AllowAny]
    allowed_methods = ('DELETE',)
    queryset = tenniscode_models.AnonClubComment.objects.all()
    serializer_class = AnonClubCommentSerializer

    def delete(self, request, club_id, comment_id, *args, **kwargs):
        comment = api_util.get_object_or_400(tenniscode_models.AnonClubComment, id= comment_id)

        print('request.data', request.data)
        writer_pw = request.data.get('writer_pw', None)
        if not writer_pw:
            return Response(
                data= {'detail': '비밀번호를 입력하세요.'},
                status= status.HTTP_400_BAD_REQUEST
            )

        if comment.writer_pw != writer_pw:
            return Response(
                data= {'detail': '비밀번호가 다릅니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment.is_deleted = True
        comment.save()
        return Response(
            status= status.HTTP_204_NO_CONTENT
        )


