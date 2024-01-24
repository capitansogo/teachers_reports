from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from main import views
from main.views import diploma_lessons

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('diploma_lessons/', diploma_lessons, name='diploma_lessons'),
]

# Добавьте следующие строки только для разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
