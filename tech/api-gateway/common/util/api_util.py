import json
from django.core.exceptions import ValidationError
def validate_param_exists(key, request):
    value = request.query_params.get(key, '').strip()
    if value == '':
        raise ValidationError(json.dumps({key: '필수 항목입니다.'}, ensure_ascii=False))
    return value

def get_path_string(request):
    full_path = request.get_full_path()
    params = full_path.split('?')
    if len(params) > 1:
        return '?' + params[1]
    else:
        return ''

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

from rest_framework.exceptions import ValidationError, ParseError

def _get_queryset(klass):
    """
    Return a QuerySet or a Manager.
    Duck typing in action: any class with a `get()` method (for
    get_object_or_404) or a `filter()` method (for get_list_or_404) might do
    the job.
    """
    # If it is a model class or anything else with ._default_manager
    if hasattr(klass, '_default_manager'):
        return klass._default_manager.all()
    return klass

def get_object_or_400(klass, *args, **kwargs):
    """
    Use get() to return an object, or raise a Http404 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Like with QuerySet.get(), MultipleObjectsReturned is raised if more than
    one object is found.
    """
    queryset = _get_queryset(klass)
    if not hasattr(queryset, 'get'):
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise ValidationError(klass.__name__)

def get_param_or_400(request, param, *args, **kwargs):
    got = request.data.get(param, None)
    if got: return got
    raise ValidationError(param)