"""
URL configuration for PrimeFit project.

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
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Member URLs
    path('', views.member_home, name='member_home'),
    path('member/home/', views.member_home, name='member_home'),
    path('member/account/', views.member_account, name='member_account'),
    
    # Instructor URLs
    path('instructor/account/', views.instructor_account, name='instructor_account'),
    path('instructor/classes/', views.instructor_class_management, name='instructor_classes'),
    
    # Manager URLs
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/members/', views.manager_members, name='manager_members'),
    path('manager/classes/', views.manager_classes, name='manager_classes'),
    path('manager/checkins/', views.manager_checkins, name='manager_checkins'),
    path('manager/machines/', views.manager_machines, name='manager_machines'),
    path('manager/payments/', views.manager_payments, name='manager_payments'),
    path('manager/plans/', views.manager_plans, name='manager_plans'),
]
