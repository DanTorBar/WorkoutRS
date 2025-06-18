# recommendation_evaluator.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WorkoutRS.settings")
import django
django.setup()

import pandas as pd
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from main.models.exercise import Exercise
from main.models.workout import Workout, WorkoutExercise
from main.models.social import Favourite, Comment
from main.models.users import HealthProfile
from main.models.logs import ViewLog
from main.models.recommendations import RecommendCache

# Importa tus funciones de recomendación extendidas
from main.recommendations.recommender import init_recommender, recommend_exercises, recommend_workouts

def get_user_context(user_id):
    """
    Devuelve un dict con campos relevantes del perfil del usuario para inspección, incluyendo:
      - Datos personales: edad, género, nombre completo (opcional)
      - BMI
      - Objetivos (goals)
      - Condiciones médicas (conditions)
      - Equipamiento disponible (equipment)
      - Entorno disponible (environment)
      - Imported minutes semanales: neat, cardio_mod, cardio_vig
      - Niveles fallback: neat_level, cardio_mod_level, cardio_vig_level, strength_level
      - Métricas de historial de interacciones: conteo de vistas, favoritos, comentarios
    """
    context = {'user_id': user_id}
    try:
        prof = HealthProfile.objects.get(user_id=user_id)
    except HealthProfile.DoesNotExist:
        return context

    now = timezone.now()

    # --- Datos personales ---
    # Edad
    if prof.date_of_birth:
        today = now.date()
        age = (today - prof.date_of_birth).days // 365
    else:
        age = None
    context['age'] = age

    # Nombre completo (opcional, si lo quieres mostrar)
    try:
        full_name = prof.full_name()
    except:
        full_name = None
    context['full_name'] = full_name

    # Género
    context['gender'] = getattr(prof, 'gender', None)

    # --- BMI ---
    if getattr(prof, 'height_cm', None) and getattr(prof, 'weight_kg', None):
        try:
            bmi = float(prof.weight_kg) / ((prof.height_cm/100)**2)
        except:
            bmi = None
    else:
        bmi = None
    context['bmi'] = bmi

    # --- Objetivos ---
    try:
        context['goals'] = prof.get_goals_list()
    except Exception:
        context['goals'] = []

    # --- Condiciones médicas ---
    try:
        context['conditions'] = prof.get_conditions_list()
    except Exception:
        context['conditions'] = []

    # --- Equipamiento disponible ---
    try:
        context['equipment'] = prof.get_equipment_list()
    except Exception:
        context['equipment'] = []

    # --- Entorno disponible ---
    try:
        context['environment'] = prof.get_environment_list()
    except Exception:
        context['environment'] = []

    # --- Imported minutes semanales ---
    context['imported_neat_min'] = getattr(prof, 'imported_neat_min', None)
    context['imported_cardio_mod_min'] = getattr(prof, 'imported_cardio_mod_min', None)
    context['imported_cardio_vig_min'] = getattr(prof, 'imported_cardio_vig_min', None)

    # --- Niveles fallback ---
    context['neat_level'] = getattr(prof, 'neat_level', None)
    context['cardio_mod_level'] = getattr(prof, 'cardio_mod_level', None)
    context['cardio_vig_level'] = getattr(prof, 'cardio_vig_level', None)
    context['strength_level'] = getattr(prof, 'strength_level', None)

    # --- Métricas de historial de interacciones ---
    # Conteo de vistas, favoritos y comentarios totales y en último mes, para contexto
    # Vistas
    try:
        ct_ex = ContentType.objects.get_for_model(Exercise)
        views_qs = ViewLog.objects.filter(content_type=ct_ex, user_id=user_id)
        total_views = views_qs.count()
        last_month = now - datetime.timedelta(days=30)
        recent_views = views_qs.filter(timestamp__gte=last_month).count()
    except:
        total_views = None
        recent_views = None
    context['total_views'] = total_views
    context['recent_views_30d'] = recent_views

    # Favoritos ejercicios
    try:
        fav_ex_qs = Favourite.objects.filter(user_id=user_id, exercise_id__isnull=False)
        total_fav_ex = fav_ex_qs.count()
        recent_fav_ex = fav_ex_qs.filter(date_added__gte=last_month).count()
    except:
        total_fav_ex = None
        recent_fav_ex = None
    context['total_fav_exercises'] = total_fav_ex
    context['recent_fav_exercises_30d'] = recent_fav_ex

    # Comentarios ejercicios
    try:
        com_ex_qs = Comment.objects.filter(user_id=user_id, exercise_id__isnull=False)
        total_com_ex = com_ex_qs.count()
        recent_com_ex = com_ex_qs.filter(date_added__gte=last_month).count()
    except:
        total_com_ex = None
        recent_com_ex = None
    context['total_comments_exercises'] = total_com_ex
    context['recent_comments_exercises_30d'] = recent_com_ex

    # Favoritos rutinas
    try:
        fav_wk_qs = Favourite.objects.filter(user_id=user_id, workout_id__isnull=False)
        total_fav_wk = fav_wk_qs.count()
        recent_fav_wk = fav_wk_qs.filter(date_added__gte=last_month).count()
    except:
        total_fav_wk = None
        recent_fav_wk = None
    context['total_fav_workouts'] = total_fav_wk
    context['recent_fav_workouts_30d'] = recent_fav_wk

    # Comentarios rutinas
    try:
        com_wk_qs = Comment.objects.filter(user_id=user_id, workout_id__isnull=False)
        total_com_wk = com_wk_qs.count()
        recent_com_wk = com_wk_qs.filter(date_added__gte=last_month).count()
    except:
        total_com_wk = None
        recent_com_wk = None
    context['total_comments_workouts'] = total_com_wk
    context['recent_comments_workouts_30d'] = recent_com_wk

    return context

def describe_exercise(ex_id):
    """
    Devuelve un dict con atributos de ejercicio para inspección:
    - exerciseName, exerciseCategory, equipment, músculos primarios/secundarios, likes_count
    """
    try:
        ex = Exercise.objects.prefetch_related('priMuscles','secMuscles').get(id=ex_id)
    except Exercise.DoesNotExist:
        return {'exercise_id': ex_id}
    info = {
        'exercise_id': ex_id,
        'exerciseName': ex.exerciseName,
        'exerciseCategory': ex.exerciseCategory,
        'equipment': ex.equipment,
        'likes_count': ex.likes_count,
    }
    # Músculos
    pri = list(ex.priMuscles.values_list('name', flat=True))
    sec = list(ex.secMuscles.values_list('name', flat=True))
    info['muscles_primary'] = pri
    info['muscles_secondary'] = sec
    return info

def describe_workout(wk_id):
    """
    Devuelve un dict con atributos de rutina para inspección:
    - workoutName, workoutCategory, level, gender, bodyPart, likes_count, lista de exercise IDs
    - Además, si Workout tuviera campos de environment o equipment required, se pueden agregar aquí.
    """
    try:
        wk = Workout.objects.prefetch_related('workoutexercise_set').get(id=wk_id)
    except Workout.DoesNotExist:
        return {'workout_id': wk_id}
    info = {
        'workout_id': wk_id,
        'workoutName': wk.workoutName,
        'workoutCategory': wk.workoutCategory,
        'level': wk.level,
        'gender': wk.gender,
        'bodyPart': wk.bodyPart,
        'likes_count': wk.likes_count,
    }
    # Ejercicios incluidos
    ex_ids = list(WorkoutExercise.objects.filter(workout=wk).values_list('exercise_id', flat=True))
    info['exercise_ids'] = ex_ids
    # Si Workout tiene otros atributos relevantes, agrégalos:
    # Por ejemplo, entorno o equipamiento necesario:
    if hasattr(wk, 'environment'):
        try:
            envs = list(wk.environment.values_list('name', flat=True))
            info['workout_environment'] = envs
        except:
            pass
    if hasattr(wk, 'equipment_required'):  # ejemplo de campo
        info['workout_equipment_required'] = getattr(wk, 'equipment_required', None)
    return info

def evaluate_recommendations_for_users(user_ids=None, top_n=5):
    """
    Para cada user_id en user_ids (o todos con HealthProfile si user_ids=None),
    obtiene contexto ampliado, recomendaciones de ejercicios y rutinas, y devuelve dos DataFrames:
      - df_ex: incluye columnas de contexto extenso y atributos de cada ejercicio recomendado.
      - df_wk: similar para rutinas.
    """
    # Inicializa el sistema (si no se ha llamado aún)
    init_recommender()

    # Determinar lista de usuarios a evaluar
    if user_ids is None:
        user_ids = list(HealthProfile.objects.values_list('user_id', flat=True))
    results_ex = []
    results_wk = []

    for user_id in user_ids:
        # Contexto ampliado
        ctx = get_user_context(user_id)

        # Recomendaciones
        try:
            rec_ex = recommend_exercises(user_id=user_id, top_n=top_n)
        except Exception as e:
            print(f"[WARN] recommend_exercises fallo para user {user_id}: {e}")
            rec_ex = pd.DataFrame(columns=['id','exerciseName'])
        try:
            rec_wk = recommend_workouts(user_id=user_id, top_n=top_n)
        except Exception as e:
            print(f"[WARN] recommend_workouts fallo para user {user_id}: {e}")
            rec_wk = pd.DataFrame(columns=['id','workoutName'])

        # Para cada ejercicio recomendado, describir
        for rank, row in rec_ex.reset_index(drop=True).iterrows():
            ex_id = row.get('id')
            desc = describe_exercise(ex_id) if ex_id is not None else {}
            entry = {
                'user_id': user_id,
                'rec_rank': rank+1,
                **ctx,
                **desc
            }
            results_ex.append(entry)

        # Para cada rutina recomendada, describir
        for rank, row in rec_wk.reset_index(drop=True).iterrows():
            wk_id = row.get('id')
            desc = describe_workout(wk_id) if wk_id is not None else {}
            entry = {
                'user_id': user_id,
                'rec_rank': rank+1,
                **ctx,
                **desc
            }
            results_wk.append(entry)

    df_ex = pd.DataFrame(results_ex)
    df_wk = pd.DataFrame(results_wk)
    return df_ex, df_wk

def main():
    """
    Ejecuta la evaluación de recomendaciones para todos los usuarios y exporta los resultados a CSV.
    """
    print("Evaluando recomendaciones para todos los usuarios...")
    df_ex, df_wk = evaluate_recommendations_for_users(top_n=5)
    print("Exportando resultados a 'eval_ex.csv' y 'eval_wk.csv'...")
    df_ex.to_csv('eval_ex.csv', index=False)
    df_wk.to_csv('eval_wk.csv', index=False)
    print("Ejercicios recomendados:", len(df_ex), "Rutinas recomendadas:", len(df_wk))

if __name__ == "__main__":
    main()
