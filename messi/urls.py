from django.urls import path
from.import views
urlpatterns=[
    path("leo/",views.leo,name="leo"),
    path("index/",views.index,name="index")
]
