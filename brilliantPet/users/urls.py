from django.conf.urls import url
from .views import *
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    url(r"^$", notFound.as_view()),
    url(r"^devices$", userDevices.as_view()),
    url(r"^imageupload$", imageUpload.as_view()),
    url(r"^users$", usersView.as_view()),
    url(r"^pets$", pets.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)