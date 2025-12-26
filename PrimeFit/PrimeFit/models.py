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
    userid = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_instructor_info'

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

# Model for vw_all_members
class AllMembers(models.Model):
    memberid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=254)
    phone = models.CharField(max_length=15)
    registrationdate = models.DateField()
    isactive = models.BooleanField()
    startdate = models.DateField(null=True, blank=True)
    enddate = models.DateField(null=True, blank=True)
    plan_name = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'vw_all_members'

# Model for vw_all_classes
class AllClasses(models.Model):
    classscheduleid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    instructor_name = models.CharField(max_length=100)
    date = models.DateField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    room = models.CharField(max_length=50)
    maxparticipants = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'vw_all_classes'

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

# Model for vw_machines
class Machines(models.Model):
    machineid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    manufacturer = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    installationdate = models.DateField()
    maintenancedate = models.DateField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'vw_machines'

# Model for vw_payments
class Payments(models.Model):
    paymentid = models.AutoField(primary_key=True)
    member_name = models.CharField(max_length=100)
    plan_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duedate = models.DateField()
    paymentdate = models.DateField(null=True, blank=True)
    ispayed = models.BooleanField()
    paymentmethod = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'vw_payments'

# Model for vw_plans
class Plans(models.Model):
    planid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    monthlyprice = models.DecimalField(max_digits=10, decimal_places=2)
    access24h = models.BooleanField()
    description = models.TextField(null=True, blank=True)
    isactive = models.BooleanField()
    
    class Meta:
        managed = False
        db_table = 'vw_plans'

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
