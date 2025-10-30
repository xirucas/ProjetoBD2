from django.db import models
from django.contrib.auth.models import AbstractUser
from .mongodb_manager import mongo_manager
from datetime import datetime
import json

# Modelos PostgreSQL (para dados relacionais e autenticação)
class CustomUser(AbstractUser):
    """Usuário customizado para autenticação (PostgreSQL)"""
    USER_TYPES = [
        ('member', 'Member'),
        ('instructor', 'Instructor'), 
        ('manager', 'Manager')
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='member')
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"

class Plan(models.Model):
    """Planos da academia (PostgreSQL)"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Membership(models.Model):
    """Associação de membros aos planos (PostgreSQL)"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

# Classes para MongoDB (para dados não-relacionais e logs)
class MongoBaseModel:
    """Classe base para modelos MongoDB"""
    
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.collection = mongo_manager.get_collection(collection_name)
    
    def insert_one(self, document):
        """Insere um documento"""
        if self.collection is not None:
            document['created_at'] = datetime.utcnow()
            return self.collection.insert_one(document)
        return None
    
    def find(self, filter_dict=None):
        """Busca documentos"""
        if self.collection is not None:
            return self.collection.find(filter_dict or {})
        return []
    
    def find_one(self, filter_dict):
        """Busca um documento"""
        if self.collection is not None:
            return self.collection.find_one(filter_dict)
        return None
    
    def update_one(self, filter_dict, update_dict):
        """Atualiza um documento"""
        if self.collection is not None:
            update_dict['updated_at'] = datetime.utcnow()
            return self.collection.update_one(filter_dict, {'$set': update_dict})
        return None
    
    def delete_one(self, filter_dict):
        """Deleta um documento"""
        if self.collection is not None:
            return self.collection.delete_one(filter_dict)
        return None

class CheckIn(MongoBaseModel):
    """Check-ins dos membros (MongoDB)"""
    
    def __init__(self):
        super().__init__('checkins')
    
    def create_checkin(self, user_id, username):
        """Cria um novo check-in"""
        checkin_data = {
            'user_id': user_id,
            'username': username,
            'checkin_time': datetime.utcnow(),
            'checkout_time': None,
            'duration_minutes': None
        }
        return self.insert_one(checkin_data)
    
    def checkout(self, checkin_id):
        """Registra o checkout"""
        checkin = self.find_one({'_id': checkin_id})
        if checkin:
            checkout_time = datetime.utcnow()
            duration = (checkout_time - checkin['checkin_time']).total_seconds() / 60
            
            return self.update_one(
                {'_id': checkin_id},
                {
                    'checkout_time': checkout_time,
                    'duration_minutes': duration
                }
            )
        return None

class WorkoutLog(MongoBaseModel):
    """Logs de treinos (MongoDB)"""
    
    def __init__(self):
        super().__init__('workout_logs')
    
    def log_workout(self, user_id, exercises):
        """Registra um treino"""
        workout_data = {
            'user_id': user_id,
            'exercises': exercises,
            'date': datetime.utcnow().date().isoformat(),
            'duration_minutes': None,
            'notes': ''
        }
        return self.insert_one(workout_data)

class Equipment(MongoBaseModel):
    """Equipamentos da academia (MongoDB)"""
    
    def __init__(self):
        super().__init__('equipment')
    
    def add_equipment(self, name, category, status='active'):
        """Adiciona um equipamento"""
        equipment_data = {
            'name': name,
            'category': category,
            'status': status,
            'maintenance_date': None,
            'notes': ''
        }
        return self.insert_one(equipment_data)

class ClassSchedule(MongoBaseModel):
    """Horários de aulas (MongoDB)"""
    
    def __init__(self):
        super().__init__('class_schedules')
    
    def create_class(self, instructor_id, class_name, date_time, max_participants):
        """Cria uma nova aula"""
        class_data = {
            'instructor_id': instructor_id,
            'class_name': class_name,
            'date_time': date_time,
            'max_participants': max_participants,
            'enrolled_participants': [],
            'status': 'scheduled'
        }
        return self.insert_one(class_data)

# Instâncias globais dos modelos MongoDB
checkin_model = CheckIn()
workout_model = WorkoutLog()
equipment_model = Equipment()
class_schedule_model = ClassSchedule()