from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from .models import checkin_model, workout_model, equipment_model, class_schedule_model
from .models import Plan, Membership

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'user_type'):
            if user.user_type == 'manager':
                return '/manager/dashboard/'
            elif user.user_type == 'instructor':
                return '/instructor/account/'
            else:
                return '/'  # member home
        return '/'

# Member Views

def member_home(request):
    # Dados do PostgreSQL
    user_membership = Membership.objects.filter(user=request.user, is_active=True).first()
    
    # Dados do MongoDB
    recent_checkins = list(checkin_model.find({'user_id': request.user.id}).sort([('checkin_time', -1)]).limit(5)) if checkin_model.collection is not None else []
    recent_workouts = list(workout_model.find({'user_id': request.user.id}).sort([('created_at', -1)]).limit(5)) if workout_model.collection is not None else []
    
    context = {
        'user_type': 'member',
        'membership': user_membership,
        'recent_checkins': recent_checkins,
        'recent_workouts': recent_workouts
    }
    return render(request, 'Member/HomePage.html', context)


@login_required
def member_account(request):
    user_membership = Membership.objects.filter(user=request.user, is_active=True).first()
    context = {
        'user_type': 'member',
        'membership': user_membership
    }
    return render(request, 'Member/Account.html', context)

# Instructor Views
@login_required
def instructor_account(request):
    return render(request, 'Instructor/Account.html', {'user_type': 'instructor'})

@login_required
def instructor_class_management(request):
    return render(request, 'Instructor/ClassManagement.html', {'user_type': 'instructor'})

# Manager Views
@login_required
def manager_dashboard(request):
    from .models import CustomUser
    
    # Dados do PostgreSQL
    total_members = CustomUser.objects.filter(user_type='member').count()
    total_instructors = CustomUser.objects.filter(user_type='instructor').count()
    active_memberships = Membership.objects.filter(is_active=True).count()
    
    # Dados do MongoDB
    today_checkins = []
    if checkin_model.collection is not None:
        from datetime import datetime, timezone
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_checkins = list(checkin_model.find({
            'checkin_time': {'$gte': today_start}
        }))
    
    context = {
        'user_type': 'manager',
        'total_members': total_members,
        'total_instructors': total_instructors,
        'active_memberships': active_memberships,
        'today_checkins_count': len(today_checkins)
    }
    return render(request, 'Manager/Dashboard.html', context)

@login_required
def manager_members(request):
    from .models import CustomUser
    members = CustomUser.objects.filter(user_type='member')
    context = {
        'user_type': 'manager',
        'members': members
    }
    return render(request, 'Manager/Members.html', context)

@login_required
def manager_classes(request):
    classes = list(class_schedule_model.find()) if class_schedule_model.collection is not None else []
    context = {
        'user_type': 'manager',
        'classes': classes
    }
    return render(request, 'Manager/Classes.html', context)

@login_required
def manager_checkins(request):
    checkins = list(checkin_model.find().sort([('checkin_time', -1)]).limit(50)) if checkin_model.collection is not None else []
    context = {
        'user_type': 'manager',
        'checkins': checkins
    }
    return render(request, 'Manager/Check-ins.html', context)

@login_required
def manager_machines(request):
    machines = list(equipment_model.find()) if equipment_model.collection is not None else []
    context = {
        'user_type': 'manager',
        'machines': machines
    }
    return render(request, 'Manager/Machines.html', context)

@login_required
def manager_payments(request):
    memberships = Membership.objects.select_related('user', 'plan').all()
    context = {
        'user_type': 'manager',
        'memberships': memberships
    }
    return render(request, 'Manager/Payments.html', context)

@login_required
def manager_plans(request):
    plans = Plan.objects.all()
    context = {
        'user_type': 'manager',
        'plans': plans
    }
    return render(request, 'Manager/Plans.html', context)
