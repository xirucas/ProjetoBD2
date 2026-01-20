DROP PROCEDURE IF EXISTS sp_create_machine;
DROP PROCEDURE IF EXISTS sp_update_machine;
DROP PROCEDURE IF EXISTS sp_change_machine_status;
DROP PROCEDURE IF EXISTS sp_create_member;
DROP PROCEDURE IF EXISTS sp_book_class;
DROP PROCEDURE IF EXISTS sp_update_last_login;
DROP PROCEDURE IF EXISTS sp_update_member;
DROP PROCEDURE IF EXISTS sp_change_member_status;
DROP PROCEDURE IF EXISTS sp_update_plan;
DROP PROCEDURE IF EXISTS sp_member_update_profile;
DROP PROCEDURE IF EXISTS sp_instructor_update_profile;
DROP PROCEDURE IF EXISTS sp_change_user_password;
DROP PROCEDURE IF EXISTS sp_process_member_payment;

CREATE OR REPLACE PROCEDURE sp_create_member(
    p_name VARCHAR(100),
    p_password VARCHAR(255),
    p_nif CHAR(9),
    p_email VARCHAR(254),
    p_phone VARCHAR(15),
    p_iban VARCHAR(34),
    p_birthdate DATE,
    p_gender VARCHAR(10),
    p_address VARCHAR(255),
    p_city VARCHAR(100),
    p_postalcode VARCHAR(20),
    p_plan INTEGER
)
LANGUAGE plpgsql 
SECURITY DEFINER 
SET search_path = public
AS $$
DECLARE
    v_userid INTEGER;
    v_memberid INTEGER;
BEGIN
    INSERT INTO USERS (email, password, name, usertypeid, isactive)
    VALUES (p_email, p_password, p_name, 3, TRUE)
    RETURNING userid INTO v_userid;

    INSERT INTO MEMBER (userid, nif, phone, iban, birthdate, gender, address, city, postalcode)
    VALUES (v_userid, p_nif, p_phone, p_iban, p_birthdate, p_gender, p_address, p_city, p_postalcode)
    RETURNING memberid INTO v_memberid;

    INSERT INTO MEMBERSUBSCRIPTION (memberid, planid, startdate, enddate, isactive)
    VALUES (v_memberid, p_plan, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 year', TRUE);

    RAISE NOTICE 'User criado com ID: %, Membro criado com ID: %', v_userid, v_memberid;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_book_class(
    IN p_userid INTEGER,
    IN p_classscheduleid INTEGER
)
LANGUAGE plpgsql AS $$
DECLARE
    v_memberid INTEGER;
BEGIN
    -- Get memberid from userid
    SELECT m.memberid INTO v_memberid 
    FROM member m 
    WHERE m.userid = p_userid;
    
    -- Check if member exists
    IF v_memberid IS NULL THEN
        RAISE EXCEPTION 'Member not found for user ID %', p_userid;
    END IF;
    
    -- Insert the class booking
    INSERT INTO CLASSBOOKING (memberid, classscheduleid, bookingdate)
    VALUES (v_memberid, p_classscheduleid, CURRENT_TIMESTAMP);
    
    RAISE NOTICE 'Class booking created successfully for member % in class schedule %', v_memberid, p_classscheduleid;
    
END;
$$;

-- Stored procedure to update user's last login timestamp
CREATE OR REPLACE PROCEDURE sp_update_last_login(
    IN p_userid INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Update the last_login field for the specified user
    UPDATE users 
    SET last_login = CURRENT_TIMESTAMP 
    WHERE userid = p_userid;
    
    -- Check if the user was found and updated
    IF NOT FOUND THEN
        RAISE EXCEPTION 'User with ID % not found', p_userid;
    END IF;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error updating last login for user ID %: %', p_userid, SQLERRM;
END;
$$;

-- Procedure to update member information
DROP PROCEDURE IF EXISTS sp_update_member;

CREATE OR REPLACE PROCEDURE sp_update_member(
    p_memberid INTEGER,
    p_name VARCHAR(100),
    p_email VARCHAR(254),
    p_nif CHAR(9),
    p_phone VARCHAR(15),
    p_iban VARCHAR(34),
    p_birthdate DATE,
    p_gender VARCHAR(10),
    p_address VARCHAR(255),
    p_city VARCHAR(100),
    p_postalcode VARCHAR(20),
    p_plan INTEGER,
    p_status VARCHAR(20) DEFAULT 'ativo'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_userid INTEGER;
    v_current_subscription INTEGER;
    v_is_active BOOLEAN;
BEGIN
    -- Get userid from memberid
    SELECT m.userid INTO v_userid 
    FROM member m 
    WHERE m.memberid = p_memberid;
    
    IF v_userid IS NULL THEN
        RAISE EXCEPTION 'Member with ID % not found', p_memberid;
    END IF;
    
    -- Determinar se o usuário deve estar ativo baseado no status
    v_is_active := CASE 
        WHEN p_status = 'ativo' THEN TRUE 
        ELSE FALSE 
    END;
    
    -- Update user information including active status
    UPDATE users 
    SET email = p_email, 
        name = p_name,
        isactive = v_is_active
    WHERE userid = v_userid;
    
    -- Update member information
    UPDATE member 
    SET nif = p_nif,
        phone = p_phone,
        iban = p_iban,
        birthdate = p_birthdate,
        gender = p_gender,
        address = p_address,
        city = p_city,
        postalcode = p_postalcode
    WHERE memberid = p_memberid;
    
    -- Solução para constraint: deletar subscrições inativas antigas e manter apenas uma por status
    IF NOT v_is_active THEN
        -- Se mudando para inativo, deletar todas as subscrições inativas existentes primeiro
        DELETE FROM membersubscription 
        WHERE memberid = p_memberid AND isactive = FALSE;
    END IF;
    
    -- Desativar todas as subscrições ativas
    UPDATE membersubscription 
    SET isactive = FALSE
    WHERE memberid = p_memberid AND isactive = TRUE;
    
    -- Update subscription if plan changed
    IF p_plan IS NOT NULL AND p_plan != 0 THEN
        -- Buscar a subscrição mais recente
        SELECT subscriptionid INTO v_current_subscription
        FROM membersubscription 
        WHERE memberid = p_memberid 
        ORDER BY subscriptionid DESC
        LIMIT 1;
        
        IF v_current_subscription IS NOT NULL AND v_is_active THEN
            -- Se ativando, atualizar a subscrição mais recente
            UPDATE membersubscription 
            SET planid = p_plan,
                isactive = TRUE,
                startdate = CURRENT_DATE,
                enddate = CURRENT_DATE + INTERVAL '1 year'
            WHERE subscriptionid = v_current_subscription;
        ELSIF v_current_subscription IS NOT NULL AND NOT v_is_active THEN
            -- Se desativando, apenas atualizar o plano mas manter inativo
            UPDATE membersubscription 
            SET planid = p_plan
            WHERE subscriptionid = v_current_subscription;
        ELSIF v_current_subscription IS NULL THEN
            -- Criar nova subscrição se não existir nenhuma
            INSERT INTO membersubscription (memberid, planid, startdate, enddate, isactive)
            VALUES (p_memberid, p_plan, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 year', v_is_active);
        END IF;
    ELSE
        -- Se não mudou o plano, apenas atualizar o status da subscrição mais recente
        IF v_is_active THEN
            UPDATE membersubscription 
            SET isactive = TRUE,
                startdate = CURRENT_DATE,
                enddate = CURRENT_DATE + INTERVAL '1 year'
            WHERE memberid = p_memberid 
            AND subscriptionid = (
                SELECT subscriptionid 
                FROM membersubscription 
                WHERE memberid = p_memberid 
                ORDER BY subscriptionid DESC 
                LIMIT 1
            );
        END IF;
    END IF;
    
    RAISE NOTICE 'Member % updated successfully with status %', p_memberid, p_status;
END;
$$;

-- Procedimento para alterar apenas o status de um membro
CREATE OR REPLACE PROCEDURE sp_change_member_status(
    p_memberid INTEGER,
    p_status VARCHAR(20)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_userid INTEGER;
    v_is_active BOOLEAN;
BEGIN
    -- Get userid from memberid
    SELECT m.userid INTO v_userid 
    FROM member m 
    WHERE m.memberid = p_memberid;
    
    IF v_userid IS NULL THEN
        RAISE EXCEPTION 'Member with ID % not found', p_memberid;
    END IF;
    
    -- Determinar se o usuário deve estar ativo baseado no status
    v_is_active := CASE 
        WHEN p_status = 'ativo' THEN TRUE 
        ELSE FALSE 
    END;
    
    -- Update user active status
    UPDATE users 
    SET isactive = v_is_active
    WHERE userid = v_userid;
    
    -- Update subscription active status
    UPDATE membersubscription 
    SET isactive = v_is_active
    WHERE memberid = p_memberid;
    
    RAISE NOTICE 'Member % status changed to %', p_memberid, p_status;
END;
$$;

-- Stored procedures for class management

-- Procedure to create a new class
CREATE OR REPLACE PROCEDURE sp_create_class(
    p_name VARCHAR(100),
    p_instructorid INTEGER,
    p_room VARCHAR(50),
    p_capacity INTEGER,
    p_duration_minutes INTEGER,
    OUT p_classid INTEGER
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO class (name, instructorid, room, capacity, duration_minutes, isactive)
    VALUES (p_name, p_instructorid, p_room, p_capacity, p_duration_minutes, true)
    RETURNING classid INTO p_classid;
    
    RAISE NOTICE 'Class created with ID: %', p_classid;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error creating class: %', SQLERRM;
END;
$$;

-- Procedure to schedule a class
CREATE OR REPLACE PROCEDURE sp_schedule_class(
    p_classid INTEGER,
    p_date DATE,
    p_starttime TIME,
    p_endtime TIME,
    p_maxparticipants INTEGER,
    OUT p_classscheduleid INTEGER
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Verify class exists and is active
    IF NOT EXISTS (SELECT 1 FROM class WHERE classid = p_classid AND isactive = true) THEN
        RAISE EXCEPTION 'Class with ID % not found or inactive', p_classid;
    END IF;
    
    -- Insert the class schedule
    INSERT INTO classschedule (classid, date, starttime, endtime, maxparticipants, isactive)
    VALUES (p_classid, p_date, p_starttime, p_endtime, p_maxparticipants, true)
    RETURNING classscheduleid INTO p_classscheduleid;
    
    RAISE NOTICE 'Class scheduled with ID: %', p_classscheduleid;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error scheduling class: %', SQLERRM;
END;
$$;

-- Procedure to create and schedule a class in one step
CREATE OR REPLACE PROCEDURE sp_create_and_schedule_class(
    p_class_name VARCHAR(100),
    p_instructorid INTEGER,
    p_room VARCHAR(50),
    p_capacity INTEGER,
    p_duration_minutes INTEGER,
    p_date DATE,
    p_starttime TIME,
    p_endtime TIME,
    p_maxparticipants INTEGER,
    OUT p_classscheduleid INTEGER
)
LANGUAGE plpgsql AS $$
DECLARE
    v_classid INTEGER;
BEGIN
    -- Create the class first
    CALL sp_create_class(p_class_name, p_instructorid, p_room, p_capacity, p_duration_minutes, v_classid);
    
    -- Schedule the class
    CALL sp_schedule_class(v_classid, p_date, p_starttime, p_endtime, p_maxparticipants, p_classscheduleid);
    
    RAISE NOTICE 'Class created and scheduled with schedule ID: %', p_classscheduleid;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error creating and scheduling class: %', SQLERRM;
END;
$$;

-- Function to check class schedule conflicts for room
CREATE OR REPLACE FUNCTION fn_check_room_conflict(
    p_room VARCHAR(50),
    p_date DATE,
    p_starttime TIME,
    p_endtime TIME,
    p_exclude_schedule_id INTEGER DEFAULT NULL
) RETURNS BOOLEAN
LANGUAGE plpgsql AS $$
DECLARE
    v_conflict_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_conflict_count
    FROM classschedule cs
    JOIN class c ON cs.classid = c.classid
    WHERE c.room = p_room 
      AND cs.date = p_date 
      AND cs.isactive = true
      AND c.isactive = true
      AND (p_exclude_schedule_id IS NULL OR cs.classscheduleid != p_exclude_schedule_id)
      AND (
          (p_starttime BETWEEN cs.starttime AND cs.endtime) OR
          (p_endtime BETWEEN cs.starttime AND cs.endtime) OR
          (cs.starttime BETWEEN p_starttime AND p_endtime) OR
          (cs.endtime BETWEEN p_starttime AND p_endtime)
      );
    
    RETURN v_conflict_count > 0;
END;
$$;

-- Function to check class schedule conflicts for instructor
CREATE OR REPLACE FUNCTION fn_check_instructor_conflict(
    p_instructorid INTEGER,
    p_date DATE,
    p_starttime TIME,
    p_endtime TIME,
    p_exclude_schedule_id INTEGER DEFAULT NULL
) RETURNS BOOLEAN
LANGUAGE plpgsql AS $$
DECLARE
    v_conflict_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_conflict_count
    FROM classschedule cs
    JOIN class c ON cs.classid = c.classid
    WHERE c.instructorid = p_instructorid 
      AND cs.date = p_date 
      AND cs.isactive = true
      AND c.isactive = true
      AND (p_exclude_schedule_id IS NULL OR cs.classscheduleid != p_exclude_schedule_id)
      AND (
          (p_starttime BETWEEN cs.starttime AND cs.endtime) OR
          (p_endtime BETWEEN cs.starttime AND cs.endtime) OR
          (cs.starttime BETWEEN p_starttime AND p_endtime) OR
          (cs.endtime BETWEEN p_starttime AND p_endtime)
      );
    
    RETURN v_conflict_count > 0;
END;
$$;

-- Procedure to update class schedule
CREATE OR REPLACE PROCEDURE sp_update_class_schedule(
    p_classscheduleid INTEGER,
    p_date DATE,
    p_starttime TIME,
    p_endtime TIME,
    p_maxparticipants INTEGER
)
LANGUAGE plpgsql AS $$
DECLARE
    v_current_enrolled INTEGER;
BEGIN
    -- Check if schedule exists
    IF NOT EXISTS (SELECT 1 FROM classschedule WHERE classscheduleid = p_classscheduleid AND isactive = true) THEN
        RAISE EXCEPTION 'Class schedule with ID % not found or inactive', p_classscheduleid;
    END IF;
    
    -- Check if new max participants is not less than current enrolled
    SELECT COUNT(*) INTO v_current_enrolled
    FROM classbooking cb
    WHERE cb.classscheduleid = p_classscheduleid;
    
    IF p_maxparticipants < v_current_enrolled THEN
        RAISE EXCEPTION 'Cannot reduce max participants to % as there are already % members enrolled', 
                        p_maxparticipants, v_current_enrolled;
    END IF;
    
    -- Update the schedule
    UPDATE classschedule 
    SET date = p_date, 
        starttime = p_starttime, 
        endtime = p_endtime, 
        maxparticipants = p_maxparticipants
    WHERE classscheduleid = p_classscheduleid;
    
    RAISE NOTICE 'Class schedule % updated successfully', p_classscheduleid;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error updating class schedule: %', SQLERRM;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_create_machine(
    p_name VARCHAR(100),
    p_serialnumber VARCHAR(50),
    p_type VARCHAR(50),
    p_manufacturer VARCHAR(100),
    p_model VARCHAR(100),
    p_installationdate DATE,
    p_machinestatusid INTEGER DEFAULT 1
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Verificar se o código (serialnumber) já existe
    IF EXISTS (SELECT 1 FROM machine WHERE serialnumber = p_serialnumber) THEN
        RAISE EXCEPTION 'Este código já está em uso: %', p_serialnumber;
    END IF;
    
    -- Verificar se o nome já existe
    IF EXISTS (SELECT 1 FROM machine WHERE name = p_name) THEN
        RAISE EXCEPTION 'Este nome já está em uso: %', p_name;
    END IF;
    
    -- Inserir nova máquina
    INSERT INTO machine (
        name, 
        serialnumber, 
        type, 
        manufacturer, 
        model, 
        installationdate, 
        machinestatusid
    ) VALUES (
        p_name, 
        p_serialnumber, 
        p_type, 
        p_manufacturer, 
        p_model, 
        p_installationdate, 
        p_machinestatusid
    );
    
    RAISE NOTICE 'Machine created successfully: %', p_name;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error creating machine: %', SQLERRM;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_update_machine(
    p_machineid INTEGER,
    p_name VARCHAR(100),
    p_serialnumber VARCHAR(50),
    p_type VARCHAR(50),
    p_manufacturer VARCHAR(100),
    p_model VARCHAR(100),
    p_installationdate DATE,
    p_machinestatusid INTEGER
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Verificar se a máquina existe
    IF NOT EXISTS (SELECT 1 FROM machine WHERE machineid = p_machineid) THEN
        RAISE EXCEPTION 'Machine not found with ID: %', p_machineid;
    END IF;
    
    -- Verificar se o código já existe em outra máquina
    IF EXISTS (
        SELECT 1 FROM machine 
        WHERE serialnumber = p_serialnumber 
        AND machineid != p_machineid
    ) THEN
        RAISE EXCEPTION 'Este código já está em uso: %', p_serialnumber;
    END IF;
    
    -- Verificar se o nome já existe em outra máquina
    IF EXISTS (
        SELECT 1 FROM machine 
        WHERE name = p_name 
        AND machineid != p_machineid
    ) THEN
        RAISE EXCEPTION 'Este nome já está em uso: %', p_name;
    END IF;
    
    -- Atualizar máquina
    UPDATE machine 
    SET name = p_name,
        serialnumber = p_serialnumber,
        type = p_type,
        manufacturer = p_manufacturer,
        model = p_model,
        installationdate = p_installationdate,
        machinestatusid = p_machinestatusid
    WHERE machineid = p_machineid;
    
    RAISE NOTICE 'Machine % updated successfully', p_machineid;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error updating machine: %', SQLERRM;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_change_machine_status(
    p_machineid INTEGER,
    p_new_status INTEGER,
    p_maintenance_date DATE DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Verificar se a máquina existe
    IF NOT EXISTS (SELECT 1 FROM machine WHERE machineid = p_machineid) THEN
        RAISE EXCEPTION 'Machine not found with ID: %', p_machineid;
    END IF;
    
    -- Verificar se o status existe
    IF NOT EXISTS (SELECT 1 FROM machinestatus WHERE machinestatusid = p_new_status) THEN
        RAISE EXCEPTION 'Invalid machine status ID: %', p_new_status;
    END IF;
    
    -- Atualizar status da máquina
    IF p_new_status = 2 AND p_maintenance_date IS NOT NULL THEN
        -- Em manutenção com data
        UPDATE machine 
        SET machinestatusid = p_new_status,
            maintenancedate = p_maintenance_date
        WHERE machineid = p_machineid;
    ELSE
        -- Outros status sem data de manutenção obrigatória
        UPDATE machine 
        SET machinestatusid = p_new_status
        WHERE machineid = p_machineid;
    END IF;
    
    RAISE NOTICE 'Machine % status changed successfully to %', p_machineid, p_new_status;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Error changing machine status: %', SQLERRM;
END;
$$;

-- Stored procedure para atualizar planos
CREATE OR REPLACE PROCEDURE sp_update_plan(
    p_planid INTEGER,
    p_name VARCHAR(80),
    p_monthlyprice DECIMAL(10,2),
    p_description TEXT,
    p_access24h BOOLEAN
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Validações
    IF p_name IS NULL OR TRIM(p_name) = '' THEN
        RAISE EXCEPTION 'Nome do plano não pode estar vazio';
    END IF;
    
    IF p_monthlyprice IS NULL OR p_monthlyprice < 0 THEN
        RAISE EXCEPTION 'Preço mensal deve ser maior ou igual a zero';
    END IF;
    
    -- Verificar se o plano existe
    IF NOT EXISTS (SELECT 1 FROM plan WHERE planid = p_planid) THEN
        RAISE EXCEPTION 'Plano com ID % não encontrado', p_planid;
    END IF;
    
    -- Verificar se o nome já existe em outro plano
    IF EXISTS (
        SELECT 1 FROM plan 
        WHERE LOWER(TRIM(name)) = LOWER(TRIM(p_name)) 
        AND planid != p_planid 
        AND isactive = true
    ) THEN
        RAISE EXCEPTION 'Já existe um plano com o nome "%"', p_name;
    END IF;
    
    -- Atualizar o plano
    UPDATE plan 
    SET 
        name = TRIM(p_name),
        monthlyprice = p_monthlyprice,
        description = p_description,
        access24h = COALESCE(p_access24h, false),
        updated_at = CURRENT_TIMESTAMP
    WHERE planid = p_planid;
    
    RAISE NOTICE 'Plano % atualizado com sucesso', p_planid;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erro ao atualizar plano: %', SQLERRM;
END;
$$;

-- Procedure for member self-update (without plan changes)
DROP PROCEDURE IF EXISTS sp_member_update_profile;

CREATE OR REPLACE PROCEDURE sp_member_update_profile(
    p_userid INTEGER,
    p_name VARCHAR(100),
    p_email VARCHAR(254),
    p_phone VARCHAR(15),
    p_birthdate DATE,
    p_gender VARCHAR(10),
    p_nif CHAR(9),
    p_address VARCHAR(255),
    p_city VARCHAR(100),
    p_postalcode VARCHAR(20),
    p_iban VARCHAR(34)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_memberid INTEGER;
BEGIN
    -- Verificar se o utilizador existe e é um membro
    SELECT m.memberid INTO v_memberid
    FROM member m
    JOIN users u ON m.userid = u.userid
    WHERE u.userid = p_userid AND u.usertypeid = 3;
    
    IF v_memberid IS NULL THEN
        RAISE EXCEPTION 'Membro não encontrado ou utilizador não é um membro';
    END IF;
    
    -- Atualizar informações do utilizador
    UPDATE users 
    SET name = p_name, 
        email = p_email
    WHERE userid = p_userid;
    
    -- Atualizar informações do membro
    UPDATE member 
    SET phone = p_phone,
        birthdate = p_birthdate,
        gender = p_gender,
        nif = p_nif,
        address = p_address,
        city = p_city,
        postalcode = p_postalcode,
        iban = p_iban
    WHERE memberid = v_memberid;
    
    RAISE NOTICE 'Perfil do membro % atualizado com sucesso', v_memberid;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erro ao atualizar perfil: %', SQLERRM;
END;
$$;


CREATE OR REPLACE PROCEDURE sp_change_user_password(
    p_userid INTEGER,
    p_current_password VARCHAR(255),
    p_new_password VARCHAR(255)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_stored_password VARCHAR(255);
    v_user_exists BOOLEAN := FALSE;
BEGIN
    -- Verificar se o utilizador existe
    SELECT password INTO v_stored_password
    FROM users
    WHERE userid = p_userid AND isactive = true;
    
    IF v_stored_password IS NULL THEN
        RAISE EXCEPTION 'Utilizador não encontrado ou inativo';
    END IF;

    -- Atualizar a password
    UPDATE users 
    SET password = p_new_password
    WHERE userid = p_userid;
    
    RAISE NOTICE 'Password do utilizador % alterada com sucesso', p_userid;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erro ao alterar password: %', SQLERRM;
END;
$$;

-- Procedure for processing member payments
DROP PROCEDURE IF EXISTS sp_process_member_payment;

CREATE OR REPLACE PROCEDURE sp_process_member_payment(
    p_paymentid INTEGER,
    p_userid INTEGER,
    p_payment_method VARCHAR(50)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_payment_exists BOOLEAN := FALSE;
    v_payment_amount DECIMAL(10,2);
    v_member_name VARCHAR(100);
BEGIN
    -- Verificar se o pagamento existe, pertence ao membro e está pendente
    SELECT 
        CASE WHEN COUNT(*) > 0 THEN TRUE ELSE FALSE END,
        MAX(p.amount),
        MAX(u.name)
    INTO v_payment_exists, v_payment_amount, v_member_name
    FROM payment p
    JOIN membersubscription ms ON p.subscriptionid = ms.subscriptionid
    JOIN member m ON ms.memberid = m.memberid
    JOIN users u ON m.userid = u.userid
    WHERE p.paymentid = p_paymentid
      AND m.userid = p_userid
      AND p.ispayed = false;
    
    IF NOT v_payment_exists THEN
        RAISE EXCEPTION 'Pagamento não encontrado, já processado ou não pertence ao utilizador';
    END IF;
    
    -- Atualizar o pagamento
    UPDATE payment 
    SET ispayed = true,
        paymentdate = CURRENT_DATE,
        paymentmethod = p_payment_method
    WHERE paymentid = p_paymentid;
    
    RAISE NOTICE 'Pagamento % processado: €% via % para %', 
                 p_paymentid, v_payment_amount, p_payment_method, v_member_name;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erro ao processar pagamento: %', SQLERRM;
END;
$$;

-- Procedure for creating instructors
DROP PROCEDURE IF EXISTS sp_create_instructor;

CREATE OR REPLACE PROCEDURE sp_create_instructor(
    p_name VARCHAR(100),
    p_password VARCHAR(255),
    p_nif CHAR(9),
    p_email VARCHAR(254),
    p_phone VARCHAR(15),
    p_hired_at DATE
)
LANGUAGE plpgsql AS $$
DECLARE
    v_userid INTEGER;
    v_instructorid INTEGER;
BEGIN
    -- Verificar se email já existe
    IF EXISTS (SELECT 1 FROM USERS WHERE email = p_email) THEN
        RAISE EXCEPTION 'Este email já está registado no sistema';
    END IF;
    
    -- Verificar se NIF já existe
    IF EXISTS (SELECT 1 FROM INSTRUCTOR WHERE nif = p_nif) THEN
        RAISE EXCEPTION 'Este NIF já está registado como instrutor';
    END IF;

    -- Criar user
    INSERT INTO USERS (email, password, name, usertypeid, isactive)
    VALUES (p_email, p_password, p_name, 2, TRUE)
    RETURNING userid INTO v_userid;

    -- Criar instrutor
    INSERT INTO INSTRUCTOR (userid, nif, phone, isactive, created_at)
    VALUES (v_userid, p_nif, p_phone, TRUE, p_hired_at)
    RETURNING instructorid INTO v_instructorid;

    RAISE NOTICE 'Instrutor criado com ID: %, User criado com ID: %', v_instructorid, v_userid;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erro ao criar instrutor: %', SQLERRM;
END;
$$;

-- Procedure for updating instructors
DROP PROCEDURE IF EXISTS sp_update_instructor;

CREATE OR REPLACE PROCEDURE sp_update_instructor(
    p_instructorid INTEGER,
    p_name VARCHAR(100),
    p_nif CHAR(9),
    p_email VARCHAR(254),
    p_phone VARCHAR(15),
    p_hired_at DATE,
    p_isactive BOOLEAN
)
LANGUAGE plpgsql AS $$
DECLARE
    v_userid INTEGER;
    v_existing_instructor_id INTEGER;
    v_existing_user_id INTEGER;
BEGIN
    -- Obter userid do instrutor
    SELECT userid INTO v_userid
    FROM INSTRUCTOR
    WHERE instructorid = p_instructorid;
    
    IF v_userid IS NULL THEN
        RAISE EXCEPTION 'Instrutor não encontrado com ID: %', p_instructorid;
    END IF;
    
    -- Verificar se email já existe (excluindo o próprio user)
    SELECT userid INTO v_existing_user_id
    FROM USERS
    WHERE email = p_email AND userid != v_userid;
    
    IF v_existing_user_id IS NOT NULL THEN
        RAISE EXCEPTION 'Este email já está registado no sistema';
    END IF;
    
    -- Verificar se NIF já existe (excluindo o próprio instrutor)
    SELECT instructorid INTO v_existing_instructor_id
    FROM INSTRUCTOR
    WHERE nif = p_nif AND instructorid != p_instructorid;
    
    IF v_existing_instructor_id IS NOT NULL THEN
        RAISE EXCEPTION 'Este NIF já está registado como instrutor';
    END IF;

    -- Atualizar user
    UPDATE USERS
    SET email = p_email,
        name = p_name,
        isactive = p_isactive
    WHERE userid = v_userid;

    -- Atualizar instrutor
    UPDATE INSTRUCTOR
    SET nif = p_nif,
        phone = p_phone,
        isactive = p_isactive,
        created_at = p_hired_at
    WHERE instructorid = p_instructorid;

    RAISE NOTICE 'Instrutor % atualizado com sucesso', p_instructorid;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erro ao atualizar instrutor: %', SQLERRM;
END;
$$;

-- Procedimento para instrutor atualizar seu próprio perfil
CREATE OR REPLACE PROCEDURE sp_instructor_update_profile(
    IN p_userid INTEGER,
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(254),
    IN p_phone VARCHAR(15)
)
LANGUAGE plpgsql AS $$
BEGIN
    -- Verificar se o usuário é um instrutor
    IF NOT EXISTS (
        SELECT 1 FROM USERS u 
        JOIN INSTRUCTOR i ON u.userid = i.userid 
        WHERE u.userid = p_userid AND u.usertypeid = 2
    ) THEN
        RAISE EXCEPTION 'Usuário não é um instrutor válido';
    END IF;

    -- Verificar se email já existe para outro usuário
    IF EXISTS (SELECT 1 FROM USERS WHERE email = p_email AND userid != p_userid) THEN
        RAISE EXCEPTION 'Este email já está sendo usado por outro usuário';
    END IF;

    -- Atualizar dados do usuário
    UPDATE USERS 
    SET name = p_name,
        email = p_email
    WHERE userid = p_userid;

    -- Atualizar telefone do instrutor
    UPDATE INSTRUCTOR 
    SET phone = p_phone
    WHERE userid = p_userid;

    RAISE NOTICE 'Perfil do instrutor atualizado com sucesso para userid %', p_userid;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erro ao atualizar perfil do instrutor: %', SQLERRM;
END;
$$;

CREATE OR REPLACE FUNCTION fn_generate_financial_report()
RETURNS TABLE(
    financial_data JSON,
    statistics JSON
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        -- Dados financeiros principais
        (SELECT json_agg(row_to_json(fd))
         FROM (
            SELECT 
                p.paymentid,
                p.amount,
                p.paymentdate,
                p.paymentmethod,
                CASE 
                    WHEN p.ispayed = true THEN 'Pago'
                    WHEN p.paymentdate IS NULL AND p.duedate < CURRENT_DATE THEN 'Em Atraso'
                    ELSE 'Pendente'
                END as payment_status,
                m.memberid,
                u.name as member_name,
                u.email as member_email,
                ms.subscriptionid,
                pl.name as planname,
                pl.monthlyprice as plan_price,
                ms.startdate as subscription_start,
                ms.enddate as subscription_end,
                CASE 
                    WHEN ms.isactive = true THEN 'ativo'
                    ELSE 'inativo'
                END as subscription_status,
                EXTRACT(YEAR FROM p.paymentdate) as payment_year,
                EXTRACT(MONTH FROM p.paymentdate) as payment_month,
                p.duedate,
                p.reference
            FROM payment p
            JOIN membersubscription ms ON p.subscriptionid = ms.subscriptionid
            JOIN member m ON ms.memberid = m.memberid
            JOIN users u ON m.userid = u.userid
            JOIN plan pl ON ms.planid = pl.planid
            ORDER BY p.paymentdate DESC NULLS LAST, p.duedate DESC
         ) fd)::JSON as financial_data,
        
        -- Estatísticas agregadas
        (SELECT json_build_object(
            'total_payments', (SELECT COUNT(*) FROM payment),
            'total_amount', (SELECT COALESCE(SUM(amount), 0) FROM payment),
            'average_payment', (SELECT COALESCE(AVG(amount), 0) FROM payment),
            'payments_by_method', (
                SELECT json_object_agg(paymentmethod, count)
                FROM (
                    SELECT 
                        COALESCE(paymentmethod, 'Não Especificado') as paymentmethod, 
                        COUNT(*) as count
                    FROM payment
                    GROUP BY paymentmethod
                ) pm
            ),
            'payments_by_status', (
                SELECT json_object_agg(status, count)
                FROM (
                    SELECT 
                        CASE 
                            WHEN ispayed = true THEN 'Pago'
                            WHEN paymentdate IS NULL AND duedate < CURRENT_DATE THEN 'Em Atraso'
                            ELSE 'Pendente'
                        END as status, 
                        COUNT(*) as count
                    FROM payment
                    GROUP BY 
                        CASE 
                            WHEN ispayed = true THEN 'Pago'
                            WHEN paymentdate IS NULL AND duedate < CURRENT_DATE THEN 'Em Atraso'
                            ELSE 'Pendente'
                        END
                ) ps
            ),
            'monthly_revenue', (
                SELECT json_object_agg(
                    CONCAT(EXTRACT(YEAR FROM paymentdate), '-', 
                           LPAD(EXTRACT(MONTH FROM paymentdate)::text, 2, '0')), 
                    monthly_total
                )
                FROM (
                    SELECT 
                        EXTRACT(YEAR FROM paymentdate) as year,
                        EXTRACT(MONTH FROM paymentdate) as month,
                        paymentdate,
                        SUM(amount) as monthly_total
                    FROM payment
                    WHERE ispayed = true AND paymentdate IS NOT NULL
                    GROUP BY EXTRACT(YEAR FROM paymentdate), EXTRACT(MONTH FROM paymentdate), paymentdate
                    ORDER BY year DESC, month DESC
                    LIMIT 12
                ) mr
            ),
            'report_generated_at', NOW()
        ))::JSON as statistics;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;