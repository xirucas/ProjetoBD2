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
    i.userid
FROM instructor i
LEFT JOIN users u ON i.userid = u.userid;

-- View for instructor classes
CREATE OR REPLACE VIEW vw_instructor_classes AS
SELECT 
    c.classid, 
    c.name, 
    c.room, 
    c.capacity, 
    c.duration_minutes,
    c.instructorid,
    i.userid
FROM class c
JOIN instructor i ON c.instructorid = i.instructorid
WHERE c.isactive = true;

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
