from django.db import models


class ConversationType(models.TextChoices):
    Group = 'G'
    OneToOne = 'O'
