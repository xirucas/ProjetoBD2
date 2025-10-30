"""
Exemplo de uso híbrido: PostgreSQL + MongoDB no PrimeFit

Este arquivo demonstra como usar ambos os bancos de dados:
- PostgreSQL: para dados relacionais (usuários, planos, memberships)
- MongoDB: para dados não-relacionais (check-ins, logs, equipamentos)
"""

from django.contrib.auth import get_user_model
from .models import Plan, Membership, checkin_model, workout_model, equipment_model
from datetime import datetime, date

User = get_user_model()

def exemplo_uso_hibrido():
    """
    Exemplo de como usar PostgreSQL e MongoDB juntos
    """
    
    # 1. POSTGRESQL - Criar usuário e plano
    # Criando um plano no PostgreSQL
    plano_basico = Plan.objects.create(
        name="Plano Básico",
        description="Acesso à academia e equipamentos básicos",
        price=99.90,
        duration_months=1
    )
    
    # Criando um usuário no PostgreSQL
    usuario = User.objects.create_user(
        username="joao123",
        email="joao@email.com",
        first_name="João",
        last_name="Silva",
        user_type="member"
    )
    
    # Criando membership (relacionamento entre usuário e plano)
    membership = Membership.objects.create(
        user=usuario,
        plan=plano_basico,
        start_date=date.today(),
        end_date=date(2024, 12, 31)
    )
    
    # 2. MONGODB - Registrar check-in
    # Criando check-in no MongoDB
    checkin_result = checkin_model.create_checkin(
        user_id=usuario.id,
        username=usuario.username
    )
    
    # 3. MONGODB - Registrar treino
    exercicios = [
        {"nome": "Supino", "series": 3, "repeticoes": 12, "peso": 80},
        {"nome": "Agachamento", "series": 4, "repeticoes": 10, "peso": 100},
        {"nome": "Rosca Direta", "series": 3, "repeticoes": 15, "peso": 20}
    ]
    
    workout_result = workout_model.log_workout(
        user_id=usuario.id,
        exercises=exercicios
    )
    
    # 4. MONGODB - Adicionar equipamento
    equipment_result = equipment_model.add_equipment(
        name="Esteira Profissional",
        category="Cardio",
        status="active"
    )
    
    print("Dados criados com sucesso!")
    print(f"Usuário PostgreSQL: {usuario}")
    print(f"Plano PostgreSQL: {plano_basico}")
    print(f"Membership PostgreSQL: {membership}")
    print(f"Check-in MongoDB: {checkin_result.inserted_id if checkin_result else 'Erro'}")
    print(f"Workout MongoDB: {workout_result.inserted_id if workout_result else 'Erro'}")
    print(f"Equipment MongoDB: {equipment_result.inserted_id if equipment_result else 'Erro'}")

def consultar_dados_hibridos(user_id):
    """
    Exemplo de como consultar dados de ambos os bancos
    """
    
    # Dados do PostgreSQL
    usuario = User.objects.get(id=user_id)
    membership = Membership.objects.filter(user=usuario, is_active=True).first()
    
    # Dados do MongoDB
    checkins = list(checkin_model.find({'user_id': user_id}))
    workouts = list(workout_model.find({'user_id': user_id}))
    
    resultado = {
        'usuario': {
            'nome': f"{usuario.first_name} {usuario.last_name}",
            'tipo': usuario.user_type,
            'email': usuario.email
        },
        'plano': {
            'nome': membership.plan.name if membership else None,
            'preco': float(membership.plan.price) if membership else None
        },
        'checkins_total': len(checkins),
        'workouts_total': len(workouts),
        'ultimo_checkin': checkins[-1]['checkin_time'] if checkins else None
    }
    
    return resultado

def estatisticas_academia():
    """
    Exemplo de consultas agregadas usando ambos os bancos
    """
    
    # PostgreSQL - Estatísticas de usuários e planos
    total_membros = User.objects.filter(user_type='member').count()
    total_instrutores = User.objects.filter(user_type='instructor').count()
    memberships_ativas = Membership.objects.filter(is_active=True).count()
    receita_mensal = sum([m.plan.price for m in Membership.objects.filter(is_active=True)])
    
    # MongoDB - Estatísticas de uso
    total_checkins = checkin_model.collection.count_documents({}) if checkin_model.collection else 0
    total_workouts = workout_model.collection.count_documents({}) if workout_model.collection else 0
    total_equipamentos = equipment_model.collection.count_documents({}) if equipment_model.collection else 0
    
    # Checkins de hoje
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    checkins_hoje = checkin_model.collection.count_documents({
        'checkin_time': {'$gte': hoje}
    }) if checkin_model.collection else 0
    
    return {
        'postgresql': {
            'total_membros': total_membros,
            'total_instrutores': total_instrutores,
            'memberships_ativas': memberships_ativas,
            'receita_mensal': float(receita_mensal)
        },
        'mongodb': {
            'total_checkins': total_checkins,
            'total_workouts': total_workouts,
            'total_equipamentos': total_equipamentos,
            'checkins_hoje': checkins_hoje
        }
    }