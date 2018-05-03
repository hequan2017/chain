from django.db import models


from django.db import models
from django.contrib.auth.models import AbstractUser


class Names(AbstractUser):
   ps = models.CharField(max_length=1024,verbose_name="备注",null=True,blank=True)



