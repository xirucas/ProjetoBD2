/*==============================================================*/
/* DBMS name:      PostgreSQL 9.x                               */
/* Created on:     29/10/2025 10:12:47                          */
/*==============================================================*/

-- DROP TABLES AND INDEXES IN DEPENDENCY ORDER (child to parent)
-- First drop foreign key constraints to avoid dependency issues
DROP TABLE IF EXISTS CHECKIN CASCADE;
DROP TABLE IF EXISTS CLASSBOOKING CASCADE;
DROP TABLE IF EXISTS PAYMENT CASCADE;
DROP TABLE IF EXISTS MEMBERSUBSCRIPTION CASCADE;
DROP TABLE IF EXISTS CLASSSCHEDULE CASCADE;
DROP TABLE IF EXISTS MACHINEMAINTENANCELOG CASCADE;
DROP TABLE IF EXISTS CLASS CASCADE;
DROP TABLE IF EXISTS MACHINE CASCADE;
DROP TABLE IF EXISTS USERS CASCADE;
DROP TABLE IF EXISTS MEMBER CASCADE;
DROP TABLE IF EXISTS INSTRUCTOR CASCADE;
DROP TABLE IF EXISTS PLAN CASCADE;
DROP TABLE IF EXISTS MACHINESTATUS CASCADE;
DROP TABLE IF EXISTS USERTYPE CASCADE;

-- CREATE TABLES IN DEPENDENCY ORDER (parent to child)

/*==============================================================*/
/* Table: USERTYPE                                              */
/*==============================================================*/
CREATE TABLE USERTYPE (
   USERTYPEID           SERIAL               PRIMARY KEY,
   LABEL                VARCHAR(50)          NOT NULL UNIQUE CHECK (LABEL IN ('Gestor', 'Instrutor', 'Membro')),
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   UPDATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP
);

/*==============================================================*/
/* Table: MACHINESTATUS                                         */
/*==============================================================*/
CREATE TABLE MACHINESTATUS (
   MACHINESTATUSID      SERIAL               PRIMARY KEY,
   STATUS               VARCHAR(30)          NOT NULL UNIQUE,
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   UPDATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP
);

/*==============================================================*/
/* Table: PLAN                                                  */
/*==============================================================*/
CREATE TABLE PLAN (
   PLANID               SERIAL               PRIMARY KEY,
   NAME                 VARCHAR(80)          NOT NULL UNIQUE CHECK (LENGTH(TRIM(NAME)) > 0),
   MONTHLYPRICE         DECIMAL(10,2)        NOT NULL CHECK (MONTHLYPRICE >= 0),
   ACCESS24H            BOOLEAN              NOT NULL DEFAULT FALSE,
   DESCRIPTION          TEXT,
   ISACTIVE             BOOLEAN              NOT NULL DEFAULT TRUE,
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   UPDATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP
);

/*==============================================================*/
/* Table: USERS                                                 */
/*==============================================================*/
CREATE TABLE USERS (
   USERID               SERIAL               PRIMARY KEY,
   EMAIL                VARCHAR(254)         NOT NULL UNIQUE CHECK (EMAIL ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
   PASSWORD             VARCHAR(255)         NOT NULL CHECK (LENGTH(PASSWORD) >= 8),
   NAME                 VARCHAR(120)         NOT NULL CHECK (LENGTH(TRIM(NAME)) > 0),
   USERTYPEID           INTEGER              NOT NULL,
   ISACTIVE             BOOLEAN              NOT NULL DEFAULT TRUE,
   LAST_LOGIN           TIMESTAMP            NULL,
   PASSWORD_CHANGED_AT  TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   UPDATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT FK_USERS_USERTYPE FOREIGN KEY (USERTYPEID) 
      REFERENCES USERTYPE (USERTYPEID) ON DELETE RESTRICT ON UPDATE CASCADE
);

/*==============================================================*/
/* Table: INSTRUCTOR                                            */
/*==============================================================*/
CREATE TABLE INSTRUCTOR (
   INSTRUCTORID         SERIAL               PRIMARY KEY,
   USERID               INTEGER              UNIQUE,
   NIF                  CHAR(9)              NOT NULL UNIQUE CHECK (NIF ~ '^[0-9]{9}$'),
   PHONE                VARCHAR(15)          CHECK (PHONE ~ '^[0-9+\-\s()]+$'),
   ISACTIVE             BOOLEAN              NOT NULL DEFAULT TRUE,
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   UPDATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT FK_INSTRUCTOR_USER FOREIGN KEY (USERID) 
      REFERENCES USERS (USERID) ON DELETE SET NULL ON UPDATE CASCADE
);

/*==============================================================*/
/* Table: MEMBER                                                */
/*==============================================================*/
CREATE TABLE MEMBER (
   MEMBERID             SERIAL               PRIMARY KEY,
   USERID               INTEGER              UNIQUE,
   NIF                  CHAR(9)              NOT NULL UNIQUE CHECK (NIF ~ '^[0-9]{9}$'),
   PHONE                VARCHAR(15)          NOT NULL CHECK (PHONE ~ '^[0-9+\-\s()]+$'),
   IBAN                 VARCHAR(34)          NOT NULL CHECK (LENGTH(IBAN) BETWEEN 15 AND 34),
   REGISTRATIONDATE     DATE                 NOT NULL DEFAULT CURRENT_DATE,
   BIRTHDATE            DATE                 NOT NULL,
   GENDER               VARCHAR(10)          CHECK (GENDER IN ('Masculino', 'Feminino', 'Outro')),
   ADDRESS              VARCHAR(255)         NOT NULL,
   CITY                 VARCHAR(100)         NOT NULL,
   POSTALCODE           VARCHAR(20)          NOT NULL,
   ISACTIVE             BOOLEAN              NOT NULL DEFAULT TRUE,
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   UPDATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT FK_MEMBER_USER FOREIGN KEY (USERID) 
      REFERENCES USERS (USERID) ON DELETE SET NULL ON UPDATE CASCADE
);

/*==============================================================*/
/* Table: MACHINE                                               */
/*==============================================================*/
CREATE TABLE MACHINE (
   MACHINEID            SERIAL               PRIMARY KEY,
   MACHINESTATUSID      INTEGER              NOT NULL,
   NAME                 VARCHAR(100)         NOT NULL CHECK (LENGTH(TRIM(NAME)) > 0),
   TYPE                 VARCHAR(50)          NOT NULL,
   MANUFACTURER         VARCHAR(100),
   MODEL                VARCHAR(100),
   SERIALNUMBER         VARCHAR(50)          UNIQUE,
   INSTALLATIONDATE     DATE                 NOT NULL DEFAULT CURRENT_DATE,
   MAINTENANCEDATE      DATE                 NOT NULL,
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   UPDATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT FK_MACHINE_STATUS FOREIGN KEY (MACHINESTATUSID) 
      REFERENCES MACHINESTATUS (MACHINESTATUSID) ON DELETE RESTRICT ON UPDATE CASCADE,
   CONSTRAINT CHK_MAINTENANCE_AFTER_INSTALL CHECK (MAINTENANCEDATE >= INSTALLATIONDATE)
);

/*==============================================================*/
/* Table: CLASS                                                 */
/*==============================================================*/
CREATE TABLE CLASS (
   CLASSID              SERIAL               PRIMARY KEY,
   INSTRUCTORID         INTEGER              NOT NULL,
   NAME                 VARCHAR(80)          NOT NULL CHECK (LENGTH(TRIM(NAME)) > 0),
   DESCRIPTION          TEXT,
   ROOM                 VARCHAR(20)          NOT NULL CHECK (LENGTH(TRIM(ROOM)) > 0),
   CAPACITY             INTEGER              NOT NULL CHECK (CAPACITY > 0 AND CAPACITY <= 100),
   DURATION_MINUTES     INTEGER              CHECK (DURATION_MINUTES > 0 AND DURATION_MINUTES <= 180),
   ISACTIVE             BOOLEAN              NOT NULL DEFAULT TRUE,
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   UPDATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT FK_CLASS_INSTRUCTOR FOREIGN KEY (INSTRUCTORID) 
      REFERENCES INSTRUCTOR (INSTRUCTORID) ON DELETE RESTRICT ON UPDATE CASCADE
);

/*==============================================================*/
/* Table: MEMBERSUBSCRIPTION                                    */
/*==============================================================*/
CREATE TABLE MEMBERSUBSCRIPTION (
   SUBSCRIPTIONID       SERIAL               PRIMARY KEY,
   PLANID               INTEGER              NOT NULL,
   MEMBERID             INTEGER              NOT NULL,
   STARTDATE            DATE                 NOT NULL DEFAULT CURRENT_DATE,
   ENDDATE              DATE                 NOT NULL,
   ISACTIVE             BOOLEAN              NOT NULL DEFAULT TRUE,
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   UPDATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT FK_MEMBERSUBSCRIPTION_MEMBER FOREIGN KEY (MEMBERID) 
      REFERENCES MEMBER (MEMBERID) ON DELETE RESTRICT ON UPDATE CASCADE,
   CONSTRAINT FK_MEMBERSUBSCRIPTION_PLAN FOREIGN KEY (PLANID) 
      REFERENCES PLAN (PLANID) ON DELETE RESTRICT ON UPDATE CASCADE,
   CONSTRAINT CHK_SUBSCRIPTION_DATES CHECK (ENDDATE IS NULL OR ENDDATE >= STARTDATE),
   CONSTRAINT UQ_ACTIVE_SUBSCRIPTION UNIQUE (MEMBERID, ISACTIVE) 
      DEFERRABLE INITIALLY DEFERRED
);

/*==============================================================*/
/* Table: CLASSSCHEDULE                                         */
/*==============================================================*/
CREATE TABLE CLASSSCHEDULE (
   CLASSSCHEDULEID      SERIAL               PRIMARY KEY,
   CLASSID              INTEGER              NOT NULL,
   DATE                 DATE                 NOT NULL,
   STARTTIME            TIME                 NOT NULL,
   ENDTIME              TIME                 NOT NULL,
   MAXPARTICIPANTS      INTEGER              CHECK (MAXPARTICIPANTS > 0),
   ISACTIVE             BOOLEAN              NOT NULL DEFAULT TRUE,
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   UPDATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT FK_CLASSSCHEDULE_CLASS FOREIGN KEY (CLASSID) 
      REFERENCES CLASS (CLASSID) ON DELETE RESTRICT ON UPDATE CASCADE,
   CONSTRAINT CHK_SCHEDULE_TIMES CHECK (ENDTIME > STARTTIME),
   CONSTRAINT UQ_CLASS_DATETIME UNIQUE (CLASSID, DATE, STARTTIME)
);

/*==============================================================*/
/* Table: MACHINEMAINTENANCELOG                                 */
/*==============================================================*/
CREATE TABLE MACHINEMAINTENANCELOG (
   LOGID                SERIAL               PRIMARY KEY,
   MACHINEID            INTEGER              NOT NULL,
   MAINTENANCEDATE      DATE                 NOT NULL DEFAULT CURRENT_DATE,
   DESCRIPTION          TEXT                 NOT NULL CHECK (LENGTH(TRIM(DESCRIPTION)) > 0),
   TECHNICIAN          VARCHAR(80)          NOT NULL CHECK (LENGTH(TRIM(TECHNICIAN)) > 0),
   COST                 DECIMAL(10,2)        NOT NULL CHECK (COST >= 0),
   MAINTENANCETYPE      VARCHAR(50)          NOT NULL DEFAULT 'ROUTINE',
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT FK_MAINTENANCELOG_MACHINE FOREIGN KEY (MACHINEID) 
      REFERENCES MACHINE (MACHINEID) ON DELETE RESTRICT ON UPDATE CASCADE
);

/*==============================================================*/
/* Table: PAYMENT                                               */
/*==============================================================*/
CREATE TABLE PAYMENT (
   PAYMENTID            SERIAL               PRIMARY KEY,
   SUBSCRIPTIONID       INTEGER              NOT NULL,
   AMOUNT               DECIMAL(10,2)        NOT NULL CHECK (AMOUNT > 0),
   ISPAYED              BOOLEAN              NOT NULL DEFAULT FALSE,
   DUEDATE              DATE                 NOT NULL,
   PAYMENTDATE          DATE                 NULL,
   PAYMENTMETHOD        VARCHAR(50),
   REFERENCE            VARCHAR(100)         UNIQUE,
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   UPDATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT FK_PAYMENT_SUBSCRIPTION FOREIGN KEY (SUBSCRIPTIONID) 
      REFERENCES MEMBERSUBSCRIPTION (SUBSCRIPTIONID) ON DELETE RESTRICT ON UPDATE CASCADE,
   CONSTRAINT CHK_PAYMENT_DATE CHECK (PAYMENTDATE IS NULL OR PAYMENTDATE >= DUEDATE)
);

/*==============================================================*/
/* Table: CLASSBOOKING                                          */
/*==============================================================*/
CREATE TABLE CLASSBOOKING (
   BOOKINGID            SERIAL               PRIMARY KEY,
   MEMBERID             INTEGER              NOT NULL,
   CLASSSCHEDULEID      INTEGER              NOT NULL,
   BOOKINGDATE          TIMESTAMP            NOT NULL DEFAULT CURRENT_TIMESTAMP,
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   UPDATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT FK_CLASSBOOKING_MEMBER FOREIGN KEY (MEMBERID) 
      REFERENCES MEMBER (MEMBERID) ON DELETE RESTRICT ON UPDATE CASCADE,
   CONSTRAINT FK_CLASSBOOKING_SCHEDULE FOREIGN KEY (CLASSSCHEDULEID) 
      REFERENCES CLASSSCHEDULE (CLASSSCHEDULEID) ON DELETE RESTRICT ON UPDATE CASCADE,
   CONSTRAINT UQ_MEMBER_CLASS_BOOKING UNIQUE (MEMBERID, CLASSSCHEDULEID)
);

/*==============================================================*/
/* Table: CHECKIN                                               */
/*==============================================================*/
CREATE TABLE CHECKIN (
   CHECKINID            SERIAL               PRIMARY KEY,
   MEMBERID             INTEGER              NOT NULL,
   DATE                 DATE                 NOT NULL DEFAULT CURRENT_DATE,
   ENTRANCETIME         TIME                 NOT NULL DEFAULT CURRENT_TIME,
   EXITTIME             TIME                 NULL,
   CREATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   UPDATED_AT           TIMESTAMP            DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT FK_CHECKIN_MEMBER FOREIGN KEY (MEMBERID) 
      REFERENCES MEMBER (MEMBERID) ON DELETE RESTRICT ON UPDATE CASCADE,
   CONSTRAINT CHK_CHECKIN_TIMES CHECK (EXITTIME IS NULL OR EXITTIME > ENTRANCETIME)
);

-- CREATE PERFORMANCE INDEXES
-- Indexes for frequent queries and foreign keys
-- CREATE PERFORMANCE INDEXES
-- Indexes chosen to support frequent queries and filters.
-- Note: UNIQUE and PRIMARY KEY constraints already create indexes; avoid duplicating them.

-- MEMBER indexes
-- NIF is UNIQUE, so no separate index needed. Keep partial index for active members and registration lookup.
CREATE INDEX IF NOT EXISTS IDX_MEMBER_ACTIVE ON MEMBER (ISACTIVE) WHERE ISACTIVE = TRUE;
CREATE INDEX IF NOT EXISTS IDX_MEMBER_REGISTRATION_DATE ON MEMBER (REGISTRATIONDATE);

-- INSTRUCTOR indexes
-- NIF is UNIQUE (no separate index). Keep partial index for active instructors.
CREATE INDEX IF NOT EXISTS IDX_INSTRUCTOR_ACTIVE ON INSTRUCTOR (ISACTIVE) WHERE ISACTIVE = TRUE;

-- CHECKIN indexes
-- Composite index for member + date to support recent checkins per member.
CREATE INDEX IF NOT EXISTS IDX_CHECKIN_MEMBER_DATE ON CHECKIN (MEMBERID, DATE);
-- Separate index on date for queries like "WHERE date = CURRENT_DATE".
CREATE INDEX IF NOT EXISTS IDX_CHECKIN_DATE ON CHECKIN (DATE);
-- ENTRANCETIME is rarely filtered alone; omit index unless proven needed.

-- CLASS indexes
CREATE INDEX IF NOT EXISTS IDX_CLASS_INSTRUCTOR ON CLASS (INSTRUCTORID);
CREATE INDEX IF NOT EXISTS IDX_CLASS_ACTIVE ON CLASS (ISACTIVE) WHERE ISACTIVE = TRUE;
CREATE INDEX IF NOT EXISTS IDX_CLASS_ROOM ON CLASS (ROOM);

-- CLASSSCHEDULE indexes
CREATE INDEX IF NOT EXISTS IDX_CLASSSCHEDULE_CLASS ON CLASSSCHEDULE (CLASSID);
CREATE INDEX IF NOT EXISTS IDX_CLASSSCHEDULE_DATE_TIME ON CLASSSCHEDULE (DATE, STARTTIME);
CREATE INDEX IF NOT EXISTS IDX_CLASSSCHEDULE_ACTIVE ON CLASSSCHEDULE (ISACTIVE) WHERE ISACTIVE = TRUE;

-- CLASSBOOKING indexes
CREATE INDEX IF NOT EXISTS IDX_CLASSBOOKING_MEMBER ON CLASSBOOKING (MEMBERID);
CREATE INDEX IF NOT EXISTS IDX_CLASSBOOKING_SCHEDULE ON CLASSBOOKING (CLASSSCHEDULEID);
CREATE INDEX IF NOT EXISTS IDX_CLASSBOOKING_BOOKING_DATE ON CLASSBOOKING (BOOKINGDATE);

-- MEMBERSUBSCRIPTION indexes
CREATE INDEX IF NOT EXISTS IDX_MEMBERSUBSCRIPTION_MEMBER ON MEMBERSUBSCRIPTION (MEMBERID);
CREATE INDEX IF NOT EXISTS IDX_MEMBERSUBSCRIPTION_PLAN ON MEMBERSUBSCRIPTION (PLANID);
CREATE INDEX IF NOT EXISTS IDX_MEMBERSUBSCRIPTION_ACTIVE ON MEMBERSUBSCRIPTION (ISACTIVE) WHERE ISACTIVE = TRUE;
CREATE INDEX IF NOT EXISTS IDX_MEMBERSUBSCRIPTION_DATES ON MEMBERSUBSCRIPTION (STARTDATE, ENDDATE);

-- PAYMENT indexes
CREATE INDEX IF NOT EXISTS IDX_PAYMENT_SUBSCRIPTION ON PAYMENT (SUBSCRIPTIONID);
CREATE INDEX IF NOT EXISTS IDX_PAYMENT_DUE_DATE ON PAYMENT (DUEDATE);
CREATE INDEX IF NOT EXISTS IDX_PAYMENT_UNPAID_DUE ON PAYMENT (DUEDATE) WHERE ISPAYED = FALSE;

-- MACHINE indexes
CREATE INDEX IF NOT EXISTS IDX_MACHINE_STATUS ON MACHINE (MACHINESTATUSID);
CREATE INDEX IF NOT EXISTS IDX_MACHINE_MAINTENANCE_DATE ON MACHINE (MAINTENANCEDATE);
CREATE INDEX IF NOT EXISTS IDX_MACHINE_TYPE ON MACHINE (TYPE);

-- MACHINEMAINTENANCELOG indexes
CREATE INDEX IF NOT EXISTS IDX_MAINTENANCELOG_MACHINE ON MACHINEMAINTENANCELOG (MACHINEID);
CREATE INDEX IF NOT EXISTS IDX_MAINTENANCELOG_DATE ON MACHINEMAINTENANCELOG (MAINTENANCEDATE);

-- PLAN indexes
CREATE INDEX IF NOT EXISTS IDX_PLAN_ACTIVE ON PLAN (ISACTIVE) WHERE ISACTIVE = TRUE;
CREATE INDEX IF NOT EXISTS IDX_PLAN_PRICE ON PLAN (MONTHLYPRICE);

-- USERTYPE / USERS
CREATE INDEX IF NOT EXISTS IDX_USERTYPE_LABEL ON USERTYPE (LABEL);
CREATE INDEX IF NOT EXISTS IDX_USERS_USERTYPE ON USERS (USERTYPEID);
CREATE INDEX IF NOT EXISTS IDX_USERS_ACTIVE ON USERS (ISACTIVE) WHERE ISACTIVE = TRUE;
CREATE INDEX IF NOT EXISTS IDX_USERS_LAST_LOGIN ON USERS (LAST_LOGIN);

-- Avoid creating explicit indexes on columns that already have UNIQUE constraints (e.g. MEMBER.NIF, MEMBER.USERID, INSTRUCTOR.NIF, INSTRUCTOR.USERID, USERS.EMAIL)

-- CREATE TRIGGERS FOR AUTOMATIC TIMESTAMPS
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.UPDATED_AT = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply timestamp triggers to all tables with UPDATED_AT
CREATE TRIGGER update_usertype_updated_at BEFORE UPDATE ON USERTYPE FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_machinestatus_updated_at BEFORE UPDATE ON MACHINESTATUS FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_instructor_updated_at BEFORE UPDATE ON INSTRUCTOR FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_plan_updated_at BEFORE UPDATE ON PLAN FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_member_updated_at BEFORE UPDATE ON MEMBER FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON USERS FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_machine_updated_at BEFORE UPDATE ON MACHINE FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_class_updated_at BEFORE UPDATE ON CLASS FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_membersubscription_updated_at BEFORE UPDATE ON MEMBERSUBSCRIPTION FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_classschedule_updated_at BEFORE UPDATE ON CLASSSCHEDULE FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payment_updated_at BEFORE UPDATE ON PAYMENT FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_classbooking_updated_at BEFORE UPDATE ON CLASSBOOKING FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_checkin_updated_at BEFORE UPDATE ON CHECKIN FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- CREATE SECURITY POLICIES (ROW LEVEL SECURITY)
-- Enable RLS on sensitive tables
ALTER TABLE MEMBER ENABLE ROW LEVEL SECURITY;
ALTER TABLE PAYMENT ENABLE ROW LEVEL SECURITY;
ALTER TABLE MEMBERSUBSCRIPTION ENABLE ROW LEVEL SECURITY;
ALTER TABLE USERS ENABLE ROW LEVEL SECURITY;

-- INSERT DEFAULT DATA
INSERT INTO USERTYPE (LABEL) VALUES 
('Gestor'),
('Instrutor'),
('Membro');

INSERT INTO MACHINESTATUS (STATUS) VALUES 
('Em manutenção'),
('Em funcionamento'),
('Avariada');

INSERT INTO PLAN (NAME, MONTHLYPRICE, ACCESS24H, DESCRIPTION) VALUES
('Basico', 20, FALSE, 'Apenas tem acesso durante o horário de funcionamento'),
('Premium', 30, TRUE, 'Acesso 24/7 com todas as comodidades'),
('Estudante', 15, TRUE, 'Tarifa especial para estudantes');

-- GRANT PERMISSIONS (adjust as needed for your security model)
-- CREATE ROLE gym_user;
-- CREATE ROLE gym_admin;
-- 
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO gym_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gym_admin;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO gym_user, gym_admin;

select u.userid, m.memberid, u.email, u.password from users u 
join member m on u.userid = m.userid


SELECT * FROM classbooking

