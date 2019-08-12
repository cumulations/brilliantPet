from django.conf.urls import url
from .views import *
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r"^base64/$", imageUpload_base64.as_view()),
    url(r"^$", imageUpload.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)