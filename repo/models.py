from django.db import models
from django.contrib.auth.models import User

class File(models.Model):
    name = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default='ADMIN')
    filetype = models.CharField(max_length=10, null=False, default='private')

class FileRepo(models.Model):
    document_name = models.CharField(max_length=100)
    document_src = models.FileField(upload_to='file/', blank=True, null=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, default=1)