from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView

from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView

from profiles.views import ProfileFollowToggle, RegisterView, activate_user_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('measurements.urls', namespace='measurements')),
    path('register/', RegisterView.as_view(), name='register'),
    re_path(r'^activate/(?P<code>[a-z0-9].*)/$', activate_user_view, name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('profile-follow/', ProfileFollowToggle.as_view(), name='follow'),
    path('u/', include('profiles.urls', namespace='profiles')),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
]
