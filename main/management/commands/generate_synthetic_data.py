# workout/management/commands/generate_synthetic_data.py

from faker import Faker
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models.exercise import Exercise
from main.models.workout import Workout
from main.models.social import Favourite, Comment
from main.models.users import Condition, Environment, Equipment, Goal, HealthProfile
from main.models.logs import ViewLog
from django.contrib.contenttypes.models import ContentType

# Constantes de categorías (tal como las tienes tú)
CARDIO_CATS = [
    'Cardio,Caminar','Cardio,Máquinas de fitness','Cardio,Correr','Cardio,Ciclismo',
    'Cardio,Ejercicios/Pliamétricos','Cardio,Aerobic/Baile','Cardio,Yoga/Pilates',
    'Cardio,Deporte/Entrenamiento','Cardio,Programas/Vídeos de entrenamiento',
    'Cardio,Programas de entrenamiento/Vídeos','Cardio,Ejercicios de rehabilitación'
]
EXERCISE_CATS = [
    'Muslos','Pecho','Antebrazos','Trapecios','Espalda','Abdominales','Tríceps',
    'Gemelos','Bíceps','Zona lumbar','Hombros'
]
ROUTINE_CATS = [
    'Fuerza y cardio combinados','Yoga','Caminar','Solo entrenamiento de cardio','Pilates',
    'Cardio','Solo entrenamiento de fuerza','Entrenamiento de carrera y competición',
    'Tonificación','Entrenamiento en circuito','Estiramientos','N/A'
]

# Mapeo de objetivos a categorías preferidas
GOAL_TO_EX = {
    'Mejora de la resistencia': CARDIO_CATS,
    'Pérdida de peso': CARDIO_CATS,
    'Mantenimiento de la salud': CARDIO_CATS + EXERCISE_CATS,
    'Mejorar la salud mental': EXERCISE_CATS,
    'Aumentar la fuerza': EXERCISE_CATS,
    'Ganancia muscular': EXERCISE_CATS,
    'Preparación deportiva': EXERCISE_CATS,
    'Mejora de la flexibilidad': ['Cardio,Yoga/Pilates'],
    'Mejorar la movilidad': ['Cardio,Yoga/Pilates'],
    'Mejorar la postura': ['Cardio,Yoga/Pilates'],
}
GOAL_TO_WK = {
    'Mejora de la resistencia': ['Solo entrenamiento de cardio','Cardio','Entrenamiento de carrera y competición'],
    'Pérdida de peso': ['Solo entrenamiento de cardio','Cardio','Entrenamiento en circuito'],
    'Aumentar la fuerza': ['Solo entrenamiento de fuerza','Entrenamiento en circuito'],
    'Ganancia muscular': ['Solo entrenamiento de fuerza','Entrenamiento en circuito'],
    'Preparación deportiva': ['Entrenamiento de carrera y competición'],
    'Mejora de la flexibilidad': ['Yoga','Pilates','Estiramientos'],
    'Mejorar la movilidad': ['Yoga','Pilates','Estiramientos'],
    'Mejorar la postura': ['Yoga','Pilates'],
    'Mantenimiento de la salud': ROUTINE_CATS,
    'Mejorar la salud mental': ROUTINE_CATS,
}

ENV_TO_EQUIP = {
    'Gimnasio': ['Mancuernas','Barra olímpica','Bandas de resistencia','Máquinas de gimnasio','Banco de pesas','TRX','Fitball','Rueda de abdominales'],
    'Casa':     ['Mancuernas','Kettlebell','Bandas de resistencia','Esterilla de yoga','Rueda de abdominales','TRX','Fitball','Comba'],
    'Aire Libre':['Cinta de correr','Bicicleta estática','Comba']
}
ENV_TO_WK = {
    'Gimnasio': ['Solo entrenamiento de fuerza','Entrenamiento en circuito','Fuerza y cardio combinados','Tonificación'],
    'Casa':     ['Yoga','Pilates','Estiramientos'],
    'Aire Libre':['Caminar','Solo entrenamiento de cardio','Entrenamiento de carrera y competición']
}

class Command(BaseCommand):
    help = 'Genera usuarios sintéticos y datos de interacción sesgados por objetivos, equipamiento y entorno'

    def add_arguments(self, parser):
        parser.add_argument('--clusters',      type=int, default=60, help='Número aproximado de clusters')
        parser.add_argument('--per_cluster',   type=int, default=10, help='Usuarios por cluster')
        parser.add_argument('--inter_per_user',type=int, default=30, help='Interacciones por usuario')

    def handle(self, *args, **options):
        fake = Faker()
        clusters       = options['clusters']
        per_cluster    = options['per_cluster']
        inter_per_user = options['inter_per_user']

        # Carga datos estáticos
        exercises  = list(Exercise.objects.all())
        workouts   = list(Workout.objects.all())
        goals      = list(Goal.objects.all())
        conditions = list(Condition.objects.all())
        equipments = list(Equipment.objects.all())
        environments = list(Environment.objects.all())
        ex_ct      = ContentType.objects.get_for_model(Exercise)
        wk_ct      = ContentType.objects.get_for_model(Workout)

        total = clusters * per_cluster
        self.stdout.write(f'🛠 Generando ~{total} usuarios sintéticos…')

        for c in range(clusters):
            for i in range(per_cluster):
                # 1) Crear usuario y perfil de salud
                username = f'synth_{c}_{i}'
                user = User.objects.create_user(username=username, password='pass1234')
                prof = HealthProfile.objects.create(
                    user=user,
                    date_of_birth=fake.date_between(start_date='-70y', end_date='-18y'),
                    gender=random.choice(['masculino','femenino','otro','desconocido']),
                    height_cm=random.randint(150,190),
                    weight_kg=round(random.uniform(50,100),2),
                    neat_level=random.randint(0,5),
                    cardio_mod_level=random.randint(0,5),
                    cardio_vig_level=random.randint(0,5),
                    strength_level=random.randint(0,5),
                )
                # Asignar M2M
                chosen_goals = random.sample(goals, k=random.randint(1,2))
                prof.goals.set(chosen_goals)
                prof.conditions.set(random.sample(conditions, k=random.randint(0,1)))
                prof.equipment.set(random.sample(equipments, k=random.randint(1,3)))
                prof.environment.set(random.sample(environments, k=1))  # uno por usuario

                # Definir preferencias según objetivos, equipamiento y entorno
                ex_pref = set()
                wk_pref = set()
                for g in chosen_goals:
                    ex_pref.update(GOAL_TO_EX.get(g.name, []))
                    wk_pref.update(GOAL_TO_WK.get(g.name, []))
                # añadir equipamiento
                ex_pref.update([e.name for e in prof.equipment.all()])
                # añadir entorno
                env_name = prof.environment.first().name
                ex_pref.update(ENV_TO_EQUIP.get(env_name, []))
                wk_pref.update(ENV_TO_WK.get(env_name, []))

                # 2) Generar interacciones sesgadas
                for _ in range(inter_per_user):
                    if random.random() < 0.7:
                        # Ejercicio
                        candidates = [e for e in exercises if e.exerciseCategory in ex_pref]
                        ex = random.choice(candidates) if candidates and random.random()<0.8 else random.choice(exercises)
                        ViewLog.objects.create(user=user, content_type=ex_ct, object_id=ex.id)
                        if random.random() < 0.1:
                            Favourite.objects.create(user=user, exercise=ex)
                        if random.random() < 0.05:
                            Comment.objects.create(user=user, exercise=ex, comment=fake.sentence())
                    else:
                        # Rutina
                        candidates = [w for w in workouts if w.workoutCategory in wk_pref]
                        wk = random.choice(candidates) if candidates and random.random()<0.8 else random.choice(workouts)
                        ViewLog.objects.create(user=user, content_type=wk_ct, object_id=wk.id)
                        if random.random() < 0.1:
                            Favourite.objects.create(user=user, workout=wk)
                        if random.random() < 0.05:
                            Comment.objects.create(user=user, workout=wk, comment=fake.sentence())

        self.stdout.write(self.style.SUCCESS(f'✅ Generados {total} usuarios e interacciones.'))
