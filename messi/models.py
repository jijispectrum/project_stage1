from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15)
    location = models.CharField(max_length=100)
