DO $$
BEGIN

  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'gestor_db') THEN
    REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM gestor_db;
    REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM gestor_db;
    REVOKE ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public FROM gestor_db;
    REVOKE ALL ON SCHEMA public FROM gestor_db;
    REVOKE CONNECT ON DATABASE postgres FROM gestor_db;
  ELSE
    CREATE ROLE gestor_db LOGIN PASSWORD 'Deloitte@303';
  END IF;

  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'instrutor_db') THEN
    REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM instrutor_db;
    REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM instrutor_db;
    REVOKE ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public FROM instrutor_db;
    REVOKE ALL ON SCHEMA public FROM instrutor_db;
    REVOKE CONNECT ON DATABASE postgres FROM instrutor_db;
  ELSE
    CREATE ROLE instrutor_db LOGIN PASSWORD 'Deloitte@303';
  END IF;

  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'membro_db') THEN
    REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM membro_db;
    REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM membro_db;
    REVOKE ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public FROM membro_db;
    REVOKE ALL ON SCHEMA public FROM membro_db;
    REVOKE CONNECT ON DATABASE postgres FROM membro_db;
  ELSE
    CREATE ROLE membro_db LOGIN PASSWORD 'Deloitte@303';
  END IF;

  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'guest_db') THEN
    REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM guest_db;
    REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM guest_db;
    REVOKE ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public FROM guest_db;
    REVOKE ALL ON SCHEMA public FROM guest_db;
    REVOKE CONNECT ON DATABASE postgres FROM guest_db;
  ELSE
    CREATE ROLE guest_db LOGIN PASSWORD 'Deloitte@303';
  END IF;

END$$;

GRANT CONNECT ON DATABASE postgres TO gestor_db, instrutor_db, membro_db, guest_db;
GRANT USAGE ON SCHEMA public TO gestor_db, instrutor_db, membro_db, guest_db;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO gestor_db;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO gestor_db;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO gestor_db;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO gestor_db;

-- Views específicas para gestores 
GRANT SELECT ON 
  vw_dashboard_stats,
  vw_manager_members_management,
  vw_manager_class_schedule,
  vw_manager_schedule_filters,
  vw_existing_classes,
  vw_class_enrolled_members,
  vw_machine_summary,
  vw_machine_inventory,
  vw_machine_categories,
  vw_machine_brands,
  vw_machine_statuses,
  vw_machine_detail,
  vw_payment_dashboard_summary,
  vw_payment_recent_transactions,
  vw_payment_history,
  vw_payment_monthly_summary,
  vw_total_active_members,
  vw_plan_statistics,
  vw_plan_details,
  vw_manager_recent_checkins,
  vw_manager_upcoming_classes,
  vw_manager_dashboard_stats
TO gestor_db;

GRANT USAGE, SELECT ON SEQUENCE
  users_userid_seq,
  member_memberid_seq,
  membersubscription_subscriptionid_seq
TO gestor_db;

GRANT EXECUTE ON FUNCTION
  fn_generate_financial_report
  TO gestor_db;


GRANT SELECT ON
  member, membersubscription, plan, payment,
  class, classbooking, classschedule, checkin
TO membro_db;

GRANT INSERT, UPDATE, DELETE ON
  member, membersubscription, classbooking, users
TO membro_db;

-- Views específicas para membros
GRANT SELECT ON
  vw_member_data,
  vw_member_stats_month,
  vw_member_schedule_classes,
  vw_member_available_classes,
  vw_member_account_details,
  vw_member_payment_history,
  vw_member_checkin_history,
  vw_member_userid_lookup,
  vw_member_enrolled_classes,
  vw_user_password_check,
  vw_member_class_history,
  vw_member_class_evaluation_details
TO membro_db;

-- Tabelas adicionais necessárias para views
GRANT SELECT ON
  users, usertype, instructor
TO membro_db;

GRANT UPDATE ON users, payment TO membro_db;

GRANT USAGE, SELECT ON SEQUENCE
  member_memberid_seq,
  membersubscription_subscriptionid_seq,
  classbooking_bookingid_seq
TO membro_db;

-- Permissões para procedimentos do membro
GRANT EXECUTE ON FUNCTION 
  fn_check_room_conflict,
  fn_check_instructor_conflict
TO membro_db;

GRANT EXECUTE ON PROCEDURE 
sp_book_class,
sp_member_update_profile,
sp_change_user_password,
sp_process_member_payment,
sp_update_last_login TO membro_db;

GRANT SELECT ON
  instructor, class, classschedule, machine,
  machinemaintenancelog, classbooking
TO instrutor_db;

GRANT INSERT, UPDATE, DELETE ON
  instructor, class, classschedule, users
TO instrutor_db;

-- Views específicas para instrutores
GRANT SELECT ON
  vw_instructor_info,
  vw_instructor_classes,
  vw_instructor_stats_month,
  vw_instructor_daily_dashboard,
  vw_instructor_classes_today,
  vw_instructor_next_class_members,
  vw_instructor_class_history,
  vw_instructor_week_performance,
  vw_instructor_popular_classes,
  vw_user_password_check
TO instrutor_db;

-- Tabelas adicionais necessárias para views
GRANT SELECT ON
  users, usertype, member, payment
TO instrutor_db;

GRANT UPDATE (last_login) ON users TO instrutor_db;

GRANT USAGE, SELECT ON SEQUENCE
  instructor_instructorid_seq,
  class_classid_seq,
  classschedule_classscheduleid_seq
TO instrutor_db;

-- Permissões para procedimentos do instrutor
GRANT EXECUTE ON FUNCTION 
  fn_check_room_conflict,
  fn_check_instructor_conflict
TO instrutor_db;

GRANT EXECUTE ON PROCEDURE 
  sp_update_last_login,
  sp_instructor_update_profile
TO instrutor_db;

-- Views para login e registro
GRANT SELECT ON 
  vw_user_authentication, 
  vw_email_exists,
  vw_plan
TO guest_db;

-- Tabelas básicas para registro de novos membros
GRANT SELECT ON 
  USERS, USERTYPE, PLAN
TO guest_db;

GRANT UPDATE ON USERS TO guest_db;
GRANT INSERT ON USERS, MEMBER, MEMBERSUBSCRIPTION TO guest_db;

-- Permissões para sequences necessárias para inserir dados
GRANT USAGE, SELECT ON SEQUENCE
  USERS_USERID_SEQ,
  MEMBER_MEMBERID_SEQ,
  MEMBERSUBSCRIPTION_SUBSCRIPTIONID_SEQ
TO guest_db;

-- Permissões para procedimentos do guest

GRANT EXECUTE ON PROCEDURE 
  sp_create_member,
  sp_update_last_login
TO guest_db;


GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO gestor_db;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT EXECUTE ON FUNCTIONS TO gestor_db;

