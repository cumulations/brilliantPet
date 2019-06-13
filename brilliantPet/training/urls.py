from django.conf.urls import url
from .views import *
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    url(r"^$", trainingView.as_view()),
]


urlpatterns = format_suffix_patterns(urlpatterns)