from traceback import print_exc

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from django.conf import settings
from django.contrib import auth
from django.shortcuts import redirect
from rest_framework import serializers, viewsets, mixins, generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

import rticler.owner_viewsets as rticler_owner_viewsets

from rticler.models.article import Article
from rticler.models.article import TempArticle

from rticler.models.comment import Comment

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class ArticleViewSet(rticler_owner_viewsets.OwnerModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    permission_classes = (AllowAny, )

class TempArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempArticle
        fields = '__all__'

class TempArticleViewSet(rticler_owner_viewsets.FullOwnerModelViewSet):
    serializer_class = TempArticleSerializer
    queryset = TempArticle.objects.all()
    permission_classes = (IsAuthenticated,)

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class CommentViewSet(rticler_owner_viewsets.OwnerModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (AllowAny,)
