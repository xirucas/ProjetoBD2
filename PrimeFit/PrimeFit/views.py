from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db import connection
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from .models import (
    PlanDetails, UserAuthentication, Plan, EmailExists, MemberStatsMonth, 
    MemberScheduleClasses, MemberAccountDetails, MemberData, Plan, PlanTable,
    InstructorInfo, InstructorClasses, ClassSchedules, DashboardStats, ManagerClassSchedule,
    MemberPaymentHistory, MemberCheckinHistory, InstructorMonthlyStats, InstructorDailyDashboard, InstructorClassesToday, InstructorNextClassMembers, InstructorClassHistory, InstructorWeekPerformance, InstructorPopularClasses,
    ManagerMembersManagement, ManagerScheduleFilters, ExistingClasses, ClassEnrolledMembers,
    ClassesForMember, AllMembers, AllClasses, MemberAvailableClasses, RoomConflictCheck, InstructorConflictCheck,
    MachineSummary, MachineInventory, MachineCategories, MachineBrands, MachineStatuses, MachineDetail,
    PaymentDashboardSummary, PaymentRecentTransactions, PaymentHistory, PaymentMonthlySummary, TotalActiveMembers, PlanStatistics
)

# Helper functions for conflict checking
def check_room_conflict(room, date, start_time, end_time, exclude_schedule_id=None):
    """Check if there's a room scheduling conflict"""
    with connection.cursor() as cursor:
        if exclude_schedule_id:
            cursor.execute("SELECT fn_check_room_conflict(%s, %s, %s, %s, %s)", 
                         [room, date, start_time, end_time, exclude_schedule_id])
        else:
            cursor.execute("SELECT fn_check_room_conflict(%s, %s, %s, %s)", 
                         [room, date, start_time, end_time])
        return cursor.fetchone()[0]

def check_instructor_conflict(instructor_id, date, start_time, end_time, exclude_schedule_id=None):
    """Check if there's an instructor scheduling conflict"""
    with connection.cursor() as cursor:
        if exclude_schedule_id:
            cursor.execute("SELECT fn_check_instructor_conflict(%s, %s, %s, %s, %s)", 
                         [instructor_id, date, start_time, end_time, exclude_schedule_id])
        else:
            cursor.execute("SELECT fn_check_instructor_conflict(%s, %s, %s, %s)", 
                         [instructor_id, date, start_time, end_time])
        return cursor.fetchone()[0]

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

        # Buscar aulas disponíveis usando o modelo da view
        # Primeiro obter o memberid do usuário
        with connection.cursor() as cursor:
            cursor.execute("SELECT memberid FROM member WHERE userid = %s", [user_data['userid']])
            member_result = cursor.fetchone()
            member_id = member_result[0] if member_result else None

        if member_id:
            # Buscar todas as aulas disponíveis
            all_available = MemberAvailableClasses.objects.all()
            
            # Filtrar aulas onde o membro já não está inscrito
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT classscheduleid FROM classbooking WHERE memberid = %s
                """, [member_id])
                enrolled_classes = [row[0] for row in cursor.fetchall()]
            
            # Converter para lista excluindo aulas já inscritas
            available_classes = []
            for class_item in all_available:
                if class_item.classscheduleid not in enrolled_classes:
                    available_classes.append({
                        'classscheduleid': class_item.classscheduleid,
                        'class_name': class_item.class_name,
                        'date': class_item.date,
                        'starttime': class_item.starttime,
                        'endtime': class_item.endtime,
                        'room': class_item.room,
                        'instructor_name': class_item.instructor_name,
                        'available_spots': class_item.available_spots
                    })
        else:
            available_classes = []

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

        dashboard_stats = InstructorDailyDashboard.objects.filter(userid=user_data['userid']).first()

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
        # Obter todos os membros com ordenação consistente
        members_queryset = ManagerMembersManagement.objects.all().order_by('memberid')

        plans = Plan.objects.all()

        # Aplicar filtros se houver
        search_query = request.GET.get('search', '')
        status_filter = request.GET.get('status', 'todos')
        plan_filter = request.GET.get('plan', 'todos')
        
        if search_query:
            members_queryset = members_queryset.filter(
                member_name__icontains=search_query
            ) | members_queryset.filter(
                email__icontains=search_query
            ) | members_queryset.filter(
                member_phone__icontains=search_query
            )

        if status_filter and status_filter != 'todos':
            members_queryset = members_queryset.filter(status__iexact=status_filter)
            
        if plan_filter and plan_filter != 'todos':
            members_queryset = members_queryset.filter(plan_name=plan_filter)
        
        # Configurar paginação - 10 membros por página
        paginator = Paginator(members_queryset, 10)
        page_number = request.GET.get('page')
        
        try:
            members = paginator.page(page_number)
        except PageNotAnInteger:
            # Se a página não for um número inteiro, mostrar a primeira página
            members = paginator.page(1)
        except EmptyPage:
            # Se a página estiver fora do intervalo, mostrar a última página
            members = paginator.page(paginator.num_pages)

    except Exception as e:
        messages.error(request, f'Erro ao carregar membros: {str(e)}')
        members = []
    
    context = {
        'plans': plans,
        'user_data': user_data,
        'members': members,
        'search_query': search_query,
        'status_filter': status_filter,
        'plan_filter': plan_filter,
        'total_members': members_queryset.count() if 'members_queryset' in locals() else 0
    }
    return render(request, 'Manager/Members.html', context)

@custom_login_required
def manager_member_detail(request, member_id=None):
    """
    View única para criar, visualizar e editar membros
    - GET sem member_id: Formulário de criação
    - GET com member_id: Visualização/Edição do membro
    - POST sem member_id: Criar novo membro
    - POST com member_id: Atualizar membro existente
    """
    user_data = get_user_data(request)
    member = None
    is_edit_mode = request.GET.get('edit') == 'true'
    
    # Carregar planos disponíveis
    try:
        plans = Plan.objects.all()
    except Exception as e:
        plans = []
        messages.error(request, f'Erro ao carregar planos: {str(e)}')
    
    # Se tem member_id, buscar o membro
    if member_id:
        try:
            member = ManagerMembersManagement.objects.get(memberid=member_id)
        except ManagerMembersManagement.DoesNotExist:
            messages.error(request, 'Membro não encontrado.')
            return redirect('manager_members')
    
    if request.method == 'POST':
        # Obter dados do formulário
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        nif = request.POST.get('nif', '').strip()
        phone = request.POST.get('phone', '').strip()
        iban = request.POST.get('iban', '').strip()
        birth_date = request.POST.get('birthdate', '')
        gender = request.POST.get('gender', '')
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        postal_code = request.POST.get('postalcode', '').strip()
        plan_id = request.POST.get('plan', '')
        
        # Validações básicas
        if not name or not email:
            messages.error(request, 'Nome e email são obrigatórios.')
            return render(request, 'Manager/MemberDetail.html', {
                'user_data': user_data,
                'member': member,
                'plans': plans,
                'is_edit_mode': True,
            })
        
        try:
            if member_id:
                # ATUALIZAR MEMBRO EXISTENTE
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_update_member(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [member_id, name, email, nif, phone, iban, birth_date, gender, address, city, postal_code, plan_id])
                
                messages.success(request, 'Membro atualizado com sucesso!')
                return redirect('manager_member_detail', member_id=member_id)
            
            else:
                # CRIAR NOVO MEMBRO
                password = request.POST.get('password', '')
                if not password:
                    messages.error(request, 'Password é obrigatória para novos membros.')
                    return render(request, 'Manager/MemberDetail.html', {
                        'user_data': user_data,
                        'member': None,
                        'plans': plans,
                        'is_edit_mode': True,
                    })
                
                # Verificar se email já existe
                if EmailExists.objects.filter(email=email).exists():
                    messages.error(request, 'Este email já está registado.')
                    return render(request, 'Manager/MemberDetail.html', {
                        'user_data': user_data,
                        'member': None,
                        'plans': plans,
                        'is_edit_mode': True,
                    })
                
                # Criar membro
                hashed_password = make_password(password)
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_create_member(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [name, hashed_password, nif, email, phone, iban, birth_date, gender, address, city, postal_code, plan_id])
                
                messages.success(request, 'Membro criado com sucesso!')
                return redirect('manager_members')
                
        except Exception as e:
            messages.error(request, f'Erro ao salvar membro: {str(e)}')
    
    context = {
        'user_data': user_data,
        'member': member,
        'plans': plans,
        'is_edit_mode': is_edit_mode or not member_id,  # Sempre em modo edição para novos membros
        'is_new': not member_id,
    }
    
    return render(request, 'Manager/MemberDetail.html', context)

@custom_login_required
def manager_classes(request):
    from datetime import datetime
    user_data = get_user_data(request)
    
    try:
        # Data padrão (hoje)
        selected_date_str = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        
        # Converter string para objeto date se necessário
        if isinstance(selected_date_str, str):
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        else:
            selected_date = selected_date_str
            
        selected_instructor = request.GET.get('instructor', '')
        selected_room = request.GET.get('room', '')
        
        # Buscar aulas usando o model ManagerClassSchedule
        classes_queryset = ManagerClassSchedule.objects.filter(class_date=selected_date)
        
        # Aplicar filtros se fornecidos
        if selected_instructor:
            classes_queryset = classes_queryset.filter(instructorid=selected_instructor)
            
        if selected_room:
            classes_queryset = classes_queryset.filter(room=selected_room)
        
        # Ordenar por horário e sala
        classes_queryset = classes_queryset.order_by('starttime', 'room')
        
        # Converter para lista de dicionários para manter compatibilidade com o template
        classes = list(classes_queryset.values(
            'classscheduleid', 'class_date', 'class_name', 'room', 'classid', 
            'instructorid', 'instructor_name', 'starttime', 'endtime', 
            'start_time', 'end_time', 'start_hour', 'start_minute',
            'max_capacity', 'enrolled_count', 'class_status', 'occupation_percentage'
        ))
        
        # Buscar dados para os filtros usando o model
        filters_queryset = ManagerScheduleFilters.objects.all()
        instructors = filters_queryset.filter(filter_type='instructor')
        rooms = filters_queryset.filter(filter_type='room')

    except Exception as e:
        classes = []
        instructors = []
        rooms = []
        # Preservar os valores dos filtros mesmo em caso de erro
        selected_date_str = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except:
            selected_date = timezone.now().date()
            selected_date_str = selected_date.strftime('%Y-%m-%d')
        selected_instructor = request.GET.get('instructor', '')
        selected_room = request.GET.get('room', '')
        messages.error(request, f'Erro ao carregar aulas: {str(e)}')
    
    context = {
        'user_data': user_data,
        'classes': classes,
        'instructors': list(instructors),
        'rooms': list(rooms),
        'selected_date': selected_date,
        'selected_date_str': selected_date_str,
        'selected_instructor': selected_instructor,
        'selected_room': selected_room,
    }
    return render(request, 'Manager/Classes.html', context)

@custom_login_required
def manager_machines(request):  
    user_data = get_user_data(request)
    
    try:
        # Obter estatísticas resumo das máquinas
        machine_summary = MachineSummary.objects.first()
        
        # Obter todas as máquinas com ordenação consistente
        machines_queryset = MachineInventory.objects.all().order_by('machineid')
        
        # Obter categorias e status únicos para filtros
        categories = MachineInventory.objects.values_list('categoria', flat=True).distinct().order_by('categoria')
        statuses = MachineInventory.objects.values_list('status', flat=True).distinct().order_by('status')
        
        # Aplicar filtros se houver
        search_query = request.GET.get('search', '')
        category_filter = request.GET.get('category', 'todos')
        status_filter = request.GET.get('status', 'todos')
        
        # Por enquanto, não aplicar nenhum filtro para debug
        if search_query:
            machines_queryset = machines_queryset.filter(
                 nome__icontains=search_query
            ) | machines_queryset.filter(
                 codigo__icontains=search_query
            ) | machines_queryset.filter(
                 marca__icontains=search_query
            ) | machines_queryset.filter(
                 modelo__icontains=search_query
            )
        
        if category_filter != 'todos':
            machines_queryset = machines_queryset.filter(categoria__iexact=category_filter)
            
        # Testar apenas o filtro de status primeiro com comparação direta
        if status_filter != 'todos':
            machines_queryset = machines_queryset.filter(status=status_filter)
        
        # Configurar paginação - 10 máquinas por página
        paginator = Paginator(machines_queryset, 10)
        page_number = request.GET.get('page')
        
        try:
            machines = paginator.page(page_number)
        except PageNotAnInteger:
            # Se a página não for um número inteiro, mostrar a primeira página
            machines = paginator.page(1)
        except EmptyPage:
            # Se a página estiver fora do intervalo, mostrar a última página
            machines = paginator.page(paginator.num_pages)

    except Exception as e:
        machine_summary = None
        machines = []
        categories = []
        statuses = []
        search_query = ''
        category_filter = 'todos'
        status_filter = 'todos'
        messages.error(request, f'Erro ao carregar máquinas: {str(e)}')
    
    context = {
        'user_data': user_data,
        'machine_summary': machine_summary,
        'machines': machines,
        'categories': categories,
        'statuses': statuses,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'total_machines': machines_queryset.count() if 'machines_queryset' in locals() else 0
    }
    return render(request, 'Manager/Machines.html', context)

@custom_login_required
def manager_machine_detail(request, machine_id=None):
    """
    View única para criar, visualizar e editar máquinas
    - GET sem machine_id: Formulário de criação
    - GET com machine_id: Visualização/Edição da máquina
    - POST sem machine_id: Criar nova máquina
    - POST com machine_id: Atualizar máquina existente
    """
    user_data = get_user_data(request)
    machine = None
    is_edit_mode = request.GET.get('edit') == 'true'
    
    # Obter dados para dropdowns usando models
    try:
        categories = list(MachineCategories.objects.all().values_list('categoria', flat=True))
        brands = list(MachineBrands.objects.all().values_list('marca', flat=True))
        statuses = list(MachineStatuses.objects.all().values('machinestatusid', 'status'))
    except Exception as e:
        categories = []
        brands = []
        statuses = []
        messages.error(request, f'Erro ao carregar dados: {str(e)}')
    
    # Se tem machine_id, buscar a máquina
    if machine_id:
        try:
            machine = MachineDetail.objects.get(machineid=machine_id)
        except MachineDetail.DoesNotExist:
            messages.error(request, 'Máquina não encontrada.')
            return redirect('manager_machines')
    
    if request.method == 'POST':
        # Obter dados do formulário
        nome = request.POST.get('nome', '').strip()
        codigo = request.POST.get('codigo', '').strip()
        categoria = request.POST.get('categoria', '').strip()
        new_categoria = request.POST.get('new_categoria', '').strip()
        marca = request.POST.get('marca', '').strip()
        new_marca = request.POST.get('new_marca', '').strip()
        modelo = request.POST.get('modelo', '').strip()
        data_aquisicao = request.POST.get('data_aquisicao', '')
        status_id = request.POST.get('status_id', '')
        
        # Usar nova categoria se fornecida
        final_categoria = new_categoria if new_categoria else categoria
        final_marca = new_marca if new_marca else marca
        
        # Validações básicas
        if not nome or not codigo:
            messages.error(request, 'Nome e código são obrigatórios.')
            return render(request, 'Manager/MachineDetail.html', {
                'user_data': user_data,
                'machine': machine,
                'categories': categories,
                'brands': brands,
                'statuses': statuses,
                'is_edit_mode': True,
            })
        
        try:
            if machine_id:
                # ATUALIZAR MÁQUINA EXISTENTE usando procedimento
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_update_machine(%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [machine_id, nome, codigo, final_categoria, final_marca, modelo, data_aquisicao, status_id])
                
                messages.success(request, 'Máquina atualizada com sucesso!')
                return redirect('manager_machine_detail', machine_id=machine_id)
            
            else:
                # CRIAR NOVA MÁQUINA usando procedimento
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_create_machine(%s, %s, %s, %s, %s, %s, %s)
                    """, [nome, codigo, final_categoria, final_marca, modelo, data_aquisicao, status_id or 1])
                
                messages.success(request, 'Máquina criada com sucesso!')
                return redirect('manager_machines')
                
        except Exception as e:
            messages.error(request, f'Erro ao salvar máquina: {str(e)}')
    
    context = {
        'user_data': user_data,
        'machine': machine,
        'categories': categories,
        'brands': brands,
        'statuses': statuses,
        'is_edit_mode': is_edit_mode or not machine_id,  # Sempre em modo edição para novas máquinas
        'is_new': not machine_id,
    }
    
    return render(request, 'Manager/MachineDetail.html', context)

@custom_login_required
def manager_machine_change_status(request, machine_id):
    """Alterar status de uma máquina usando procedimento"""
    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        maintenance_date = request.POST.get('maintenance_date', None)
        
        try:
            # Usar procedimento para alterar status
            with connection.cursor() as cursor:
                if new_status == '2' and maintenance_date:  # Em manutenção
                    cursor.execute("""
                        CALL sp_change_machine_status(%s, %s, %s)
                    """, [machine_id, new_status, maintenance_date])
                else:
                    cursor.execute("""
                        CALL sp_change_machine_status(%s, %s)
                    """, [machine_id, new_status])
            
            messages.success(request, 'Status da máquina atualizado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar status: {str(e)}')
    
    return redirect('manager_machines')

@custom_login_required
def manager_plans(request):
    user_data = get_user_data(request)

    dashboard_stats = PlanStatistics.objects.all()
    total_active_members = TotalActiveMembers.objects.first()
    plan_details = PlanDetails.objects.all()

    context = {
        'user_data': user_data,
        'dashboard_stats': dashboard_stats,
        'total_active_members': total_active_members,
        'plan_details': plan_details,
    }

    return render(request, 'Manager/Plans.html', context)

@custom_login_required
def manager_plan_edit(request, plan_id):
    """Editar um plano específico"""
    user_data = get_user_data(request)
    
    try:
        # Buscar o plano na tabela real
        plan = PlanTable.objects.get(planid=plan_id, isactive=True)
        
        # Buscar estatísticas do plano
        try:
            plan_stats = PlanStatistics.objects.get(planid=plan_id)
        except PlanStatistics.DoesNotExist:
            plan_stats = None
            
    except PlanTable.DoesNotExist:
        messages.error(request, 'Plano não encontrado.')
        return redirect('manager_plans')
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            monthlyprice = request.POST.get('monthlyprice', '')
            description = request.POST.get('description', '').strip()
            access24h = request.POST.get('access24h') == 'on'
            
            # Validações
            if not name:
                messages.error(request, 'Nome do plano é obrigatório.')
                return render(request, 'Manager/PlanEdit.html', {
                    'user_data': user_data,
                    'plan': plan,
                    'plan_stats': plan_stats,
                })
            
            if not monthlyprice:
                messages.error(request, 'Preço mensal é obrigatório.')
                return render(request, 'Manager/PlanEdit.html', {
                    'user_data': user_data,
                    'plan': plan,
                    'plan_stats': plan_stats,
                })
            
            try:
                monthlyprice = float(monthlyprice)
                if monthlyprice < 0:
                    raise ValueError("Preço não pode ser negativo")
            except ValueError:
                messages.error(request, 'Preço mensal deve ser um valor válido maior ou igual a zero.')
                return render(request, 'Manager/PlanEdit.html', {
                    'user_data': user_data,
                    'plan': plan,
                    'plan_stats': plan_stats,
                })
            
            # Limitar tamanhos
            if len(name) > 80:
                messages.error(request, 'Nome do plano não pode ter mais de 80 caracteres.')
                return render(request, 'Manager/PlanEdit.html', {
                    'user_data': user_data,
                    'plan': plan,
                    'plan_stats': plan_stats,
                })
            
            if description and len(description) > 500:
                description = description[:500]
            
            # Usar stored procedure para atualizar
            with connection.cursor() as cursor:
                cursor.execute("""
                    CALL sp_update_plan(%s, %s, %s, %s, %s)
                """, [plan_id, name, monthlyprice, description or None, access24h])
            
            messages.success(request, 'Plano atualizado com sucesso!')
            return redirect('manager_plans')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar plano: {str(e)}')
            return render(request, 'Manager/PlanEdit.html', {
                'user_data': user_data,
                'plan': plan,
                'plan_stats': plan_stats,
            })
    
    # GET request
    context = {
        'user_data': user_data,
        'plan': plan,
        'plan_stats': plan_stats,
    }
    
    return render(request, 'Manager/PlanEdit.html', context)

@custom_login_required
def manager_class_new(request):
    """Criar nova marcação de aula"""
    user_data = get_user_data(request)
    
    if request.method == 'POST':
        try:
            # Dados do formulário
            class_id = request.POST.get('class_id')
            new_class_name = request.POST.get('new_class_name', '').strip()
            instructor_id = request.POST.get('instructor_id')
            room = request.POST.get('room')
            new_room = request.POST.get('new_room', '').strip()
            date = request.POST.get('date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            max_participants = request.POST.get('max_participants')
            duration_minutes = request.POST.get('duration_minutes', 60)
            
            # Validações básicas
            if not instructor_id:
                messages.error(request, 'Instrutor é obrigatório.')
                return redirect('manager_class_new')
            
            if not date or not start_time or not end_time:
                messages.error(request, 'Data, hora de início e fim são obrigatórios.')
                return redirect('manager_class_new')
            
            if not max_participants:
                messages.error(request, 'Número máximo de participantes é obrigatório.')
                return redirect('manager_class_new')
            
            # Determinar sala (existente ou nova)
            final_room = new_room if new_room else room
            if not final_room:
                messages.error(request, 'Sala é obrigatória.')
                return redirect('manager_class_new')
            
            with connection.cursor() as cursor:
                # Usar função helper para verificar conflito de sala
                if check_room_conflict(final_room, date, start_time, end_time):
                    messages.error(request, 'Já existe uma aula agendada nesta sala e horário.')
                    return redirect('manager_class_new')
                
                # Usar função helper para verificar conflito de instrutor
                if check_instructor_conflict(instructor_id, date, start_time, end_time):
                    messages.error(request, 'O instrutor já tem uma aula agendada neste horário.')
                    return redirect('manager_class_new')
                
                # Criar ou usar aula existente
                if class_id and class_id != 'new':
                    # Usar aula existente - criar apenas o agendamento
                    cursor.execute("""
                        CALL sp_schedule_class(%s, %s, %s, %s, %s, NULL)
                    """, [class_id, date, start_time, end_time, max_participants])
                else:
                    # Criar nova aula e agendamento em uma operação
                    if not new_class_name:
                        messages.error(request, 'Nome da aula é obrigatório ao criar nova aula.')
                        return redirect('manager_class_new')
                    
                    cursor.execute("""
                        CALL sp_create_and_schedule_class(%s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
                    """, [new_class_name, instructor_id, final_room, max_participants, 
                          duration_minutes, date, start_time, end_time, max_participants])
                
                messages.success(request, 'Aula agendada com sucesso!')
                return redirect('manager_classes')
                
        except Exception as e:
            messages.error(request, f'Erro ao criar aula: {str(e)}')
            return redirect('manager_class_new')
    
    # GET request - mostrar formulário
    try:
        # Buscar aulas existentes usando a view
        existing_classes = list(ExistingClasses.objects.all().values(
            'classid', 'name', 'room', 'duration_minutes'
        ))
        
        # Buscar instrutores ativos usando a view existente
        instructors = ManagerScheduleFilters.objects.filter(filter_type='instructor')
        
        # Buscar salas existentes usando a view existente
        rooms = ManagerScheduleFilters.objects.filter(filter_type='room')
        
    except Exception as e:
        existing_classes = []
        instructors = []
        rooms = []
        messages.error(request, f'Erro ao carregar dados: {str(e)}')
    
    context = {
        'user_data': user_data,
        'existing_classes': existing_classes,
        'instructors': list(instructors),
        'rooms': list(rooms),
    }
    return render(request, 'Manager/ClassNew.html', context)

@custom_login_required  
def manager_class_view(request, class_id):
    """Ver detalhes de uma aula agendada"""
    user_data = get_user_data(request)
    
    try:
        # Buscar detalhes da aula agendada
        class_details = ManagerClassSchedule.objects.get(classscheduleid=class_id)
        
        # Buscar membros inscritos usando a view
        enrolled_members = ClassEnrolledMembers.objects.filter(
            classscheduleid=class_id
        ).values(
            'member_name', 'memberid', 'email', 'phone', 'plan_name', 'bookingdate'
        ).order_by('bookingdate')
        
        # Converter para lista para compatibilidade com o template
        enrolled_members = list(enrolled_members)
        
    except ManagerClassSchedule.DoesNotExist:
        messages.error(request, 'Aula não encontrada.')
        return redirect('manager_classes')
    except Exception as e:
        messages.error(request, f'Erro ao carregar detalhes da aula: {str(e)}')
        return redirect('manager_classes')
    
    context = {
        'user_data': user_data,
        'class_details': class_details,
        'enrolled_members': enrolled_members,
    }
    return render(request, 'Manager/ClassView.html', context)

@custom_login_required
def manager_class_edit(request, class_id):
    """Editar uma aula agendada"""
    user_data = get_user_data(request)
    
    try:
        class_details = ManagerClassSchedule.objects.get(classscheduleid=class_id)
    except ManagerClassSchedule.DoesNotExist:
        messages.error(request, 'Aula não encontrada.')
        return redirect('manager_classes')
    
    if request.method == 'POST':
        try:
            # Dados do formulário
            date = request.POST.get('date')
            start_time = request.POST.get('start_time')  
            end_time = request.POST.get('end_time')
            max_participants = request.POST.get('max_participants')
            
            # Validações
            if not date or not start_time or not end_time or not max_participants:
                messages.error(request, 'Todos os campos são obrigatórios.')
                return redirect('manager_class_edit', class_id=class_id)
            
            with connection.cursor() as cursor:
                # Usar função helper para verificar conflito de sala (excluindo aula atual)
                if check_room_conflict(class_details.room, date, start_time, end_time, class_id):
                    messages.error(request, 'Já existe uma aula agendada nesta sala e horário.')
                    return redirect('manager_class_edit', class_id=class_id)
                
                # Usar função helper para verificar conflito de instrutor (excluindo aula atual)
                if check_instructor_conflict(class_details.instructorid, date, start_time, end_time, class_id):
                    messages.error(request, 'O instrutor já tem uma aula agendada neste horário.')
                    return redirect('manager_class_edit', class_id=class_id)
                
                # Usar stored procedure para atualizar aula
                cursor.execute("""
                    CALL sp_update_class_schedule(%s, %s, %s, %s, %s)
                """, [class_id, date, start_time, end_time, max_participants])
                
                messages.success(request, 'Aula atualizada com sucesso!')
                return redirect('manager_classes')
                
        except Exception as e:
            messages.error(request, f'Erro ao atualizar aula: {str(e)}')
            return redirect('manager_class_edit', class_id=class_id)
    
    # GET request
    context = {
        'user_data': user_data,
        'class_details': class_details,
    }
    return render(request, 'Manager/ClassEdit.html', context)


@custom_login_required
def manager_payments(request):
    user_data = get_user_data(request)
    
    # Inicializar filtros fora do try para evitar UnboundLocalError
    status_filter = request.GET.get('status', '')
    plano_filter = request.GET.get('plano', '')
    search_query = request.GET.get('search', '')
    
    # Filtros de data - definir valores padrão para o mês atual
    from datetime import date
    today = date.today()
    first_day_current_month = date(today.year, today.month, 1)
    
    # Se é o último dia do mês, usar o dia atual, senão usar o último dia do mês
    import calendar
    last_day_current_month = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    
    data_inicio_str = request.GET.get('data_inicio', first_day_current_month.strftime('%Y-%m-%d'))
    data_fim_str = request.GET.get('data_fim', last_day_current_month.strftime('%Y-%m-%d'))
    
    # Converter strings para objetos date
    try:
        data_inicio = date.fromisoformat(data_inicio_str) if data_inicio_str else first_day_current_month
        data_fim = date.fromisoformat(data_fim_str) if data_fim_str else last_day_current_month
    except ValueError:
        data_inicio = first_day_current_month
        data_fim = last_day_current_month

    try:
        # 1. Resumo dos 4 quadrados superiores
        dashboard_summary = PaymentDashboardSummary.objects.first()
        if not dashboard_summary:
            # Fallback caso não haja dados
            dashboard_summary = {
                'receita_mensal': 0,
                'pagamentos_hoje': 0,
                'transacoes_hoje': 0,
                'pendentes': 0,
                'pagamentos_pendentes': 0,
                'em_atraso': 0,
                'pagamentos_em_atraso': 0
            }
        
        # 2. Últimos 3 pagamentos recentes (hoje)
        recent_transactions = PaymentRecentTransactions.objects.all()[:3]
        
        # 3. Histórico de pagamentos com filtros
        # Base queryset
        payment_history = PaymentHistory.objects.all()
        
        # Aplicar filtros
        if status_filter and status_filter != 'Todos os Status':
            payment_history = payment_history.filter(status=status_filter)
        
        if plano_filter and plano_filter != 'Todos os Planos':
            payment_history = payment_history.filter(plano=plano_filter)
        
        if search_query:
            payment_history = payment_history.filter(nome_membro__icontains=search_query)
        
        # Filtrar por intervalo de datas (usar data_vencimento como referência)
        payment_history = payment_history.filter(
            data_vencimento__gte=data_inicio,
            data_vencimento__lte=data_fim
        )
        
        # Paginação
        paginator = Paginator(payment_history, 10)  # 10 pagamentos por página
        page = request.GET.get('page')
        try:
            payments_page = paginator.page(page)
        except PageNotAnInteger:
            payments_page = paginator.page(1)
        except EmptyPage:
            payments_page = paginator.page(paginator.num_pages)
        
        # 4. Resumo mensal para quadrados inferiores
        monthly_summary = PaymentMonthlySummary.objects.first()
        if not monthly_summary:
            # Fallback caso não haja dados
            monthly_summary = {
                'total_faturado': 0,
                'total_recebido': 0,
                'pendentes': 0,
                'em_atraso': 0,
                'metodos_pagamento': 'Sem dados disponíveis'
            }
        
        # 5. Opções para filtros (dinâmicas)
        status_options = ['Todos os Status'] + list(
            PaymentHistory.objects.values_list('status', flat=True).distinct()
        )
        plano_options = ['Todos os Planos'] + list(
            PaymentHistory.objects.values_list('plano', flat=True).distinct()
        )

    except Exception as e:
        print(f"ERRO na função manager_payments: {str(e)}")
        messages.error(request, f'Erro ao carregar dados de pagamentos: {str(e)}')
        # Inicializar valores padrão em caso de erro
        dashboard_summary = {
            'receita_mensal': 0,
            'pagamentos_hoje': 0,
            'transacoes_hoje': 0,
            'pendentes': 0,
            'pagamentos_pendentes': 0,
            'em_atraso': 0,
            'pagamentos_em_atraso': 0
        }
        recent_transactions = []
        payments_page = []
        monthly_summary = {
            'total_faturado': 0,
            'total_recebido': 0,
            'pendentes': 0,
            'em_atraso': 0,
            'metodos_pagamento': 'Sem dados disponíveis'
        }
        status_options = ['Todos os Status']
        plano_options = ['Todos os Planos']
    try:
        data_inicio = date.fromisoformat(data_inicio_str) if data_inicio_str else first_day_current_month
        data_fim = date.fromisoformat(data_fim_str) if data_fim_str else last_day_current_month
    except ValueError:
        data_inicio = first_day_current_month
        data_fim = last_day_current_month

    try:
        # 1. Resumo dos 4 quadrados superiores
        dashboard_summary = PaymentDashboardSummary.objects.first()
        if not dashboard_summary:
            # Fallback caso não haja dados
            dashboard_summary = {
                'receita_mensal': 0,
                'pagamentos_hoje': 0,
                'transacoes_hoje': 0,
                'pendentes': 0,
                'pagamentos_pendentes': 0,
                'em_atraso': 0,
                'pagamentos_em_atraso': 0
            }
        
        # 2. Últimos 3 pagamentos recentes (hoje)
        recent_transactions = PaymentRecentTransactions.objects.all()[:3]
        
        # 3. Histórico de pagamentos com filtros
        # Base queryset
        payment_history = PaymentHistory.objects.all()
        
        # Aplicar filtros
        if status_filter and status_filter != 'Todos os Status':
            payment_history = payment_history.filter(status=status_filter)
        
        if plano_filter and plano_filter != 'Todos os Planos':
            payment_history = payment_history.filter(plano=plano_filter)
        
        if search_query:
            payment_history = payment_history.filter(nome_membro__icontains=search_query)
        
        # Filtrar por intervalo de datas (usar data_vencimento como referência)
        payment_history = payment_history.filter(
            data_vencimento__gte=data_inicio,
            data_vencimento__lte=data_fim
        )
        
        # Paginação
        paginator = Paginator(payment_history, 10)  # 10 pagamentos por página
        page = request.GET.get('page')
        try:
            payments_page = paginator.page(page)
        except PageNotAnInteger:
            payments_page = paginator.page(1)
        except EmptyPage:
            payments_page = paginator.page(paginator.num_pages)
        
        # 4. Resumo mensal para quadrados inferiores
        monthly_summary = PaymentMonthlySummary.objects.first()
        if not monthly_summary:
            # Fallback caso não haja dados
            monthly_summary = {
                'total_faturado': 0,
                'total_recebido': 0,
                'pendentes': 0,
                'em_atraso': 0,
                'metodos_pagamento': 'Sem dados disponíveis'
            }
        
        # 5. Opções para filtros (dinâmicas)
        status_options = ['Todos os Status'] + list(
            PaymentHistory.objects.values_list('status', flat=True).distinct()
        )
        plano_options = ['Todos os Planos'] + list(
            PaymentHistory.objects.values_list('plano', flat=True).distinct()
        )

    except Exception as e:
        messages.error(request, f'Erro ao carregar dados de pagamentos: {str(e)}')

    context = {
        'user_data': user_data,
        'dashboard_summary': dashboard_summary,
        'recent_transactions': recent_transactions,
        'payments_page': payments_page,
        'monthly_summary': monthly_summary,
        'status_options': status_options,
        'plano_options': plano_options,
        'status_filter': status_filter,
        'plano_filter': plano_filter,
        'search_query': search_query,
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d'),
        'data_inicio_obj': data_inicio,
        'data_fim_obj': data_fim,
    }

    return render(request, 'Manager/Payments.html', context)

@custom_login_required    
def manager_payments_export(request):
    """Exportar relatório de pagamentos em formato CSV"""
    
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="relatorio_pagamentos.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID Pagamento', 'Membro', 'ID Membro', 'Plano', 'Valor', 
        'Método Pagamento', 'Data Vencimento', 'Data Pagamento', 'Status'
    ])
    
    # Aplicar os mesmos filtros da interface
    status_filter = request.GET.get('status', '')
    plano_filter = request.GET.get('plano', '')
    search_query = request.GET.get('search', '')
    
    payments = PaymentHistory.objects.all()
    
    if status_filter and status_filter != 'Todos os Status':
        payments = payments.filter(status=status_filter)
    
    if plano_filter and plano_filter != 'Todos os Planos':
        payments = payments.filter(plano=plano_filter)
    
    if search_query:
        payments = payments.filter(nome_membro__icontains=search_query)
    
    for payment in payments:
        writer.writerow([
            payment.paymentid,
            payment.nome_membro,
            payment.id_membro,
            payment.plano,
            payment.valor,
            payment.metodo_pagamento,
            payment.data_vencimento.strftime('%d/%m/%Y') if payment.data_vencimento else '',
            payment.data_pagamento.strftime('%d/%m/%Y') if payment.data_pagamento else '',
            payment.status
        ])
    
    return response
