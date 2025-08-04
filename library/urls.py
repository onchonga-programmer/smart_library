"""
URL configuration for library project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
"""
Main URLs configuration for the GreenLeaf Library System
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
        template_name='books/registration/login.html',
        redirect_authenticated_user=True,
        success_url='/'
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/'
    ), name='logout'),
    
    path('signup/', views.signup, name='signup'),
    
    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='books/registration/password_reset.html',
        email_template_name='books/registration/password_reset_email.html',
        subject_template_name='books/registration/password_reset_subject.txt',
        success_url='/password-reset/done/'
    ), name='password_reset'),
    
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='books/registration/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='books/registration/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ), name='password_reset_confirm'),
    
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='books/registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # User profile and dashboard
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Books app URLs
    path('books/', include('books.urls')),
    
    # API URLs (for future AJAX functionality)
    #path('api/', include('api.urls')),
    
    # Search (global search across all apps)
    path('search/', views.global_search, name='global_search'),
    
    # Admin custom URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-reports/', views.admin_reports, name='admin_reports'),
    
    # Help and documentation
    path('help/', views.help_center, name='help'),
    path('faq/', views.faq, name='faq'),
    path('terms/', views.terms_of_service, name='terms'),
    path('privacy/', views.privacy_policy, name='privacy'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error pages
handler404 = 'library.views.custom_404'
handler500 = 'library.views.custom_500'
handler403 = 'library.views.custom_403'
handler400 = 'library.views.custom_400'