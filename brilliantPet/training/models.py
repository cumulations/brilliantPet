from django.db import models

# Create your models here.


class Training(models.Model):

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=45, null = False)
    link = models.CharField(max_length=145, null=False)
    type = models.CharField(max_length=45, null=False)
    is_active = models.IntegerField(null=False, default = 1)
    created_date = models.DateField(auto_now_add=True)