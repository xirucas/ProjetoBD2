from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password

# Autenticação usando tabela USERS do PostgreSQL
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email e password são obrigatórios.')
            return render(request, 'auth/login.html')
        
        # Verificar credenciais na tabela USERS
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT u.userid, u.email, u.password, u.usertypeid, u.isactive, ut.label
                    FROM users u
                    JOIN usertype ut ON u.usertypeid = ut.usertypeid
                    WHERE u.email = %s AND u.isactive = true
                """, [email])
                
                user_data = cursor.fetchone()
                
                if user_data and check_password(password, user_data[2]):
                    # Criar sessão de usuário
                    request.session['user_id'] = user_data[0]
                    request.session['email'] = user_data[1]
                    request.session['user_type_id'] = user_data[3]
                    request.session['user_type'] = user_data[5]
                    request.session['is_authenticated'] = True
                    
                    # Atualizar last_login
                    cursor.execute("""
                        UPDATE users SET last_login = CURRENT_TIMESTAMP 
                        WHERE userid = %s
                    """, [user_data[0]])
                    
                    # Redirecionar baseado no tipo de usuário
                    if user_data[3] == 1:  # Gestor
                        return redirect('manager_dashboard')
                    elif user_data[3] == 2:  # Instrutor
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
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type', '3')  # Default: Membro
        
        if not email or not password:
            messages.error(request, 'Email e password são obrigatórios.')
            return render(request, 'auth/register.html')
            
        if password != confirm_password:
            messages.error(request, 'As passwords não coincidem.')
            return render(request, 'auth/register.html')
            
        if len(password) < 8:
            messages.error(request, 'A password deve ter pelo menos 8 caracteres.')
            return render(request, 'auth/register.html')
        
        try:
            with connection.cursor() as cursor:
                # Verificar se email já existe
                cursor.execute("SELECT userid FROM users WHERE email = %s", [email])
                if cursor.fetchone():
                    messages.error(request, 'Este email já está registado.')
                    return render(request, 'auth/register.html')
                
                # Criar novo usuário
                hashed_password = make_password(password)
                cursor.execute("""
                    INSERT INTO users (email, password, usertypeid, isactive)
                    VALUES (%s, %s, %s, %s)
                """, [email, hashed_password, user_type, True])
                
                messages.success(request, 'Conta criada com sucesso! Pode fazer login.')
                return redirect('login')
                
        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {str(e)}')
    
    return render(request, 'auth/register.html')

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
            'user_type_id': request.session.get('user_type_id'),
            'user_type': request.session.get('user_type'),
            'is_authenticated': True
        }
    return None

# Member Views
@custom_login_required
def member_home(request):
    user_data = get_user_data(request)
    
    try:
        with connection.cursor() as cursor:
            # Buscar dados do membro
            cursor.execute("""
                SELECT m.memberid, m.name, m.email, m.registrationdate, 
                       ms.subscriptionid, ms.startdate, ms.enddate, ms.isactive as subscription_active,
                       p.name as plan_name, p.monthlyprice
                FROM member m
                LEFT JOIN membersubscription ms ON m.memberid = ms.memberid AND ms.isactive = true
                LEFT JOIN plan p ON ms.planid = p.planid
                WHERE m.userid = %s AND m.isactive = true
            """, [user_data['userid']])
            
            member_info = cursor.fetchone()
            
            # Buscar check-ins recentes
            cursor.execute("""
                SELECT checkinid, date, entrancetime, exittime
                FROM checkin 
                WHERE memberid = (SELECT memberid FROM member WHERE userid = %s)
                ORDER BY date DESC, entrancetime DESC
                LIMIT 5
            """, [user_data['userid']])
            
            recent_checkins = cursor.fetchall()
    
    except Exception as e:
        member_info = None
        recent_checkins = []
        messages.error(request, f'Erro ao carregar dados: {str(e)}')
    
    context = {
        'user_data': user_data,
        'member_info': member_info,
        'recent_checkins': recent_checkins
    }
    return render(request, 'Member/HomePage.html', context)

@custom_login_required
def member_account(request):
    user_data = get_user_data(request)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.memberid, m.name, m.nif, m.email, m.phone, m.iban, m.registrationdate,
                       ms.startdate, ms.enddate, p.name as plan_name, p.monthlyprice, p.access24h
                FROM member m
                LEFT JOIN membersubscription ms ON m.memberid = ms.memberid AND ms.isactive = true
                LEFT JOIN plan p ON ms.planid = p.planid
                WHERE m.userid = %s
            """, [user_data['userid']])
            
            member_details = cursor.fetchone()
    
    except Exception as e:
        member_details = None
        messages.error(request, f'Erro ao carregar dados da conta: {str(e)}')
    
    context = {
        'user_data': user_data,
        'member_details': member_details
    }
    return render(request, 'Member/Account.html', context)

# Instructor Views
@custom_login_required
def instructor_account(request):
    user_data = get_user_data(request)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT i.instructorid, i.name, i.nif, i.email, i.phone, i.isactive
                FROM instructor i
                WHERE i.userid = %s
            """, [user_data['userid']])
            
            instructor_info = cursor.fetchone()
            
            # Buscar aulas do instrutor
            cursor.execute("""
                SELECT c.classid, c.name, c.room, c.capacity, c.duration_minutes
                FROM class c
                WHERE c.instructorid = (SELECT instructorid FROM instructor WHERE userid = %s)
                AND c.isactive = true
            """, [user_data['userid']])
            
            classes = cursor.fetchall()
    
    except Exception as e:
        instructor_info = None
        classes = []
        messages.error(request, f'Erro ao carregar dados: {str(e)}')
    
    context = {
        'user_data': user_data,
        'instructor_info': instructor_info,
        'classes': classes
    }
    return render(request, 'Instructor/Account.html', context)

@custom_login_required
def instructor_class_management(request):
    user_data = get_user_data(request)
    
    try:
        with connection.cursor() as cursor:
            # Buscar horários das aulas do instrutor
            cursor.execute("""
                SELECT cs.classscheduleid, c.name, cs.date, cs.starttime, cs.endtime, 
                       cs.maxparticipants, c.room
                FROM classschedule cs
                JOIN class c ON cs.classid = c.classid
                WHERE c.instructorid = (SELECT instructorid FROM instructor WHERE userid = %s)
                AND cs.isactive = true
                ORDER BY cs.date, cs.starttime
            """, [user_data['userid']])
            
            class_schedules = cursor.fetchall()
    
    except Exception as e:
        class_schedules = []
        messages.error(request, f'Erro ao carregar horários: {str(e)}')
    
    context = {
        'user_data': user_data,
        'class_schedules': class_schedules
    }
    return render(request, 'Instructor/ClassManagement.html', context)

# Manager Views
@custom_login_required
def manager_dashboard(request):
    user_data = get_user_data(request)
    
    # Verificar se é gestor
    if user_data['user_type_id'] != 1:
        messages.error(request, 'Acesso negado. Apenas gestores podem aceder ao dashboard.')
        return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            # Total de membros
            cursor.execute("SELECT COUNT(*) FROM member WHERE isactive = true")
            total_members = cursor.fetchone()[0]
            
            # Total de instrutores
            cursor.execute("SELECT COUNT(*) FROM instructor WHERE isactive = true")
            total_instructors = cursor.fetchone()[0]
            
            # Subscrições ativas
            cursor.execute("SELECT COUNT(*) FROM membersubscription WHERE isactive = true")
            active_memberships = cursor.fetchone()[0]
            
            # Check-ins de hoje
            cursor.execute("""
                SELECT COUNT(*) FROM checkin 
                WHERE date = CURRENT_DATE
            """)
            today_checkins_count = cursor.fetchone()[0]
    
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
    
    if user_data['user_type_id'] != 1:
        messages.error(request, 'Acesso negado.')
        return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.memberid, m.name, m.email, m.phone, m.registrationdate, m.isactive,
                       ms.startdate, ms.enddate, p.name as plan_name
                FROM member m
                LEFT JOIN membersubscription ms ON m.memberid = ms.memberid AND ms.isactive = true
                LEFT JOIN plan p ON ms.planid = p.planid
                ORDER BY m.registrationdate DESC
            """)
            
            members = cursor.fetchall()
    
    except Exception as e:
        members = []
        messages.error(request, f'Erro ao carregar membros: {str(e)}')
    
    context = {
        'user_data': user_data,
        'members': members
    }
    return render(request, 'Manager/Members.html', context)

@custom_login_required
def manager_classes(request):
    user_data = get_user_data(request)
    
    if user_data['user_type_id'] != 1:
        messages.error(request, 'Acesso negado.')
        return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT cs.classscheduleid, c.name, i.name as instructor_name, 
                       cs.date, cs.starttime, cs.endtime, c.room, cs.maxparticipants
                FROM classschedule cs
                JOIN class c ON cs.classid = c.classid
                JOIN instructor i ON c.instructorid = i.instructorid
                WHERE cs.isactive = true
                ORDER BY cs.date, cs.starttime
            """)
            
            classes = cursor.fetchall()
    
    except Exception as e:
        classes = []
        messages.error(request, f'Erro ao carregar aulas: {str(e)}')
    
    context = {
        'user_data': user_data,
        'classes': classes
    }
    return render(request, 'Manager/Classes.html', context)

@custom_login_required
def manager_checkins(request):
    user_data = get_user_data(request)
    
    if user_data['user_type_id'] != 1:
        messages.error(request, 'Acesso negado.')
        return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.checkinid, m.name, c.date, c.entrancetime, c.exittime
                FROM checkin c
                JOIN member m ON c.memberid = m.memberid
                ORDER BY c.date DESC, c.entrancetime DESC
                LIMIT 100
            """)
            
            checkins = cursor.fetchall()
    
    except Exception as e:
        checkins = []
        messages.error(request, f'Erro ao carregar check-ins: {str(e)}')
    
    context = {
        'user_data': user_data,
        'checkins': checkins
    }
    return render(request, 'Manager/Check-ins.html', context)

@custom_login_required
def manager_machines(request):
    user_data = get_user_data(request)
    
    if user_data['user_type_id'] != 1:
        messages.error(request, 'Acesso negado.')
        return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.machineid, m.name, m.type, m.manufacturer, m.model, 
                       ms.status, m.installationdate, m.maintenancedate
                FROM machine m
                JOIN machinestatus ms ON m.machinestatusid = ms.machinestatusid
                ORDER BY m.name
            """)
            
            machines = cursor.fetchall()
    
    except Exception as e:
        machines = []
        messages.error(request, f'Erro ao carregar máquinas: {str(e)}')
    
    context = {
        'user_data': user_data,
        'machines': machines
    }
    return render(request, 'Manager/Machines.html', context)

@custom_login_required
def manager_payments(request):
    user_data = get_user_data(request)
    
    if user_data['user_type_id'] != 1:
        messages.error(request, 'Acesso negado.')
        return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.paymentid, m.name as member_name, pl.name as plan_name,
                       p.amount, p.duedate, p.paymentdate, p.ispayed, p.paymentmethod
                FROM payment p
                JOIN membersubscription ms ON p.subscriptionid = ms.subscriptionid
                JOIN member m ON ms.memberid = m.memberid
                JOIN plan pl ON ms.planid = pl.planid
                ORDER BY p.duedate DESC
            """)
            
            payments = cursor.fetchall()
    
    except Exception as e:
        payments = []
        messages.error(request, f'Erro ao carregar pagamentos: {str(e)}')
    
    context = {
        'user_data': user_data,
        'payments': payments
    }
    return render(request, 'Manager/Payments.html', context)

@custom_login_required
def manager_plans(request):
    user_data = get_user_data(request)
    
    if user_data['user_type_id'] != 1:
        messages.error(request, 'Acesso negado.')
        return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT planid, name, monthlyprice, access24h, description, isactive
                FROM plan
                ORDER BY monthlyprice
            """)
            
            plans = cursor.fetchall()
    
    except Exception as e:
        plans = []
        messages.error(request, f'Erro ao carregar planos: {str(e)}')
    
    context = {
        'user_data': user_data,
        'plans': plans
    }
    return render(request, 'Manager/Plans.html', context)
