# recommendation_evaluator.py
import pandas as pd
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from main.models.exercise import Exercise
from main.models.workout import Workout, WorkoutExercise
from main.models.social import Favourite, Comment
from main.models.users import HealthProfile
from main.models.logs import ViewLog
from main.models.recommendations import RecommendCache

# Importa tus funciones de recomendación
from main.recommendations.recommendations import init_recommender, recommend_exercises, recommend_workouts

def get_user_context(user_id):
    """
    Devuelve un dict con campos relevantes del perfil del usuario para inspección:
    - edad, género, BMI, niveles (cardio, fuerza), objetivos (goals)
    """
    context = {'user_id': user_id}
    try:
        prof = HealthProfile.objects.get(user_id=user_id)
    except HealthProfile.DoesNotExist:
        return context
    # Edad
    if prof.date_of_birth:
        today = timezone.now().date()
        age = (today - prof.date_of_birth).days // 365
    else:
        age = None
    context['age'] = age
    # Género
    context['gender'] = getattr(prof, 'gender', None)
    # BMI
    if getattr(prof, 'height_cm', None) and getattr(prof, 'weight_kg', None):
        try:
            bmi = float(prof.weight_kg) / ((prof.height_cm/100)**2)
        except:
            bmi = None
    else:
        bmi = None
    context['bmi'] = bmi
    # Niveles de actividad
    context['cardio_vig_level'] = getattr(prof, 'cardio_vig_level', None)
    context['strength_level'] = getattr(prof, 'strength_level', None)
    # Goals: lista de strings
    try:
        context['goals'] = list(prof.goals.values_list('name', flat=True))
    except:
        context['goals'] = []
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
    """
    try:
        wk = Workout.objects.get(id=wk_id)
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
    return info

def evaluate_recommendations_for_users(user_ids=None, top_n=5):
    """
    Para cada user_id en user_ids (o todos con HealthProfile si user_ids=None),
    obtiene contexto, recomendaciones de ejercicios y rutinas, y devuelve dos DataFrames:
      - df_ex: columnas [user_id, edad, gender, bmi, cardio_vig_level, strength_level, goals,
                        rec_rank, exercise_id, exerciseName, exerciseCategory, equipment,
                        muscles_primary, muscles_secondary, likes_count]
      - df_wk: columnas [user_id, edad, gender, bmi, cardio_vig_level, strength_level, goals,
                        rec_rank, workout_id, workoutName, workoutCategory, level, gender, bodyPart,
                        likes_count, exercise_ids]
    Útil para inspección manual o análisis sencillo.
    """
    # Inicializa el sistema (si no se ha llamado aún)
    init_recommender()

    # Determinar lista de usuarios a evaluar
    if user_ids is None:
        # todos los usuarios con HealthProfile
        user_ids = list(HealthProfile.objects.values_list('user_id', flat=True))
    results_ex = []
    results_wk = []

    for user_id in user_ids:
        # Contexto
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
        # Para cada recomendado, describir
        for rank, row in rec_ex.reset_index(drop=True).iterrows():
            ex_id = row['id']
            desc = describe_exercise(ex_id)
            entry = {
                'user_id': user_id,
                'rec_rank': rank+1,
                **ctx,
                **desc
            }
            results_ex.append(entry)
        for rank, row in rec_wk.reset_index(drop=True).iterrows():
            wk_id = row['id']
            desc = describe_workout(wk_id)
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

# Ejemplo de uso en Django shell:
# >>> from main.recommendations.recommendation_evaluator import evaluate_recommendations_for_users
# >>> df_ex, df_wk = evaluate_recommendations_for_users(top_n=5)
# >>> display(df_ex.head(20))
# >>> display(df_wk.head(20))
#
# Puedes filtrar luego por user_id o por category:
# >>> df_ex[df_ex['user_id']==42]
# >>> df_ex[df_ex['exerciseCategory']=='Pecho']
#
# O guardar en CSV:
# >>> df_ex.to_csv('eval_ex.csv', index=False)
# >>> df_wk.to_csv('eval_wk.csv', index=False)
