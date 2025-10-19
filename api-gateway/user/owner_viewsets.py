from rest_framework.response import Response
from rest_framework import serializers, viewsets, mixins
from rest_framework import generics, mixins, views
from django_filters.rest_framework import DjangoFilterBackend


class GenericViewSet(viewsets.ViewSetMixin, generics.GenericAPIView):
    """
    The GenericViewSet class does not provide any actions by default,
    but does include the base set of generic view behavior, such as
    the `get_object` and `get_queryset` methods.
    """
    pass

from rest_framework import status
from rest_framework.settings import api_settings
class OwnerCreateModelMixin:
    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        # This QueryDict instance is immutable 오류 회피
        # https://velog.io/@qlgks1/Django-request-HttpRequest-QueryDict

        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # ApiClient로 테스트할 때는 dict로 진행됨.. 뭐 이래 이거
        if hasattr(request.data, '_mutable'):
            request.data._mutable = True
        request.data['user'] = request.user.pk

        if hasattr(request.data, '_mutable'):
            request.data._mutable = False

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

class OwnerListModelMixin:
    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(
            user= request.user.pk
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class OwnerRetrieveModelMixin:
    """
    Retrieve a model instance.
    """
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class OwnerUpdateModelMixin:
    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.user != request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class OwnerDestroyModelMixin:
    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

class OwnerModelViewSet(OwnerCreateModelMixin,
                   mixins.RetrieveModelMixin,
                   OwnerUpdateModelMixin,
                   OwnerDestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = '__all__'

class FullOwnerModelViewSet(OwnerCreateModelMixin,
                   OwnerRetrieveModelMixin,
                   OwnerUpdateModelMixin,
                   OwnerDestroyModelMixin,
                   OwnerListModelMixin,
                   GenericViewSet):
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = '__all__'

class OwnerModelViewSetAnonRetrieveOnly(OwnerCreateModelMixin,
                   mixins.RetrieveModelMixin,
                   OwnerUpdateModelMixin,
                   OwnerDestroyModelMixin,
                   OwnerListModelMixin,
                   GenericViewSet):
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = '__all__'


from rest_framework import permissions
class OwnerPermission(permissions.BasePermission):
    """
    Object-level permission to only allow updating his own profile
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # obj here is a UserProfile instance
        return obj.user == request.user
