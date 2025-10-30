from django.contrib.auth import get_user_model

User = get_user_model()

# Criar superusuário manager
admin_user = User.objects.create_superuser(
    username='admin',
    email='admin@primefit.com',
    password='admin123',
    first_name='Admin',
    last_name='Manager',
    user_type='manager'
)
print(f'Superusuário criado: {admin_user.username} (manager)')

# Criar usuário instrutor
instructor = User.objects.create_user(
    username='instructor1',
    email='instructor@primefit.com',
    password='inst123',
    first_name='João',
    last_name='Silva',
    user_type='instructor'
)
print(f'Instrutor criado: {instructor.username}')

# Criar usuário membro
member = User.objects.create_user(
    username='member1',
    email='member@primefit.com',
    password='mem123',
    first_name='Maria',
    last_name='Santos',
    user_type='member'
)
print(f'Membro criado: {member.username}')

print('Todos os usuários criados com sucesso!')