from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User  

# Create your models here.
class Pet(models.Model):
    Type = models.CharField(max_length=200)
    owner = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
    )
    description = models.TextField()
    voters = models.ManyToManyField(User, related_name='voted_pets', blank=True)  

    def __str__(self):
        return self.Type

    def get_absolute_url(self):
        return reverse("pet_detail", kwargs={"pk": self.pk})
