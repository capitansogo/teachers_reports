from django.urls import path, include

from main import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
]
