import random

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser
from django.core import validators
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail

from utils.validators import validate_username

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, phone_number, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()

        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, phone_number=phone_number, is_staff=is_staff, is_superuser=is_superuser, is_active = True, date_joined=now, **extra_fields)

        if not extra_fields.get("no_password"):
            user.set_password(password)

        user.save(using=self._db)

        return user
    
    def create_user(self, username=None, email=None, phone_number=None, password=None, **extra_fields):
        if username is None:
            if email:
                username = email.split("@", 1)[0]
            elif phone_number:
                username = username = random.choice('abcdefghijklmnopqrstuvwxyz') + str(phone_number)[-7:]
        self._create_user(username, email, phone_number, password, False, False, **extra_fields)
    
    def create_superuser(self, username, email, phone_number, password, **extra_fields):
        self._create_user(username, email, phone_number, password, True, True, **extra_fields)
    
    def get_by_phone(self, phone_number):
        return self.get(**{"phone_number":phone_number})

         
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_("username"), unique=True, max_length=32, validators=[validators.RegexValidator(r'[a-zA-Z][a-zA-Z0-9./_]+$', _('Enter a valid username starting with a-z. '
                    'This value may contain only letters, numbers '
                    'and underscore characters.'), 'invalid')], help_text=_('Required. 30 characters or fewer starting with a letter. Letters, digits and underscore only.'), 
                    error_messages={'unique':_("A user with that username already exists."),})
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    email = models.EmailField(_("email"), unique=True, blank=True, null=True)
    phone_number = models.BigIntegerField(_("phone number"), null=True, blank=True, validators=[validators.RegexValidator(r'989[0-3,9]\d{8}')], error_messages={'unique': _("A user with that phone number already exists.")})

    is_staff = models.BooleanField(_("is staff"), default=False)
    is_active = models.BooleanField(_("is active"), default=True)

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_seen = models.DateTimeField(_('last seen date'), null=True)

    objects = UserManager()

    REQUIRED_FIELDS = ["email", "phone_number"]
    USERNAME_FIELD = "username"

    class Meta:
        db_table = 'users'
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name
    
    def short_name(self):
        return self.first_name
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    @property
    def is_loggedin_user(self):
        return self.phone_number is not None or self.email is not None
    
    def save(self, *args, **kwargs):
        if self.email is not None and self.email.strip() == "":
            self.email = None
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nick_name = models.CharField(_("nickname"), max_length=150, blank=True)
    birthday = models.DateField(_("birthday"), blank=True, null=True)
    avatar = models.ImageField(_("avatar"), blank=True, null=True)
    province = models.ForeignKey(to="Province", verbose_name=_("province"), null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    @property
    def get_first_name(self):
        return self.user.first_name
    
    @property
    def get_last_name(self):
        return self.user.last_name
    
    def get_nickname(self):
        return self.nick_name if self.nick_name else self.user.first_name

class Device(models.Model):
    WEB = 1
    IOS = 2
    ANDROID = 3
    DEVICE_TYPE_CHOICES = (
        (WEB, 'web'),
        (IOS, 'ios'),
        (ANDROID, 'android'),
    )
    user = models.ForeignKey(User, related_name='devices', on_delete=models.CASCADE)
    device_uuid = models.UUIDField(_('Device UUID'), null=True)
    last_login = models.DateTimeField(_('last login date'), null=True)
    device_type = models.PositiveSmallIntegerField(choices=DEVICE_TYPE_CHOICES, default=WEB)
    device_os = models.CharField(_('device os'), max_length=20, blank=True)
    device_model = models.CharField(_('device model'), max_length=50, blank=True)
    app_version = models.CharField(_('app version'), max_length=20, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)

class Province(models.Model):
    name = models.CharField(max_length=50)
    is_valid = models.BooleanField(default=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
