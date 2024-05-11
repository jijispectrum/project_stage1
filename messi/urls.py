from django.urls import path
from.import views
urlpatterns=[
    path("leo/",views.leo,name="leo"),
    path("",views.index,name="index"),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('product/', views.product, name='product'),
]
