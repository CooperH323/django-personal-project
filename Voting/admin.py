from django.contrib import admin
from .models import Pet
# Register your models here.
class PetAdmin(admin.ModelAdmin):
    list_display = (
        'Type',
        'owner',
        'description',
    )

admin.site.register(Pet, PetAdmin)