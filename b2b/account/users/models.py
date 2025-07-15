from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.hashers import make_password
from django.contrib import auth
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.apps import apps
from django.core.validators import MinValueValidator
from decimal import Decimal


# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user_object(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)

        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)

        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        user = self._create_user_object(email, password, **extra_fields)
        user.save(using=self._db)
        return user

    async def _acreate_user(self, email, password, **extra_fields):
        """See _create_user()"""
        user = self._create_user_object(email, password, **extra_fields)
        await user.asave(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    create_user.alters_data = True

    async def acreate_user(self, email=None, password=None, **extra_fields):
        """
        Async version of create_user.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return await self._acreate_user(email, password, **extra_fields)

    acreate_user.alters_data = True

    def create_superuser(self, email=None, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    create_superuser.alters_data = True

    async def acreate_superuser(self, email=None, password=None, **extra_fields):
        """
        Async version of create_superuser.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return await self._acreate_user(email, password, **extra_fields)

    acreate_superuser.alters_data = True

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        """
        Return users that have the given permission.
        """
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the backend argument."
                )
        elif not isinstance(backend, str):
            raise TypeError("backend must be a dotted import path string (got %r)." % backend)
        else:
            backend = auth.load_backend(backend)

        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    balance = models.DecimalField(
        _("balance"),
        max_digits=12,
        decimal_places=0,
        default=0,
        help_text="تومان",
        validators=[MinValueValidator(Decimal("0"))],
    )
    email = models.EmailField(_("email address"), unique=True)
    email_verify = models.BooleanField(
        default=False,
        help_text=_("email verification by sending activation link or code."),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. " "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
