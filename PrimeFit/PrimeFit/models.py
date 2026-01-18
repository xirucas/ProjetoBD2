from django.db import models

# Model for vw_user_authentication
class UserAuthentication(models.Model):
    userid = models.AutoField(primary_key=True)
    email = models.CharField(max_length=254)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    usertypeid = models.IntegerField()
    isactive = models.BooleanField()
    user_type_label = models.CharField(max_length=50)
    
    class Meta:
        managed = False
        db_table = 'vw_user_authentication'

# Model for vw_plan (used in registration)
class Plan(models.Model):
    planid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    monthlyprice = models.DecimalField(max_digits=10, decimal_places=2)
    access24h = models.BooleanField()
    
    class Meta:
        managed = False
        db_table = 'vw_plan'

# Model for actual plan table (for editing)
class PlanTable(models.Model):
    planid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80)
    monthlyprice = models.DecimalField(max_digits=10, decimal_places=2)
    access24h = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    isactive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False
        db_table = 'plan'

# Model for vw_email_exists
class EmailExists(models.Model):
    userid = models.AutoField(primary_key=True)
    email = models.CharField(max_length=254)
    
    class Meta:
        managed = False
        db_table = 'vw_email_exists'

# Model for vw_member_stats_month
class MemberStatsMonth(models.Model):
    checkin_count = models.IntegerField()
    class_bookings = models.IntegerField()
    total_hours = models.FloatField()
    next_payment = models.DateField(null=True, blank=True)
    payment_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    memberid = models.IntegerField(primary_key=True)
    userid = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_member_stats_month'

# Model for vw_member_schedule_classes
class MemberScheduleClasses(models.Model):
    class_name = models.CharField(max_length=100)
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    room = models.CharField(max_length=50)
    instructor_name = models.CharField(max_length=100)
    userid = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_member_schedule_classes'

# Model for vw_member_available_classes
class MemberAvailableClasses(models.Model):
    classscheduleid = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=100)
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    room = models.CharField(max_length=50)
    instructor_name = models.CharField(max_length=100)
    available_spots = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_member_available_classes'

# Model for vw_member_account_details
class MemberAccountDetails(models.Model):
    memberid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    nif = models.CharField(max_length=9)
    email = models.CharField(max_length=254)
    phone = models.CharField(max_length=15)
    iban = models.CharField(max_length=34)
    birthdate = models.DateField()
    gender = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postalcode = models.CharField(max_length=20)
    registrationdate = models.DateField()
    startdate = models.DateField(null=True, blank=True)
    enddate = models.DateField(null=True, blank=True)
    next_payment_date = models.DateField(null=True, blank=True)
    plan_name = models.CharField(max_length=100, null=True, blank=True)
    monthlyprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    access24h = models.BooleanField(null=True, blank=True)
    userid = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_member_account_details'

# Model for vw_instructor_info
class InstructorInfo(models.Model):
    instructorid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    nif = models.CharField(max_length=9)
    email = models.CharField(max_length=254)
    phone = models.CharField(max_length=15)
    isactive = models.BooleanField()
    hired_at = models.DateField()
    userid = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_instructor_info'

class InstructorMonthlyStats(models.Model):
    instructorid = models.AutoField(primary_key=True)
    userid = models.IntegerField()
    instructor_name = models.CharField(max_length=100)
    classes_month = models.IntegerField()
    students_month = models.IntegerField()
    hours_month = models.FloatField()
    stats_year = models.IntegerField()
    stats_month = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'vw_instructor_stats_month'

# Model for vw_instructor_classes
class InstructorClasses(models.Model):
    classid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    room = models.CharField(max_length=50)
    capacity = models.IntegerField()
    duration_minutes = models.IntegerField()
    instructorid = models.IntegerField()
    userid = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_instructor_classes'

class InstructorClassesToday(models.Model):
    classid = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=100)
    room = models.CharField(max_length=50)
    capacity = models.IntegerField()
    duration_minutes = models.IntegerField()
    classscheduleid = models.IntegerField()
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    maxparticipants = models.IntegerField()
    start_time = models.CharField(max_length=5)
    end_time = models.CharField(max_length=5)
    time_slot = models.CharField(max_length=13)
    enrolled_students = models.IntegerField()
    instructorid = models.IntegerField()
    userid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'vw_instructor_classes_today'

# Model for vw_class_schedules
class ClassSchedules(models.Model):
    classscheduleid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    maxparticipants = models.IntegerField()
    room = models.CharField(max_length=50)
    instructorid = models.IntegerField()
    userid = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_class_schedules'

# Model for vw_dashboard_stats
class DashboardStats(models.Model):
    total_members = models.IntegerField()
    total_instructors = models.IntegerField()
    active_memberships = models.IntegerField()
    today_checkins = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_dashboard_stats'


# Model for vw_all_checkins
class AllCheckins(models.Model):
    checkinid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date = models.DateField()
    entrancetime = models.TimeField()
    exittime = models.TimeField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'vw_all_checkins'


# Model for vw_member_payment_history
class MemberPaymentHistory(models.Model):
    paymentid = models.AutoField(primary_key=True)
    payment_date = models.DateField()
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paymentmethod = models.CharField(max_length=50, null=True, blank=True)
    payment_status = models.CharField(max_length=20)
    paymentdate = models.DateField(null=True, blank=True)
    memberid = models.IntegerField()
    userid = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_member_payment_history'

# Model for vw_member_checkin_history
class MemberCheckinHistory(models.Model):
    checkinid = models.AutoField(primary_key=True)
    checkin_date = models.DateField()
    entrancetime = models.TimeField()
    exittime = models.TimeField(null=True, blank=True)
    duration_hours = models.FloatField(null=True, blank=True)
    duration_formatted = models.CharField(max_length=50, null=True, blank=True)
    memberid = models.IntegerField()
    userid = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_member_checkin_history'

# Model for vw_instructor_next_class_members
class InstructorNextClassMembers(models.Model):
    class_name = models.CharField(max_length=100)
    class_time = models.CharField(max_length=5)
    room = models.CharField(max_length=50)
    date = models.DateField()
    classscheduleid = models.IntegerField()
    instructorid = models.IntegerField()
    instructor_userid = models.IntegerField()
    member_name = models.CharField(max_length=100)
    memberid = models.IntegerField(primary_key=True)
    plan_name = models.CharField(max_length=100, null=True, blank=True)
    total_enrolled = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_instructor_next_class_members'

# Model for vw_instructor_class_history
class InstructorClassHistory(models.Model):
    date = models.DateField()
    schedule = models.CharField(max_length=11)  # Format: HH:MM-HH:MM
    class_name = models.CharField(max_length=100)
    room = models.CharField(max_length=50)
    enrolled = models.IntegerField()
    present = models.IntegerField()
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    instructorid = models.IntegerField()
    instructor_userid = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_instructor_class_history'


# Model for vw_instructor_week_performance
class InstructorWeekPerformance(models.Model):
    instructorid = models.IntegerField(primary_key=True)
    instructor_userid = models.IntegerField()
    instructor_name = models.CharField(max_length=100)
    total_classes = models.IntegerField()
    total_students = models.IntegerField()
    total_capacity = models.IntegerField()
    average_attendance = models.DecimalField(max_digits=5, decimal_places=2)
    
    class Meta:
        managed = False
        db_table = 'vw_instructor_week_performance'

# Model for vw_instructor_popular_classes
class InstructorPopularClasses(models.Model):
    instructorid = models.IntegerField()
    instructor_userid = models.IntegerField()
    class_name = models.CharField(max_length=100, primary_key=True)
    room = models.CharField(max_length=50)
    total_sessions = models.IntegerField()
    total_capacity = models.IntegerField()
    total_attendees = models.IntegerField()
    occupation_rate = models.DecimalField(max_digits=5, decimal_places=2)
    popularity_rank = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_instructor_popular_classes'

class ManagerMembersManagement(models.Model):
    memberid = models.AutoField(primary_key=True)
    member_name = models.CharField(max_length=100)
    email = models.CharField(max_length=254)
    member_phone = models.CharField(max_length=15)
    plan_name = models.CharField(max_length=100)   
    status = models.CharField(max_length=20)
    member_registration_date = models.DateField()
    planid = models.IntegerField()
    total_members = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'vw_manager_members_management'

# Model for vw_manager_class_schedule
class ManagerClassSchedule(models.Model):
    classscheduleid = models.AutoField(primary_key=True)
    class_date = models.DateField()
    class_name = models.CharField(max_length=100)
    room = models.CharField(max_length=50)
    classid = models.IntegerField()
    instructorid = models.IntegerField()
    instructor_name = models.CharField(max_length=100)
    starttime = models.TimeField()
    endtime = models.TimeField()
    start_time = models.CharField(max_length=5)
    end_time = models.CharField(max_length=5)
    start_hour = models.IntegerField()
    start_minute = models.IntegerField()
    max_capacity = models.IntegerField()
    enrolled_count = models.IntegerField()
    class_status = models.CharField(max_length=20)
    occupation_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    class Meta:
        managed = False
        db_table = 'vw_manager_class_schedule'

# Model for vw_manager_schedule_filters
class ManagerScheduleFilters(models.Model):
    filter_type = models.CharField(max_length=20, primary_key=True)
    filter_id = models.IntegerField(null=True, blank=True)
    filter_name = models.CharField(max_length=100)
    display_text = models.CharField(max_length=100)
    
    class Meta:
        managed = False
        db_table = 'vw_manager_schedule_filters'


# Model for vw_existing_classes
class ExistingClasses(models.Model):
    classid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    instructor_name = models.CharField(max_length=150)
    room = models.CharField(max_length=50)
    capacity = models.IntegerField()
    duration_minutes = models.IntegerField()
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_existing_classes'


# Model for vw_class_enrolled_members  
class ClassEnrolledMembers(models.Model):
    classscheduleid = models.IntegerField()
    member_name = models.CharField(max_length=150)
    memberid = models.IntegerField()
    email = models.CharField(max_length=254)
    phone = models.CharField(max_length=15)
    plan_name = models.CharField(max_length=100, null=True, blank=True)
    bookingdate = models.DateTimeField()
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_class_enrolled_members'


# Model for vw_member_data
class MemberData(models.Model):
    memberid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    registrationdate = models.DateField()
    subscriptionid = models.IntegerField(null=True, blank=True)
    startdate = models.DateField(null=True, blank=True)
    enddate = models.DateField(null=True, blank=True)
    subscription_active = models.BooleanField(null=True, blank=True)
    plan_name = models.CharField(max_length=100, null=True, blank=True)
    monthlyprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    userid = models.IntegerField()
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_member_data'


# Model for vw_classes_for_member
class ClassesForMember(models.Model):
    classscheduleid = models.IntegerField(primary_key=True)
    class_name = models.CharField(max_length=100)
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    room = models.CharField(max_length=50)
    instructor_name = models.CharField(max_length=150)
    available_spots = models.IntegerField()
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_classes_for_member'


# Model for vw_all_members
class AllMembers(models.Model):
    memberid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    registrationdate = models.DateField()
    isactive = models.BooleanField()
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_all_members'


# Model for vw_all_classes  
class AllClasses(models.Model):
    classscheduleid = models.IntegerField(primary_key=True)
    class_name = models.CharField(max_length=100)
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    instructor_name = models.CharField(max_length=150)
    room = models.CharField(max_length=50)
    max_participants = models.IntegerField()
    enrolled_count = models.IntegerField()
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_all_classes'


# Model for vw_instructor_daily_dashboard 
class InstructorDailyDashboard(models.Model):
    instructorid = models.IntegerField(primary_key=True)
    userid = models.IntegerField()
    instructor_name = models.CharField(max_length=150)
    classes_today = models.IntegerField()
    students_confirmed = models.IntegerField()
    occupation_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    next_class_time = models.CharField(max_length=5, null=True, blank=True)
    next_class_name = models.CharField(max_length=100, null=True, blank=True)
    next_class_room = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_instructor_daily_dashboard'


# Model for room conflict checking function
class RoomConflictCheck(models.Model):
    room = models.CharField(max_length=50)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    exclude_schedule_id = models.IntegerField(null=True, blank=True)
    has_conflict = models.BooleanField()
    
    class Meta:
        managed = False  # This represents a function call
        db_table = 'fn_check_room_conflict'


# Model for instructor conflict checking function  
class InstructorConflictCheck(models.Model):
    instructor_id = models.IntegerField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    exclude_schedule_id = models.IntegerField(null=True, blank=True)
    has_conflict = models.BooleanField()
    
    class Meta:
        managed = False  # This represents a function call
        db_table = 'fn_check_instructor_conflict'


# Complete model list for all database views:
# ✅ vw_user_authentication - UserAuthentication
# ✅ vw_email_exists - EmailExists  
# ✅ vw_plan - Plan
# ✅ vw_member_data - MemberData
# ✅ vw_member_stats_month - MemberStatsMonth
# ✅ vw_member_schedule_classes - MemberScheduleClasses
# ✅ vw_member_available_classes - MemberAvailableClasses
# ✅ vw_classes_for_member - ClassesForMember
# ✅ vw_member_account_details - MemberAccountDetails
# ✅ vw_instructor_info - InstructorInfo
# ✅ vw_instructor_classes - InstructorClasses
# ✅ vw_class_schedules - ClassSchedules
# ✅ vw_dashboard_stats - DashboardStats
# ✅ vw_all_members - AllMembers
# ✅ vw_all_classes - AllClasses
# ✅ vw_all_checkins - AllCheckins
# ✅ vw_machines - Machines
# ✅ vw_payments - Payments
# ✅ vw_member_payment_history - MemberPaymentHistory
# ✅ vw_member_checkin_history - MemberCheckinHistory
# ✅ vw_instructor_stats_month - InstructorMonthlyStats
# ✅ vw_instructor_daily_dashboard - InstructorDailyDashboard
# ✅ vw_instructor_classes_today - InstructorClassesToday
# ✅ vw_instructor_next_class_members - InstructorNextClassMembers
# ✅ vw_instructor_class_history - InstructorClassHistory
# ✅ vw_instructor_week_performance - InstructorWeekPerformance
# ✅ vw_instructor_popular_classes - InstructorPopularClasses
# ✅ vw_manager_members_management - ManagerMembersManagement
# ✅ vw_manager_class_schedule - ManagerClassSchedule
# ✅ vw_manager_schedule_filters - ManagerScheduleFilters
# ✅ vw_existing_classes - ExistingClasses
# ✅ vw_class_enrolled_members - ClassEnrolledMembers
# ✅ fn_check_room_conflict - RoomConflictCheck
# ✅ fn_check_instructor_conflict - InstructorConflictCheck
# ✅ vw_machine_summary - MachineSummary
# ✅ vw_machine_inventory - MachineInventory


# Model for vw_machine_summary
class MachineSummary(models.Model):
    id = models.IntegerField(primary_key=True, default=1)  # Fake ID for aggregation views
    total_machines = models.IntegerField()
    functioning_machines = models.IntegerField()
    maintenance_machines = models.IntegerField()
    out_of_service_machines = models.IntegerField()
    functioning_percentage = models.DecimalField(max_digits=5, decimal_places=1)
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_machine_summary'


# Model for vw_machine_inventory  
class MachineInventory(models.Model):
    machineid = models.IntegerField(primary_key=True)
    codigo = models.CharField(max_length=50)
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    data_aquisicao = models.DateField()
    ultima_manutencao = models.DateField()
    status = models.CharField(max_length=30)
    machinestatusid = models.IntegerField()
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_machine_inventory'


# Model para vw_machine_categories
class MachineCategories(models.Model):
    categoria = models.CharField(max_length=50, primary_key=True)
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_machine_categories'


# Model para vw_machine_brands
class MachineBrands(models.Model):
    marca = models.CharField(max_length=100, primary_key=True)
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_machine_brands'


# Model para vw_machine_statuses
class MachineStatuses(models.Model):
    machinestatusid = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=30)
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_machine_statuses'


# Model para vw_machine_detail
class MachineDetail(models.Model):
    machineid = models.IntegerField(primary_key=True)
    codigo = models.CharField(max_length=50)
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    data_aquisicao = models.DateField()
    ultima_manutencao = models.DateField()
    status = models.CharField(max_length=30)
    machinestatusid = models.IntegerField()
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_machine_detail'


# ======================================================================
# MODELS PARA GERENCIAMENTO DE PAGAMENTOS (DASHBOARD DE PAGAMENTOS)
# ======================================================================

# Model para vw_payment_dashboard_summary - Resumo dos 4 quadrados superiores
class PaymentDashboardSummary(models.Model):
    id = models.IntegerField(primary_key=True, default=1)  # Fake ID for Django ORM
    receita_mensal = models.DecimalField(max_digits=10, decimal_places=2)
    pagamentos_hoje = models.DecimalField(max_digits=10, decimal_places=2)
    transacoes_hoje = models.IntegerField()
    pendentes = models.DecimalField(max_digits=10, decimal_places=2)
    pagamentos_pendentes = models.IntegerField()
    em_atraso = models.DecimalField(max_digits=10, decimal_places=2)
    pagamentos_em_atraso = models.IntegerField()
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_payment_dashboard_summary'


# Model para vw_payment_recent_transactions - 3 últimos pagamentos recentes
class PaymentRecentTransactions(models.Model):
    paymentid = models.IntegerField(primary_key=True)
    valor = models.CharField(max_length=20)  # Formatado como "€XX.XX"
    nome_membro = models.CharField(max_length=100)
    id_membro = models.CharField(max_length=20)  # Formatado como "ID: XXXX"
    plano = models.CharField(max_length=100)
    metodo_pagamento = models.CharField(max_length=50)
    data_pagamento = models.DateField()
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_payment_recent_transactions'


# Model para vw_payment_history - Histórico completo com filtros
class PaymentHistory(models.Model):
    paymentid = models.IntegerField(primary_key=True)
    nome_membro = models.CharField(max_length=100)
    id_membro = models.IntegerField()
    plano = models.CharField(max_length=100)
    valor = models.CharField(max_length=20)  # Formatado como "€XX.XX"
    metodo_pagamento = models.CharField(max_length=50)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20)
    duedate = models.DateField()
    valor_numerico = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_payment_history'


# Model para vw_payment_monthly_summary - Resumo mensal para quadrados inferiores
class PaymentMonthlySummary(models.Model):
    id = models.IntegerField(primary_key=True)  # Fake ID for Django ORM
    total_faturado = models.DecimalField(max_digits=10, decimal_places=2)
    total_recebido = models.DecimalField(max_digits=10, decimal_places=2)
    pendentes = models.DecimalField(max_digits=10, decimal_places=2)
    em_atraso = models.DecimalField(max_digits=10, decimal_places=2)
    metodos_pagamento = models.TextField(null=True, blank=True)  # String dinâmica com métodos
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_payment_monthly_summary'

# ============================================================================
# MODELS PARA GERENCIAMENTO DE PLANOS
# ============================================================================

# Model para vw_plan_statistics - Estatísticas dos planos (4 quadrados do topo)
class PlanStatistics(models.Model):
    planid = models.IntegerField(primary_key=True)
    plan_name = models.CharField(max_length=100)
    monthlyprice = models.DecimalField(max_digits=10, decimal_places=2)
    access24h = models.BooleanField()
    member_count = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=1)
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_plan_statistics'

# Model para vw_total_active_members - Total de membros ativos (4º quadrado)
class TotalActiveMembers(models.Model):
    total_members = models.IntegerField(primary_key=True)
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_total_active_members'

# Model para vw_plan_details - Detalhes dos planos (cartas inferiores)
class PlanDetails(models.Model):
    planid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    monthlyprice = models.DecimalField(max_digits=10, decimal_places=2)
    access24h = models.BooleanField()
    description = models.TextField(null=True, blank=True)
    member_count = models.IntegerField()
    price_display = models.CharField(max_length=20)  # Formatado como "€XX/mês"
    
    class Meta:
        managed = False  # This is a database view
        db_table = 'vw_plan_details'

