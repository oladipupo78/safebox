from django.db import models
from django.contrib.auth.models import User


class Member(models.Model):
    name = models.CharField(max_length=30, null=False)
    email = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.name
