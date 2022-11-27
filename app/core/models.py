from typing import Optional
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for User models."""

    def create_user(
        self, email: str, password: Optional[str] = None, **kwargs
    ) -> "User":
        """Create and return a new User, adding them to the DB."""
        if not email:
            raise ValueError("User must have an email address.")

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: Optional[str] = None, **kwargs
    ) -> "User":
        """Create and return a new superuser User, adding them to the DB."""
        user = self.create_user(email, password, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.EmailField(max_length=255, unique=True)
    """Primary Key. Email to identify a user."""

    name = models.CharField(max_length=255)
    """Plain text name of the user. Arbitrary."""

    is_active = models.BooleanField(default=True)
    """True if the account is active in the system."""

    is_staff = models.BooleanField(default=False)
    """True if the user is a staff user and able to perform admin functions."""

    objects = UserManager()

    USERNAME_FIELD = "email"
