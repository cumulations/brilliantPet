from django.db import models

# Create your models here.


class Training(models.Model):

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=45, null = False)
    link = models.CharField(max_length=145, null=False)
    type = models.CharField(max_length=45, null=False)
    is_active = models.IntegerField(null=False, default = 1)
<<<<<<< HEAD
    created_date = models.DateField(auto_now_add=True)
=======
    created_date = models.DateField(auto_now_add=True)
>>>>>>> 595b93d5f57d559438d4ff6e62dda1269dce7af5
