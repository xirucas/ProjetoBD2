from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db import connections
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from django.core.signals import request_finished
from django.dispatch import receiver
import json
from datetime import datetime
from .models import (
    PlanDetails, UserAuthentication, Plan, EmailExists, MemberStatsMonth, 
    MemberScheduleClasses, MemberAccountDetails, Plan, PlanTable,
    InstructorInfo, InstructorClasses, ManagerClassSchedule,
    MemberPaymentHistory,  InstructorMonthlyStats, InstructorDailyDashboard, InstructorClassesToday, InstructorNextClassMembers, InstructorClassHistory, InstructorWeekPerformance, InstructorPopularClasses,
    ManagerMembersManagement, ManagerScheduleFilters, ExistingClasses, ClassEnrolledMembers,
    MemberAvailableClasses,
    MachineSummary, MachineInventory, MachineCategories, MachineBrands, MachineStatuses, MachineDetail,
    PaymentDashboardSummary, PaymentRecentTransactions, PaymentHistory, PaymentMonthlySummary, TotalActiveMembers, PlanStatistics,
    MemberUseridLookup, MemberEnrolledClasses, UserPasswordCheck, MemberClassHistory, MemberClassEvaluationDetails,
    ManagerRecentCheckins, ManagerUpcomingClasses, ManagerDashboardStats
)

_mongodb_manager_instance = None

def get_mongodb_manager():
    global _mongodb_manager_instance
    if _mongodb_manager_instance is None:
        try:
            from .mongodb_manager import MongoDBManager
            _mongodb_manager_instance = MongoDBManager()
        except Exception as e:
            return None
    return _mongodb_manager_instance

def close_mongodb_manager():
    global _mongodb_manager_instance
    if _mongodb_manager_instance is not None:
        try:
            _mongodb_manager_instance.close()
        except:
            pass
        _mongodb_manager_instance = None

@receiver(request_finished)
def cleanup_mongodb_connection(sender, **kwargs):
    pass

def get_user_connection(user_type_id=None):

    if user_type_id is None:
        # Usado para login e operações antes da autenticação
        return connections['guest']
    elif user_type_id == 1:  # Gestor
        return connections['manager']
    elif user_type_id == 2:  # Instrutor
        return connections['instructor']
    else:  # Membro (user_type_id = 3 ou outros)
        return connections['member']

def custom_login_required(function):
    def wrap(request, *args, **kwargs):
        if not request.session.get('is_authenticated'):
            messages.error(request, 'É necessário fazer login para aceder a esta página.')
            return redirect('login')
        return function(request, *args, **kwargs)
    return wrap

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

def get_user_db_connection(request):
    user_data = get_user_data(request)
    if user_data:
        return get_user_connection(user_data['user_type_id'])
    else:
        return get_user_connection()  

def get_user_db_name(request):
    user_data = get_user_data(request)
    if user_data is None:
        return 'guest'
    elif user_data['user_type_id'] == 1:  # Gestor
        return 'manager'
    elif user_data['user_type_id'] == 2:  # Instrutor
        return 'instructor'
    else:  # Membro
        return 'member'

def get_user_db_alias(request):
    return get_user_db_name(request)

def check_room_conflict(room, date, start_time, end_time, exclude_schedule_id=None, user_type_id=None):
    conn = get_user_connection(user_type_id)
    with conn.cursor() as cursor:
        if exclude_schedule_id:
            cursor.execute("SELECT fn_check_room_conflict(%s, %s, %s, %s, %s)", 
                         [room, date, start_time, end_time, exclude_schedule_id])
        else:
            cursor.execute("SELECT fn_check_room_conflict(%s, %s, %s, %s)", 
                         [room, date, start_time, end_time])
        return cursor.fetchone()[0]

def check_instructor_conflict(instructor_id, date, start_time, end_time, exclude_schedule_id=None, user_type_id=None):
    conn = get_user_connection(user_type_id)
    with conn.cursor() as cursor:
        if exclude_schedule_id:
            cursor.execute("SELECT fn_check_instructor_conflict(%s, %s, %s, %s, %s)", 
                         [instructor_id, date, start_time, end_time, exclude_schedule_id])
        else:
            cursor.execute("SELECT fn_check_instructor_conflict(%s, %s, %s, %s)", 
                         [instructor_id, date, start_time, end_time])
        return cursor.fetchone()[0]

# Authentication Views
def login_view(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        

        if not email or not password:
            messages.error(request, 'Email e password são obrigatórios.')
            return render(request, 'auth/login.html')

        try:
            user_data = UserAuthentication.objects.using('guest').filter(email=email).first()
            
            if user_data and check_password(password, user_data.password):

                request.session['user_id'] = user_data.userid
                request.session['email'] = user_data.email
                request.session['user_name'] = user_data.name
                request.session['user_type_id'] = user_data.usertypeid
                request.session['user_type'] = user_data.user_type_label
                request.session['is_authenticated'] = True

                conn = get_user_connection(user_data.usertypeid)
                with conn.cursor() as cursor:
                    cursor.execute("CALL sp_update_last_login(%s)", [user_data.userid])

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
        plans = list(Plan.objects.using('guest').values('planid', 'name', 'monthlyprice', 'access24h'))
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
        nif = request.POST.get('nif', '')
        phone = request.POST.get('phone', '')
        iban = request.POST.get('iban', '')
        birth_date = request.POST.get('birthdate', '')
        gender = request.POST.get('gender', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        postal_code = request.POST.get('postalcode', '')
        plan = request.POST.get('plan', '')

        # Validações básicas
        if not name or not email or not password:
            messages.error(request, 'Nome, email e password são obrigatórios.')
            return render(request, 'auth/register.html', context)

        if not plan:
            messages.error(request, 'Deve selecionar um plano.')
            return render(request, 'auth/register.html', context)

        try:
            if EmailExists.objects.using('guest').filter(email=email).exists():
                messages.error(request, 'Este email já está registado.')
                return render(request, 'auth/register.html', context)
            
            hashed_password = make_password(password)
            
            conn = get_user_connection() 
            
            with conn.cursor() as cursor:
                cursor.execute("CALL sp_create_member(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                             [name, hashed_password, nif, email, phone, iban, birth_date, gender, address, city, postal_code, plan])

            messages.success(request, 'Conta criada com sucesso! Pode fazer login.')
            return redirect('login')
                
        except Exception as e:
            messages.error(request, f'Erro ao criar conta: {str(e)}')
            return render(request, 'auth/register.html', context)

    return render(request, 'auth/register.html', context)

# Member Views
@custom_login_required
def member_home(request):
    user_data = get_user_data(request)

    recent_checkins = month_classes_frequented = total_hours = 0
    next_payment = ""
    payment_price = ""
    schedule_classes = []
    available_classes = []
    class_history_paginated = None
    is_booking = False

    try:
        db_name = get_user_db_name(request)

        stats = MemberStatsMonth.objects.using(db_name).filter(userid=user_data['userid']).first()

        if stats:
            recent_checkins = stats.checkin_count or 0
            month_classes_frequented = stats.class_bookings or 0
            total_hours = round(stats.total_hours or 0)
            next_payment = stats.next_payment if stats.next_payment else "Pagamento em dia"
            payment_price = f"{round(stats.payment_price, 2)}€" if stats.next_payment and stats.payment_price else "0.00€"

        schedule_classes_data = MemberScheduleClasses.objects.using(db_name).filter(userid=user_data['userid'])
        schedule_classes = list(schedule_classes_data.values(
            'class_name', 'date', 'starttime', 'endtime', 'room', 'instructor_name'
        ))

        member_lookup = MemberUseridLookup.objects.using(db_name).filter(userid=user_data['userid']).first()
        member_id = member_lookup.memberid if member_lookup else None

        if member_id:
            # Buscar todas as aulas disponíveis
            all_available = MemberAvailableClasses.objects.using(db_name).all()

            # Filtrar aulas onde o membro já não está inscrito usando model
            enrolled_classes_data = MemberEnrolledClasses.objects.using(db_name).filter(memberid=member_id)
            enrolled_classes = [enrolled.classscheduleid for enrolled in enrolled_classes_data]

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

            # Buscar histórico de aulas com paginação
            class_history_queryset = MemberClassHistory.objects.using(db_name).filter(memberid=member_id).order_by('-date', '-starttime')

            # Paginação para histórico de aulas
            paginator = Paginator(class_history_queryset, 5)  # 5 aulas por página
            page = request.GET.get('history_page')
            
            try:
                class_history_paginated = paginator.page(page)
            except PageNotAnInteger:
                class_history_paginated = paginator.page(1)
            except EmptyPage:
                class_history_paginated = paginator.page(paginator.num_pages)

            # Adicionar informação sobre avaliações após a paginação
            try:
                mongo_manager = get_mongodb_manager()
                
                if mongo_manager is None:
                   for class_item in class_history_paginated:
                        class_item.is_evaluated = False
                else:
                    for idx, class_item in enumerate(class_history_paginated):
                       # Verificar se a aula já foi avaliada
                        try:
                            existing_evaluation = mongo_manager.get_class_evaluation(
                                user_data['userid'], 
                                class_item.classscheduleid
                            )
                            is_evaluated = existing_evaluation is not None
                            class_item.is_evaluated = is_evaluated
                        except Exception as mongo_err:
                            class_item.is_evaluated = False
                        
            except Exception as e:
                for class_item in class_history_paginated:
                    class_item.is_evaluated = False
        else:
            available_classes = []
            class_history_paginated = None

    except Exception as e:
        messages.error(request, f'Erro ao carregar dados: {str(e)}')
    
    if request.method == 'POST':
        is_booking = True
        classscheduleid = request.POST.get('classscheduleid')

        try:
            conn = get_user_db_connection(request)

            with conn.cursor() as cursor:
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
        'class_history_paginated': class_history_paginated,
        'is_booking': is_booking,
    }

    return render(request, 'Member/HomePage.html', context)

@custom_login_required
def member_account(request):
    user_data = get_user_data(request)

    if user_data['user_type_id'] != 3:
        messages.error(request, 'Acesso negado. Apenas membros podem aceder à conta de membro.')
        return redirect('login')

    member_details = None
    payment_history = []
    checkin_history = []
    payment_status = 'Em dia'
    payment_status_class = 'text-success'
    
    try:
        db_name = get_user_db_name(request)

        member_details = MemberAccountDetails.objects.using(db_name).filter(userid=user_data['userid']).first()

        payment_history_queryset = MemberPaymentHistory.objects.using(db_name).filter(
            userid=user_data['userid']
        ).order_by('-payment_date')
        
        # Paginação para histórico de pagamentos
        paginator = Paginator(payment_history_queryset, 5)  # 5 pagamentos por página
        page = request.GET.get('page')
        try:
            payment_history = paginator.page(page)
        except PageNotAnInteger:
            payment_history = paginator.page(1)
        except EmptyPage:
            payment_history = paginator.page(paginator.num_pages)
        
        # Calcular status de pagamento baseado nos pagamentos pendentes
        if payment_history_queryset:
            # Verificar se há pagamentos em atraso
            pagamentos_em_atraso = [p for p in payment_history_queryset if p.payment_status == 'Em Atraso']
            # Verificar se há pagamentos pendentes
            pagamentos_pendentes = [p for p in payment_history_queryset if p.payment_status == 'Pendente']
            
            if pagamentos_em_atraso:
                payment_status = 'Em Atraso'
                payment_status_class = 'text-danger'
            elif pagamentos_pendentes:
                payment_status = 'Por Pagar'
                payment_status_class = 'text-warning'
            else:
                payment_status = 'Em dia'
                payment_status_class = 'text-success'
        
    except Exception as e:
        member_details = None
        payment_history = []
        checkin_history = []
        messages.error(request, f'Erro ao carregar dados da conta: {str(e)}')
    
    context = {
        'user_data': user_data,
        'member_details': member_details,
        'payment_history': payment_history,
        'checkin_history': checkin_history,
        'payment_status': payment_status,
        'payment_status_class': payment_status_class
    }
    return render(request, 'Member/Account.html', context)

@custom_login_required
def member_account_edit(request):
    user_data = get_user_data(request)

    if user_data['user_type_id'] != 3:
        messages.error(request, 'Acesso negado. Apenas membros podem editar o perfil.')
        return redirect('login')

    member_details = None
    
    try:
        db_name = get_user_db_name(request)
        
        # Buscar dados do membro
        member_details = MemberAccountDetails.objects.using(db_name).filter(userid=user_data['userid']).first()
        
        if not member_details:
            messages.error(request, 'Dados do membro não encontrados.')
            return redirect('member_account')
        
        if request.method == 'POST':
            # Processar atualização dos dados
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            birthdate = request.POST.get('birthdate')
            gender = request.POST.get('gender')
            nif = request.POST.get('nif')
            address = request.POST.get('address')
            city = request.POST.get('city')
            postalcode = request.POST.get('postalcode')
            iban = request.POST.get('iban')
            
            # Validações básicas
            if not name or not email:
                messages.error(request, 'Nome e email são obrigatórios.')
                return render(request, 'Member/AccountEdit.html', {'member_details': member_details, 'user_data': user_data})
            
            try:
                conn = get_user_db_connection(request)
                with conn.cursor() as cursor:
                    # Usar procedimento para atualizar perfil do membro
                    cursor.execute("""
                        CALL sp_member_update_profile(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [user_data['userid'], name, email, phone, birthdate or None, 
                          gender or None, nif, address, city, postalcode, iban])
                
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('member_account')
                
            except Exception as e:
                messages.error(request, f'Erro ao atualizar perfil: {str(e)}')
    
    except Exception as e:
        messages.error(request, f'Erro ao carregar dados: {str(e)}')
        return redirect('member_account')
    
    context = {
        'user_data': user_data,
        'member_details': member_details
    }
    return render(request, 'Member/AccountEdit.html', context)

@custom_login_required
def member_change_password(request):
    user_data = get_user_data(request)

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if user_data['user_type_id'] != 3:
        error_msg = 'Acesso negado. Apenas membros podem alterar a password.'
        if is_ajax:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('login')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validações
        if not current_password or not new_password or not confirm_password:
            error_msg = 'Todos os campos são obrigatórios.'
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('member_account_edit')
        
        if new_password != confirm_password:
            error_msg = 'A nova password e a confirmação não coincidem.'
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('member_account_edit')
        
        if len(new_password) < 6:
            error_msg = 'A nova password deve ter pelo menos 6 caracteres.'
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('member_account_edit')
        
        try:
            db_name = get_user_db_name(request)

            # Verificar password atual usando model
            user_password = UserPasswordCheck.objects.using(db_name).filter(userid=user_data['userid']).first()
            
            if not user_password:
                error_msg = 'Erro interno: usuário não encontrado.'
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({'success': False, 'error': error_msg})
                messages.error(request, error_msg)
                return redirect('member_account_edit')
            
            if not check_password(current_password, user_password.password):
                error_msg = 'Password atual incorreta.'
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({'success': False, 'error': error_msg})
                messages.error(request, error_msg)
                return redirect('member_account_edit')

            # Usar procedimento para alterar password
            hashed_password = make_password(new_password)
            conn = get_user_db_connection(request)
            with conn.cursor() as cursor:
                cursor.execute("""
                    CALL sp_change_user_password(%s, %s, %s)
                """, [user_data['userid'], current_password, hashed_password])

            success_msg = 'Password alterada com sucesso!'
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': True, 'message': success_msg})
            messages.success(request, success_msg)
            
        except Exception as e:
            error_msg = f'Erro ao alterar password: {str(e)}'
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)

    return redirect('member_account_edit')

@custom_login_required
def member_process_payment(request):
    user_data = get_user_data(request)

    if user_data['user_type_id'] != 3:
        messages.error(request, 'Acesso negado. Apenas membros podem processar pagamentos.')
        return redirect('login')
    
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        payment_method = request.POST.get('payment_method')

        try:
            try:
                post_data = {k: request.POST.getlist(k) if len(request.POST.getlist(k))>1 else request.POST.get(k) for k in request.POST.keys()}
            except Exception:
                post_data = dict(request.POST)

            # Validações básicas
            if not payment_id or not payment_method:
                messages.error(request, 'ID do pagamento e método de pagamento são obrigatórios.')
                return redirect('member_account')

            db_name = get_user_db_name(request)

            # Verificar se o pagamento pertence ao membro e está pendente
            payment_check = MemberPaymentHistory.objects.using(db_name).filter(
                paymentid=payment_id,
                userid=user_data['userid'],
                payment_status__in=['Pendente', 'Em Atraso']
            ).first()

            if not payment_check:
                messages.error(request, 'Pagamento não encontrado ou já foi processado.')
                return redirect('member_account')

            # Processar o pagamento usando procedimento
            try:
                # Usar conexão apropriada para o membro
                conn = get_user_db_connection(request)
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_process_member_payment(%s, %s, %s)
                    """, [payment_id, user_data['userid'], payment_method])

                messages.success(request, f'Pagamento de €{getattr(payment_check, "payment_amount", "?")} processado com sucesso via {payment_method}!')

            except Exception as e:
                messages.error(request, f'Erro ao processar pagamento: {str(e)}')

        except Exception as e:
            messages.error(request, f'Erro ao verificar pagamento: {str(e)}')
    
    return redirect('member_account')

@custom_login_required
def evaluate_class(request, classscheduleid):
    # Add detailed debug logging for evaluation flow
    if request.method == 'POST':
        # Basic request / user info
        user_data = get_user_data(request)
        try:
            # Obter dados do formulário
            rating = int(request.POST.get('rating', 0))
            comment = request.POST.get('comment', '').strip()

            # Validações
            if not (1 <= rating <= 5):
                messages.error(request, 'Por favor, selecione uma classificação de 1 a 5 estrelas.')
                return redirect('member_home')

            # Verificar se a aula existe no histórico do membro e obter instructor_id
            db_alias = get_user_db_alias(request)
            member_lookup = MemberUseridLookup.objects.using(db_alias).filter(userid=user_data['userid']).first()

            if not member_lookup:
                messages.error(request, 'Membro não encontrado.')
                return redirect('member_home')

            # Verificar se a aula existe no histórico e obter dados completos
            class_info = None
            try:
                # Usar a view em vez de query direta
                evaluation_details = MemberClassEvaluationDetails.objects.using(db_alias).filter(
                    classscheduleid=classscheduleid,
                    booking_memberid=member_lookup.memberid
                ).first()

                if evaluation_details:
                    class_info = {
                        'classscheduleid': evaluation_details.classscheduleid,
                        'instructor_id': evaluation_details.instructorid,
                        'class_name': evaluation_details.class_name,
                        'member_name': evaluation_details.member_name
                    }

            except Exception as db_error:
                messages.error(request, 'Erro ao verificar dados da aula.')
                return redirect('member_home')

            if not class_info:
                messages.error(request, 'Aula não encontrada no seu histórico.')
                return redirect('member_home')

            # Salvar avaliação no MongoDB
            mongo_manager = get_mongodb_manager()

            if mongo_manager is None:
                messages.error(request, 'Sistema de avaliações temporariamente indisponível.')
                return redirect('member_home')

            # Verificar se já existe avaliação
            try:
                existing_evaluation = mongo_manager.get_class_evaluation(user_data['userid'], classscheduleid, member_id=member_lookup.memberid)
            except Exception as mongo_err:
                existing_evaluation = None

            if existing_evaluation:
                messages.warning(request, 'Você já avaliou esta aula anteriormente.')
                return redirect('member_home')

            # Criar nova avaliação
            evaluation_data = {
                'user_id': user_data['userid'],
                'class_schedule_id': classscheduleid,
                'rating': rating,
                'comment': comment,
                'member_id': member_lookup.memberid,
                'member_name': class_info['member_name'],
                'instructor_id': class_info['instructor_id'],
                'class_name': class_info['class_name']
            }

            try:
                result = mongo_manager.add_class_evaluation(**evaluation_data)
            except Exception as mongo_add_err:
                result = False

            if result:
                messages.success(request, 'Avaliação enviada com sucesso! Obrigado pelo seu feedback.')
            else:
                messages.error(request, 'Erro ao enviar avaliação. Tente novamente.')

        except Exception as e:
            messages.error(request, f'Erro ao processar avaliação: {str(e)}')

    return redirect('member_home')

# Instructor Views
@custom_login_required
def instructor_account(request):
    user_data = get_user_data(request)

    if user_data['user_type_id'] != 2:
        messages.error(request, 'Acesso negado. Apenas instrutores podem aceder à conta de instrutor.')
        return redirect('login')

    instructor_info = None
    classes = []
    schedule_grid = {}
    monthly_info = None
    recent_evaluations = []

    try:
        db_name = get_user_db_name(request)
        
        # Buscar informações do instrutor usando model
        instructor_info = InstructorInfo.objects.using(db_name).filter(userid=user_data['userid']).first()
        
        # Buscar aulas do instrutor usando model
        classes = InstructorClasses.objects.using(db_name).filter(userid=user_data['userid']).values(
            'classid', 'name', 'room', 'capacity', 'duration_minutes'
        )

        # Buscar horário semanal do instrutor
        weekly_schedule = InstructorClasses.objects.using(db_name).filter(
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
        monthly_info = InstructorMonthlyStats.objects.using(db_name).filter(userid=user_data['userid']).first()

        # Buscar as últimas 4 avaliações do instrutor do MongoDB
        instructor_average_rating = 0
        if instructor_info and instructor_info.instructorid:
            try:
                mongo_manager = get_mongodb_manager()
                if mongo_manager is not None:
                    recent_evaluations = mongo_manager.get_instructor_recent_evaluations(
                        instructor_info.instructorid, limit=4
                    )
                    # Calcular média de avaliações do instrutor
                    instructor_average_rating = mongo_manager.get_instructor_average_rating(instructor_info.instructorid)
                else:
                    recent_evaluations = []
            except Exception:
                recent_evaluations = []

    except Exception as e:
        messages.error(request, f'Erro ao carregar dados: {str(e)}')

    context = {
        'user_data': user_data,
        'instructor_info': instructor_info,
        'classes': classes, 
        'monthly_info': monthly_info,
        'schedule_grid': schedule_grid,
        'recent_evaluations': recent_evaluations,
        'instructor_average_rating': instructor_average_rating
    }

    return render(request, 'Instructor/Account.html', context)

@custom_login_required
def instructor_account_edit(request):
    user_data = get_user_data(request)

    if user_data['user_type_id'] != 2:
        messages.error(request, 'Acesso negado. Apenas instrutores podem editar o perfil.')
        return redirect('login')
    
    instructor_info = None
    
    try:
        db_name = get_user_db_name(request)
        
        # Buscar dados do instrutor
        instructor_info = InstructorInfo.objects.using(db_name).filter(userid=user_data['userid']).first()
        
        if not instructor_info:
            messages.error(request, 'Dados do instrutor não encontrados.')
            return redirect('instructor_account')

        if request.method == 'POST':
            # Processar atualização dos dados
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            

            # Validações básicas
            if not name or not email:
                messages.error(request, 'Nome e email são obrigatórios.')
                return render(request, 'Instructor/AccountEdit.html', {'instructor_info': instructor_info, 'user_data': user_data})
            
            try:
                # Usar conexão apropriada para o instrutor
                conn = get_user_db_connection(request)

                with conn.cursor() as cursor:
                    # Usar procedimento para atualizar perfil do instrutor
                    cursor.execute("""
                        CALL sp_instructor_update_profile(%s, %s, %s, %s)
                    """, [user_data['userid'], name, email, phone])
                
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('instructor_account')
                
            except Exception as e:
                messages.error(request, f'Erro ao atualizar perfil: {str(e)}')

    
    except Exception as e:
        messages.error(request, f'Erro ao carregar dados: {str(e)}')
        return redirect('instructor_account')
    
    context = {
        'user_data': user_data,
        'instructor_info': instructor_info
    }
    return render(request, 'Instructor/AccountEdit.html', context)

@custom_login_required
def instructor_change_password(request):
    user_data = get_user_data(request)

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if user_data['user_type_id'] != 2:
        error_msg = 'Acesso negado. Apenas instrutores podem alterar a password.'
        if is_ajax:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('login')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validações
        if not current_password or not new_password or not confirm_password:
            error_msg = 'Todos os campos são obrigatórios.'
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('instructor_account_edit')
        
        if new_password != confirm_password:
            error_msg = 'A nova password e a confirmação não coincidem.'
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('instructor_account_edit')
        
        if len(new_password) < 6:
            error_msg = 'A nova password deve ter pelo menos 6 caracteres.'
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('instructor_account_edit')
        
        try:
            db_name = get_user_db_name(request)
            # Verificar password atual usando model
            user_password = UserPasswordCheck.objects.using(db_name).filter(userid=user_data['userid']).first()
            
            if not user_password:
                error_msg = 'Erro interno: usuário não encontrado.'
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({'success': False, 'error': error_msg})
                messages.error(request, error_msg)
                return redirect('instructor_account_edit')
            
            if not check_password(current_password, user_password.password):
                error_msg = 'Password atual incorreta.'
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({'success': False, 'error': error_msg})
                messages.error(request, error_msg)
                return redirect('instructor_account_edit')

            # Usar procedimento para alterar password
            hashed_password = make_password(new_password)
            conn = get_user_db_connection(request)
            with conn.cursor() as cursor:
                cursor.execute("""
                    CALL sp_change_user_password(%s, %s, %s)
                """, [user_data['userid'], current_password, hashed_password])

            success_msg = 'Password alterada com sucesso!'
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': True, 'message': success_msg})
            messages.success(request, success_msg)
            
        except Exception as e:
            error_msg = f'Erro ao alterar password: {str(e)}'
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)

    return redirect('instructor_account_edit')

@custom_login_required
def instructor_class_management(request):
    user_data = get_user_data(request)

    today_date = timezone.now().date()
    dashboard_stats = {}
    class_today = []
    next_class_members = []
    class_history = []
    weekly_performance = None
    popular_classes = []
     
    try:
        db_name = get_user_db_name(request)

        dashboard_stats = InstructorDailyDashboard.objects.using(db_name).filter(userid=user_data['userid']).first()

        class_today = InstructorClassesToday.objects.using(db_name).filter(userid=user_data['userid']).order_by('starttime')

        # Buscar membros da próxima aula
        next_class_members = InstructorNextClassMembers.objects.using(db_name).filter(instructor_userid=user_data['userid']).order_by('member_name')

        # Buscar histórico de aulas da última semana
        class_history = InstructorClassHistory.objects.using(db_name).filter(instructor_userid=user_data['userid']).values(
            'date', 'schedule', 'class_name', 'room', 'enrolled', 'rate', 'instructorid', 'instructor_userid'
        ).order_by('date', 'schedule')

        # Buscar performance semanal do instrutor
        weekly_performance = InstructorWeekPerformance.objects.using(db_name).filter(instructor_userid=user_data['userid']).first()

        # Buscar aulas populares do instrutor
        popular_classes = InstructorPopularClasses.objects.using(db_name).filter(instructor_userid=user_data['userid']).order_by('popularity_rank')


    except Exception as e:
        messages.error(request, f'Erro ao carregar horários: {str(e)}')
    
    context = {
        'today_date': today_date,
        'user_data': user_data,
        'dashboard_stats': dashboard_stats,
        'class_today': class_today,
        'next_class_members': next_class_members,
        'class_history': class_history,
        'weekly_performance': weekly_performance,
        'popular_classes': popular_classes
    }
    return render(request, 'Instructor/ClassManagement.html', context)

@custom_login_required
def instructor_class_evaluations(request, class_name):
    from django.http import JsonResponse
    
    user_data = get_user_data(request)
    
    if user_data['user_type_id'] != 2:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    
    try:
        # Buscar informações do instrutor
        db_alias = get_user_db_alias(request)
        instructor_info = InstructorInfo.objects.using(db_alias).filter(userid=user_data['userid']).first()
        
        if not instructor_info:
            return JsonResponse({'error': 'Instrutor não encontrado'}, status=404)
        
        # Buscar avaliações no MongoDB
        mongo_manager = get_mongodb_manager()
        
        if mongo_manager is None:
            return JsonResponse({'error': 'MongoDB não disponível'}, status=503)
        
        # Buscar avaliações por instructor_id e class_name
        evaluations = list(mongo_manager.evaluations.find({
            "instructor_id": instructor_info.instructorid,
            "class_name": class_name
        }).sort("date", -1))  # Ordenar por data decrescente
        
        # Converter ObjectId para string e formatar dados
        evaluations_data = []
        for eval in evaluations:
            evaluations_data.append({
                'member_name': eval.get('member_name', 'Membro Anônimo'),
                'rating': eval.get('rating', 0),
                'comment': eval.get('comment', ''),
                'date': eval.get('date').strftime('%d/%m/%Y %H:%M') if eval.get('date') else 'Data não disponível'
            })
        
        return JsonResponse({
            'success': True,
            'class_name': class_name,
            'evaluations': evaluations_data,
            'total': len(evaluations_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Erro ao buscar avaliações: {str(e)}'}, status=500)

# Manager Views
@custom_login_required
def manager_dashboard(request):
    user_data = get_user_data(request)

    total_members = 0
    total_instructors = 0
    active_memberships = 0
    today_checkins_count = 0
    today_classes = 0
    monthly_revenue = 0
    recent_checkins = []
    upcoming_classes = []
    
    
    try:
        db_alias = get_user_db_alias(request)
        
        # Buscar estatísticas usando model
        stats = ManagerDashboardStats.objects.using(db_alias).first()
        
        if stats:
            total_members = stats.total_members
            total_instructors = stats.total_instructors
            active_memberships = stats.active_memberships
            today_checkins_count = stats.today_checkins
            today_classes = stats.today_classes
            monthly_revenue = stats.monthly_revenue
            
        # Buscar check-ins recentes do dia
        recent_checkins = ManagerRecentCheckins.objects.using(db_alias).all()[:10]

        # Buscar próximas aulas do dia
        upcoming_classes = ManagerUpcomingClasses.objects.using(db_alias).all()[:10]
 

    except Exception as e:
        messages.error(request, f'Erro ao carregar estatísticas: {str(e)}')

    context = {
        'user_data': user_data,
        'total_members': total_members,
        'total_instructors': total_instructors,
        'active_memberships': active_memberships,
        'today_checkins_count': today_checkins_count,
        'today_classes': today_classes,
        'monthly_revenue': monthly_revenue,
        'recent_checkins': recent_checkins,
        'upcoming_classes': upcoming_classes
    }
    
    return render(request, 'Manager/Dashboard.html', context)

@custom_login_required
def manager_members(request):
    
    user_data = get_user_data(request)

    try:
        db_alias = get_user_db_alias(request)
        
        # Obter todos os membros com ordenação consistente
        members_queryset = ManagerMembersManagement.objects.using(db_alias).all().order_by('memberid')

        plans = Plan.objects.using(db_alias).all()

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
    user_data = get_user_data(request)
   
    member = None
    is_edit_mode = request.GET.get('edit') == 'true'
    
    # Carregar planos disponíveis
    try:
        db_alias = get_user_db_alias(request)
        plans = Plan.objects.using(db_alias).all()
    except Exception as e:
        plans = []
        messages.error(request, f'Erro ao carregar planos: {str(e)}')
    
    # Se tem member_id, buscar o membro
    if member_id:
        try:
            db_alias = get_user_db_alias(request)
            member = ManagerMembersManagement.objects.using(db_alias).get(memberid=member_id)
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
        status = request.POST.get('member_status', 'ativo')

        member_status = status.lower()
  
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
                conn = get_user_db_connection(request)
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_update_member(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [member_id, name, email, nif, phone, iban, birth_date, gender, address, city, postal_code, plan_id, member_status])
                
                messages.success(request, f'Membro atualizado com sucesso! Status: {member_status}')
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
                
                # Verificar se email já existe usando conexão manager
                if EmailExists.objects.using('manager').filter(email=email).exists():
                    messages.error(request, 'Este email já está registado.')
                    return render(request, 'Manager/MemberDetail.html', {
                        'user_data': user_data,
                        'member': None,
                        'plans': plans,
                        'is_edit_mode': True,
                    })
                
                # Criar membro
                hashed_password = make_password(password)
                conn = get_user_db_connection(request)
                
                with conn.cursor() as cursor:

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
        db_alias = get_user_db_alias(request)
        classes_queryset = ManagerClassSchedule.objects.using(db_alias).filter(class_date=selected_date)
        
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
        db_alias = get_user_db_alias(request)
        filters_queryset = ManagerScheduleFilters.objects.using(db_alias).all()
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
        db_alias = get_user_db_alias(request)
        
        # Obter estatísticas resumo das máquinas
        machine_summary = MachineSummary.objects.using(db_alias).first()
        
        # Obter todas as máquinas com ordenação consistente
        machines_queryset = MachineInventory.objects.using(db_alias).all().order_by('machineid')
        
        # Obter categorias e status únicos para filtros
        categories = MachineInventory.objects.using(db_alias).values_list('categoria', flat=True).distinct().order_by('categoria')
        statuses = MachineInventory.objects.using(db_alias).values_list('status', flat=True).distinct().order_by('status')
        
        # Aplicar filtros se houver
        search_query = request.GET.get('search', '')
        category_filter = request.GET.get('category', 'todos')
        status_filter = request.GET.get('status', 'todos')
        
        original_count = machines_queryset.count()
        
        # Aplicar filtro de busca
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
    user_data = get_user_data(request)
    
    machine = None
    is_edit_mode = request.GET.get('edit') == 'true'
    
    # Obter dados para dropdowns usando models
    try:
        db_alias = get_user_db_alias(request)
        
        categories = list(MachineCategories.objects.using(db_alias).all().values_list('categoria', flat=True))
        
        brands = list(MachineBrands.objects.using(db_alias).all().values_list('marca', flat=True))
        
        statuses = list(MachineStatuses.objects.using(db_alias).all().values('machinestatusid', 'status'))
        
    except Exception as e:
        categories = []
        brands = []
        statuses = []
        messages.error(request, f'Erro ao carregar dados: {str(e)}')
    
    # Se tem machine_id, buscar a máquina
    if machine_id:
        try:
            db_alias = get_user_db_alias(request)
            machine = MachineDetail.objects.using(db_alias).get(machineid=machine_id)
            
            # Remover o status atual da máquina da lista para evitar loops (máquina não pode ter o mesmo status)
            current_status = {'machinestatusid': machine.machinestatusid, 'status': machine.status}
            
            if current_status in statuses:
                statuses.remove(current_status)
                
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
        new_status = request.POST.get('new_status', '')
        maintenance_date = request.POST.get('maintenance_date', None)
        
        # Se há new_status (mudança de status via checkbox), usar ele em vez de status_id
        final_status = new_status if new_status else status_id
        
        # Validação crítica: garantir que final_status não está vazio para atualizações
        if machine_id and not final_status:
            final_status = str(machine.machinestatusid)  # Manter status atual se não especificado
        elif not machine_id and not final_status:
            final_status = '2'  # Status padrão para novas máquinas: "Em funcionamento"
        
        # Validação adicional: verificar se é um número válido
        try:
            final_status_int = int(final_status)
        except ValueError:
            if machine_id:
                final_status = str(machine.machinestatusid)
            else:
                final_status = '2'  # "Em funcionamento" para novas máquinas
        
        # Usar nova categoria se fornecida
        final_categoria = new_categoria if new_categoria else categoria
        final_marca = new_marca if new_marca else marca
        
        # Validação da data de aquisição
        if data_aquisicao:
            try:
                from datetime import datetime
                # Tentar parsing da data para validar formato
                datetime.strptime(data_aquisicao, '%Y-%m-%d')
            except ValueError:
                data_aquisicao = None
        else:
            data_aquisicao = None
        
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
                conn = get_user_db_connection(request)
                with conn.cursor() as cursor:
                    # Se há mudança de status e data de manutenção, tratar separadamente
                    if new_status and maintenance_date:
                     
                        # Primeiro atualizar os dados básicos da máquina
                        cursor.execute("""
                            CALL sp_update_machine(%s, %s, %s, %s, %s, %s, %s, %s)
                        """, [machine_id, nome, codigo, final_categoria, final_marca, modelo, data_aquisicao, machine.machinestatusid])
                        
                        # Depois alterar o status com data de manutenção
                        cursor.execute("""
                            CALL sp_change_machine_status(%s, %s, %s)
                        """, [machine_id, int(final_status), maintenance_date])
                        
                    else:
                        cursor.execute("""
                            CALL sp_update_machine(%s, %s, %s, %s, %s, %s, %s, %s)
                        """, [machine_id, nome, codigo, final_categoria, final_marca, modelo, data_aquisicao, int(final_status)])

                messages.success(request, 'Máquina atualizada com sucesso!')
                return redirect('manager_machine_detail', machine_id=machine_id)
            
            else:

                # CRIAR NOVA MÁQUINA usando procedimento
                conn = get_user_db_connection(request)
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_create_machine(%s, %s, %s, %s, %s, %s, %s)
                    """, [nome, codigo, final_categoria, final_marca, modelo, data_aquisicao, int(final_status)])

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
    if request.method == 'POST':
  
        new_status = request.POST.get('new_status')
        maintenance_date = request.POST.get('maintenance_date', None)

        # Validações básicas
        if not new_status:
            messages.error(request, 'Status é obrigatório.')
            return redirect('manager_machines')
        
        try:
            db_alias = get_user_db_alias(request)
            
            # Verificar status atual da máquina
            machine = MachineDetail.objects.using(db_alias).get(machineid=machine_id)
            current_status_id = machine.machinestatusid

            # Verificar se é uma mudança válida
            if str(current_status_id) == str(new_status):
                messages.warning(request, 'A máquina já está neste status.')
                return redirect('manager_machines')
            
            # Usar procedimento para alterar status
            conn = get_user_db_connection(request)
            with conn.cursor() as cursor: 
                # Se está mudando PARA manutenção (status 2) OU está saindo DE manutenção (status atual é 2)
                # e tem data de manutenção fornecida, usar a versão com data
                needs_maintenance_date = (new_status == '2' or (current_status_id == 2 and new_status != '2')) and maintenance_date

                if needs_maintenance_date:

                    cursor.execute("""
                        CALL sp_change_machine_status(%s, %s, %s)
                    """, [machine_id, new_status, maintenance_date])
                    
                else:
                    cursor.execute("""
                        CALL sp_change_machine_status(%s, %s)
                    """, [machine_id, new_status])
                    
            messages.success(request, 'Status da máquina atualizado com sucesso!')
            
        except MachineDetail.DoesNotExist:
            messages.error(request, 'Máquina não encontrada.')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar status: {str(e)}')
    else:
        messages.error(request, 'Método não permitido.')
    
    return redirect('manager_machines')

@custom_login_required
def manager_plans(request):
    user_data = get_user_data(request)

    db_alias = get_user_db_alias(request)
    dashboard_stats = PlanStatistics.objects.using(db_alias).all()
    total_active_members = TotalActiveMembers.objects.using(db_alias).first()
    plan_details = PlanDetails.objects.using(db_alias).all()

    context = {
        'user_data': user_data,
        'dashboard_stats': dashboard_stats,
        'total_active_members': total_active_members,
        'plan_details': plan_details,
    }

    return render(request, 'Manager/Plans.html', context)

@custom_login_required
def manager_plan_edit(request, plan_id):
    user_data = get_user_data(request)
    
    try:
        db_alias = get_user_db_alias(request)
        
        # Buscar o plano na tabela real
        plan = PlanTable.objects.using(db_alias).get(planid=plan_id, isactive=True)
        
        # Buscar estatísticas do plano
        try:
            plan_stats = PlanStatistics.objects.using(db_alias).get(planid=plan_id)
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
            conn = get_user_db_connection(request)
            with conn.cursor() as cursor:
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
    user_data = get_user_data(request)
    
    if request.method == 'POST':
        try:
            # Dados do formulário
            class_name = request.POST.get('class_name')
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

            user_data = get_user_data(request)
            conn = get_user_db_connection(request)
            
            with conn.cursor() as cursor:
                # Usar função helper para verificar conflito de sala
                if check_room_conflict(final_room, date, start_time, end_time, user_type_id=user_data['user_type_id']):
                    messages.error(request, 'Já existe uma aula agendada nesta sala e horário.')
                    return redirect('manager_class_new')
                
                # Usar função helper para verificar conflito de instrutor
                if check_instructor_conflict(instructor_id, date, start_time, end_time, user_type_id=user_data['user_type_id']):
                    messages.error(request, 'O instrutor já tem uma aula agendada neste horário.')
                    return redirect('manager_class_new')
                
                # Criar nova aula e agendamento em uma operação

                if new_class_name == '':
                    new_class_name = class_name
                cursor.execute("""
                    CALL sp_create_and_schedule_class(%s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
                """, [new_class_name, instructor_id, final_room, max_participants, 
                      duration_minutes, date, start_time, end_time, max_participants])

                messages.success(request, 'Aula agendada com sucesso!')
                return redirect('manager_classes')
                
        except Exception as e:
            messages.error(request, f'Erro ao criar aula: {str(e)}')
            return redirect('manager_class_new')
    
    try:
        db_alias = get_user_db_alias(request)
        
        # Buscar aulas existentes usando a view
        existing_classes = list(ExistingClasses.objects.using(db_alias).all().values(
            'name'
        ).distinct())

        # Buscar instrutores ativos usando a view existente
        instructors = ManagerScheduleFilters.objects.using(db_alias).filter(filter_type='instructor')
        instructors_list = list(instructors)


        # Buscar salas existentes usando a view existente
        rooms = ManagerScheduleFilters.objects.using(db_alias).filter(filter_type='room')
        rooms_list = list(rooms)
        
    except Exception as e:
        existing_classes = []
        instructors_list = []
        rooms_list = []
        messages.error(request, f'Erro ao carregar dados: {str(e)}')
    
    context = {
        'user_data': user_data,
        'existing_classes': existing_classes,
        'instructors': instructors_list,
        'rooms': rooms_list,
    }
    
    return render(request, 'Manager/ClassNew.html', context)

@custom_login_required  
def manager_class_view(request, class_id):
    user_data = get_user_data(request)
    
    try:
        db_alias = get_user_db_alias(request)
        
        # Buscar detalhes da aula agendada
        class_details = ManagerClassSchedule.objects.using(db_alias).get(classscheduleid=class_id)
        
        # Buscar membros inscritos usando a view
        enrolled_members = ClassEnrolledMembers.objects.using(db_alias).filter(
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
    user_data = get_user_data(request)
    
    try:
        db_alias = get_user_db_alias(request)
        class_details = ManagerClassSchedule.objects.using(db_alias).get(classscheduleid=class_id)
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
            
            user_data = get_user_data(request)
            conn = get_user_db_connection(request)
            with conn.cursor() as cursor:
                # Usar função helper para verificar conflito de sala (excluindo aula atual)
                if check_room_conflict(class_details.room, date, start_time, end_time, class_id, user_data['user_type_id']):
                    messages.error(request, 'Já existe uma aula agendada nesta sala e horário.')
                    return redirect('manager_class_edit', class_id=class_id)
                
                # Usar função helper para verificar conflito de instrutor (excluindo aula atual)
                if check_instructor_conflict(class_details.instructorid, date, start_time, end_time, class_id, user_data['user_type_id']):
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
        db_alias = get_user_db_alias(request)
        
        # 1. Resumo dos 4 quadrados superiores
        dashboard_summary = PaymentDashboardSummary.objects.using(db_alias).first()
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
        recent_transactions = PaymentRecentTransactions.objects.using(db_alias).all()[:3]
        
        # 3. Histórico de pagamentos com filtros
        # Base queryset
        payment_history = PaymentHistory.objects.using(db_alias).all()
        
        # Aplicar filtros
        if status_filter and status_filter != 'Todos os Status':
            payment_history = payment_history.filter(status=status_filter)
        
        if plano_filter and plano_filter != 'Todos os Planos':
            payment_history = payment_history.filter(plano=plano_filter)
        
        if search_query:
            payment_history = payment_history.filter(nome_membro__icontains=search_query)
        
        # Filtrar por intervalo de datas - usando SQL raw em vez de Q
        if data_inicio and data_fim:
            payment_history = payment_history.extra(
                where=["(data_vencimento >= %s AND data_vencimento <= %s) OR (data_pagamento IS NOT NULL AND data_pagamento >= %s AND data_pagamento <= %s)"],
                params=[data_inicio, data_fim, data_inicio, data_fim]
            )
        elif data_inicio:
            payment_history = payment_history.extra(
                where=["data_vencimento >= %s OR (data_pagamento IS NOT NULL AND data_pagamento >= %s)"],
                params=[data_inicio, data_inicio]
            )
        elif data_fim:
            payment_history = payment_history.extra(
                where=["data_vencimento <= %s OR (data_pagamento IS NOT NULL AND data_pagamento <= %s)"],
                params=[data_fim, data_fim]
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
        monthly_summary = PaymentMonthlySummary.objects.using(db_alias).first()
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
            PaymentHistory.objects.using(db_alias).values_list('status', flat=True).distinct()
        )
        plano_options = ['Todos os Planos'] + list(
            PaymentHistory.objects.using(db_alias).values_list('plano', flat=True).distinct()
        )

    except Exception as e:
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
    
    db_alias = get_user_db_alias(request)
    payments = PaymentHistory.objects.using(db_alias).all()
    
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

@custom_login_required
def manager_instructors(request):
    user_data = get_user_data(request)

    try:
        db_alias = get_user_db_alias(request)
        
        # Obter todos os instrutores com ordenação consistente
        instructors_queryset = InstructorInfo.objects.using(db_alias).all().order_by('instructorid')

        # Aplicar filtros se houver
        search_query = request.GET.get('search', '')
        status_filter = request.GET.get('status', 'todos')
        
        if search_query:
            instructors_queryset = instructors_queryset.filter(
                name__icontains=search_query
            ) | instructors_queryset.filter(
                email__icontains=search_query
            ) | instructors_queryset.filter(
                phone__icontains=search_query
            )

        if status_filter and status_filter != 'todos':
            instructors_queryset = instructors_queryset.filter(isactive=(status_filter == 'true'))
        
        # Configurar paginação - 10 instrutores por página
        paginator = Paginator(instructors_queryset, 10)
        page_number = request.GET.get('page')
        
        try:
            instructors = paginator.page(page_number)
        except PageNotAnInteger:
            # Se a página não for um número inteiro, mostrar a primeira página
            instructors = paginator.page(1)
        except EmptyPage:
            # Se a página estiver fora do intervalo, mostrar a última página
            instructors = paginator.page(paginator.num_pages)

        # Adicionar avaliação média para cada instrutor após a paginação
        try:
            mongo_manager = get_mongodb_manager()
            if mongo_manager:
                # Para cada instrutor na página atual, buscar a avaliação média
                for instructor in instructors:
                    try:
                        instructor.average_rating = mongo_manager.get_instructor_average_rating(instructor.instructorid)
                    except Exception as rating_err:
                        instructor.average_rating = 0
            else:
                # Se MongoDB não estiver disponível, definir rating como 0
                for instructor in instructors:
                    instructor.average_rating = 0
        except Exception as mongo_err:
            # Se MongoDB falhar completamente, continua sem informação de avaliação
            for instructor in instructors:
                instructor.average_rating = 0

    except Exception as e:
        messages.error(request, f'Erro ao carregar instrutores: {str(e)}')
        instructors = []
    
    context = {
        'user_data': user_data,
        'instructors': instructors,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_instructors': instructors_queryset.count() if 'instructors_queryset' in locals() else 0
    }
    return render(request, 'Manager/Instructors.html', context)

@custom_login_required
def manager_instructor_detail(request, instructor_id=None):
    user_data = get_user_data(request)
    instructor = None
    is_edit_mode = request.GET.get('edit') == 'true'
    is_new = instructor_id is None
    
    # Se tem instructor_id, buscar o instrutor
    if instructor_id:
        try:
            db_alias = get_user_db_alias(request)
            instructor = InstructorInfo.objects.using(db_alias).get(instructorid=instructor_id)
        except InstructorInfo.DoesNotExist:
            messages.error(request, 'Instrutor não encontrado.')
            return redirect('manager_instructors')
    
    if request.method == 'POST':
        # Obter dados do formulário
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        nif = request.POST.get('nif', '').strip()
        phone = request.POST.get('phone', '').strip()
        hired_at = request.POST.get('hired_at', '')
        password = request.POST.get('password', '')
        isactive = request.POST.get('isactive')
        
        # Validações básicas
        if not name or not email or not nif or not hired_at:
            messages.error(request, 'Nome, email, NIF e data de contratação são obrigatórios.')
            return render(request, 'Manager/InstructorDetail.html', {
                'user_data': user_data,
                'instructor': instructor,
                'is_edit_mode': True,
                'is_new': is_new,
            })
        
        # Validação de NIF (9 dígitos)
        if not nif.isdigit() or len(nif) != 9:
            messages.error(request, 'NIF deve ter exatamente 9 dígitos.')
            return render(request, 'Manager/InstructorDetail.html', {
                'user_data': user_data,
                'instructor': instructor,
                'is_edit_mode': True,
                'is_new': is_new,
            })
        
        # Validação de password (apenas para novos instrutores)
        if is_new:
            if not password or len(password) < 8:
                messages.error(request, 'Password deve ter pelo menos 8 caracteres.')
                return render(request, 'Manager/InstructorDetail.html', {
                    'user_data': user_data,
                    'instructor': instructor,
                    'is_edit_mode': True,
                    'is_new': is_new,
                })
        
        try:
            if is_new:
                # Criar novo instrutor
                hashed_password = make_password(password)
                conn = get_user_db_connection(request)
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_create_instructor(%s, %s, %s, %s, %s, %s)
                    """, [name, hashed_password, nif, email, phone or None, hired_at])
                
                messages.success(request, 'Instrutor criado com sucesso!')
                return redirect('manager_instructors')
            else:
                # Atualizar instrutor existente
                conn = get_user_db_connection(request)
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_update_instructor(%s, %s, %s, %s, %s, %s, %s)
                    """, [instructor_id, name, nif, email, phone or None, hired_at, isactive])
                
                messages.success(request, 'Instrutor atualizado com sucesso!')
                return redirect('manager_instructor_detail', instructor_id=instructor_id)
                
        except Exception as e:
            messages.error(request, f'Erro ao {"criar" if is_new else "atualizar"} instrutor: {str(e)}')
            return render(request, 'Manager/InstructorDetail.html', {
                'user_data': user_data,
                'instructor': instructor,
                'is_edit_mode': True,
                'is_new': is_new,
            })
    
    # GET request
    context = {
        'user_data': user_data,
        'instructor': instructor,
        'is_edit_mode': is_edit_mode,
        'is_new': is_new,
    }
    return render(request, 'Manager/InstructorDetail.html', context)

@custom_login_required
def financial_report(request):
    user_data = get_user_data(request)

    # Verificar se é manager
    if user_data['user_type_id'] != 1:
        messages.error(request, 'Acesso negado. Apenas managers podem gerar relatórios financeiros.')
        return redirect('login')

    try:
        # Usar conexão de manager para o relatório
        conn = get_user_db_connection(request)

        financial_data = []
        statistics = {}
        
        with conn.cursor() as cursor:
            # Usar função stored procedure para obter dados
            cursor.execute("SELECT * FROM fn_generate_financial_report()")
            result = cursor.fetchone()
            
            if result:
                financial_data = result[0] if result[0] else []
                statistics = result[1] if result[1] else {}
        
        # Verificar se é request de download
        if request.GET.get('download') == 'true':
            
            # Preparar dados completos para download
            complete_report = {
                'report_info': {
                    'title': 'Relatório Financeiro PrimeFit',
                    'generated_at': datetime.now().isoformat(),
                    'generated_by': user_data['user_name'],
                    'total_records': len(financial_data) if financial_data else 0
                },
                'statistics': statistics,
                'financial_data': financial_data
            }
            
            # Criar resposta HTTP para download
            response = HttpResponse(
                content_type='application/json; charset=utf-8'
            )
            
            # Definir headers para download
            filename = f"relatorio_financeiro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            # Escrever JSON no response
            json.dump(complete_report, response, indent=2, default=str, ensure_ascii=False)
            return response
        
        else:
            # Exibir relatório na página
            context = {
                'user_data': user_data,
                'financial_data': financial_data,
                'statistics': statistics
            }
            return render(request, 'Manager/FinancialReport.html', context)
                
    except Exception as e:
        messages.error(request, f'Erro ao gerar relatório financeiro: {str(e)}')
        return redirect('manager_dashboard')
