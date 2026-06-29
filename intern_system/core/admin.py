from django.contrib import admin
from .models import Department, Intern, SchoolSupervisor, PoliceSupervisor, Comment, Message
from .models import UserProfile

admin.site.register(Department)
admin.site.register(Intern)
admin.site.register(SchoolSupervisor)
admin.site.register(PoliceSupervisor)
admin.site.register(Comment)
admin.site.register(UserProfile)
admin.site.register(Message)
