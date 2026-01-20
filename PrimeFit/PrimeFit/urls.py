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
    path('member/account/edit/', views.member_account_edit, name='member_account_edit'),
    path('member/account/change-password/', views.member_change_password, name='member_change_password'),
    path('member/payment/process/', views.member_process_payment, name='member_process_payment'),
    path('member/evaluate-class/<int:classscheduleid>/', views.evaluate_class, name='evaluate_class'),
    
    # Instructor URLs
    path('instructor/account/', views.instructor_account, name='instructor_account'),
    path('instructor/account/edit/', views.instructor_account_edit, name='instructor_account_edit'),
    path('instructor/account/change-password/', views.instructor_change_password, name='instructor_change_password'),
    path('instructor/classes/', views.instructor_class_management, name='instructor_classes'),
    path('instructor/class-evaluations/<str:class_name>/', views.instructor_class_evaluations, name='instructor_class_evaluations'),
    
    # Manager URLs
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/members/', views.manager_members, name='manager_members'),
    path('manager/members/new/', views.manager_member_detail, name='manager_member_new'),
    path('manager/members/<int:member_id>/', views.manager_member_detail, name='manager_member_detail'),
    path('manager/classes/', views.manager_classes, name='manager_classes'),
    path('manager/classes/new/', views.manager_class_new, name='manager_class_new'),
    path('manager/classes/<int:class_id>/view/', views.manager_class_view, name='manager_class_view'),
    path('manager/classes/<int:class_id>/edit/', views.manager_class_edit, name='manager_class_edit'),
    path('manager/instructors/', views.manager_instructors, name='manager_instructors'),
    path('manager/instructors/new/', views.manager_instructor_detail, name='manager_instructor_new'),
    path('manager/instructors/<int:instructor_id>/', views.manager_instructor_detail, name='manager_instructor_detail'),
    path('manager/machines/', views.manager_machines, name='manager_machines'),
    path('manager/machines/new/', views.manager_machine_detail, name='manager_machine_new'),
    path('manager/machines/<int:machine_id>/', views.manager_machine_detail, name='manager_machine_detail'),
    path('manager/machines/<int:machine_id>/change-status/', views.manager_machine_change_status, name='manager_machine_change_status'),
    path('manager/payments/', views.manager_payments, name='manager_payments'),
    path('manager/payments/export/', views.manager_payments_export, name='manager_payments_export'),
    path('manager/financial-report/', views.financial_report, name='manager_financial_report'),
    path('manager/plans/', views.manager_plans, name='manager_plans'),
    path('manager/plans/<int:plan_id>/edit/', views.manager_plan_edit, name='manager_plan_edit'),
]
