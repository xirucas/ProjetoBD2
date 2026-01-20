from django.db import models

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

class Plan(models.Model):
    planid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    monthlyprice = models.DecimalField(max_digits=10, decimal_places=2)
    access24h = models.BooleanField()
    
    class Meta:
        managed = False
        db_table = 'vw_plan'

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

class EmailExists(models.Model):
    userid = models.AutoField(primary_key=True)
    email = models.CharField(max_length=254)
    
    class Meta:
        managed = False
        db_table = 'vw_email_exists'

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

class InstructorClasses(models.Model):
    classid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    room = models.CharField(max_length=50)
    capacity = models.IntegerField()
    duration_minutes = models.IntegerField()
    instructorid = models.IntegerField()
    userid = models.IntegerField()
    classscheduleid = models.IntegerField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    starttime = models.TimeField(null=True, blank=True)
    endtime = models.TimeField(null=True, blank=True)
    start_time = models.CharField(max_length=5, null=True, blank=True) 
    end_time = models.CharField(max_length=5, null=True, blank=True)   
    day_of_week = models.IntegerField(null=True, blank=True)  
    current_participants = models.IntegerField(null=True, blank=True)
    max_participants = models.IntegerField(null=True, blank=True)
    maxparticipants = models.IntegerField(null=True, blank=True)  
    isactive = models.BooleanField(default=True)
    
    class Meta:
        managed = False
        db_table = 'vw_instructor_classes'

class InstructorClassesToday(models.Model):
    classid = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=100)
    room = models.CharField(max_length=50)
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    maxparticipants = models.IntegerField()
    enrolled_students = models.IntegerField()
    instructorid = models.IntegerField()
    userid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'vw_instructor_classes_today'

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

class DashboardStats(models.Model):
    total_members = models.IntegerField()
    total_instructors = models.IntegerField()
    active_memberships = models.IntegerField()
    today_checkins = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_dashboard_stats'

class AllCheckins(models.Model):
    checkinid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date = models.DateField()
    entrancetime = models.TimeField()
    exittime = models.TimeField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'vw_all_checkins'

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

class InstructorClassHistory(models.Model):
    date = models.DateField()
    schedule = models.CharField(max_length=11)
    class_name = models.CharField(max_length=100)
    room = models.CharField(max_length=50)
    enrolled = models.IntegerField()
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    instructorid = models.IntegerField()
    instructor_userid = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_instructor_class_history'

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
    member_gender = models.CharField(max_length=10)
    member_birthdate = models.DateField()
    member_address = models.CharField(max_length=255)
    member_nif = models.CharField(max_length=15)
    member_city = models.CharField(max_length=100)
    member_postalcode = models.CharField(max_length=20)
    member_iban = models.CharField(max_length=34)
    status = models.CharField(max_length=20)
    member_registration_date = models.DateField()
    planid = models.IntegerField()
    total_members = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'vw_manager_members_management'

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

class ManagerScheduleFilters(models.Model):
    filter_type = models.CharField(max_length=20, primary_key=True)
    filter_id = models.IntegerField(null=True, blank=True)
    filter_name = models.CharField(max_length=100)
    display_text = models.CharField(max_length=100)
    
    class Meta:
        managed = False
        db_table = 'vw_manager_schedule_filters'

class ExistingClasses(models.Model):
    classid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    instructor_name = models.CharField(max_length=150)
    room = models.CharField(max_length=50)
    capacity = models.IntegerField()
    duration_minutes = models.IntegerField()
    
    class Meta:
        managed = False  
        db_table = 'vw_existing_classes'

class ClassEnrolledMembers(models.Model):
    classscheduleid = models.IntegerField()
    member_name = models.CharField(max_length=150)
    memberid = models.IntegerField()
    email = models.CharField(max_length=254)
    phone = models.CharField(max_length=15)
    plan_name = models.CharField(max_length=100, null=True, blank=True)
    bookingdate = models.DateTimeField()
    
    class Meta:
        managed = False  
        db_table = 'vw_class_enrolled_members'

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
        managed = False  
        db_table = 'vw_member_data'

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
        managed = False  
        db_table = 'vw_classes_for_member'

class AllMembers(models.Model):
    memberid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    registrationdate = models.DateField()
    isactive = models.BooleanField()
    
    class Meta:
        managed = False  
        db_table = 'vw_all_members'

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
        managed = False  
        db_table = 'vw_all_classes'

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
        managed = False  
        db_table = 'vw_instructor_daily_dashboard'

class RoomConflictCheck(models.Model):
    room = models.CharField(max_length=50)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    exclude_schedule_id = models.IntegerField(null=True, blank=True)
    has_conflict = models.BooleanField()
    
    class Meta:
        managed = False  
        db_table = 'fn_check_room_conflict'

class InstructorConflictCheck(models.Model):
    instructor_id = models.IntegerField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    exclude_schedule_id = models.IntegerField(null=True, blank=True)
    has_conflict = models.BooleanField()
    
    class Meta:
        managed = False  
        db_table = 'fn_check_instructor_conflict'

class MachineSummary(models.Model):
    id = models.IntegerField(primary_key=True, default=1) 
    total_machines = models.IntegerField()
    functioning_machines = models.IntegerField()
    maintenance_machines = models.IntegerField()
    out_of_service_machines = models.IntegerField()
    functioning_percentage = models.DecimalField(max_digits=5, decimal_places=1)
    
    class Meta:
        managed = False  
        db_table = 'vw_machine_summary'

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
        managed = False  
        db_table = 'vw_machine_inventory'

class MachineCategories(models.Model):
    categoria = models.CharField(max_length=50, primary_key=True)
    
    class Meta:
        managed = False  
        db_table = 'vw_machine_categories'

class MachineBrands(models.Model):
    marca = models.CharField(max_length=100, primary_key=True)
    
    class Meta:
        managed = False  
        db_table = 'vw_machine_brands'

class MachineStatuses(models.Model):
    machinestatusid = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=30)
    
    class Meta:
        managed = False  
        db_table = 'vw_machine_statuses'

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
        managed = False  
        db_table = 'vw_machine_detail'

class PaymentDashboardSummary(models.Model):
    id = models.IntegerField(primary_key=True, default=1)  
    receita_mensal = models.DecimalField(max_digits=10, decimal_places=2)
    pagamentos_hoje = models.DecimalField(max_digits=10, decimal_places=2)
    transacoes_hoje = models.IntegerField()
    pendentes = models.DecimalField(max_digits=10, decimal_places=2)
    pagamentos_pendentes = models.IntegerField()
    em_atraso = models.DecimalField(max_digits=10, decimal_places=2)
    pagamentos_em_atraso = models.IntegerField()
    
    class Meta:
        managed = False  
        db_table = 'vw_payment_dashboard_summary'

class PaymentRecentTransactions(models.Model):
    paymentid = models.IntegerField(primary_key=True)
    valor = models.CharField(max_length=20) 
    nome_membro = models.CharField(max_length=100)
    id_membro = models.CharField(max_length=20) 
    plano = models.CharField(max_length=100)
    metodo_pagamento = models.CharField(max_length=50)
    data_pagamento = models.DateField()
    
    class Meta:
        managed = False  
        db_table = 'vw_payment_recent_transactions'

class PaymentHistory(models.Model):
    paymentid = models.IntegerField(primary_key=True)
    nome_membro = models.CharField(max_length=100)
    id_membro = models.IntegerField()
    plano = models.CharField(max_length=100)
    valor = models.CharField(max_length=20)  
    metodo_pagamento = models.CharField(max_length=50)
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20)
    duedate = models.DateField()
    valor_numerico = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        managed = False  
        db_table = 'vw_payment_history'


class PaymentMonthlySummary(models.Model):
    id = models.IntegerField(primary_key=True)  # Fake ID for Django ORM
    total_faturado = models.DecimalField(max_digits=10, decimal_places=2)
    total_recebido = models.DecimalField(max_digits=10, decimal_places=2)
    pendentes = models.DecimalField(max_digits=10, decimal_places=2)
    em_atraso = models.DecimalField(max_digits=10, decimal_places=2)
    metodos_pagamento = models.TextField(null=True, blank=True) 
    
    class Meta:
        managed = False  
        db_table = 'vw_payment_monthly_summary'

class PlanStatistics(models.Model):
    planid = models.IntegerField(primary_key=True)
    plan_name = models.CharField(max_length=100)
    monthlyprice = models.DecimalField(max_digits=10, decimal_places=2)
    access24h = models.BooleanField()
    member_count = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=1)
    
    class Meta:
        managed = False  
        db_table = 'vw_plan_statistics'

class TotalActiveMembers(models.Model):
    total_members = models.IntegerField(primary_key=True)
    
    class Meta:
        managed = False  
        db_table = 'vw_total_active_members'

class PlanDetails(models.Model):
    planid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    monthlyprice = models.DecimalField(max_digits=10, decimal_places=2)
    access24h = models.BooleanField()
    description = models.TextField(null=True, blank=True)
    member_count = models.IntegerField()
    price_display = models.CharField(max_length=20)  
    
    class Meta:
        managed = False  
        db_table = 'vw_plan_details'

class MemberUseridLookup(models.Model):
    memberid = models.IntegerField(primary_key=True)
    userid = models.IntegerField()
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=254)
    
    class Meta:
        managed = False
        db_table = 'vw_member_userid_lookup'

class MemberEnrolledClasses(models.Model):
    memberid = models.IntegerField()
    classscheduleid = models.IntegerField(primary_key=True)
    bookingdate = models.DateTimeField()
    class_name = models.CharField(max_length=100)
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    
    class Meta:
        managed = False
        db_table = 'vw_member_enrolled_classes'

class UserPasswordCheck(models.Model):
    userid = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=255)
    isactive = models.BooleanField()
    
    class Meta:
        managed = False
        db_table = 'vw_user_password_check'

class MemberClassHistory(models.Model):
    classscheduleid = models.IntegerField(primary_key=True)
    class_name = models.CharField(max_length=80)
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    room = models.CharField(max_length=20)
    instructor_name = models.CharField(max_length=120)
    class_description = models.TextField(null=True, blank=True)
    userid = models.IntegerField()
    memberid = models.IntegerField()
    booking_date = models.DateTimeField()
    
    class Meta:
        managed = False
        db_table = 'vw_member_class_history'

class MemberClassEvaluationDetails(models.Model):
    classscheduleid = models.IntegerField(primary_key=True)
    instructorid = models.IntegerField()
    class_name = models.CharField(max_length=100)
    member_name = models.CharField(max_length=100)
    memberid = models.IntegerField()
    booking_memberid = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_member_class_evaluation_details'

class ManagerRecentCheckins(models.Model):
    checkinid = models.AutoField(primary_key=True)
    member_name = models.CharField(max_length=100)
    memberid = models.IntegerField()
    entrancetime = models.TimeField()
    exittime = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20)
    
    class Meta:
        managed = False
        db_table = 'vw_manager_recent_checkins'

class ManagerUpcomingClasses(models.Model):
    classid = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=100)
    starttime = models.TimeField()
    endtime = models.TimeField()
    instructor_name = models.CharField(max_length=100)
    instructorid = models.IntegerField()
    room = models.CharField(max_length=50)
    maxcapacity = models.IntegerField()
    enrolled_count = models.IntegerField()
    is_full = models.BooleanField()
    
    class Meta:
        managed = False
        db_table = 'vw_manager_upcoming_classes'

class ManagerDashboardStats(models.Model):
    total_members = models.IntegerField()
    total_instructors = models.IntegerField()
    active_memberships = models.IntegerField()
    today_checkins = models.IntegerField()
    today_classes = models.IntegerField()
    monthly_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        managed = False
        db_table = 'vw_manager_dashboard_stats'
