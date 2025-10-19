from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import base.models as base_models
from common.util import model_util, datetime_util
import common.util.slack as slack

import uuid
from django.dispatch import receiver

from django.db.models.signals import post_save

from django.db import models
from django.contrib.auth.models import AbstractUser
from itertools import chain

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        data[f.name] = f.value_from_object(instance)
    # for f in opts.many_to_many:
    #     data[f.name] = [i.id for i in f.value_from_object(instance)]
    return data

class CustomUser(AbstractUser):
    username = None
    first_name = None
    last_name = None
    id = models.UUIDField(default=uuid.uuid4, primary_key= True)
    email = models.EmailField(unique=True, db_index= True, blank=True, null=True)
    secondary_email = models.EmailField(db_index= True, blank=True, null=True)

    # @ id / 트위터같은
    user_golbang_id = models.CharField(max_length= 16, blank=True, null=True, unique=True, db_index=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    unique_together = [['email', 'secondary_email']]

    def __str__(self):
        return self.email

    @property
    def to_obj(self):
        dict_obj = to_dict(self)
        return dict_obj

    @property
    def profile(self):
        return self.userprofile

    @property
    def info(self):
        return self.userinfo

    @property
    def setting(self):
        return self.usersetting

    @property
    def system(self):
        return self.usersystem

    @property
    def custom(self):
        return self.usercustom

    @property
    def joined_at(self):
        return datetime_util.pretty_date(self.created_at)

class UserProfile(base_models.RoBase):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    nickname = models.CharField(max_length= 16, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    userimage = models.FileField(
        blank=True, null=True,
        upload_to=model_util.upload_to_userimage
    )

    profile_json = models.TextField(blank=True, null=True)

class UserInfo(base_models.RoBase):

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length= 64, blank=True, null=True)

    info_json = models.TextField(blank=True, null=True)

class UserSetting(base_models.RoBase):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_marketing_content_sendible = models.BooleanField(default= False)

    setting_json = models.TextField(blank=True, null=True)

class UserSystem(base_models.RoBase):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_active = models.BooleanField(default= True)

    system_json = models.TextField(blank=True, null=True)

class UserCustom(base_models.RoBase):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    usercss = models.FileField(
        blank=True, null=True,
        upload_to=model_util.upload_to_usercss
    )
    theme_colors_json = models.TextField(blank=True, null=True)
# {
#     "primary": "blue-12",
#     "lightprimary": "blue-8",
#     "secondary": "green-12",

#     "dark": "purple-12",
#     "accent": "purple-12",

#     "positive": "btc-blue",
#     "negative": "red-12",

#     "info": "blue-grey-6",
#     "warning": "amber-10"
# }

    custom_json = models.TextField(blank=True, null=True)

    @property
    def usercss_wo_exp(self):
        if not self.usercss:
            return ''
        return self.usercss.url.split('?')[0]

@receiver(post_save, sender=CustomUser)
def custom_user_post_save(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user= instance)
        profile.nickname = instance.email.split('@')[0]
        profile.save()

        UserInfo.objects.create(user= instance)
        UserSetting.objects.create(user= instance)
        UserSystem.objects.create(user= instance)
        UserCustom.objects.create(user= instance)
