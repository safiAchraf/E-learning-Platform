from django.contrib import admin
from .models import user, course, learner, chapitres
admin.site.register(user)
admin.site.register(course)
admin.site.register(learner)
admin.site.register(chapitres)

# Register your models here.
