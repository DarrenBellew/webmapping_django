# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser




#from django.db import models



class User(AbstractUser):
    location = models.PointField(
        blank=True,
        null=True
    )

    class Meta:

        verbose_name = "Users"


class Friends(models.Model):

    user_a = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="user_a"
    )
    user_b = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="user_b"
    )

    class Meta:
        unique_together = ("user_a", "user_b")


