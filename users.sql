/* ============================================================= */
/* LIMPEZA: REVOGAÇÃO TOTAL E REMOÇÃO DE USERS DA BD             */
/* ============================================================= */

-- Revogar privilégios em todas as tabelas existentes
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM gestor_db;
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM instrutor_db;
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM membro_db;

-- Revogar privilégios em sequences
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM gestor_db;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM instrutor_db;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM membro_db;

-- Revogar privilégios no schema
REVOKE ALL ON SCHEMA public FROM gestor_db;
REVOKE ALL ON SCHEMA public FROM instrutor_db;
REVOKE ALL ON SCHEMA public FROM membro_db;

-- Revogar CONNECT na BD (troca postgres se necessário)
REVOKE CONNECT ON DATABASE postgres FROM gestor_db;
REVOKE CONNECT ON DATABASE postgres FROM instrutor_db;
REVOKE CONNECT ON DATABASE postgres FROM membro_db;

-- Remover default privileges (necessário para permitir DROP ROLE)
ALTER DEFAULT PRIVILEGES FOR ROLE adminbd IN SCHEMA public
    REVOKE ALL PRIVILEGES ON TABLES FROM gestor_db;
ALTER DEFAULT PRIVILEGES FOR ROLE adminbd IN SCHEMA public
    REVOKE ALL PRIVILEGES ON SEQUENCES FROM gestor_db;

ALTER DEFAULT PRIVILEGES FOR ROLE adminbd IN SCHEMA public
    REVOKE ALL PRIVILEGES ON TABLES FROM instrutor_db;
ALTER DEFAULT PRIVILEGES FOR ROLE adminbd IN SCHEMA public
    REVOKE ALL PRIVILEGES ON SEQUENCES FROM instrutor_db;

ALTER DEFAULT PRIVILEGES FOR ROLE adminbd IN SCHEMA public
    REVOKE ALL PRIVILEGES ON TABLES FROM membro_db;
ALTER DEFAULT PRIVILEGES FOR ROLE adminbd IN SCHEMA public
    REVOKE ALL PRIVILEGES ON SEQUENCES FROM membro_db;

-- Finalmente remover as roles
DROP ROLE IF EXISTS gestor_db;
DROP ROLE IF EXISTS instrutor_db;
DROP ROLE IF EXISTS membro_db;

/* ============================================================= */
/* FIM DA LIMPEZA                                                */
/* ============================================================= */


/* ============================================================= */
/* CRIAÇÃO DE UTILIZADORES DA BASE DE DADOS                      */
/* ============================================================= */

-- Criar os três utilizadores (roles de login)
CREATE ROLE gestor_db    LOGIN PASSWORD 'GestorPass123!';
CREATE ROLE instrutor_db LOGIN PASSWORD 'InstrutorPass123!';
CREATE ROLE membro_db    LOGIN PASSWORD 'MembroPass123!';

-- Dar acesso básico à base de dados e ao schema
-- (troca 'postgres' pelo nome da tua BD se for outra, ex.: primefit)
GRANT CONNECT ON DATABASE postgres TO gestor_db, instrutor_db, membro_db;
GRANT USAGE ON SCHEMA public TO gestor_db, instrutor_db, membro_db;


/* ============================================================= */
/* PERMISSÕES DO GESTOR                                          */
/* Pode ver e alterar dados em TODAS as tabelas                  */
/* (mas não ganha privilégios “extra” de estrutura)              */
/* ============================================================= */

-- Permissões de dados em todas as tabelas
GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO gestor_db;

-- Permissões nas sequences (para poder fazer INSERT nas tabelas)
GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO gestor_db;

-- Default privileges para futuras tabelas e sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO gestor_db;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO gestor_db;


/* ============================================================= */
/* PERMISSÕES DO MEMBRO                                          */
/* Pode ver:                                                     */
/*   member, membersubscription, plan, payment,                  */
/*   class, classbooking, classschedule, checkin                 */
/* Pode inserir/alterar/apagar em:                               */
/*   member, membersubscription, classbooking                    */
/* ============================================================= */

-- VER (SELECT)
GRANT SELECT ON
    member,
    membersubscription,
    plan,
    payment,
    class,
    classbooking,
    classschedule,
    checkin
TO membro_db;

-- INSERIR / ALTERAR / APAGAR
GRANT INSERT, UPDATE, DELETE ON
    member,
    membersubscription,
    classbooking
TO membro_db;

-- SEQUENCES necessárias para INSERT
GRANT USAGE, SELECT ON SEQUENCE
    member_memberid_seq,
    membersubscription_subscriptionid_seq,
    classbooking_bookingid_seq
TO membro_db;


/* ============================================================= */
/* PERMISSÕES DO INSTRUTOR                                       */
/* Pode ver:                                                     */
/*   instructor, class, classschedule, machine,                  */
/*   machinemaintenancelog, classbooking                         */
/* Pode inserir/alterar/apagar em:                               */
/*   instructor, class, classschedule                            */
/* ============================================================= */

-- VER (SELECT)
GRANT SELECT ON
    instructor,
    class,
    classschedule,
    machine,
    machinemaintenancelog,
    classbooking
TO instrutor_db;

-- INSERIR / ALTERAR / APAGAR
GRANT INSERT, UPDATE, DELETE ON
    instructor,
    class,
    classschedule
TO instrutor_db;

-- SEQUENCES necessárias para INSERT
GRANT USAGE, SELECT ON SEQUENCE
    instructor_instructorid_seq,
    class_classid_seq,
    classschedule_classscheduleid_seq
TO instrutor_db;
/* ============================================================= */
