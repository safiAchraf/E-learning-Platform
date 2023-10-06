from django.contrib import admin
from .models import user, course, learner , Interests
admin.site.register(user)
admin.site.register(course)
admin.site.register(learner)
admin.site.register(Interests)
# Register your models here.
