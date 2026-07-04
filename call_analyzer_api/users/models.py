from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", User.ROLE_ADMIN)
        return self.create_user(email, password, **extra)


class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_GUEST = "guest"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_GUEST, "Guest"),
    ]

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=ROLE_INSTRUCTOR
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN
