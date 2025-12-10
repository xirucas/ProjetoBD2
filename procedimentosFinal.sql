DROP PROCEDURE IF EXISTS sp_create_member;
DROP PROCEDURE IF EXISTS sp_update_last_login;

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
    p_postalcode VARCHAR(20)
)
LANGUAGE plpgsql AS $$
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
    
    RAISE NOTICE 'User criado com ID: %, Membro criado com ID: %', v_userid, v_memberid;
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

-- Comment: This procedure safely updates the last_login timestamp for a user
-- It includes error handling to ensure the user exists and provides meaningful error messages
