from django.conf.urls import url
from .views import *
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    url(r"^$", notFound.as_view()),
    url(r"^devices$", userDevices.as_view()),
    url(r"^imageupload$", imageUploadMultipart.as_view()),
    url(r"^users$", usersView.as_view()),
    url(r"^pets$", pets.as_view()),
    url(r"^login$", userLogin.as_view()),
    url(r"^logout$", userLogout.as_view()),
    url(r"^tokenupdate$", notificationUpdate.as_view()),
    url(r"^events$", Event.as_view()),
    url(r"^lastevent$", LastEventOfTheMachine.as_view())



]

urlpatterns = format_suffix_patterns(urlpatterns)