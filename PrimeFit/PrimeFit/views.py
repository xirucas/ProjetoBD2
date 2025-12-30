from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from .models import (
    UserAuthentication, Plan, EmailExists, MemberStatsMonth, 
    MemberScheduleClasses, MemberAccountDetails,
    InstructorInfo, InstructorClasses, ClassSchedules, DashboardStats,
    AllMembers, AllClasses, AllCheckins, Machines, Payments, Plans,
    MemberPaymentHistory, MemberCheckinHistory, InstructorMonthlyStats, InstructorDashboardStats, InstructorClassesToday, InstructorNextClassMembers, InstructorClassHistory, InstructorWeekPerformance, InstructorPopularClasses
)

# Autenticação usando tabela USERS do PostgreSQL
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email e password são obrigatórios.')
            return render(request, 'auth/login.html')
        
        # Verificar credenciais usando o model UserAuthentication
        try:
            user_data = UserAuthentication.objects.filter(email=email).first()
            
            if user_data and check_password(password, user_data.password):
                # Criar sessão de usuário
                request.session['user_id'] = user_data.userid
                request.session['email'] = user_data.email
                request.session['user_name'] = user_data.name
                request.session['user_type_id'] = user_data.usertypeid
                request.session['user_type'] = user_data.user_type_label
                request.session['is_authenticated'] = True
                
                # Atualizar last_login usando procedimento armazenado
                with connection.cursor() as cursor:
                    cursor.execute("CALL sp_update_last_login(%s)", [user_data.userid])
                
                # Redirecionar baseado no tipo de usuário
                if user_data.usertypeid == 1:  # Gestor
                    return redirect('manager_dashboard')
                elif user_data.usertypeid == 2:  # Instrutor
                    return redirect('instructor_account')
                else:  # Membro
                    return redirect('member_home')
            else:
                messages.error(request, 'Email ou password incorretos.')
                    
        except Exception as e:
            messages.error(request, f'Erro no login: {str(e)}')
    
    return render(request, 'auth/login.html')

def logout_view(request):
    # Limpar sessão
    request.session.flush()
    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('login')

def register_view(request):
    try:
        plans = list(Plan.objects.values('planid', 'name', 'monthlyprice', 'access24h'))
    except Exception as e:
        plans = []
        messages.error(request, f'Erro ao carregar planos: {str(e)}')

    context = {
        'plans': plans
    }

    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        nif = request.POST.get('nif', '')
        phone = request.POST.get('phone', '')
        iban = request.POST.get('iban', '')
        birth_date = request.POST.get('birthdate', '')
        gender = request.POST.get('gender', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        postal_code = request.POST.get('postalcode', '')
        plan = request.POST.get('plan', '')
        user_type = request.POST.get('user_type', '3')  # Default to 'Member' type

        try:
            # Verificar se email já existe usando model
            if EmailExists.objects.filter(email=email).exists():
                messages.error(request, 'Este email já está registado.')
                return render(request, 'auth/register.html', context)
            
            # Criar novo usuário
            hashed_password = make_password(password)
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_create_member(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                             [name, hashed_password, nif, email, phone, iban, birth_date, gender, address, city, postal_code, plan])
            messages.success(request, 'Conta criada com sucesso! Pode fazer login.')
            return redirect('login')
                
        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {str(e)}')
            return render(request, 'auth/register.html', context)

    return render(request, 'auth/register.html', context)

# Decorator customizado para verificar autenticação
def custom_login_required(function):
    def wrap(request, *args, **kwargs):
        if not request.session.get('is_authenticated'):
            messages.error(request, 'É necessário fazer login para aceder a esta página.')
            return redirect('login')
        return function(request, *args, **kwargs)
    return wrap

# Helper para obter dados do usuário da sessão
def get_user_data(request):
    if request.session.get('is_authenticated'):
        return {
            'userid': request.session.get('user_id'),
            'email': request.session.get('email'),
            'user_name': request.session.get('user_name'),
            'user_type_id': request.session.get('user_type_id'),
            'user_type': request.session.get('user_type'),
            'is_authenticated': True
        }
    return None

# Member Views
@custom_login_required
def member_home(request):
    user_data = get_user_data(request)
    recent_checkins = month_classes_frequented = total_hours = 0
    next_payment = ""
    payment_price = ""
    schedule_classes = []
    available_classes = []
    is_booking = False
    
    try:
        # Buscar estatísticas usando model
        stats = MemberStatsMonth.objects.filter(userid=user_data['userid']).first()
        if stats:
            recent_checkins = stats.checkin_count or 0
            month_classes_frequented = stats.class_bookings or 0
            total_hours = round(stats.total_hours or 0)
            next_payment = stats.next_payment if stats.next_payment else "Pagamento em dia"
            payment_price = f"{round(stats.payment_price, 2)}€" if stats.next_payment and stats.payment_price else "0.00€"

        # Buscar aulas agendadas usando model
        schedule_classes_data = MemberScheduleClasses.objects.filter(userid=user_data['userid'])
        schedule_classes = list(schedule_classes_data.values(
            'class_name', 'date', 'starttime', 'endtime', 'room', 'instructor_name'
        ))

        # Buscar aulas disponíveis usando raw query (mais complexa)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT classscheduleid, class_name, date, starttime, endtime, room, instructor_name, available_spots
                FROM vw_member_available_classes vac
                WHERE NOT EXISTS (
                    SELECT 1 FROM classbooking cb 
                    WHERE cb.classscheduleid = vac.classscheduleid 
                    AND cb.memberid = (SELECT memberid FROM member WHERE userid = %s)
                )
            """, [user_data['userid']])

            available_classes_raw = cursor.fetchall()
            available_classes = []
            for row in available_classes_raw:
                available_classes.append({
                    'classscheduleid': row[0],
                    'class_name': row[1],
                    'date': row[2],
                    'starttime': row[3],
                    'endtime': row[4],
                    'room': row[5],
                    'instructor_name': row[6],
                    'available_spots': row[7]
                })

    except Exception as e:
        messages.error(request, f'Erro ao carregar dados: {str(e)}')
    
    if request.method == 'POST':
        is_booking = True
        classscheduleid = request.POST.get('classscheduleid')
        try:
            with connection.cursor() as cursor:
                cursor.execute("CALL sp_book_class(%s, %s)", [user_data['userid'], classscheduleid])
                messages.success(request, 'Aula reservada com sucesso!')
                return redirect('member_home')
        except Exception as e:
            messages.error(request, f'Erro ao reservar aula: {str(e)}')

    context = {
        'user_data': user_data,
        'member_resume': {
            'recent_checkins': recent_checkins,
            'month_classes_frequented': month_classes_frequented,
            'total_hours': total_hours,
            'next_payment': next_payment,
            'payment_price': payment_price
        },
        'schedule_classes': schedule_classes,
        'available_classes': available_classes,
        'is_booking': is_booking
    }
    return render(request, 'Member/HomePage.html', context)

@custom_login_required
def member_account(request):
    user_data = get_user_data(request)

    if user_data['user_type_id'] != 3:
        messages.error(request, 'Acesso negado. Apenas membros podem aceder à conta de membro.')
        return redirect('login')
    
    try:
        # Using Django ORM with the model
        member_details = MemberAccountDetails.objects.filter(userid=user_data['userid']).first()
        
        # Buscar histórico de pagamentos do membro
        payment_history = MemberPaymentHistory.objects.filter(
            userid=user_data['userid']
        ).order_by('-payment_date')[:10]  # Últimos 10 pagamentos
        
        # Buscar histórico de check-ins do membro
        checkin_history = MemberCheckinHistory.objects.filter(
            userid=user_data['userid']
        ).order_by('-checkin_date', '-entrancetime')[:15]  # Últimos 15 check-ins
    
    except Exception as e:
        member_details = None
        payment_history = []
        checkin_history = []
        messages.error(request, f'Erro ao carregar dados da conta: {str(e)}')
    
    context = {
        'user_data': user_data,
        'member_details': member_details,
        'payment_history': payment_history,
        'checkin_history': checkin_history
    }
    return render(request, 'Member/Account.html', context)

# Instructor Views
@custom_login_required
def instructor_account(request):
    user_data = get_user_data(request)

    if user_data['user_type_id'] != 2:
        messages.error(request, 'Acesso negado. Apenas instrutores podem aceder à conta de instrutor.')
        return redirect('login')

    try:
        # Buscar informações do instrutor usando model
        instructor_info = InstructorInfo.objects.filter(userid=user_data['userid']).first()
        
        # Buscar aulas do instrutor usando model
        classes = InstructorClasses.objects.filter(userid=user_data['userid']).values(
            'classid', 'name', 'room', 'capacity', 'duration_minutes'
        )
        # Garantir que sempre retorna uma lista, mesmo vazia
        classes = list(classes) if classes else []

        # Buscar horário semanal do instrutor
        weekly_schedule = InstructorClasses.objects.filter(
            userid=user_data['userid']
        ).exclude(
            classscheduleid__isnull=True
        ).values(
            'name', 'room', 'start_time', 'end_time',
            'day_of_week', 'current_participants', 'max_participants'
        ).order_by('starttime', 'day_of_week')
        
        # Organizar horário por slots de tempo e dias da semana
        schedule_grid = {}
        for schedule in weekly_schedule:
            time_slot = f"{schedule['start_time']}-{schedule['end_time']}"
            if time_slot not in schedule_grid:
                schedule_grid[time_slot] = {}
            
            # day_of_week: 0=Domingo, 1=Segunda, 2=Terça, 3=Quarta, 4=Quinta, 5=Sexta, 6=Sábado
            day_index = schedule['day_of_week']
            schedule_grid[time_slot][day_index] = {
                'name': schedule['name'],
                'room': schedule['room'],
                'current': schedule['current_participants'],
                'max': schedule['max_participants']
            }

        # Buscar estatísticas mensais do instrutor
        monthly_info = InstructorMonthlyStats.objects.filter(userid=user_data['userid']).first()

    except Exception as e:
    
        messages.error(request, f'Erro ao carregar dados: {str(e)}')
    
    context = {
        'user_data': user_data,
        'instructor_info': instructor_info,
        'classes': classes, 
        'monthly_info': monthly_info,
        'schedule_grid': schedule_grid
    }
    return render(request, 'Instructor/Account.html', context)

@custom_login_required
def instructor_class_management(request):
    user_data = get_user_data(request)
    
    # Inicializar variáveis com valores padrão
    today_date = timezone.now().date()
     
    try:
        # Buscar horários das aulas do instrutor usando model
        class_schedules = ClassSchedules.objects.filter(
            userid=user_data['userid']
        ).order_by('date', 'starttime').values(
            'classscheduleid', 'name', 'date', 'starttime', 'endtime', 'maxparticipants', 'room'
        )

        # Garantir que sempre retorna uma lista, mesmo vazia
        class_schedules = list(class_schedules) if class_schedules else []

        dashboard_stats = InstructorDashboardStats.objects.filter(userid=user_data['userid']).first()

        # Garantir que sempre retorna um dicionário, mesmo vazio
        dashboard_stats = dashboard_stats if dashboard_stats else {}

        class_today = InstructorClassesToday.objects.filter(userid=user_data['userid']).order_by('starttime')

        # Garantir que sempre retorna uma lista, mesmo vazia
        class_today = list(class_today) if class_today else []

        # Buscar membros da próxima aula
        next_class_members = InstructorNextClassMembers.objects.filter(instructor_userid=user_data['userid']).order_by('member_name')

        # Garantir que sempre retorna uma lista, mesmo vazia
        next_class_members = list(next_class_members) if next_class_members else []

        # Buscar histórico de aulas da última semana
        class_history = InstructorClassHistory.objects.filter(instructor_userid=user_data['userid']).values(
            'date', 'schedule', 'class_name', 'room', 'enrolled', 'present', 'rate', 'instructorid', 'instructor_userid'
        ).order_by('date', 'schedule')

        # Garantir que sempre retorna uma lista, mesmo vazia
        class_history = list(class_history) if class_history else []

        # Buscar performance semanal do instrutor
        weekly_performance = InstructorWeekPerformance.objects.filter(instructor_userid=user_data['userid']).first()

        # Buscar aulas populares do instrutor (ordenar por ranking crescente: 1º, 2º, 3º...)
        popular_classes = InstructorPopularClasses.objects.filter(instructor_userid=user_data['userid']).order_by('popularity_rank')

        # Garantir que sempre retorna uma lista, mesmo vazia
        popular_classes = list(popular_classes) if popular_classes else []

    except Exception as e:
        messages.error(request, f'Erro ao carregar horários: {str(e)}')
    
    context = {
        'today_date': today_date,
        'user_data': user_data,
        'class_schedules': class_schedules,
        'dashboard_stats': dashboard_stats,
        'class_today': class_today,
        'next_class_members': next_class_members,
        'class_history': class_history,
        'weekly_performance': weekly_performance,
        'popular_classes': popular_classes
    }
    return render(request, 'Instructor/ClassManagement.html', context)

# Manager Views
@custom_login_required
def manager_dashboard(request):
    user_data = get_user_data(request)
    
    try:
        # Buscar estatísticas usando model
        stats = DashboardStats.objects.first()
        if stats:
            total_members = stats.total_members
            total_instructors = stats.total_instructors
            active_memberships = stats.active_memberships
            today_checkins_count = stats.today_checkins
        else:
            total_members = total_instructors = active_memberships = today_checkins_count = 0
    
    except Exception as e:
        total_members = total_instructors = active_memberships = today_checkins_count = 0
        messages.error(request, f'Erro ao carregar estatísticas: {str(e)}')
    
    context = {
        'user_data': user_data,
        'total_members': total_members,
        'total_instructors': total_instructors,
        'active_memberships': active_memberships,
        'today_checkins_count': today_checkins_count
    }
    return render(request, 'Manager/Dashboard.html', context)

@custom_login_required
def manager_members(request):
    user_data = get_user_data(request)

    try:
        members = AllMembers.objects.order_by('-registrationdate').values(
            'memberid', 'name', 'email', 'phone', 'registrationdate', 'isactive',
            'startdate', 'enddate', 'plan_name'
        )
    
    except Exception as e:
        members = []
        messages.error(request, f'Erro ao carregar membros: {str(e)}')
    
    context = {
        'user_data': user_data,
        'members': list(members)
    }
    return render(request, 'Manager/Members.html', context)

@custom_login_required
def manager_classes(request):
    user_data = get_user_data(request)
    
    try:
        classes = AllClasses.objects.order_by('date', 'starttime').values(
            'classscheduleid', 'name', 'instructor_name', 'date', 'starttime', 'endtime', 'room', 'maxparticipants'
        )
    
    except Exception as e:
        classes = []
        messages.error(request, f'Erro ao carregar aulas: {str(e)}')
    
    context = {
        'user_data': user_data,
        'classes': list(classes)
    }
    return render(request, 'Manager/Classes.html', context)

@custom_login_required
def manager_checkins(request):
    user_data = get_user_data(request)
    
    if user_data['user_type_id'] != 1:
        messages.error(request, 'Acesso negado.')
        return redirect('login')
    
    try:
        checkins = AllCheckins.objects.order_by('-date', '-entrancetime').values(
            'checkinid', 'name', 'date', 'entrancetime', 'exittime'
        )[:100]  # Limitar a 100 registros
    
    except Exception as e:
        checkins = []
        messages.error(request, f'Erro ao carregar check-ins: {str(e)}')
    
    context = {
        'user_data': user_data,
        'checkins': list(checkins)
    }
    return render(request, 'Manager/Check-ins.html', context)

@custom_login_required
def manager_machines(request):
    user_data = get_user_data(request)
    
    try:
        machines = Machines.objects.order_by('name').values(
            'machineid', 'name', 'type', 'manufacturer', 'model', 'status', 'installationdate', 'maintenancedate'
        )
    
    except Exception as e:
        machines = []
        messages.error(request, f'Erro ao carregar máquinas: {str(e)}')
    
    context = {
        'user_data': user_data,
        'machines': list(machines)
    }
    return render(request, 'Manager/Machines.html', context)

@custom_login_required
def manager_payments(request):
    user_data = get_user_data(request)
    
    try:
        payments = Payments.objects.order_by('-duedate').values(
            'paymentid', 'member_name', 'plan_name', 'amount', 'duedate', 'paymentdate', 'ispayed', 'paymentmethod'
        )
    
    except Exception as e:
        payments = []
        messages.error(request, f'Erro ao carregar pagamentos: {str(e)}')
    
    context = {
        'user_data': user_data,
        'payments': list(payments)
    }
    return render(request, 'Manager/Payments.html', context)

@custom_login_required
def manager_plans(request):
    user_data = get_user_data(request)
    
    try:
        plans = Plans.objects.order_by('monthlyprice').values(
            'planid', 'name', 'monthlyprice', 'access24h', 'description', 'isactive'
        )
    
    except Exception as e:
        plans = []
        messages.error(request, f'Erro ao carregar planos: {str(e)}')
    
    context = {
        'user_data': user_data,
        'plans': list(plans)
    }
    return render(request, 'Manager/Plans.html', context)
