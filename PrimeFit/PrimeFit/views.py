from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Autenticação usando tabela USERS do PostgreSQL
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email e password são obrigatórios.')
            return render(request, 'auth/login.html')
        
        # Verificar credenciais usando a view vw_user_authentication
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT userid, email, name, password, usertypeid, isactive, user_type_label
                    FROM vw_user_authentication
                    WHERE email = %s
                """, [email])
                
                user_data = cursor.fetchone()
                
                if user_data and check_password(password, user_data[3]):
                    # Criar sessão de usuário
                    request.session['user_id'] = user_data[0]
                    request.session['email'] = user_data[1]
                    request.session['user_name'] = user_data[2]
                    request.session['user_type_id'] = user_data[4]
                    request.session['user_type'] = user_data[6]
                    request.session['is_authenticated'] = True
                    
                    # Atualizar last_login usando procedimento armazenado
                    cursor.execute("CALL sp_update_last_login(%s)", [user_data[0]])
                    
                    # Redirecionar baseado no tipo de usuário
                    if user_data[4] == 1:  # Gestor
                        return redirect('manager_dashboard')
                    elif user_data[4] == 2:  # Instrutor
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
        name = request.POST.get('name', '')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        nif = request.POST.get('nif', '')
        phone = request.POST.get('phone', '')
        iban = request.POST.get('iban', '')
        birth_date = request.POST.get('birth_date', '')
        gender = request.POST.get('gender', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        postal_code = request.POST.get('postal_code', '')
        user_type = request.POST.get('user_type', '3')  # Default to 'Member' type
        
        if not email or not password:
            messages.error(request, 'Email e password são obrigatórios.')
            return render(request, 'auth/register.html')
            
        if password != confirm_password:
            messages.error(request, 'As passwords não coincidem.')
            return render(request, 'auth/register.html')
            
        if len(password) < 8:
            messages.error(request, 'A password deve ter pelo menos 8 caracteres.')
            return render(request, 'auth/register.html')

        if not birth_date:
            messages.error(request, 'Data de nascimento é obrigatória.')
            return render(request, 'auth/register.html')

        if not gender:
            messages.error(request, 'Gênero é obrigatório.')
            return render(request, 'auth/register.html')

        if not address:
            messages.error(request, 'Endereço é obrigatório.')
            return render(request, 'auth/register.html')

        if not city:
            messages.error(request, 'Cidade é obrigatória.')
            return render(request, 'auth/register.html')

        if not postal_code:
            messages.error(request, 'Código postal é obrigatório.')
            return render(request, 'auth/register.html')

        try:
            with connection.cursor() as cursor:
                # Verificar se email já existe usando vista
                cursor.execute("SELECT userid, email FROM vw_email_exists WHERE email = %s", [email])
                if cursor.fetchone():
                    messages.error(request, 'Este email já está registado.')
                    return render(request, 'auth/register.html')
                
                # Criar novo usuário
                hashed_password = make_password(password)
                cursor.execute("CALL sp_create_member(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [name, hashed_password, nif, email, phone, iban, birth_date, gender, address, city, postal_code])
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
    try:
        with connection.cursor() as cursor:
            # Buscar check-ins recentes usando vista
            cursor.execute("""
                SELECT checkin_count, class_bookings, total_hours, next_payment, payment_price
                FROM vw_member_stats_month
                WHERE userid = %s
            """, [user_data['userid']])

            stats = cursor.fetchone()
            recent_checkins = stats[0]
            month_classes_frequented = stats[1]
            total_hours = round(stats[2])
            next_payment = stats[3] if stats[3] else "Pagamento em dia"
            payment_price = round(stats[4], 2) if stats[3] else "0.00€"

            cursor.execute("""
                SELECT classscheduleid, class_name, date, starttime, endtime, room
                FROM vw_member_schedule_classes
                WHERE userid = %s
            """, [user_data['userid']])

            schedule_classes = cursor.fetchall()

            cursor.execute("""
                SELECT classscheduleid, class_name, date, starttime, endtime, room, available_spots
                FROM vw_member_available_classes
                WHERE userid = %s
            """, [user_data['userid']])

            available_classes = cursor.fetchall()

    except Exception as e:
        messages.error(request, f'Erro ao carregar dados: {str(e)}')
    
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
        'available_classes': available_classes
    }
    return render(request, 'Member/HomePage.html', context)

@custom_login_required
def member_account(request):
    user_data = get_user_data(request)

    if user_data['user_type_id'] != 3:
        messages.error(request, 'Acesso negado. Apenas membros podem aceder à conta de membro.')
        return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT memberid, name, nif, email, phone, iban, birthdate, gender, address, city, postalcode, registrationdate,
                       startdate, enddate, plan_name, monthlyprice, access24h
                FROM vw_member_account_details
                WHERE userid = %s
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

    if user_data['user_type_id'] != 2:
        messages.error(request, 'Acesso negado. Apenas instrutores podem aceder à conta de instrutor.')
        return redirect('login')

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT instructorid, name, nif, email, phone, isactive
                FROM vw_instructor_info
                WHERE userid = %s
            """, [user_data['userid']])
            
            instructor_info = cursor.fetchone()
            
            # Buscar aulas do instrutor usando vista
            cursor.execute("""
                SELECT classid, name, room, capacity, duration_minutes
                FROM vw_instructor_classes
                WHERE userid = %s
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
            # Buscar horários das aulas do instrutor usando vista
            cursor.execute("""
                SELECT classscheduleid, name, date, starttime, endtime, 
                       maxparticipants, room
                FROM vw_class_schedules
                WHERE userid = %s
                ORDER BY date, starttime
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
    # if user_data['user_type_id'] != 1:
    #    messages.error(request, 'Acesso negado. Apenas gestores podem aceder ao dashboard.')
    #    return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            # Buscar estatísticas usando vista
            cursor.execute("SELECT total_members, total_instructors, active_memberships, today_checkins FROM vw_dashboard_stats")
            stats = cursor.fetchone()
            total_members, total_instructors, active_memberships, today_checkins_count = stats
    
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
    
    #if user_data['user_type_id'] != 1:
    #    messages.error(request, 'Acesso negado.')
    #    return redirect('login')

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT memberid, name, email, phone, registrationdate, isactive,
                       startdate, enddate, plan_name
                FROM vw_all_members
                ORDER BY registrationdate DESC
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
    
   # if user_data['user_type_id'] != 1:
   #     messages.error(request, 'Acesso negado.')
   #     return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT classscheduleid, name, instructor_name, 
                       date, starttime, endtime, room, maxparticipants
                FROM vw_all_classes
                ORDER BY date, starttime
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
                SELECT checkinid, name, date, entrancetime, exittime
                FROM vw_all_checkins
                ORDER BY date DESC, entrancetime DESC
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
    
   # if user_data['user_type_id'] != 1:
   #     messages.error(request, 'Acesso negado.')
   #     return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT machineid, name, type, manufacturer, model, 
                       status, installationdate, maintenancedate
                FROM vw_machines
                ORDER BY name
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
    
   # if user_data['user_type_id'] != 1:
   #     messages.error(request, 'Acesso negado.')
   #     return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT paymentid, member_name, plan_name,
                       amount, duedate, paymentdate, ispayed, paymentmethod
                FROM vw_payments
                ORDER BY duedate DESC
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
    
   # if user_data['user_type_id'] != 1:
    #    messages.error(request, 'Acesso negado.')
   #     return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT planid, name, monthlyprice, access24h, description, isactive
                FROM vw_plans
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
