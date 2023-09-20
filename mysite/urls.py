"""mysite URL routing.

For more information: https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
import mysite.views as views

urlpatterns = [
    path('', RedirectView.as_view(url='/polls/'), name='site_index'),
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include("django.contrib.auth.urls")),
    path('signup/', views.signup, name='signup'),
]
