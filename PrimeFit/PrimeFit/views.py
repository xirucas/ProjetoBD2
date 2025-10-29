from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Member Views
@login_required
def member_home(request):
    return render(request, 'Member/HomePage.html')

@login_required
def member_account(request):
    return render(request, 'Member/Account.html')

# Instructor Views
@login_required
def instructor_account(request):
    return render(request, 'Instructor/Account.html')

@login_required
def instructor_class_management(request):
    return render(request, 'Instructor/ClassManagement.html')

# Manager Views
@login_required
def manager_dashboard(request):
    return render(request, 'Manager/Dashboard.html')

@login_required
def manager_members(request):
    return render(request, 'Manager/Members.html')

@login_required
def manager_classes(request):
    return render(request, 'Manager/Classes.html')

@login_required
def manager_checkins(request):
    return render(request, 'Manager/Check-ins.html')

@login_required
def manager_machines(request):
    return render(request, 'Manager/Machines.html')

@login_required
def manager_payments(request):
    return render(request, 'Manager/Payments.html')

@login_required
def manager_plans(request):
    return render(request, 'Manager/Plans.html')
