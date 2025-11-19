DROP PROCEDURE IF EXISTS sp_create_member;

CREATE OR REPLACE PROCEDURE sp_create_member(
    p_name VARCHAR(100),
    p_password VARCHAR(255),
    p_nif CHAR(9),
    p_email VARCHAR(254),
    p_phone VARCHAR(15),
    p_iban VARCHAR(34)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_userid INTEGER;
    v_memberid INTEGER;
BEGIN
    INSERT INTO USERS (email, password, name, usertypeid, isactive)
    VALUES (p_email, p_password, p_name, 3, TRUE)
    RETURNING userid INTO v_userid;

    INSERT INTO MEMBER (userid, nif, phone, iban)
    VALUES (v_userid, p_nif, p_phone, p_iban)
    RETURNING memberid INTO v_memberid;
    
    RAISE NOTICE 'User criado com ID: %, Membro criado com ID: %', v_userid, v_memberid;
END;
$$;