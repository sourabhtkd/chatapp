import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower


# Create your models here.

class User(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("email"),
                name="user_email_ci_uniqueness",
            ),
        ]



