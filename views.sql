DROP VIEW IF EXISTS vw_user_authentication;
DROP VIEW IF EXISTS vw_email_exists;
DROP VIEW IF EXISTS vw_plan;
DROP VIEW IF EXISTS vw_member_data;
DROP VIEW IF EXISTS vw_member_stats_month;
DROP VIEW IF EXISTS vw_member_schedule_classes;
DROP VIEW IF EXISTS vw_member_available_classes;
DROP VIEW IF EXISTS vw_classes_for_member;
DROP VIEW IF EXISTS vw_member_account_details;
DROP VIEW IF EXISTS vw_instructor_info;
DROP VIEW IF EXISTS vw_instructor_classes;
DROP VIEW IF EXISTS vw_class_schedules;
DROP VIEW IF EXISTS vw_dashboard_stats;
DROP VIEW IF EXISTS vw_all_members;
DROP VIEW IF EXISTS vw_all_classes;
DROP VIEW IF EXISTS vw_all_checkins;
DROP VIEW IF EXISTS vw_machines;
DROP VIEW IF EXISTS vw_member_payment_history;
DROP VIEW IF EXISTS vw_member_checkin_history;
DROP VIEW IF EXISTS vw_instructor_stats_month;
DROP VIEW IF EXISTS vw_instructor_daily_dashboard;
DROP VIEW IF EXISTS vw_instructor_classes_today;
DROP VIEW IF EXISTS vw_instructor_next_class_members;
DROP VIEW IF EXISTS vw_instructor_class_history;
DROP VIEW IF EXISTS vw_instructor_week_performance;
DROP VIEW IF EXISTS vw_instructor_popular_classes;
DROP VIEW IF EXISTS vw_manager_members_management;
DROP VIEW IF EXISTS vw_manager_class_schedule;
DROP VIEW IF EXISTS vw_manager_schedule_filters;
DROP VIEW IF EXISTS vw_machine_categories;
DROP VIEW IF EXISTS vw_machine_brands;
DROP VIEW IF EXISTS vw_machine_statuses;
DROP VIEW IF EXISTS vw_manager_machines;
DROP VIEW IF EXISTS vw_machine_summary;
DROP VIEW IF EXISTS vw_machine_inventory;
DROP VIEW IF EXISTS vw_payment_dashboard_summary;
DROP VIEW IF EXISTS vw_payment_recent_transactions;
DROP VIEW IF EXISTS vw_payment_history;
DROP VIEW IF EXISTS vw_payment_monthly_summary;
DROP VIEW IF EXISTS vw_plan_statistics;
DROP VIEW IF EXISTS vw_plan_details;
DROP VIEW IF EXISTS vw_plan_membership_summary;
DROP VIEW IF EXISTS vw_total_active_members;
DROP VIEW IF EXISTS vw_member_userid_lookup;
DROP VIEW IF EXISTS vw_member_enrolled_classes;
DROP VIEW IF EXISTS vw_user_password_check;
DROP VIEW IF EXISTS vw_member_class_history;
DROP VIEW IF EXISTS vw_member_class_evaluation_details;
DROP VIEW IF EXISTS vw_manager_recent_checkins;
DROP VIEW IF EXISTS vw_manager_upcoming_classes;
DROP VIEW IF EXISTS vw_manager_dashboard_stats;

-- View for user authentication with user type information
CREATE OR REPLACE VIEW vw_user_authentication AS
SELECT 
    u.userid,
    u.email,
    u.name,
    u.password,
    u.usertypeid,
    u.isactive,
    ut.label AS user_type_label
FROM users u
JOIN usertype ut ON u.usertypeid = ut.usertypeid
WHERE u.isactive = true;

-- View for checking if email exists during registration
CREATE OR REPLACE VIEW vw_email_exists AS
SELECT userid, email
FROM users;

CREATE OR REPLACE VIEW vw_plan AS 
SELECT planid, name, monthlyprice, access24h
FROM plan;

-- View for member home page data
CREATE OR REPLACE VIEW vw_member_data AS
SELECT 
    m.memberid, 
    u.name, 
    u.email, 
    m.registrationdate,
    ms.subscriptionid, 
    ms.startdate, 
    ms.enddate, 
    ms.isactive as subscription_active,
    p.name as plan_name, 
    p.monthlyprice,
    m.userid
FROM member m
LEFT JOIN membersubscription ms ON m.memberid = ms.memberid AND ms.isactive = true
LEFT JOIN plan p ON ms.planid = p.planid
LEFT JOIN users u ON m.userid = u.userid
WHERE m.isactive = true;

-- View for member stats current month
CREATE OR REPLACE VIEW vw_member_stats_month AS
SELECT 
    COUNT(DISTINCT c.checkinid) AS checkin_count,
    COUNT(DISTINCT cb.bookingid) AS class_bookings,
    SUM(EXTRACT(EPOCH FROM (c.exittime - c.entrancetime)) / 3600) AS total_hours,
    MIN(pay.duedate) AS next_payment,
    pl.monthlyprice AS payment_price,
    m.memberid,
    m.userid AS userid
FROM member m
LEFT JOIN checkin c ON c.memberid = m.memberid 
    AND c.date >= DATE_TRUNC('month', CURRENT_DATE) 
    AND c.date <= CURRENT_DATE
LEFT JOIN classbooking cb ON cb.memberid = m.memberid 
    AND cb.bookingdate >= DATE_TRUNC('month', CURRENT_DATE) 
    AND cb.bookingdate <= CURRENT_TIMESTAMP
LEFT JOIN membersubscription ms ON ms.memberid = m.memberid AND ms.isactive = true
LEFT JOIN plan pl ON ms.planid = pl.planid
LEFT JOIN payment pay ON pay.subscriptionid = ms.subscriptionid 
    AND pay.ispayed = false 
    AND pay.duedate >= DATE_TRUNC('month', CURRENT_DATE)
WHERE m.isactive = true
GROUP BY m.memberid, m.userid, pl.monthlyprice;

CREATE OR REPLACE VIEW vw_member_schedule_classes AS
SELECT 
    c.name AS class_name, 
    cs.date, 
    cs.starttime, 
    cs.endtime,
    c.room,
    u.name AS instructor_name,
    m.userid
FROM classschedule cs
LEFT JOIN class c ON cs.classid = c.classid
LEFT JOIN instructor i ON c.instructorid = i.instructorid
LEFT JOIN users u ON i.userid = u.userid
LEFT JOIN classbooking cb ON cs.classscheduleid = cb.classscheduleid
LEFT JOIN member m ON cb.memberid = m.memberid
WHERE cs.isactive = true and cs.date >= CURRENT_DATE;

-- View for classes available today (can be filtered by member to exclude already booked classes)
CREATE OR REPLACE VIEW vw_member_available_classes AS
SELECT 
    cs.classscheduleid,
    c.name AS class_name, 
    c.room, 
    c.capacity, 
    c.duration_minutes,
    u.name AS instructor_name,
    cs.date,
    cs.starttime,
    cs.endtime,
    cs.maxparticipants,
    COALESCE(booking_count.total_bookings, 0) AS current_bookings,
    (cs.maxparticipants - COALESCE(booking_count.total_bookings, 0)) AS available_spots

FROM classschedule cs
JOIN class c ON cs.classid = c.classid AND c.isactive = true
JOIN instructor i ON c.instructorid = i.instructorid
JOIN users u ON i.userid = u.userid
LEFT JOIN (
    SELECT 
        classscheduleid, 
        COUNT(*) as total_bookings
    FROM classbooking 
    GROUP BY classscheduleid
) booking_count ON cs.classscheduleid = booking_count.classscheduleid
WHERE cs.isactive = true 
    AND cs.date = CURRENT_DATE 
    AND cs.starttime > CURRENT_TIME
    AND (cs.maxparticipants - COALESCE(booking_count.total_bookings, 0)) > 0;

-- View for classes available for a specific member (excluding already booked classes)
CREATE OR REPLACE VIEW vw_classes_for_member AS
SELECT 
    cs.classscheduleid,
    c.name AS class_name, 
    c.room, 
    c.capacity, 
    c.duration_minutes,
    u.name AS instructor_name,
    cs.date,
    cs.starttime,
    cs.endtime,
    cs.maxparticipants,
    COALESCE(booking_count.total_bookings, 0) AS current_bookings,
    (cs.maxparticipants - COALESCE(booking_count.total_bookings, 0)) AS available_spots,
    m.memberid,
    m.userid

FROM classschedule cs
JOIN class c ON cs.classid = c.classid AND c.isactive = true
JOIN instructor i ON c.instructorid = i.instructorid
JOIN users u ON i.userid = u.userid
CROSS JOIN member m
LEFT JOIN (
    SELECT 
        classscheduleid, 
        COUNT(*) as total_bookings
    FROM classbooking 
    GROUP BY classscheduleid
) booking_count ON cs.classscheduleid = booking_count.classscheduleid
LEFT JOIN classbooking existing_booking ON cs.classscheduleid = existing_booking.classscheduleid 
    AND existing_booking.memberid = m.memberid
WHERE cs.isactive = true 
    AND m.isactive = true
    AND cs.date = CURRENT_DATE
    AND (cs.maxparticipants - COALESCE(booking_count.total_bookings, 0)) > 0
    AND existing_booking.bookingid IS NULL; 

-- View for member account details
CREATE OR REPLACE VIEW vw_member_account_details AS
SELECT 
    m.memberid, 
    u.name, 
    m.nif, 
    u.email, 
    m.phone, 
    m.iban,
    m.birthdate,
    m.gender,
    m.address,
    m.city,
    m.postalcode,
    m.registrationdate,
    ms.startdate, 
    ms.enddate, 
    CASE 
        WHEN pt.ispayed = true THEN NULL  -- Se já foi pago, retorna NULL
        WHEN pt.duedate < CURRENT_DATE THEN NULL  -- Se está em atraso, não mostra
        ELSE pt.duedate  -- Só mostra pagamentos futuros pendentes
    END as next_payment_date,
    p.name as plan_name, 
    p.monthlyprice, 
    p.access24h,
    m.userid
FROM member m
LEFT JOIN membersubscription ms ON m.memberid = ms.memberid AND ms.isactive = true
LEFT JOIN plan p ON ms.planid = p.planid
LEFT JOIN users u ON m.userid = u.userid
LEFT JOIN payment pt ON ms.subscriptionid = pt.subscriptionid 
    AND pt.ispayed = false  -- Só pagamentos não pagos
    AND pt.duedate >= CURRENT_DATE;  -- Só pagamentos futuros ou de hoje


-- View for instructor account information
CREATE OR REPLACE VIEW vw_instructor_info AS
SELECT 
    i.instructorid, 
    u.name, 
    i.nif, 
    u.email, 
    i.phone, 
    i.isactive,
    i.created_at as hired_at,
    i.userid
FROM instructor i
LEFT JOIN users u ON i.userid = u.userid;

-- View for instructor classes with weekly schedule
CREATE OR REPLACE VIEW vw_instructor_classes AS
SELECT 
    c.classid, 
    c.name, 
    c.room, 
    c.capacity, 
    c.duration_minutes,
    c.instructorid,
    i.userid,
    cs.classscheduleid,
    cs.date,
    cs.starttime,
    cs.endtime,
    cs.maxparticipants,
    EXTRACT(DOW FROM cs.date) as day_of_week,
    TO_CHAR(cs.date, 'Day') as day_name,
    TO_CHAR(cs.starttime, 'HH24:MI') as start_time,
    TO_CHAR(cs.endtime, 'HH24:MI') as end_time,
    COALESCE(booking_count.current_participants, 0) as current_participants,
    cs.maxparticipants as max_participants
FROM class c
JOIN instructor i ON c.instructorid = i.instructorid
LEFT JOIN classschedule cs ON c.classid = cs.classid 
LEFT JOIN (
    SELECT 
        classscheduleid,
        COUNT(*) as current_participants
    FROM classbooking 
    GROUP BY classscheduleid
) booking_count ON cs.classscheduleid = booking_count.classscheduleid
WHERE c.isactive = true 
  AND cs.classscheduleid IS NOT NULL
  AND (cs.isactive = true OR cs.isactive IS NULL)
  AND cs.date >= date_trunc('week', CURRENT_DATE)  -- Início da semana (segunda-feira)
  AND cs.date < date_trunc('week', CURRENT_DATE) + INTERVAL '7 days';  -- Fim da semana (domingo)

-- View for class schedules with instructor info
CREATE OR REPLACE VIEW vw_class_schedules AS
SELECT 
    cs.classscheduleid, 
    c.name, 
    cs.date, 
    cs.starttime, 
    cs.endtime,
    cs.maxparticipants, 
    c.room,
    c.instructorid,
    i.userid
FROM classschedule cs
JOIN class c ON cs.classid = c.classid
JOIN instructor i ON c.instructorid = i.instructorid
WHERE cs.isactive = true;

-- View for dashboard statistics
CREATE OR REPLACE VIEW vw_dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM member WHERE isactive = true) as total_members,
    (SELECT COUNT(*) FROM instructor WHERE isactive = true) as total_instructors,
    (SELECT COUNT(*) FROM membersubscription WHERE isactive = true) as active_memberships,
    (SELECT COUNT(*) FROM checkin WHERE date = CURRENT_DATE) as today_checkins;

-- View for all members with subscription info
CREATE OR REPLACE VIEW vw_all_members AS
SELECT 
    m.memberid, 
    u.name, 
    u.email, 
    m.phone, 
    m.registrationdate, 
    m.isactive,
    ms.startdate, 
    ms.enddate, 
    p.name as plan_name
FROM member m
LEFT JOIN membersubscription ms ON m.memberid = ms.memberid AND ms.isactive = true
LEFT JOIN plan p ON ms.planid = p.planid
LEFT JOIN users u ON m.userid = u.userid;

-- View for all classes with instructor info
CREATE OR REPLACE VIEW vw_all_classes AS
SELECT 
    cs.classscheduleid, 
    c.name, 
    u.name as instructor_name,
    cs.date, 
    cs.starttime, 
    cs.endtime, 
    c.room, 
    cs.maxparticipants
FROM classschedule cs
JOIN class c ON cs.classid = c.classid
JOIN instructor i ON c.instructorid = i.instructorid
JOIN users u ON i.userid = u.userid
WHERE cs.isactive = true;

-- View for all check-ins with member info
CREATE OR REPLACE VIEW vw_all_checkins AS
SELECT 
    c.checkinid, 
    u.name, 
    c.date, 
    c.entrancetime, 
    c.exittime
FROM checkin c
JOIN member m ON c.memberid = m.memberid
JOIN users u ON m.userid = u.userid;

-- View for machines with status
CREATE OR REPLACE VIEW vw_machines AS
SELECT 
    m.machineid, 
    m.name, 
    m.type, 
    m.manufacturer, 
    m.model,
    ms.status, 
    m.installationdate, 
    m.maintenancedate
FROM machine m
JOIN machinestatus ms ON m.machinestatusid = ms.machinestatusid;


-- View for member payment history
CREATE OR REPLACE VIEW vw_member_payment_history AS
SELECT 
    p.paymentid,
    p.duedate as payment_date,
    p.amount as payment_amount,
    p.paymentmethod,
    CASE 
        WHEN p.ispayed = true THEN 'Pago'
        WHEN p.duedate < CURRENT_DATE THEN 'Em Atraso'
        ELSE 'Pendente'
    END as payment_status,
    p.paymentdate,
    ms.memberid,
    m.userid
FROM payment p
JOIN membersubscription ms ON p.subscriptionid = ms.subscriptionid
JOIN member m ON ms.memberid = m.memberid
ORDER BY p.duedate DESC;

-- View for member checkin history
CREATE OR REPLACE VIEW vw_member_checkin_history AS
SELECT 
    c.checkinid,
    c.date as checkin_date,
    c.entrancetime,
    c.exittime,
    CASE 
        WHEN c.exittime IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (c.exittime - c.entrancetime)) / 3600
        ELSE NULL
    END as duration_hours,
    CASE 
        WHEN c.exittime IS NOT NULL THEN 
            CONCAT(
                EXTRACT(HOUR FROM (c.exittime - c.entrancetime)), 'h ',
                LPAD(EXTRACT(MINUTE FROM (c.exittime - c.entrancetime))::text, 2, '0'), 'min'
            )
        ELSE 'Em curso'
    END as duration_formatted,
    c.memberid,
    m.userid
FROM checkin c
JOIN member m ON c.memberid = m.memberid
ORDER BY c.date DESC, c.entrancetime DESC;

CREATE OR REPLACE VIEW vw_instructor_stats_month AS
SELECT 
    i.instructorid,
    i.userid,
    u.name AS instructor_name,
    COUNT(DISTINCT cs.classscheduleid) AS classes_month,
    COUNT(DISTINCT cb.memberid) AS students_month,
    COALESCE(SUM(c.duration_minutes), 0) / 60.0 AS hours_month,
    EXTRACT(YEAR FROM cs.date) AS stats_year,
    EXTRACT(MONTH FROM cs.date) AS stats_month
FROM instructor i
LEFT JOIN users u ON i.userid = u.userid
LEFT JOIN class c ON i.instructorid = c.instructorid AND c.isactive = true
LEFT JOIN classschedule cs ON c.classid = cs.classid 
    AND cs.isactive = true
    AND cs.date >= DATE_TRUNC('month', CURRENT_DATE) 
    AND cs.date < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'
    AND cs.date <= CURRENT_DATE
LEFT JOIN classbooking cb ON cs.classscheduleid = cb.classscheduleid
WHERE i.isactive = true
GROUP BY i.instructorid, i.userid, u.name, EXTRACT(YEAR FROM cs.date), EXTRACT(MONTH FROM cs.date)
HAVING EXTRACT(YEAR FROM cs.date) IS NOT NULL AND EXTRACT(MONTH FROM cs.date) IS NOT NULL
   OR (COUNT(DISTINCT cs.classscheduleid) = 0 AND EXTRACT(YEAR FROM CURRENT_DATE) IS NOT NULL);

-- View simples para dashboard diário do instrutor
CREATE OR REPLACE VIEW vw_instructor_daily_dashboard AS
SELECT 
    i.instructorid,
    i.userid,
    u.name AS instructor_name,
    
    -- Aulas Hoje (3)
    (SELECT COUNT(*) 
     FROM classschedule cs 
     JOIN class c ON cs.classid = c.classid 
     WHERE c.instructorid = i.instructorid 
       AND cs.date = CURRENT_DATE 
       AND cs.isactive = true 
       AND c.isactive = true) AS classes_today,
    
    -- Alunos Confirmados (28)
    (SELECT COALESCE(SUM(booking_count), 0)
     FROM (
         SELECT COUNT(cb.memberid) as booking_count
         FROM classschedule cs 
         JOIN class c ON cs.classid = c.classid 
         LEFT JOIN classbooking cb ON cs.classscheduleid = cb.classscheduleid
         WHERE c.instructorid = i.instructorid 
           AND cs.date = CURRENT_DATE 
           AND cs.isactive = true 
           AND c.isactive = true
         GROUP BY cs.classscheduleid
     ) daily_bookings) AS students_confirmed,
    
    -- Taxa de Ocupação Média do Mês (84%)
    (SELECT COALESCE(ROUND(AVG(ocupacao_percentual), 0), 0)
     FROM (
         SELECT (COUNT(cb.memberid)::DECIMAL / cs.maxparticipants) * 100 as ocupacao_percentual
         FROM classschedule cs 
         JOIN class c ON cs.classid = c.classid 
         LEFT JOIN classbooking cb ON cs.classscheduleid = cb.classscheduleid
         WHERE c.instructorid = i.instructorid 
           AND cs.date >= DATE_TRUNC('month', CURRENT_DATE)
           AND cs.date <= CURRENT_DATE
           AND cs.isactive = true 
           AND c.isactive = true
         GROUP BY cs.classscheduleid, cs.maxparticipants
     ) monthly_rates) AS occupation_rate,
    
    -- Próxima Aula (17:00)
    (SELECT TO_CHAR(MIN(cs.starttime), 'HH24:MI')
     FROM classschedule cs 
     JOIN class c ON cs.classid = c.classid 
     WHERE c.instructorid = i.instructorid 
       AND cs.date = CURRENT_DATE 
       AND cs.starttime > CURRENT_TIME
       AND cs.isactive = true 
       AND c.isactive = true) AS next_class_time,
       
    -- Nome da Próxima Aula
    (SELECT c.name
     FROM classschedule cs 
     JOIN class c ON cs.classid = c.classid 
     WHERE c.instructorid = i.instructorid 
       AND cs.date = CURRENT_DATE 
       AND cs.starttime > CURRENT_TIME
       AND cs.isactive = true 
       AND c.isactive = true
     ORDER BY cs.starttime
     LIMIT 1) AS next_class_name,
       
    -- Sala da Próxima Aula  
    (SELECT c.room
     FROM classschedule cs 
     JOIN class c ON cs.classid = c.classid 
     WHERE c.instructorid = i.instructorid 
       AND cs.date = CURRENT_DATE 
       AND cs.starttime > CURRENT_TIME
       AND cs.isactive = true 
       AND c.isactive = true
     ORDER BY cs.starttime
     LIMIT 1) AS next_class_room
       
FROM instructor i
JOIN users u ON i.userid = u.userid
WHERE i.isactive = true;

-- View para listar as aulas do dia do instrutor (Minhas Aulas - Hoje)
CREATE OR REPLACE VIEW vw_instructor_classes_today AS
SELECT
    c.classid,
    c.name AS class_name,
    c.room,
    cs.date,
    cs.starttime,
    cs.endtime,
    cs.maxparticipants,
    COALESCE(booking_stats.enrolled_students, 0) AS enrolled_students,
    i.instructorid,
    i.userid

FROM class c
JOIN instructor i ON c.instructorid = i.instructorid
JOIN classschedule cs ON c.classid = cs.classid
LEFT JOIN (
    SELECT 
        cb.classscheduleid,
        COUNT(cb.memberid) AS enrolled_students
    FROM classbooking cb
    GROUP BY cb.classscheduleid
) booking_stats ON cs.classscheduleid = booking_stats.classscheduleid
WHERE c.isactive = true 
  AND cs.isactive = true
  AND cs.date = CURRENT_DATE
ORDER BY cs.starttime;

-- View para mostrar os membros inscritos na próxima aula do instrutor
CREATE OR REPLACE VIEW vw_instructor_next_class_members AS
SELECT 
    -- Informações da aula
    c.name AS class_name,
    TO_CHAR(cs.starttime, 'HH24:MI') AS class_time,
    c.room,
    cs.date,
    cs.classscheduleid,
    i.instructorid,
    i.userid AS instructor_userid,
    
    -- Informações dos membros inscritos
    u.name AS member_name,
    m.memberid,
    pl.name AS plan_name,
    
    -- Contagem total de inscritos na aula
    (SELECT COUNT(*) 
     FROM classbooking cb2 
     WHERE cb2.classscheduleid = cs.classscheduleid) AS total_enrolled

FROM class c
JOIN instructor i ON c.instructorid = i.instructorid
JOIN classschedule cs ON c.classid = cs.classid
JOIN classbooking cb ON cs.classscheduleid = cb.classscheduleid
JOIN member m ON cb.memberid = m.memberid
JOIN users u ON m.userid = u.userid
LEFT JOIN membersubscription ms ON m.memberid = ms.memberid AND ms.isactive = true
LEFT JOIN plan pl ON ms.planid = pl.planid
WHERE c.isactive = true 
  AND cs.isactive = true
  AND cs.date = CURRENT_DATE
  AND cs.starttime = (
      -- Subquery para encontrar a próxima aula do instrutor
      SELECT MIN(cs2.starttime)
      FROM classschedule cs2
      JOIN class c2 ON cs2.classid = c2.classid
      WHERE c2.instructorid = i.instructorid
        AND cs2.date = CURRENT_DATE
        AND cs2.starttime > CURRENT_TIME
        AND cs2.isactive = true
        AND c2.isactive = true
  )
ORDER BY u.name;

-- View para histórico de aulas da última semana do instrutor
CREATE OR REPLACE VIEW vw_instructor_class_history AS
SELECT 
    cs.date,
    CONCAT(TO_CHAR(cs.starttime, 'HH24:MI'), '-', TO_CHAR(cs.endtime, 'HH24:MI')) AS schedule,
    c.name AS class_name,
    c.room AS room,
    COUNT(cb.memberid) AS enrolled,
    CASE 
        WHEN COUNT(cb.memberid) > 0 THEN 
            ROUND((COUNT(cb.memberid)::DECIMAL / cs.maxparticipants) * 100, 0)
        ELSE 0 
    END AS rate,
    i.instructorid,
    i.userid AS instructor_userid
FROM class c
JOIN instructor i ON c.instructorid = i.instructorid
JOIN classschedule cs ON c.classid = cs.classid
LEFT JOIN classbooking cb ON cs.classscheduleid = cb.classscheduleid
WHERE c.isactive = true 
  AND cs.isactive = true
  AND cs.date >= DATE_TRUNC('week', CURRENT_DATE) - INTERVAL '7 days'  -- Início da semana anterior (segunda)
  AND cs.date < DATE_TRUNC('week', CURRENT_DATE)  -- Fim da semana anterior (domingo)
GROUP BY cs.classscheduleid, cs.date, cs.starttime, cs.endtime, c.name, c.room, cs.maxparticipants, i.instructorid, i.userid
ORDER BY cs.date DESC, cs.starttime DESC;

-- Vista para performance semanal do instrutor baseado na semana anterior
CREATE OR REPLACE VIEW vw_instructor_week_performance AS
SELECT 
    i.instructorid,
    i.userid AS instructor_userid,
    u.name AS instructor_name,
    
    -- Total de aulas na semana anterior
    COUNT(DISTINCT cs.classscheduleid) AS total_classes,
    
    -- Total de alunos (soma de todas as presenças)
    COALESCE(SUM(
        CASE 
            WHEN cb.memberid IS NOT NULL THEN 1 
            ELSE 0 
        END
    ), 0) AS total_students,
    
    -- Capacidade total de todas as aulas
    COALESCE(SUM(cs.maxparticipants), 0) AS total_capacity,
    
    -- Taxa média de presença (percentual de ocupação das aulas)
    CASE 
        WHEN COALESCE(SUM(cs.maxparticipants), 0) > 0 THEN 
            ROUND((
                COALESCE(SUM(
                    CASE 
                        WHEN cb.memberid IS NOT NULL THEN 1 
                        ELSE 0 
                    END
                ), 0)::DECIMAL / COALESCE(SUM(cs.maxparticipants), 0)::DECIMAL * 100
            ), 0)
        ELSE 0
    END AS average_attendance
    
FROM instructor i
JOIN users u ON i.userid = u.userid
LEFT JOIN class c ON i.instructorid = c.instructorid 
    AND c.isactive = true
LEFT JOIN classschedule cs ON c.classid = cs.classid 
    AND cs.isactive = true
    AND cs.date >= DATE_TRUNC('week', CURRENT_DATE) - INTERVAL '7 days'  -- Início da semana anterior (segunda)
    AND cs.date < DATE_TRUNC('week', CURRENT_DATE)  -- Fim da semana anterior (domingo)
LEFT JOIN classbooking cb ON cs.classscheduleid = cb.classscheduleid
GROUP BY 
    i.instructorid, i.userid, u.name
ORDER BY total_classes DESC, average_attendance DESC;

-- Vista para aulas mais populares do instrutor na semana anterior
CREATE OR REPLACE VIEW vw_instructor_popular_classes AS
SELECT 
    i.instructorid,
    i.userid AS instructor_userid,
    c.name AS class_name,
    c.room,
    COUNT(DISTINCT cs.classscheduleid) AS total_sessions,
    COALESCE(SUM(cs.maxparticipants), 0) AS total_capacity,
    COALESCE(COUNT(cb.memberid), 0) AS total_attendees,
    
    -- Taxa média de ocupação para esta aula específica
    CASE 
        WHEN COALESCE(SUM(cs.maxparticipants), 0) > 0 THEN 
            ROUND((
                COALESCE(COUNT(cb.memberid), 0)::DECIMAL / 
                COALESCE(SUM(cs.maxparticipants), 0)::DECIMAL * 100
            ), 0)
        ELSE 0
    END AS occupation_rate,
    
    -- Ranking baseado na taxa de ocupação
    ROW_NUMBER() OVER (
        PARTITION BY i.instructorid 
        ORDER BY 
            CASE 
                WHEN COALESCE(SUM(cs.maxparticipants), 0) > 0 THEN 
                    COALESCE(COUNT(cb.memberid), 0)::DECIMAL / 
                    COALESCE(SUM(cs.maxparticipants), 0)::DECIMAL * 100
                ELSE 0
            END DESC,
            COUNT(DISTINCT cs.classscheduleid) DESC
    ) AS popularity_rank
    
FROM instructor i
JOIN class c ON i.instructorid = c.instructorid 
    AND c.isactive = true
JOIN classschedule cs ON c.classid = cs.classid 
    AND cs.isactive = true
    AND cs.date >= DATE_TRUNC('week', CURRENT_DATE) - INTERVAL '7 days'  -- Início da semana anterior (segunda)
    AND cs.date < DATE_TRUNC('week', CURRENT_DATE)  -- Fim da semana anterior (domingo)
LEFT JOIN classbooking cb ON cs.classscheduleid = cb.classscheduleid
GROUP BY 
    i.instructorid, i.userid, c.classid, c.name, c.room
HAVING COUNT(DISTINCT cs.classscheduleid) > 0  -- Apenas aulas que realmente aconteceram
ORDER BY i.instructorid, popularity_rank;

-- View para Gerenciamento de Membros do Manager
-- Esta view fornece todos os dados necessários para a interface de gestão de membros
CREATE OR REPLACE VIEW vw_manager_members_management AS
SELECT 
    m.memberid,
    u.name AS member_name,
    u.email,
    m.phone AS member_phone,
    pl.name AS plan_name,
    m.gender AS member_gender,
    m.birthdate AS member_birthdate,
    m.address AS member_address,
    m.nif AS member_nif,
    m.city AS member_city,
    m.postalcode AS member_postalcode,
    m.iban AS member_iban,
    -- Status baseado na subscrição ativa e pagamentos
    CASE 
        WHEN ms.isactive = false OR ms.enddate < CURRENT_DATE THEN 'inativo'
        WHEN EXISTS (
            SELECT 1 FROM payment p 
            WHERE p.subscriptionid = ms.subscriptionid 
              AND p.ispayed = false 
              AND p.duedate < CURRENT_DATE
        ) THEN 'inativo'
        WHEN ms.isactive = true AND ms.enddate >= CURRENT_DATE THEN 'ativo'
        ELSE 'inativo'
    END AS status,

    m.registrationdate AS member_registration_date,

    -- Dados adicionais para filtros e busca
    pl.planid,
    
    -- Para contagem total
    COUNT(*) OVER() AS total_members

FROM member m
JOIN users u ON m.userid = u.userid
LEFT JOIN membersubscription ms ON m.memberid = ms.memberid 
    AND ms.subscriptionid = (
        -- Pega a subscrição mais recente (ativa ou mais atual)
        SELECT ms2.subscriptionid 
        FROM membersubscription ms2 
        WHERE ms2.memberid = m.memberid 
        ORDER BY ms2.isactive DESC, ms2.startdate DESC 
        LIMIT 1
    )
LEFT JOIN plan pl ON ms.planid = pl.planid;

-- View para Horário de Aulas do Gestor
-- Esta view fornece informações completas para criar o horário visual de aulas por data
CREATE OR REPLACE VIEW vw_manager_class_schedule AS
SELECT 
    cs.classscheduleid,
    cs.date AS class_date,
    c.name AS class_name,
    c.room AS room,
    c.classid,
    c.instructorid,
    
    -- Informações do instrutor
    u.name AS instructor_name,
    
    -- Horários formatados
    cs.starttime,
    cs.endtime,
    TO_CHAR(cs.starttime, 'HH24:MI') AS start_time,
    TO_CHAR(cs.endtime, 'HH24:MI') AS end_time,
    EXTRACT(HOUR FROM cs.starttime) AS start_hour,
    EXTRACT(MINUTE FROM cs.starttime) AS start_minute,
    
    -- Capacidade e inscrições
    cs.maxparticipants AS max_capacity,
    COALESCE(booking_stats.enrolled_count, 0) AS enrolled_count,
    
    -- Status da aula baseado na capacidade
    CASE 
        WHEN COALESCE(booking_stats.enrolled_count, 0) >= cs.maxparticipants THEN 'Lotado'
        WHEN COALESCE(booking_stats.enrolled_count, 0) = 0 THEN 'Vazio'
        ELSE 'Disponível'
    END AS class_status,
    
    -- Percentual de ocupação
    CASE 
        WHEN cs.maxparticipants > 0 THEN 
            ROUND((COALESCE(booking_stats.enrolled_count, 0)::DECIMAL / cs.maxparticipants) * 100, 0)
        ELSE 0
    END AS occupation_percentage

FROM classschedule cs
JOIN class c ON cs.classid = c.classid
JOIN instructor i ON c.instructorid = i.instructorid
JOIN users u ON i.userid = u.userid
LEFT JOIN (
    -- Subquery para contar inscrições por aula
    SELECT 
        cb.classscheduleid,
        COUNT(cb.memberid) AS enrolled_count
    FROM classbooking cb
    GROUP BY cb.classscheduleid
) booking_stats ON cs.classscheduleid = booking_stats.classscheduleid

WHERE cs.isactive = true 
  AND c.isactive = true
  AND i.isactive = true

ORDER BY cs.date, cs.starttime, c.room;

-- View para Filtros do Horário de Aulas (Instrutores e Salas)
-- Esta view fornece listas para os filtros da interface de horário
CREATE OR REPLACE VIEW vw_manager_schedule_filters AS
SELECT 
    'instructor' AS filter_type,
    i.instructorid AS filter_id,
    u.name AS filter_name,
    u.name AS display_text
FROM instructor i
JOIN users u ON i.userid = u.userid
WHERE i.isactive = true

UNION ALL

SELECT 
    'room' AS filter_type,
    NULL AS filter_id,
    c.room AS filter_name,
    c.room AS display_text
FROM class c
JOIN classschedule cs ON c.classid = cs.classid
WHERE c.isactive = true
  AND cs.isactive = true
  AND c.room IS NOT NULL
GROUP BY c.room

ORDER BY filter_type, display_text;

-- View para aulas existentes (dropdown de criação de novas aulas)
CREATE OR REPLACE VIEW vw_existing_classes AS
SELECT DISTINCT 
    c.classid, 
    c.name, 
    c.room, 
    c.duration_minutes
FROM class c 
WHERE c.isactive = true
ORDER BY c.name;

-- View para membros inscritos em uma aula específica
CREATE OR REPLACE VIEW vw_class_enrolled_members AS
SELECT 
    cb.classscheduleid,
    u.name AS member_name,
    m.memberid,
    u.email,
    m.phone,
    pl.name AS plan_name,
    cb.bookingdate
FROM classbooking cb
JOIN member m ON cb.memberid = m.memberid
JOIN users u ON m.userid = u.userid
LEFT JOIN membersubscription ms ON m.memberid = ms.memberid AND ms.isactive = true
LEFT JOIN plan pl ON ms.planid = pl.planid
ORDER BY cb.bookingdate;

-- ===================================
-- VIEWS PARA GESTÃO DE MÁQUINAS
-- ===================================

-- View para estatísticas resumo das máquinas (cards superiores)
CREATE OR REPLACE VIEW vw_machine_summary AS
SELECT 
    1 as id,  -- Fake ID for Django ORM
    COUNT(*) AS total_machines,
    COUNT(CASE WHEN ms.status = 'Em funcionamento' THEN 1 END) AS functioning_machines,
    COUNT(CASE WHEN ms.status = 'Em manutenção' THEN 1 END) AS maintenance_machines,
    COUNT(CASE WHEN ms.status = 'Fora de Serviço' THEN 1 END) AS out_of_service_machines,
    ROUND(
        (COUNT(CASE WHEN ms.status = 'Em funcionamento' THEN 1 END) * 100.0 / COUNT(*)), 1
    ) AS functioning_percentage
FROM machine m
JOIN machinestatus ms ON m.machinestatusid = ms.machinestatusid;

-- View para listagem completa das máquinas (tabela principal)
CREATE OR REPLACE VIEW vw_machine_inventory AS
SELECT 
    m.machineid,
    m.serialnumber AS codigo,
    m.name AS nome,
    m.type AS categoria,
    m.manufacturer AS marca,
    m.model AS modelo,
    m.installationdate AS data_aquisicao,
    m.maintenancedate AS ultima_manutencao,
    ms.status,
    ms.machinestatusid
FROM machine m
JOIN machinestatus ms ON m.machinestatusid = ms.machinestatusid
ORDER BY m.machineid;

-- View para categorias de máquinas (para dropdowns)
CREATE OR REPLACE VIEW vw_machine_categories AS
SELECT DISTINCT type AS categoria
FROM machine 
WHERE type IS NOT NULL AND type != ''
ORDER BY type;

-- View para marcas de máquinas (para dropdowns)
CREATE OR REPLACE VIEW vw_machine_brands AS
SELECT DISTINCT manufacturer AS marca
FROM machine 
WHERE manufacturer IS NOT NULL AND manufacturer != ''
ORDER BY manufacturer;

-- View para status de máquinas (para dropdowns)
CREATE OR REPLACE VIEW vw_machine_statuses AS
SELECT 
    machinestatusid,
    status
FROM machinestatus
ORDER BY status;

-- View para detalhes de uma máquina específica
CREATE OR REPLACE VIEW vw_machine_detail AS
SELECT 
    m.machineid,
    m.serialnumber AS codigo,
    m.name AS nome,
    m.type AS categoria,
    m.manufacturer AS marca,
    m.model AS modelo,
    m.installationdate AS data_aquisicao,
    m.maintenancedate AS ultima_manutencao,
    ms.status,
    ms.machinestatusid
FROM machine m
JOIN machinestatus ms ON m.machinestatusid = ms.machinestatusid;

-- ======================================================================
-- VIEWS PARA GERENCIAMENTO DE PAGAMENTOS (DASHBOARD DE PAGAMENTOS)
-- ======================================================================

-- View para os 4 quadrados de resumo do dashboard de pagamentos
CREATE OR REPLACE VIEW vw_payment_dashboard_summary AS
SELECT 
    1 as id,  -- Fake ID for Django ORM
    -- Receita Mensal (pagamentos recebidos no mês atual)
    COALESCE(SUM(CASE 
        WHEN p.ispayed = true 
        AND EXTRACT(MONTH FROM p.paymentdate) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM p.paymentdate) = EXTRACT(YEAR FROM CURRENT_DATE)
        THEN p.amount 
        ELSE 0 
    END), 0) AS receita_mensal,
    
    -- Pagamentos Hoje (pagamentos recebidos hoje)
    COALESCE(SUM(CASE 
        WHEN p.ispayed = true 
        AND p.paymentdate = CURRENT_DATE
        THEN p.amount 
        ELSE 0 
    END), 0) AS pagamentos_hoje,
    
    -- Contagem de transações hoje
    COUNT(CASE 
        WHEN p.ispayed = true 
        AND p.paymentdate = CURRENT_DATE
        THEN 1 
    END) AS transacoes_hoje,
    
    -- Pendentes (valores pendentes de pagamento)
    COALESCE(SUM(CASE 
        WHEN p.ispayed = false 
        AND p.duedate >= CURRENT_DATE
        THEN p.amount 
        ELSE 0 
    END), 0) AS pendentes,
    
    -- Contagem de pagamentos pendentes
    COUNT(CASE 
        WHEN p.ispayed = false 
        AND p.duedate >= CURRENT_DATE
        THEN 1 
    END) AS pagamentos_pendentes,
    
    -- Em Atraso (valores em atraso)
    COALESCE(SUM(CASE 
        WHEN p.ispayed = false 
        AND p.duedate < CURRENT_DATE
        THEN p.amount 
        ELSE 0 
    END), 0) AS em_atraso,
    
    -- Contagem de pagamentos em atraso
    COUNT(CASE 
        WHEN p.ispayed = false 
        AND p.duedate < CURRENT_DATE
        THEN 1 
    END) AS pagamentos_em_atraso
FROM payment p;

-- View para os 3 últimos pagamentos recentes (pagamentos hoje)
CREATE OR REPLACE VIEW vw_payment_recent_transactions AS
SELECT 
    p.paymentid,
    CONCAT('€', ROUND(p.amount, 2)::text) AS valor,
    u.name AS nome_membro,
    CONCAT('ID: ', m.memberid) AS id_membro,
    pl.name AS plano,
    p.paymentmethod AS metodo_pagamento,
    p.paymentdate AS data_pagamento
FROM payment p
JOIN membersubscription ms ON p.subscriptionid = ms.subscriptionid
JOIN member m ON ms.memberid = m.memberid
JOIN users u ON m.userid = u.userid
JOIN plan pl ON ms.planid = pl.planid
WHERE p.ispayed = true 
    AND p.paymentdate = CURRENT_DATE
ORDER BY p.paymentdate DESC, p.paymentid DESC
LIMIT 3;

-- View para histórico de pagamentos com filtros
CREATE OR REPLACE VIEW vw_payment_history AS
SELECT 
    p.paymentid,
    u.name AS nome_membro,
    m.memberid AS id_membro,
    pl.name AS plano,
    CONCAT('€', ROUND(p.amount, 2)::text) AS valor,
    p.paymentmethod AS metodo_pagamento,
    p.duedate AS data_vencimento,
    p.paymentdate AS data_pagamento,
    CASE 
        WHEN p.ispayed = true THEN 'Pago'
        WHEN p.duedate < CURRENT_DATE AND p.ispayed = false THEN 'Em Atraso'
        ELSE 'Pendente'
    END AS status,
    p.duedate,
    p.amount AS valor_numerico
FROM payment p
JOIN membersubscription ms ON p.subscriptionid = ms.subscriptionid
JOIN member m ON ms.memberid = m.memberid
JOIN users u ON m.userid = u.userid
JOIN plan pl ON ms.planid = pl.planid
ORDER BY p.duedate DESC, p.paymentid DESC;

-- View para resumo mensal de pagamentos (quadrados do fundo)
CREATE OR REPLACE VIEW vw_payment_monthly_summary AS
SELECT 
    1 as id, -- Fake ID for Django ORM
    
    -- Total faturado no mês atual (baseado na data de vencimento)
    COALESCE(SUM(CASE 
        WHEN EXTRACT(MONTH FROM p.duedate) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM p.duedate) = EXTRACT(YEAR FROM CURRENT_DATE)
        THEN p.amount 
        ELSE 0 
    END), 0) AS total_faturado,
    
    -- Total recebido no mês atual (baseado na data de pagamento)
    COALESCE(SUM(CASE 
        WHEN p.ispayed = true
        AND EXTRACT(MONTH FROM p.paymentdate) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM p.paymentdate) = EXTRACT(YEAR FROM CURRENT_DATE)
        THEN p.amount 
        ELSE 0 
    END), 0) AS total_recebido,
    
    -- Pendentes (não pagos mas dentro do prazo)
    COALESCE(SUM(CASE 
        WHEN p.ispayed = false AND p.duedate >= CURRENT_DATE
        THEN p.amount 
        ELSE 0 
    END), 0) AS pendentes,
    
    -- Em atraso (não pagos e fora do prazo)
    COALESCE(SUM(CASE 
        WHEN p.ispayed = false AND p.duedate < CURRENT_DATE
        THEN p.amount 
        ELSE 0 
    END), 0) AS em_atraso,
    
    -- Métodos de pagamento dinâmicos do mês atual
    (SELECT STRING_AGG(
        CONCAT(
            method_stats.paymentmethod, ': ',
            method_stats.percentage, '% (€',
            method_stats.amount, ')'
        ), 
        ' | ' 
        ORDER BY method_stats.amount DESC
    )
    FROM (
        SELECT 
            p2.paymentmethod,
            ROUND(
                (COUNT(*) * 100.0 / 
                 NULLIF((SELECT COUNT(*) 
                        FROM payment p3 
                        WHERE p3.ispayed = true 
                          AND EXTRACT(MONTH FROM p3.paymentdate) = EXTRACT(MONTH FROM CURRENT_DATE)
                          AND EXTRACT(YEAR FROM p3.paymentdate) = EXTRACT(YEAR FROM CURRENT_DATE)), 0)
                ), 0
            ) AS percentage,
            ROUND(SUM(p2.amount), 0) AS amount
        FROM payment p2
        WHERE p2.ispayed = true 
          AND EXTRACT(MONTH FROM p2.paymentdate) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(YEAR FROM p2.paymentdate) = EXTRACT(YEAR FROM CURRENT_DATE)
          AND p2.paymentmethod IS NOT NULL
        GROUP BY p2.paymentmethod
    ) method_stats
    ) AS metodos_pagamento

FROM payment p;

-- ============================================================================
-- VISTAS PARA PÁGINA DE GERENCIAMENTO DE PLANOS
-- ============================================================================

-- DROP das vistas de planos caso já existam
DROP VIEW IF EXISTS vw_plan_statistics;
DROP VIEW IF EXISTS vw_plan_details;
DROP VIEW IF EXISTS vw_plan_membership_summary;
DROP VIEW IF EXISTS vw_total_active_members;

-- Vista para estatísticas dos planos (os 4 quadrados do topo)
CREATE OR REPLACE VIEW vw_plan_statistics AS
SELECT 
    p.planid,
    p.name AS plan_name,
    p.monthlyprice,
    p.access24h,
    COUNT(CASE WHEN ms.isactive = true AND m.isactive = true THEN 1 END) AS member_count,
    ROUND(
        (COUNT(CASE WHEN ms.isactive = true AND m.isactive = true THEN 1 END) * 100.0 / 
         NULLIF((SELECT COUNT(*) 
                FROM member m2 
                JOIN membersubscription ms2 ON m2.memberid = ms2.memberid 
                WHERE ms2.isactive = true AND m2.isactive = true), 0)
        ), 0
    ) AS percentage
FROM plan p
LEFT JOIN membersubscription ms ON p.planid = ms.planid AND ms.isactive = true
LEFT JOIN member m ON ms.memberid = m.memberid AND m.isactive = true
WHERE p.isactive = true
GROUP BY p.planid, p.name, p.monthlyprice, p.access24h
ORDER BY p.monthlyprice;

-- Vista para o total de membros ativos (quarto quadrado)
CREATE OR REPLACE VIEW vw_total_active_members AS
SELECT 
    COUNT(*) AS total_members

FROM member m
JOIN membersubscription ms ON m.memberid = ms.memberid
WHERE m.isactive = true AND ms.isactive = true;

-- Vista detalhada dos planos para as cartas inferiores
CREATE OR REPLACE VIEW vw_plan_details AS
SELECT 
    p.planid,
    p.name,
    p.monthlyprice,
    p.access24h,
    p.description,
    COUNT(CASE WHEN ms.isactive = true AND m.isactive = true THEN 1 END) AS member_count,
    CONCAT('€', p.monthlyprice, '/mês') AS price_display
FROM plan p
LEFT JOIN membersubscription ms ON p.planid = ms.planid AND ms.isactive = true
LEFT JOIN member m ON ms.memberid = m.memberid AND m.isactive = true
WHERE p.isactive = true
GROUP BY p.planid, p.name, p.monthlyprice, p.access24h, p.description
ORDER BY p.monthlyprice;

-- ============================================================================
-- VISTAS AUXILIARES PARA ELIMINAR SELECTS DIRETOS
-- ============================================================================

-- Vista para obter memberid por userid
CREATE OR REPLACE VIEW vw_member_userid_lookup AS
SELECT 
    m.memberid,
    m.userid,
    u.name,
    u.email
FROM member m
JOIN users u ON m.userid = u.userid
WHERE m.isactive = true;

-- Vista para obter classes inscritas por membro
CREATE OR REPLACE VIEW vw_member_enrolled_classes AS
SELECT 
    cb.memberid,
    cb.classscheduleid,
    cb.bookingdate,
    c.name as class_name,
    cs.date,
    cs.starttime,
    cs.endtime
FROM classbooking cb
JOIN classschedule cs ON cb.classscheduleid = cs.classscheduleid
JOIN class c ON cs.classid = c.classid
WHERE cs.isactive = true AND c.isactive = true;

-- Vista para verificação de password (só retorna se existe)
CREATE OR REPLACE VIEW vw_user_password_check AS
SELECT 
    u.userid,
    u.password,
    u.isactive
FROM users u
WHERE u.isactive = true;

-- View para histórico de aulas passadas do membro
CREATE OR REPLACE VIEW vw_member_class_history AS
SELECT 
    cs.classscheduleid,
    c.name AS class_name,
    cs.date,
    cs.starttime,
    cs.endtime,
    c.room,
    u.name AS instructor_name,
    c.description AS class_description,
    m.userid,
    m.memberid,
    cb.bookingdate AS booking_date
FROM classschedule cs
JOIN class c ON cs.classid = c.classid
JOIN instructor i ON c.instructorid = i.instructorid
JOIN users u ON i.userid = u.userid
LEFT JOIN classbooking cb ON cs.classscheduleid = cb.classscheduleid
LEFT JOIN member m ON cb.memberid = m.memberid
WHERE cs.isactive = true 
  AND c.isactive = true
  AND cs.date < CURRENT_DATE  -- Apenas aulas passadas
  AND cb.memberid IS NOT NULL  -- Apenas aulas onde o membro estava inscrito
ORDER BY cs.date DESC, cs.starttime DESC;

-- View for member class evaluation details
CREATE OR REPLACE VIEW vw_member_class_evaluation_details AS
SELECT 
    cs.classscheduleid,
    c.instructorid,
    c.name as class_name,
    u.name as member_name,
    m.memberid,
    cb.memberid as booking_memberid
FROM classschedule cs
JOIN class c ON cs.classid = c.classid
JOIN classbooking cb ON cs.classscheduleid = cb.classscheduleid
JOIN member m ON cb.memberid = m.memberid
JOIN users u ON m.userid = u.userid
WHERE c.isactive = true
  AND cs.date < CURRENT_DATE;

-- View for manager dashboard recent checkins
CREATE OR REPLACE VIEW vw_manager_recent_checkins AS
SELECT 
    c.checkinid,
    u.name as member_name,
    m.memberid,
    c.entrancetime,
    c.exittime,
    CASE 
        WHEN c.exittime IS NULL THEN 'Ativo'
        ELSE 'Finalizado'
    END as status
FROM checkin c
JOIN member m ON c.memberid = m.memberid
JOIN users u ON m.userid = u.userid
WHERE c.date = CURRENT_DATE
ORDER BY c.entrancetime DESC;

-- View for manager dashboard upcoming classes
CREATE OR REPLACE VIEW vw_manager_upcoming_classes AS
SELECT 
    c.classid,
    c.name as class_name,
    cs.starttime,
    cs.endtime,
    u.name as instructor_name,
    i.instructorid,
    c.room,
    c.capacity as maxcapacity,
    COALESCE(enrolled.count, 0) as enrolled_count,
    CASE 
        WHEN COALESCE(enrolled.count, 0) >= c.capacity THEN true
        ELSE false
    END as is_full
FROM class c
JOIN classschedule cs ON c.classid = cs.classid
JOIN instructor i ON c.instructorid = i.instructorid
JOIN users u ON i.userid = u.userid
LEFT JOIN (
    SELECT 
        cb.classscheduleid,
        COUNT(*) as count
    FROM classbooking cb
    GROUP BY cb.classscheduleid
) enrolled ON cs.classscheduleid = enrolled.classscheduleid
WHERE cs.date = CURRENT_DATE 
AND cs.starttime >= CURRENT_TIME
AND cs.isactive = true
ORDER BY cs.starttime;

-- View for manager dashboard extended stats
CREATE OR REPLACE VIEW vw_manager_dashboard_stats AS
SELECT 
    1 as id,  -- Fake ID for Django ORM
    (SELECT COUNT(*) FROM member WHERE isactive = true) as total_members,
    (SELECT COUNT(*) FROM instructor WHERE isactive = true) as total_instructors,
    (SELECT COUNT(*) FROM membersubscription WHERE isactive = true) as active_memberships,
    (SELECT COUNT(*) FROM checkin WHERE date = CURRENT_DATE) as today_checkins,
    (SELECT COUNT(*) FROM classschedule WHERE date = CURRENT_DATE AND isactive = true) as today_classes,
    (SELECT COALESCE(SUM(amount), 0) FROM payment 
     WHERE EXTRACT(MONTH FROM paymentdate) = EXTRACT(MONTH FROM CURRENT_DATE)
     AND EXTRACT(YEAR FROM paymentdate) = EXTRACT(YEAR FROM CURRENT_DATE)) as monthly_revenue;
