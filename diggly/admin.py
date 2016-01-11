from django.contrib import admin
from .models import Topic, TopicLink, SectionLink 

admin.site.register(Topic)
admin.site.register(TopicLink)
admin.site.register(SectionLink)
