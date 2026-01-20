CREATE TABLE IF NOT EXISTS daily_execution_control (
    execution_date DATE PRIMARY KEY,
    execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'PENDING'
);

-- Function que verifica se deve executar hoje
CREATE OR REPLACE FUNCTION fn_check_daily_execution()
RETURNS BOOLEAN
LANGUAGE plpgsql AS $$
DECLARE
    v_today DATE;
    v_executed BOOLEAN := FALSE;
BEGIN
    v_today := CURRENT_DATE;
    
    SELECT TRUE INTO v_executed
    FROM daily_execution_control 
    WHERE execution_date = v_today 
      AND status = 'COMPLETED';
    
    RETURN COALESCE(v_executed, FALSE);
END;
$$;

-- Function para marcar execução como concluída
CREATE OR REPLACE FUNCTION fn_mark_execution_complete()
RETURNS VOID
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO daily_execution_control (execution_date, status)
    VALUES (CURRENT_DATE, 'COMPLETED')
    ON CONFLICT (execution_date) 
    DO UPDATE SET 
        execution_time = CURRENT_TIMESTAMP,
        status = 'COMPLETED';
END;
$$;

CREATE OR REPLACE PROCEDURE sp_check_payment_history()
LANGUAGE plpgsql AS $$
DECLARE
    v_member RECORD;
    v_current_month_payment RECORD;
    v_previous_month_payment RECORD;
    v_current_month DATE;
    v_previous_month DATE;
BEGIN
    v_current_month := DATE_TRUNC('month', CURRENT_DATE);
    v_previous_month := DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month');
    
    FOR v_member IN 
        SELECT 
            ms.subscriptionid,
            ms.memberid,
            u.name as member_name,
            u.userid
        FROM membersubscription ms
        INNER JOIN member m ON ms.memberid = m.memberid
        INNER JOIN users u ON m.userid = u.userid
        WHERE ms.isactive = TRUE
          AND ms.enddate >= CURRENT_DATE
    LOOP
        -- Verificar pagamento do mês atual
        SELECT p.paymentid, p.ispayed, p.duedate, p.amount
        INTO v_current_month_payment
        FROM payment p
        WHERE p.subscriptionid = v_member.subscriptionid
          AND DATE_TRUNC('month', p.duedate) = v_current_month
        LIMIT 1;
        
        -- Verificar pagamento do mês anterior
        SELECT p.paymentid, p.ispayed, p.duedate, p.amount
        INTO v_previous_month_payment
        FROM payment p
        WHERE p.subscriptionid = v_member.subscriptionid
          AND DATE_TRUNC('month', p.duedate) = v_previous_month
        LIMIT 1;
        
        -- Log apenas casos problemáticos
        IF v_current_month_payment.paymentid IS NULL OR 
           (v_current_month_payment.ispayed = FALSE AND v_current_month_payment.duedate < CURRENT_DATE) OR
           v_previous_month_payment.paymentid IS NULL OR 
           (v_previous_month_payment.ispayed = FALSE) THEN
            
            RAISE NOTICE 'Membro %: Atual=%, Anterior=%', 
                v_member.member_name,
                CASE 
                    WHEN v_current_month_payment.paymentid IS NULL THEN 'SEM_FATURA'
                    WHEN v_current_month_payment.ispayed = TRUE THEN 'PAGO'
                    WHEN v_current_month_payment.duedate < CURRENT_DATE THEN 'ATRASO'
                    ELSE 'PENDENTE'
                END,
                CASE 
                    WHEN v_previous_month_payment.paymentid IS NULL THEN 'SEM_FATURA'
                    WHEN v_previous_month_payment.ispayed = TRUE THEN 'PAGO'
                    ELSE 'ATRASO'
                END;
        END IF;
    END LOOP;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_create_next_month_payments()
LANGUAGE plpgsql AS $$
DECLARE
    v_subscription RECORD;
    v_next_month_date DATE;
    v_due_date DATE;
    v_existing_payment INTEGER;
BEGIN
    v_next_month_date := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month');
    v_due_date := (DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month') + INTERVAL '1 month - 1 day')::DATE;
    
    FOR v_subscription IN 
        SELECT 
            ms.subscriptionid,
            ms.memberid,
            p.monthlyprice,
            m.userid,
            u.name
        FROM membersubscription ms
        INNER JOIN plan p ON ms.planid = p.planid
        INNER JOIN member m ON ms.memberid = m.memberid
        INNER JOIN users u ON m.userid = u.userid
        WHERE ms.isactive = TRUE
          AND ms.enddate >= CURRENT_DATE
    LOOP
        SELECT COUNT(*) INTO v_existing_payment
        FROM payment pay
        WHERE pay.subscriptionid = v_subscription.subscriptionid
          AND DATE_TRUNC('month', pay.duedate) = v_next_month_date;
        
        IF v_existing_payment = 0 THEN
            INSERT INTO payment (
                subscriptionid,
                amount,
                ispayed,
                duedate,
                paymentdate,
                paymentmethod,
                reference,
                created_at
            ) VALUES (
                v_subscription.subscriptionid,
                v_subscription.monthlyprice,
                FALSE,
                v_due_date,
                NULL,
                NULL,
                'PAY_' || TO_CHAR(v_next_month_date, 'YYYY_MM_') || v_subscription.memberid,
                CURRENT_TIMESTAMP
            );
            
            RAISE NOTICE 'Criado pagamento: % - €% - %', 
                v_subscription.name, 
                v_subscription.monthlyprice, 
                v_due_date;
        END IF;
    END LOOP;
END;
$$;


CREATE OR REPLACE PROCEDURE sp_update_payment_status()
LANGUAGE plpgsql AS $$
DECLARE
    v_updated_pending INTEGER := 0;
    v_updated_overdue INTEGER := 0;
    v_payment RECORD;
BEGIN
    -- Contar pagamentos pendentes do mês atual
    FOR v_payment IN
        SELECT 
            p.paymentid,
            p.duedate,
            p.amount,
            u.name as member_name
        FROM payment p
        INNER JOIN membersubscription ms ON p.subscriptionid = ms.subscriptionid
        INNER JOIN member m ON ms.memberid = m.memberid
        INNER JOIN users u ON m.userid = u.userid
        WHERE p.ispayed = FALSE
          AND DATE_TRUNC('month', p.duedate) = DATE_TRUNC('month', CURRENT_DATE)
          AND p.duedate >= CURRENT_DATE
    LOOP
        v_updated_pending := v_updated_pending + 1;
    END LOOP;
    
    -- Contar pagamentos em atraso
    FOR v_payment IN
        SELECT 
            p.paymentid,
            p.duedate,
            p.amount,
            u.name as member_name
        FROM payment p
        INNER JOIN membersubscription ms ON p.subscriptionid = ms.subscriptionid
        INNER JOIN member m ON ms.memberid = m.memberid
        INNER JOIN users u ON m.userid = u.userid
        WHERE p.ispayed = FALSE
          AND p.duedate < CURRENT_DATE
    LOOP
        v_updated_overdue := v_updated_overdue + 1;
        
        -- Log apenas atrasos críticos (>30 dias)
        IF CURRENT_DATE - v_payment.duedate > 30 THEN
            RAISE NOTICE 'ATRASO CRÍTICO: % - €% - % dias', 
                v_payment.member_name, 
                v_payment.amount,
                CURRENT_DATE - v_payment.duedate;
        END IF;
    END LOOP;
    
    RAISE NOTICE 'Status: % pendentes, % em atraso', v_updated_pending, v_updated_overdue;
END;
$$;


CREATE OR REPLACE PROCEDURE sp_daily_payment_management()
LANGUAGE plpgsql AS $$
BEGIN
    --Verificar histórico de pagamentos
    BEGIN
        CALL sp_check_payment_history();
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'Erro na verificação de histórico: %', SQLERRM;
    END;
    
    --Criar pagamentos do próximo mês
    BEGIN
        CALL sp_create_next_month_payments();
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'Erro na criação de pagamentos: %', SQLERRM;
    END;
    
    --Atualizar status dos pagamentos
    BEGIN
        CALL sp_update_payment_status();
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'Erro na atualização de status: %', SQLERRM;
    END;
    
    RAISE NOTICE 'Processamento diário concluído - %', CURRENT_TIMESTAMP;
END;
$$;


CREATE OR REPLACE PROCEDURE sp_safe_daily_payment_management()
LANGUAGE plpgsql AS $$
BEGIN
    IF NOT fn_check_daily_execution() THEN
        CALL sp_daily_payment_management();
        PERFORM fn_mark_execution_complete();
        RAISE NOTICE 'Sistema executado para o dia %', CURRENT_DATE;
    ELSE
       RAISE NOTICE 'Sistema já executado hoje (%)', CURRENT_DATE;
    END IF;
END;
$$;

-- ===============================================================
-- 9. CONFIGURAÇÃO DE AUTOMAÇÃO
-- ===============================================================

-- Procedure de configuração inicial
CREATE OR REPLACE PROCEDURE sp_setup_payment_automation()
LANGUAGE plpgsql AS $$
DECLARE
    v_job_id BIGINT;
    v_existing_jobs INTEGER;
BEGIN
    BEGIN
        CREATE EXTENSION IF NOT EXISTS pg_cron;
        
        -- Verificar se já existe job com este nome
        SELECT COUNT(*) INTO v_existing_jobs
        FROM cron.job
        WHERE jobname = 'daily-payment-management';
        
        -- Remover job existente se houver
        IF v_existing_jobs > 0 THEN
            PERFORM cron.unschedule('daily-payment-management');
            RAISE NOTICE 'Job existente removido';
        END IF;
        
        -- Agendar novo job diário às 02:00
        SELECT cron.schedule('daily-payment-management', '0 2 * * *', 'CALL sp_safe_daily_payment_management();') INTO v_job_id;
        
        RAISE NOTICE 'Automação configurada com pg_cron - Job ID: %', v_job_id;
        RAISE NOTICE 'Execução diária às 02:00 UTC';
        RAISE NOTICE 'Verificar jobs: SELECT * FROM cron.job;';
        
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Erro ao configurar pg_cron: %', SQLERRM;
            RAISE NOTICE 'Alternativas:';
            RAISE NOTICE '1. Azure Functions com trigger diário';
            RAISE NOTICE '2. Logic Apps com recorrência diária';
            RAISE NOTICE '3. Execução manual: CALL sp_safe_daily_payment_management();';
    END;
END;
$$;


/*
CALL sp_setup_payment_automation();
EXECUÇÃO:
1. Automática 
2. Manual: CALL sp_daily_payment_management();

*/

