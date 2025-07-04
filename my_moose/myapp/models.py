from django.db import models

class FormData(models.Model):
    question = models.TextField()
    survey = models.TextField()
    apiKey = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to='uploads/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
