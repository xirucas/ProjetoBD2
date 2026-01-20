/*==============================================================*/
/* SEED DATA (BEM CARREGADO) - PrimeFit                          */
/* Foco: joao.silva@primefit.com e francisco.costa@gmail.com     */
/* Compatível com o teu esquema (PK SERIAL + constraints)        */
/*==============================================================*/
TRUNCATE TABLE CHECKIN CASCADE;
TRUNCATE TABLE CLASSBOOKING CASCADE;
TRUNCATE TABLE PAYMENT CASCADE;
TRUNCATE TABLE MEMBERSUBSCRIPTION CASCADE;
TRUNCATE TABLE CLASSSCHEDULE CASCADE;
TRUNCATE TABLE MACHINEMAINTENANCELOG CASCADE;
TRUNCATE TABLE CLASS CASCADE;
TRUNCATE TABLE MACHINE CASCADE;
TRUNCATE TABLE MEMBER CASCADE;
TRUNCATE TABLE INSTRUCTOR CASCADE;
TRUNCATE TABLE USERS RESTART IDENTITY CASCADE;
TRUNCATE TABLE PLAN RESTART IDENTITY CASCADE;
TRUNCATE TABLE MACHINESTATUS RESTART IDENTITY CASCADE;
TRUNCATE TABLE USERTYPE RESTART IDENTITY CASCADE;

-- Reset sequences
ALTER SEQUENCE usertype_usertypeid_seq RESTART WITH 1;
ALTER SEQUENCE machinestatus_machinestatusid_seq RESTART WITH 1;
ALTER SEQUENCE plan_planid_seq RESTART WITH 1;
ALTER SEQUENCE users_userid_seq RESTART WITH 1;
ALTER SEQUENCE instructor_instructorid_seq RESTART WITH 1;
ALTER SEQUENCE member_memberid_seq RESTART WITH 1;
ALTER SEQUENCE machine_machineid_seq RESTART WITH 1;
ALTER SEQUENCE class_classid_seq RESTART WITH 1;
ALTER SEQUENCE membersubscription_subscriptionid_seq RESTART WITH 1;
ALTER SEQUENCE classschedule_classscheduleid_seq RESTART WITH 1;
ALTER SEQUENCE machinemaintenancelog_logid_seq RESTART WITH 1;
ALTER SEQUENCE payment_paymentid_seq RESTART WITH 1;
ALTER SEQUENCE classbooking_bookingid_seq RESTART WITH 1;
ALTER SEQUENCE checkin_checkinid_seq RESTART WITH 1;

INSERT INTO USERTYPE (USERTYPEID, LABEL) VALUES
(1, 'Gestor'),
(2, 'Instrutor'),
(3, 'Membro');

INSERT INTO MACHINESTATUS (MACHINESTATUSID, STATUS) VALUES
(1, 'Em manutenção'),
(2, 'Em funcionamento'),
(3, 'Avariada'),
(4, 'Fora de Serviço');

INSERT INTO PLAN (PLANID, NAME, MONTHLYPRICE, ACCESS24H, DESCRIPTION, ISACTIVE) VALUES
(1, 'Basico',    20.00, FALSE, 'Apenas tem acesso durante o horário de funcionamento', TRUE),
(2, 'Premium',   30.00, TRUE,  'Acesso 24/7 com todas as comodidades', TRUE),
(3, 'Estudante', 15.00, TRUE,  'Tarifa especial para estudantes', TRUE);

INSERT INTO USERS (USERID, EMAIL, PASSWORD, NAME, USERTYPEID, ISACTIVE, LAST_LOGIN) VALUES
(1, 'admin@primefit.com',      'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Carlos Silva', 1, TRUE, '2026-01-19 08:30:00'),
(2, 'gestor@primefit.com',     'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Ana Costa',    1, TRUE, '2026-01-18 17:10:00'),
(3, 'supervisor@primefit.com', 'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Pedro Santos', 1, TRUE, '2026-01-17 10:05:00'),
(4, 'joao.silva@primefit.com',      'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'João Silva',        2, TRUE, '2026-01-20 09:05:00'),
(5, 'maria.santos@primefit.com',    'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Maria Santos',      2, TRUE, '2026-01-19 07:30:00'),
(6, 'ricardo.alves@primefit.com',   'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Ricardo Alves',     2, TRUE, '2026-01-18 18:00:00'),
(7, 'sofia.oliveira@primefit.com',  'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Sofia Oliveira',    2, TRUE, '2026-01-18 06:45:00'),
(8, 'bruno.fernandes@primefit.com', 'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Bruno Fernandes',   2, TRUE, '2026-01-17 19:30:00'),
(9, 'ines.moura@primefit.com',      'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Inês Moura',        2, TRUE, '2026-01-18 09:10:00'),
(10,'tiago.bastos@primefit.com',    'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Tiago Bastos',      2, TRUE, '2026-01-17 12:40:00'),
(11,'francisco.costa@gmail.com',    'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Francisco Costa',   3, TRUE, '2026-01-20 07:20:00'),
(12,'tiago.rodrigues@gmail.com',    'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Tiago Rodrigues',   3, TRUE, '2026-01-18 07:00:00'),
(13,'patricia.martins@gmail.com',   'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Patrícia Martins',  3, TRUE, '2026-01-18 18:30:00'),
(14,'andre.sousa@gmail.com',        'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'André Sousa',       3, TRUE, '2026-01-18 19:15:00'),
(15,'carolina.pereira@gmail.com',   'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Carolina Pereira',  3, TRUE, '2026-01-18 08:45:00'),
(16,'miguel.ferreira@gmail.com',    'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Miguel Ferreira',   3, TRUE, '2026-01-18 20:00:00'),
(17,'beatriz.gomes@gmail.com',      'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Beatriz Gomes',     3, TRUE, '2026-01-18 07:30:00'),
(18,'diogo.carvalho@gmail.com',     'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Diogo Carvalho',    3, TRUE, '2026-01-18 18:00:00'),
(19,'rita.lopes@gmail.com',         'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Rita Lopes',        3, TRUE, '2026-01-18 19:00:00'),
(20,'nuno.dias@gmail.com',          'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Nuno Dias',         3, TRUE, '2026-01-18 06:30:00'),
(21,'ines.ribeiro@gmail.com',       'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Inês Ribeiro',      3, TRUE, '2026-01-18 17:45:00'),
(22,'catarina.mendes@gmail.com',    'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Catarina Mendes',   3, TRUE, '2026-01-18 09:00:00'),
(23,'rafael.tavares@gmail.com',     'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Rafael Tavares',    3, TRUE, '2026-01-18 21:00:00'),
(24,'mariana.azevedo@gmail.com',    'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Mariana Azevedo',   3, TRUE, '2026-01-18 10:15:00'),
(25,'goncalo.pinto@gmail.com',      'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Gonçalo Pinto',     3, TRUE, '2026-01-18 16:30:00'),
(26,'sara.vieira@gmail.com',        'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Sara Vieira',       3, TRUE, '2026-01-18 11:00:00'),
(27,'hugo.moreira@gmail.com',       'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Hugo Moreira',      3, TRUE, '2026-01-18 22:00:00'),
(28,'joana.cunha@gmail.com',        'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Joana Cunha',       3, TRUE, '2026-01-18 08:00:00'),
(29,'vasco.monteiro@gmail.com',     'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Vasco Monteiro',    3, TRUE, '2026-01-18 15:00:00'),
(30,'leonor.ramos@gmail.com',       'pbkdf2_sha256$1000000$fCMSCex4VgdMDQC7V7GqF8$7WOI1MvnphAD1MFNUJFqyspTWXIilefu+/u7rKcoG6M=', 'Leonor Ramos',      3, TRUE, '2026-01-18 12:30:00');

INSERT INTO INSTRUCTOR (INSTRUCTORID, USERID, NIF, PHONE, ISACTIVE) VALUES
(1,  4,  '123456789', '+351912345678', TRUE),
(2,  5,  '234567890', '+351923456789', TRUE),
(3,  6,  '345678901', '+351934567890', TRUE),
(4,  7,  '456789012', '+351945678901', TRUE),
(5,  8,  '567890123', '+351956789012', TRUE),
(6,  9,  '678901234', '+351967890123', TRUE),
(7,  10, '789012345', '+351978901234', TRUE);

INSERT INTO MEMBER (MEMBERID, USERID, NIF, PHONE, IBAN, REGISTRATIONDATE, BIRTHDATE, GENDER, ADDRESS, CITY, POSTALCODE, ISACTIVE) VALUES
(1,  11, '121212121', '+351912121212', 'PT50000000000000000000011', '2025-08-01', '1990-06-06', 'Masculino', 'Rua dos Navegadores, 56', 'Funchal', '9000-900', TRUE),
(2,  12, '111111111', '+351911111111', 'PT50000000000000000000001', '2025-03-20', '1990-05-15', 'Masculino', 'Rua das Flores, 123', 'Lisboa', '1000-100', TRUE),
(3,  13, '222222222', '+351922222222', 'PT50000000000000000000002', '2025-04-05', '1992-08-22', 'Feminino',  'Avenida da Liberdade, 45', 'Lisboa', '1250-096', TRUE),
(4,  14, '333333333', '+351933333333', 'PT50000000000000000000003', '2025-04-10', '1988-11-30', 'Masculino', 'Rua de Santa Catarina, 67', 'Porto', '4000-200', TRUE),
(5,  15, '444444444', '+351944444444', 'PT50000000000000000000004', '2025-05-12', '1995-03-14', 'Feminino',  'Praça da República, 89', 'Coimbra', '3000-150', TRUE),
(6,  16, '555555555', '+351955555555', 'PT50000000000000000000005', '2025-05-20', '1991-07-08', 'Masculino', 'Rua Nova, 234', 'Braga', '4700-300', TRUE),
(7,  17, '666666666', '+351966666666', 'PT50000000000000000000006', '2025-06-01', '1993-12-25', 'Feminino',  'Avenida Central, 456', 'Faro', '8000-400', TRUE),
(8,  18, '777777777', '+351977777777', 'PT50000000000000000000007', '2025-06-15', '1989-09-17', 'Masculino', 'Rua do Sol, 78', 'Setúbal', '2900-500', TRUE),
(9,  19, '888888888', '+351988888888', 'PT50000000000000000000008', '2025-07-01', '1994-04-03', 'Feminino',  'Largo do Município, 90', 'Évora', '7000-600', TRUE),
(10, 20, '999999998', '+351999999998', 'PT50000000000000000000009', '2025-07-10', '1987-01-29', 'Masculino', 'Rua da Paz, 12', 'Aveiro', '3800-700', TRUE),
(11, 21, '101010101', '+351910101010', 'PT50000000000000000000010', '2025-07-20', '1996-10-11', 'Feminino',  'Avenida da Praia, 34', 'Cascais', '2750-800', TRUE),
(12, 22, '131313131', '+351913131313', 'PT50000000000000000000012', '2025-08-10', '1992-02-18', 'Feminino',  'Praça do Império, 78', 'Lisboa', '1400-110', TRUE),
(13, 23, '141414141', '+351914141414', 'PT50000000000000000000013', '2025-08-20', '1988-08-24', 'Masculino', 'Rua Augusta, 90', 'Lisboa', '1100-200', TRUE),
(14, 24, '151515151', '+351915151515', 'PT50000000000000000000014', '2025-09-01', '1995-11-07', 'Feminino',  'Avenida dos Aliados, 123', 'Porto', '4000-300', TRUE),
(15, 25, '161616161', '+351916161616', 'PT50000000000000000000015', '2025-09-10', '1991-03-21', 'Masculino', 'Rua do Comércio, 145', 'Porto', '4000-400', TRUE),
(16, 26, '171717171', '+351917171717', 'PT50000000000000000000016', '2025-09-15', '1993-05-13', 'Feminino',  'Largo Camões, 167', 'Lisboa', '1200-500', TRUE),
(17, 27, '181818181', '+351918181818', 'PT50000000000000000000017', '2025-10-01', '1989-12-01', 'Masculino', 'Rua Garrett, 189', 'Lisboa', '1200-600', TRUE),
(18, 28, '191919191', '+351919191919', 'PT50000000000000000000018', '2025-10-10', '1994-07-19', 'Feminino',  'Avenida Fontes Pereira, 201', 'Lisboa', '1050-700', TRUE),
(19, 29, '202020202', '+351920202020', 'PT50000000000000000000019', '2025-10-15', '1987-04-27', 'Masculino', 'Rua Braamcamp, 223', 'Lisboa', '1250-800', TRUE),
(20, 30, '212121212', '+351921212121', 'PT50000000000000000000020', '2025-10-20', '1996-09-09', 'Feminino',  'Praça Marquês Pombal, 245', 'Lisboa', '1250-900', TRUE);

INSERT INTO MACHINE (MACHINEID, MACHINESTATUSID, NAME, TYPE, MANUFACTURER, MODEL, SERIALNUMBER, INSTALLATIONDATE, MAINTENANCEDATE) VALUES
(1,  2, 'Passadeira ProRun 3000',        'Cardio',      'Technogym',      'RunNow 3K',  'PF-RUN-0001', '2024-10-10', '2025-12-15'),
(2,  2, 'Bicicleta Indoor Sprint',      'Cardio',      'LifeFitness',    'IC-7',       'PF-BIK-0002', '2024-11-05', '2025-11-20'),
(3,  2, 'Elíptica AirGlide',            'Cardio',      'Precor',         'EG-12',      'PF-ELI-0003', '2024-12-01', '2025-10-10'),
(4,  1, 'Leg Press 45º',                'Musculação',  'Panatta',        'LP-45',      'PF-LEG-0004', '2024-09-20', '2026-01-10'),
(5,  3, 'Smith Machine',                'Musculação',  'Hammer Strength','SM-2',       'PF-SMI-0005', '2024-08-15', '2026-01-05'),
(6,  2, 'Crossover Cabos',              'Musculação',  'Cybex',          'CX-4',       'PF-CRO-0006', '2025-01-12', '2025-12-28'),
(7,  2, 'Remo Concept',                 'Cardio',      'Concept2',       'RowErg',     'PF-ROW-0007', '2025-02-02', '2025-12-01'),
(8,  4, 'Stepper ClimbMax',             'Cardio',      'Matrix',         'CL-10',      'PF-STE-0008', '2024-07-07', '2026-01-02'),
(9,  2, 'Banco Supino',                 'Musculação',  'Rogue',          'BN-01',      'PF-BEN-0009', '2025-03-20', '2025-11-15'),
(10, 1, 'Hack Squat',                   'Musculação',  'Panatta',        'HS-7',       'PF-HAC-0010', '2025-04-10', '2026-01-12'),
(11, 2, 'Multiestação',                 'Musculação',  'Technogym',      'MS-100',     'PF-MUL-0011', '2025-05-06', '2025-12-20'),
(12, 2, 'Abdominal Crunch',             'Musculação',  'Precor',         'AC-9',       'PF-ABD-0012', '2025-06-01', '2025-12-05'),
(13, 2, 'Extensão de Pernas',           'Musculação',  'Cybex',          'LE-3',       'PF-EXT-0013', '2025-06-15', '2026-01-08'),
(14, 2, 'Peck Deck',                    'Musculação',  'LifeFitness',    'PD-5',       'PF-PEC-0014', '2025-07-10', '2025-12-18'),
(15, 3, 'Remo Sentado',                 'Musculação',  'Matrix',         'SR-1',       'PF-SRO-0015', '2025-07-25', '2026-01-03');

INSERT INTO MACHINEMAINTENANCELOG (LOGID, MACHINEID, MAINTENANCEDATE, DESCRIPTION, TECHNICIAN, COST, MAINTENANCETYPE) VALUES
(1,  1,  '2025-12-15', 'Lubrificação da lona e calibração do motor',           'TecnoGym PT',      45.00, 'ROUTINE'),
(2,  2,  '2025-11-20', 'Ajuste do sistema de resistência e revisão geral',     'FitService',       35.00, 'ROUTINE'),
(3,  3,  '2025-10-10', 'Substituição de rolamentos e teste de carga',          'Precor Assist',    80.00, 'REPAIR'),
(4,  4,  '2026-01-10', 'Troca de cabo e afinação do carril',                   'Panatta Tech',    120.00, 'REPAIR'),
(5,  5,  '2026-01-05', 'Reparação de guias e aperto estrutural',               'Hammer PT',        95.00, 'REPAIR'),
(6,  6,  '2025-12-28', 'Substituição de polias gastas',                        'FitService',       60.00, 'REPAIR'),
(7,  7,  '2025-12-01', 'Limpeza do rail e troca de corrente',                  'Concept2 Partner', 55.00, 'ROUTINE'),
(8,  8,  '2026-01-02', 'Diagnóstico elétrico (equipamento retirado)',          'Matrix Support',   25.00, 'INSPECTION'),
(9,  9,  '2025-11-15', 'Revestimento do banco e verificação de soldas',        'Rogue Repair',     40.00, 'ROUTINE'),
(10, 10, '2026-01-12', 'Substituição de amortecedores e teste final',          'Panatta Tech',    150.00, 'REPAIR'),
(11, 11, '2025-12-20', 'Revisão anual completa (cabos + lubrificação)',        'TecnoGym PT',     200.00, 'ROUTINE'),
(12, 12, '2025-12-05', 'Aperto de parafusos e alinhamento',                    'Precor Assist',    30.00, 'ROUTINE'),
(13, 13, '2026-01-08', 'Troca de cabo + ajuste de polias',                     'FitService',       65.00, 'REPAIR'),
(14, 14, '2025-12-18', 'Substituição de manípulos',                            'LifeFitness PT',   50.00, 'REPAIR'),
(15, 15, '2026-01-03', 'Diagnóstico e marcação de peça',                       'Matrix Support',   20.00, 'INSPECTION');

INSERT INTO CLASS (CLASSID, INSTRUCTORID, NAME, DESCRIPTION, ROOM, CAPACITY, DURATION_MINUTES, ISACTIVE) VALUES
(1,  1, 'Funcional HIIT',            'Treino intervalado de alta intensidade (corpo inteiro).', 'Sala A', 20, 45, TRUE),
(2,  1, 'Força Total',               'Força e técnica com progressões semanais.',              'Sala B', 16, 60, TRUE),
(3,  2, 'Yoga Flow',                 'Mobilidade, respiração e relaxamento.',                 'Sala C', 22, 60, TRUE),
(4,  3, 'Cycling',                   'Aula de bike indoor com variações de ritmo.',           'Sala D', 25, 45, TRUE),
(5,  4, 'Pilates',                   'Core, estabilidade e postura.',                         'Sala C', 18, 50, TRUE),
(6,  5, 'Zumba',                     'Cardio com coreografias simples e energia alta.',       'Sala A', 30, 50, TRUE),
(7,  6, 'Mobilidade & Alongamentos', 'Alongamentos e prevenção de lesões.',                   'Sala B', 20, 40, TRUE),
(8,  7, 'Boxe Fit',                  'Técnicas base + circuito de condicionamento.',          'Sala E', 18, 55, TRUE);

INSERT INTO CLASSSCHEDULE (CLASSSCHEDULEID, CLASSID, DATE, STARTTIME, ENDTIME, MAXPARTICIPANTS, ISACTIVE) VALUES
(1,  1, '2026-01-20', '07:30', '08:15', 20, TRUE),
(2,  3, '2026-01-20', '18:00', '19:00', 22, TRUE),
(3,  4, '2026-01-20', '19:15', '20:00', 25, TRUE),
(4,  2, '2026-01-21', '12:30', '13:30', 16, TRUE),
(5,  6, '2026-01-21', '18:00', '18:50', 30, TRUE),
(6,  5, '2026-01-21', '19:10', '20:00', 18, TRUE),
(7,  7, '2026-01-22', '08:00', '08:40', 20, TRUE),
(8,  1, '2026-01-22', '18:30', '19:15', 20, TRUE),
(9,  4, '2026-01-22', '19:30', '20:15', 25, TRUE),
(10, 3, '2026-01-23', '07:45', '08:45', 22, TRUE),
(11, 8, '2026-01-23', '18:00', '18:55', 18, TRUE),
(12, 6, '2026-01-23', '19:10', '20:00', 30, TRUE),
(13, 5, '2026-01-24', '10:00', '10:50', 18, TRUE),
(14, 2, '2026-01-24', '11:15', '12:15', 16, TRUE),
(15, 1, '2026-01-24', '17:30', '18:15', 20, TRUE),
(16, 4, '2026-01-25', '10:30', '11:15', 25, TRUE),
(17, 3, '2026-01-25', '11:30', '12:30', 22, TRUE),
(18, 7, '2026-01-25', '17:30', '18:10', 20, TRUE),
(19, 2, '2026-01-26', '08:00', '09:00', 16, TRUE),
(20, 6, '2026-01-26', '18:30', '19:20', 30, TRUE),
(21, 1, '2026-01-13', '07:30', '08:15', 20, TRUE),
(22, 2, '2026-01-13', '18:30', '19:30', 16, TRUE),
(23, 1, '2026-01-15', '07:30', '08:15', 20, TRUE),
(24, 2, '2026-01-15', '18:30', '19:30', 16, TRUE),
(25, 1, '2026-01-18', '10:00', '10:45', 20, TRUE),
(26, 2, '2026-01-19', '12:30', '13:30', 16, TRUE);

INSERT INTO MEMBERSUBSCRIPTION (SUBSCRIPTIONID, PLANID, MEMBERID, STARTDATE, ENDDATE, ISACTIVE) VALUES
(1,  2,  1,  '2025-12-01', '2026-12-01', TRUE),
(2,  1,  2,  '2025-10-01', '2026-10-01', TRUE),
(3,  3,  3,  '2025-10-01', '2026-10-01', TRUE),
(4,  1,  4,  '2025-10-01', '2026-10-01', TRUE),
(5,  3,  5,  '2025-10-01', '2026-10-01', TRUE),
(6,  2,  6,  '2025-10-01', '2026-10-01', TRUE),
(7,  1,  7,  '2025-10-01', '2026-10-01', TRUE),
(8,  2,  8,  '2025-10-01', '2026-10-01', TRUE),
(9,  1,  9,  '2025-10-01', '2026-10-01', TRUE),
(10, 3,  10, '2025-10-01', '2026-10-01', TRUE),
(11, 2,  11, '2025-10-01', '2026-10-01', TRUE),
(12, 3,  12, '2025-10-01', '2026-10-01', TRUE),
(13, 2,  13, '2025-10-01', '2026-10-01', TRUE),
(14, 2,  14, '2025-10-01', '2026-10-01', TRUE),
(15, 1,  15, '2025-10-01', '2026-10-01', TRUE),
(16, 1,  16, '2025-10-01', '2026-10-01', TRUE),
(17, 3,  17, '2025-10-01', '2026-10-01', TRUE),
(18, 2,  18, '2025-10-01', '2026-10-01', TRUE),
(19, 2,  19, '2025-10-01', '2026-10-01', TRUE),
(20, 3,  20, '2025-10-01', '2026-10-01', TRUE);

INSERT INTO PAYMENT (PAYMENTID, SUBSCRIPTIONID, AMOUNT, ISPAYED, DUEDATE, PAYMENTDATE, PAYMENTMETHOD, REFERENCE) VALUES
(1,  1, 30.00, TRUE,  '2025-09-30', '2025-09-28', 'MBWAY',                 'PF-202509-S01-01'),
(2,  1, 30.00, TRUE,  '2025-10-31', '2025-10-31', 'Cartão',                'PF-202510-S01-02'),
(3,  1, 30.00, TRUE,  '2025-11-30', '2025-12-02', 'Referência Multibanco', 'PF-202511-S01-03'),
(4,  1, 30.00, TRUE,  '2025-12-31', '2025-12-30', 'MBWAY',                 'PF-202512-S01-04'),
(5,  1, 30.00, TRUE,  '2026-01-31', '2026-01-31', 'Cartão',                'PF-202601-S01-05'),
(6,  1, 30.00, FALSE, '2026-02-28', NULL,         'Referência Multibanco', 'PF-202602-S01-06'),
(7,  1, 30.00, FALSE, '2026-03-31', NULL,         'Referência Multibanco', 'PF-202603-S01-07'),

(8,  2, 20.00, TRUE,  '2025-09-30', '2025-09-30', 'Cartão',                'PF-202509-S02-01'),
(9,  2, 20.00, TRUE,  '2025-10-31', '2025-10-29', 'MBWAY',                 'PF-202510-S02-02'),
(10, 2, 20.00, TRUE,  '2025-11-30', '2025-11-30', 'Cartão',                'PF-202511-S02-03'),
(11, 2, 20.00, TRUE,  '2025-12-31', '2026-01-03', 'Referência Multibanco', 'PF-202512-S02-04'),
(12, 2, 20.00, FALSE, '2026-01-31', NULL,         'Referência Multibanco', 'PF-202601-S02-05'),
(13, 2, 20.00, FALSE, '2026-02-28', NULL,         'Referência Multibanco', 'PF-202602-S02-06'),
(14, 2, 20.00, FALSE, '2026-03-31', NULL,         'Referência Multibanco', 'PF-202603-S02-07'),

(15, 3, 15.00, TRUE,  '2025-09-30', '2025-09-27', 'MBWAY',                 'PF-202509-S03-01'),
(16, 3, 15.00, TRUE,  '2025-10-31', '2025-10-31', 'Cartão',                'PF-202510-S03-02'),
(17, 3, 15.00, TRUE,  '2025-11-30', '2025-12-01', 'Referência Multibanco', 'PF-202511-S03-03'),
(18, 3, 15.00, TRUE,  '2025-12-31', '2025-12-31', 'MBWAY',                 'PF-202512-S03-04'),
(19, 3, 15.00, TRUE,  '2026-01-31', '2026-01-30', 'MBWAY',                 'PF-202601-S03-05'),
(20, 3, 15.00, FALSE, '2026-02-28', NULL,         'Referência Multibanco', 'PF-202602-S03-06'),
(21, 3, 15.00, FALSE, '2026-03-31', NULL,         'Referência Multibanco', 'PF-202603-S03-07'),

(22, 4, 20.00, TRUE,  '2025-09-30', '2025-09-29', 'Cartão',                'PF-202509-S04-01'),
(23, 4, 20.00, TRUE,  '2025-10-31', '2025-10-30', 'MBWAY',                 'PF-202510-S04-02'),
(24, 4, 20.00, TRUE,  '2025-11-30', '2025-11-30', 'Cartão',                'PF-202511-S04-03'),
(25, 4, 20.00, TRUE,  '2025-12-31', '2026-01-02', 'Referência Multibanco', 'PF-202512-S04-04'),
(26, 4, 20.00, TRUE,  '2026-01-31', '2026-02-03', 'Referência Multibanco', 'PF-202601-S04-05'),
(27, 4, 20.00, FALSE, '2026-02-28', NULL,         'Referência Multibanco', 'PF-202602-S04-06'),
(28, 4, 20.00, FALSE, '2026-03-31', NULL,         'Referência Multibanco', 'PF-202603-S04-07'),

(29, 5, 15.00, TRUE,  '2025-09-30', '2025-09-30', 'MBWAY',                 'PF-202509-S05-01'),
(30, 5, 15.00, TRUE,  '2025-10-31', '2025-10-31', 'Cartão',                'PF-202510-S05-02'),
(31, 5, 15.00, TRUE,  '2025-11-30', '2025-11-29', 'MBWAY',                 'PF-202511-S05-03'),
(32, 5, 15.00, TRUE,  '2025-12-31', '2026-01-05', 'Referência Multibanco', 'PF-202512-S05-04'),
(33, 5, 15.00, FALSE, '2026-01-31', NULL,         'Referência Multibanco', 'PF-202601-S05-05'),
(34, 5, 15.00, FALSE, '2026-02-28', NULL,         'Referência Multibanco', 'PF-202602-S05-06'),
(35, 5, 15.00, FALSE, '2026-03-31', NULL,         'Referência Multibanco', 'PF-202603-S05-07'),

(36, 6, 30.00, TRUE,  '2025-09-30', '2025-09-28', 'Cartão',                'PF-202509-S06-01'),
(37, 6, 30.00, TRUE,  '2025-10-31', '2025-10-31', 'Cartão',                'PF-202510-S06-02'),
(38, 6, 30.00, TRUE,  '2025-11-30', '2025-11-30', 'MBWAY',                 'PF-202511-S06-03'),
(39, 6, 30.00, TRUE,  '2025-12-31', '2025-12-30', 'MBWAY',                 'PF-202512-S06-04'),
(40, 6, 30.00, TRUE,  '2026-01-31', '2026-01-31', 'Cartão',                'PF-202601-S06-05'),
(41, 6, 30.00, FALSE, '2026-02-28', NULL,         'Referência Multibanco', 'PF-202602-S06-06'),
(42, 6, 30.00, FALSE, '2026-03-31', NULL,         'Referência Multibanco', 'PF-202603-S06-07'),

(43, 7, 20.00, TRUE,  '2025-09-30', '2025-09-27', 'MBWAY',                 'PF-202509-S07-01'),
(44, 7, 20.00, TRUE,  '2025-10-31', '2025-11-02', 'Referência Multibanco', 'PF-202510-S07-02'),
(45, 7, 20.00, TRUE,  '2025-11-30', '2025-11-30', 'Cartão',                'PF-202511-S07-03'),
(46, 7, 20.00, TRUE,  '2025-12-31', '2026-01-01', 'Referência Multibanco', 'PF-202512-S07-04'),
(47, 7, 20.00, FALSE, '2026-01-31', NULL,         'Referência Multibanco', 'PF-202601-S07-05'),
(48, 7, 20.00, FALSE, '2026-02-28', NULL,         'Referência Multibanco', 'PF-202602-S07-06'),
(49, 7, 20.00, FALSE, '2026-03-31', NULL,         'Referência Multibanco', 'PF-202603-S07-07'),

(50, 8, 30.00, TRUE,  '2025-09-30', '2025-09-29', 'Cartão',                'PF-202509-S08-01'),
(51, 8, 30.00, TRUE,  '2025-10-31', '2025-10-30', 'MBWAY',                 'PF-202510-S08-02'),
(52, 8, 30.00, TRUE,  '2025-11-30', '2025-12-01', 'Referência Multibanco', 'PF-202511-S08-03'),
(53, 8, 30.00, TRUE,  '2025-12-31', '2025-12-31', 'Cartão',                'PF-202512-S08-04'),
(54, 8, 30.00, TRUE,  '2026-01-31', '2026-02-02', 'Referência Multibanco', 'PF-202601-S08-05'),
(55, 8, 30.00, FALSE, '2026-02-28', NULL,         'Referência Multibanco', 'PF-202602-S08-06'),
(56, 8, 30.00, FALSE, '2026-03-31', NULL,         'Referência Multibanco', 'PF-202603-S08-07'),

(57, 9, 20.00, TRUE,  '2025-09-30', '2025-09-30', 'MBWAY',                 'PF-202509-S09-01'),
(58, 9, 20.00, TRUE,  '2025-10-31', '2025-10-31', 'Cartão',                'PF-202510-S09-02'),
(59, 9, 20.00, TRUE,  '2025-11-30', '2025-11-28', 'MBWAY',                 'PF-202511-S09-03'),
(60, 9, 20.00, TRUE,  '2025-12-31', '2026-01-04', 'Referência Multibanco', 'PF-202512-S09-04'),
(61, 9, 20.00, FALSE, '2026-01-31', NULL,         'Referência Multibanco', 'PF-202601-S09-05'),
(62, 9, 20.00, FALSE, '2026-02-28', NULL,         'Referência Multibanco', 'PF-202602-S09-06'),
(63, 9, 20.00, FALSE, '2026-03-31', NULL,         'Referência Multibanco', 'PF-202603-S09-07'),

(64, 10,15.00, TRUE,  '2025-09-30', '2025-09-29', 'Cartão',                'PF-202509-S10-01'),
(65, 10,15.00, TRUE,  '2025-10-31', '2025-10-31', 'MBWAY',                 'PF-202510-S10-02'),
(66, 10,15.00, TRUE,  '2025-11-30', '2025-11-30', 'Cartão',                'PF-202511-S10-03'),
(67, 10,15.00, TRUE,  '2025-12-31', '2025-12-30', 'MBWAY',                 'PF-202512-S10-04'),
(68, 10,15.00, TRUE,  '2026-01-31', '2026-01-31', 'Cartão',                'PF-202601-S10-05'),
(69, 10,15.00, FALSE, '2026-02-28', NULL,         'Referência Multibanco', 'PF-202602-S10-06'),
(70, 10,15.00, FALSE, '2026-03-31', NULL,         'Referência Multibanco', 'PF-202603-S10-07'),

(71, 11,15.00, TRUE,  '2025-09-30', '2025-09-30', 'MBWAY',                 'PF-202509-S11-01'),
(72, 11,15.00, TRUE,  '2025-10-31', '2025-11-01', 'Referência Multibanco', 'PF-202510-S11-02'),
(73, 11,15.00, TRUE,  '2025-11-30', '2025-11-30', 'Cartão',                'PF-202511-S11-03'),
(74, 11,15.00, TRUE,  '2025-12-31', '2026-01-02', 'Referência Multibanco', 'PF-202512-S11-04'),
(75, 11,15.00, FALSE, '2026-01-31', NULL,         'Referência Multibanco', 'PF-202601-S11-05');

INSERT INTO CLASSBOOKING (BOOKINGID, MEMBERID, CLASSSCHEDULEID, BOOKINGDATE) VALUES
(1,  1,  21, '2026-01-11 07:30:00'),
(2,  1,  22, '2026-01-11 18:30:00'),
(3,  1,  23, '2026-01-13 07:30:00'),
(4,  1,  24, '2026-01-13 18:30:00'),
(5,  1,  25, '2026-01-16 10:00:00'),
(6,  1,  26, '2026-01-17 12:30:00'),
(7,  1,  1,  '2026-01-18 07:30:00'),
(8,  1,  4,  '2026-01-19 12:30:00'),
(9,  1,  8,  '2026-01-20 18:30:00'),
(10, 1,  14, '2026-01-22 11:15:00'),
(11, 1,  19, '2026-01-24 08:00:00'),
(12, 2,  21, '2026-01-12 07:30:00'),
(13, 2,  2,  '2026-01-19 18:00:00'),
(14, 3,  24, '2026-01-12 18:30:00'),
(15, 3,  6,  '2026-01-20 19:10:00'),
(16, 4,  9,  '2026-01-21 19:30:00'),
(17, 5,  7,  '2026-01-20 08:00:00'),
(18, 6,  20, '2026-01-24 18:30:00'),
(19, 7,  11, '2026-01-21 18:00:00'),
(20, 8,  18, '2026-01-24 17:30:00'),
(21, 9,  17, '2026-01-23 11:30:00'),
(22, 10, 12, '2026-01-22 19:10:00'),
(23, 11, 10, '2026-01-21 07:50:00'),
(24, 12, 20, '2026-01-25 18:30:00'),
(25, 13, 3,  '2026-01-18 21:00:00'),
(26, 14, 5,  '2026-01-20 18:05:00'),
(27, 15, 2,  '2026-01-19 18:05:00'),
(28, 16, 18, '2026-01-24 17:30:00'),
(29, 17, 16, '2026-01-24 10:30:00'),
(30, 18, 14, '2026-01-23 11:20:00'),
(31, 19, 1,  '2026-01-18 07:35:00'),
(32, 20, 12, '2026-01-22 19:15:00');

INSERT INTO CHECKIN (CHECKINID, MEMBERID, DATE, ENTRANCETIME, EXITTIME) VALUES
(1,  1, '2026-01-14', '07:10', '08:35'),
(2,  1, '2026-01-16', '18:20', '19:40'),
(3,  1, '2026-01-18', '09:05', '10:10'),
(4,  1, '2026-01-19', '07:05', '08:00'),
(5,  1, '2026-01-20', '07:25', '08:20'),
(6,  2, '2026-01-20', '07:40', '08:30'),
(7,  3, '2026-01-20', '18:10', '19:05'),
(8,  4, '2026-01-20', '19:00', '20:05'),
(9,  5, '2026-01-20', '08:50', '09:40'),
(10, 6, '2026-01-20', '20:05', '21:00'),
(11, 7, '2026-01-16', '06:45', '07:50'),
(12, 8, '2026-01-15', '18:30', '19:25'),
(13, 9, '2026-01-14', '19:10', '20:05'),
(14, 10,'2026-01-18', '06:50', '07:40'),
(15, 11,'2026-01-17', '17:55', '18:50'),
(16, 12,'2026-01-19', '09:10', '10:05'),
(17, 13,'2026-01-18', '21:10', '22:05'),
(18, 14,'2026-01-18', '12:30', '13:25'),
(19, 15,'2026-01-16', '08:05', '09:00'),
(20, 16,'2026-01-18', '18:40', '19:35'),
(21, 17,'2026-01-19', '07:20', '08:10'),
(22, 18,'2026-01-18', '10:30', '11:20'),
(23, 19,'2026-01-17', '19:25', '20:20'),
(24, 20,'2026-01-18', '18:05', '19:00');

COMMIT;

-- Ensure sequences are set to the current maximum values to avoid
-- duplicate key errors when inserts rely on sequence.nextval (e.g. stored procedures)
SELECT setval('usertype_usertypeid_seq',        COALESCE((SELECT MAX(usertypeid) FROM usertype), 0));
SELECT setval('machinestatus_machinestatusid_seq', COALESCE((SELECT MAX(machinestatusid) FROM machinestatus), 0));
SELECT setval('plan_planid_seq',                 COALESCE((SELECT MAX(planid) FROM plan), 0));
SELECT setval('users_userid_seq',                COALESCE((SELECT MAX(userid) FROM users), 0));
SELECT setval('instructor_instructorid_seq',     COALESCE((SELECT MAX(instructorid) FROM instructor), 0));
SELECT setval('member_memberid_seq',             COALESCE((SELECT MAX(memberid) FROM member), 0));
SELECT setval('machine_machineid_seq',           COALESCE((SELECT MAX(machineid) FROM machine), 0));
SELECT setval('class_classid_seq',               COALESCE((SELECT MAX(classid) FROM class), 0));
SELECT setval('membersubscription_subscriptionid_seq', COALESCE((SELECT MAX(subscriptionid) FROM membersubscription), 0));
SELECT setval('classschedule_classscheduleid_seq', COALESCE((SELECT MAX(classscheduleid) FROM classschedule), 0));
SELECT setval('machinemaintenancelog_logid_seq', COALESCE((SELECT MAX(logid) FROM machinemaintenancelog), 0));
SELECT setval('payment_paymentid_seq',           COALESCE((SELECT MAX(paymentid) FROM payment), 0));
SELECT setval('classbooking_bookingid_seq',      COALESCE((SELECT MAX(bookingid) FROM classbooking), 0));
SELECT setval('checkin_checkinid_seq',           COALESCE((SELECT MAX(checkinid) FROM checkin), 0));

SELECT * from plan;