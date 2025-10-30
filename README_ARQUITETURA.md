# PrimeFit - Arquitetura Híbrida PostgreSQL + MongoDB

## Visão Geral

Este projeto utiliza uma arquitetura híbrida combinando PostgreSQL e MongoDB para diferentes tipos de dados:

### PostgreSQL (Dados Relacionais)
- **Usuários** (`CustomUser`): Autenticação e dados pessoais
- **Planos** (`Plan`): Planos de academia disponíveis
- **Memberships** (`Membership`): Relacionamento entre usuários e planos

### MongoDB (Dados Não-Relacionais)
- **Check-ins** (`checkins`): Registros de entrada/saída
- **Workout Logs** (`workout_logs`): Logs detalhados de treinos
- **Equipment** (`equipment`): Cadastro de equipamentos
- **Class Schedule** (`class_schedules`): Horários de aulas

## Configuração

### 1. PostgreSQL
Configure as variáveis no arquivo `.env`:
```
POSTGRES_DB=primefit_db
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 2. MongoDB
O MongoDB deve estar rodando em `localhost:27017` (configuração padrão).

Para instalar o MongoDB:
1. Baixe do site oficial: https://www.mongodb.com/try/download/community
2. Instale e inicie o serviço
3. O banco `primefit` será criado automaticamente

## Uso dos Modelos

### PostgreSQL (Django ORM)
```python
from django.contrib.auth import get_user_model
from .models import Plan, Membership

User = get_user_model()

# Criar usuário
usuario = User.objects.create_user(
    username="joao123",
    email="joao@email.com",
    user_type="member"
)

# Criar plano
plano = Plan.objects.create(
    name="Plano Premium",
    price=149.90,
    duration_months=1
)
```

### MongoDB (PyMongo)
```python
from .models import checkin_model, workout_model

# Registrar check-in
checkin_model.create_checkin(
    user_id=usuario.id,
    username=usuario.username
)

# Registrar treino
exercicios = [
    {"nome": "Supino", "series": 3, "repeticoes": 12}
]
workout_model.log_workout(usuario.id, exercicios)
```

## Vantagens da Arquitetura Híbrida

1. **PostgreSQL**: 
   - ACID compliance para transações críticas
   - Relacionamentos complexos
   - Autenticação e autorização
   - Integridade referencial

2. **MongoDB**:
   - Flexibilidade de schema
   - Performance para grandes volumes
   - Dados hierárquicos/aninhados
   - Escalabilidade horizontal

## Estrutura de Pastas

```
PrimeFit/
├── PrimeFit/
│   ├── models.py          # Modelos PostgreSQL e MongoDB
│   ├── views.py           # Views usando ambos os bancos
│   ├── mongodb_manager.py # Gerenciador de conexão MongoDB
│   ├── exemplo_uso_hibrido.py # Exemplos de uso
│   └── settings.py        # Configurações dos bancos
└── Templates/             # Templates HTML
```

## Comandos Úteis

### Django (PostgreSQL)
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### MongoDB
```javascript
// No MongoDB shell
use primefit
db.checkins.find()
db.workout_logs.find()
```

## Exemplo de Consulta Híbrida

```python
def dashboard_data(user_id):
    # PostgreSQL
    user = User.objects.get(id=user_id)
    membership = Membership.objects.filter(user=user).first()
    
    # MongoDB
    checkins = list(checkin_model.find({'user_id': user_id}))
    workouts = list(workout_model.find({'user_id': user_id}))
    
    return {
        'user': user,
        'membership': membership,
        'total_checkins': len(checkins),
        'total_workouts': len(workouts)
    }
```

## Monitoramento

- **PostgreSQL**: Use pgAdmin ou ferramentas similares
- **MongoDB**: Use MongoDB Compass ou mongo shell

## Backup

- **PostgreSQL**: `pg_dump primefit_db > backup.sql`
- **MongoDB**: `mongodump --db primefit`