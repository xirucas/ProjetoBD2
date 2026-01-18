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

-- View for payments with member and plan info
CREATE OR REPLACE VIEW vw_payments AS
SELECT 
    p.paymentid, 
    u.name as member_name, 
    pl.name as plan_name,
    p.amount, 
    p.duedate, 
    p.paymentdate, 
    p.ispayed, 
    p.paymentmethod
FROM payment p
JOIN membersubscription ms ON p.subscriptionid = ms.subscriptionid
JOIN member m ON ms.memberid = m.memberid
JOIN users u ON m.userid = u.userid
JOIN plan pl ON ms.planid = pl.planid;

-- View for all plans
CREATE OR REPLACE VIEW vw_plans AS
SELECT 
    planid, 
    name, 
    monthlyprice, 
    access24h, 
    description, 
    isactive
FROM plan;

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
     ) daily_bookings) AS students_today,
    
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
    c.capacity,
    c.duration_minutes,
    cs.classscheduleid,
    cs.date,
    cs.starttime,
    cs.endtime,
    cs.maxparticipants,
    TO_CHAR(cs.starttime, 'HH24:MI') AS start_time,
    TO_CHAR(cs.endtime, 'HH24:MI') AS end_time,
    CONCAT(TO_CHAR(cs.starttime, 'HH24:MI'), ' - ', TO_CHAR(cs.endtime, 'HH24:MI')) AS time_slot,
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
    cs.maxparticipants AS enrolled,
    COUNT(cb.memberid) AS present,
    CASE 
        WHEN cs.maxparticipants > 0 THEN 
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
