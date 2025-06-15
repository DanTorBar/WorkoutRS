from datetime import timedelta
import time
from tkinter import *
import os, shutil, sys
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, ID
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.analysis import KeywordAnalyzer


def almacenar_datos():
    from main.models.exercise import Exercise
    from main.models.workout import Workout
    from main.scrapping.scrapping import extraer_rutinas_y_ejercicios

    esquema_ejercicio = Schema(
        idExercise=ID(stored=True, unique=True),
        exerciseName=TEXT(stored=True, phrase=True),
        exerciseCategory=TEXT(analyzer=KeywordAnalyzer(), stored=True),
        priMuscles=TEXT(analyzer=KeywordAnalyzer(), stored=True),
        secMuscles=TEXT(analyzer=KeywordAnalyzer(), stored=True)
    )

    esquema_rutina = Schema(
        idWorkout=ID(stored=True, unique=True),
        workoutName=TEXT(stored=True, phrase=True),
        workoutCategory=TEXT(analyzer=KeywordAnalyzer(), stored=True),
        level=KEYWORD(stored=True, commas=True, lowercase=True),
        gender=KEYWORD(stored=True, commas=True, lowercase=True)
    )

    # Eliminar directorios de índices si existen
    if os.path.exists("IndexEjercicio"):
        shutil.rmtree("IndexEjercicio")
    os.mkdir("IndexEjercicio")

    if os.path.exists("IndexRutina"):
        shutil.rmtree("IndexRutina")
    os.mkdir("IndexRutina")

    # Crear índices
    ix_ejercicio = create_in("IndexEjercicio", schema=esquema_ejercicio)
    ix_rutina = create_in("IndexRutina", schema=esquema_rutina)

    # Crear writers para añadir documentos a los índices
    writer_ejercicio = ix_ejercicio.writer()
    writer_rutina = ix_rutina.writer()

    start_time = time.time()
    # extraer_rutinas_y_ejercicios()
    end_time = time.time()

    print(f"Tiempo de extracción: {end_time - start_time} segundos")

    lista_ejercicios = Exercise.objects.all()
    lista_rutinas = Workout.objects.all()

    for ejercicio in Exercise.objects.all():
        writer_ejercicio.add_document(
            idExercise=str(ejercicio.id),
            exerciseName=ejercicio.exerciseName,
            exerciseCategory=ejercicio.exerciseCategory,
            priMuscles=",".join(m.name for m in ejercicio.priMuscles.all()),
            secMuscles=",".join(m.name for m in ejercicio.secMuscles.all())
        )
        print(f"Ejercicio añadido: {ejercicio.exerciseName}")
    
    for rutina in Workout.objects.all():
        writer_rutina.add_document(
            idWorkout=str(rutina.id),
            workoutName=rutina.workoutName,
            workoutCategory=rutina.workoutCategory,
            level=rutina.level,
            gender=rutina.gender
        )
        print(f"Rutina añadida: {rutina.workoutName}")
    
    writer_ejercicio.commit()
    writer_rutina.commit()
    
    mensaje = f"Se han añadido {len(lista_ejercicios)} ejercicios y {len(lista_rutinas)} rutinas a los índices"
    
    return mensaje


def buscar_ejercicios_por_nombre_instrucciones(cadena, user, order='name'):
    from main.models.exercise import Exercise
    from main.models.social import Favourite

    try:
        ix = open_dir("IndexEjercicio")
    except Exception:
        return []
    
    with ix.searcher() as searcher:
        parser = MultifieldParser(["exerciseName"], ix.schema, group=OrGroup)
        results = searcher.search(parser.parse(f'"{cadena}"'), limit=100)
        ids = [r['idExercise'] for r in results]
    
    ejercicios = list(Exercise.objects.filter(id__in=ids).values("id", "exerciseName", "instructions"))
    
    if order == 'name':
        ejercicios = sorted(ejercicios, key=lambda x: x["exerciseName"].lower())
    elif order == 'likes_count':
        ejercicios = sorted(ejercicios, key=lambda x: x.get("likes_count", 0), reverse=True)
    
    if user and user.is_authenticated:
        favoritos = set(Favourite.objects.filter(user=user, exercise_id__in=ids).values_list('exercise_id', flat=True))
        for ejercicio in ejercicios:
            ejercicio["is_favourite"] = ejercicio["id"] in favoritos
    
    return ejercicios


def ej_buscar(name, cat, muscle, user, equipment, order='name'):
    from main.models.exercise import Exercise
    from main.models.social import Favourite

    try:
        ix = open_dir("IndexEjercicio")
    except Exception as e:
        print(f"Error opening index: {e}")
        return []

    with ix.searcher() as searcher:
        fields = ["exerciseName", "exerciseCategory", "equipment", "priMuscles", "secMuscles"]
        parser = MultifieldParser(fields, schema=ix.schema, group=OrGroup)

        query_parts = []
        if name:
            query_parts.append(f'(exerciseName:"{name}" OR exerciseName:*"{name}"*)')
        if cat:
            query_parts.append(f'(exerciseCategory:"{cat}" OR exerciseCategory:*"{cat}"*)')
        if equipment:
            query_parts.append(f'(equipment:"{equipment}" OR equipment:*"{equipment}"*)')
        if muscle:
            query_parts.append(f'((priMuscles:*"{muscle}"* OR secMuscles:"{muscle}") OR ' +  
                               f'(priMuscles:"{muscle}" OR secMuscles:"{muscle}"))')

        query_string = " AND ".join(query_parts) if query_parts else "*:*"
        query = parser.parse(query_string)
        results = searcher.search(query, limit=100)
        ids = [r['idExercise'] for r in results]
            
    ejercicios = list(Exercise.objects.filter(id__in=ids).select_related())
    
    if order == 'name':
        ejercicios = sorted(ejercicios, key=lambda x: x.exerciseName.lower())
    elif order == 'likes_count':
        ejercicios = sorted(ejercicios, key=lambda x: x.likes_count, reverse=True)
    
    if user and user.is_authenticated:
        favoritos = set(Favourite.objects.filter(user=user, exercise_id__in=ids).
                        values_list('exercise_id', flat=True))
        for ejercicio in ejercicios:
            ejercicio.is_favourite = ejercicio.id in favoritos

    return ejercicios


def ru_buscar(name, cat, level, gender, user, order='name'):
    from django.utils.timezone import now
    from main.models.workout import Workout
    from main.models.social import Favourite

    try:
        ix = open_dir("IndexRutina")
    except Exception as e:
        print(f"Error opening index: {e}")
        return []

    with ix.searcher() as searcher:
        fields = ["workoutName", "workoutCategory", "level", "gender"]
        parser = MultifieldParser(fields, schema=ix.schema, group=OrGroup)

        query_parts = []
        if name:
            query_parts.append(f'(workoutName:"{name}"* OR workoutName:"{name}")')
        if cat:
            query_parts.append(f'(workoutCategory:"{cat}" OR workoutCategory:*"{cat}"*)')
        if level:
            query_parts.append(f'level:{level}')
        if gender:
            query_parts.append(f'gender:{gender}')

        query_string = " AND ".join(query_parts) if query_parts else "*:*"
        query = parser.parse(query_string)
        results = searcher.search(query, limit=100)
        ids = [r['idWorkout'] for r in results]
    
    rutinas = list(Workout.objects.filter(id__in=ids).select_related())
    
    if order == 'name':
        rutinas = sorted(rutinas, key=lambda x: x.workoutName.lower())
    elif order == 'popularity':
        recent_period = now() - timedelta(days=14)
        for rutina in rutinas:
            rutina.recent_likes = Favourite.objects.filter(workout=rutina, date_added__gte=recent_period).count()
        rutinas = sorted(rutinas, key=lambda x: getattr(x, 'recent_likes', 0), reverse=True)
    elif order == 'likes_count':
        rutinas = sorted(rutinas, key=lambda x: x.likes_count, reverse=True)
    elif order == 'creationDate':
        rutinas = sorted(rutinas, key=lambda x: x.creationDate, reverse=True)
    
    if user and user.is_authenticated:
        favoritos = set(Favourite.objects.filter(user=user, workout_id__in=ids).values_list('workout_id', flat=True))
        for rutina in rutinas:
            rutina.is_favourite = rutina.id in favoritos
    
    return rutinas

    
def buscar_rutinas_por_nombre_descripcion(cadena, user, order='name'):
    from django.utils.timezone import now
    from main.models.workout import Workout
    from main.models.social import Favourite

    if cadena and cadena.strip() != "":
        try:
            ix = open_dir("IndexRutina")
        except Exception:
            return []
        with ix.searcher() as searcher:
            parser = MultifieldParser(["workoutName"], ix.schema, group=OrGroup)
            # Permitir búsqueda por palabras parciales (contenga los términos)
            # Ejemplo: si cadena = "fuerza total" => busca rutinas que contengan ambas palabras
            palabras = [w for w in cadena.strip().split() if w]
            if palabras:
                query = " AND ".join([f'workoutName:*{w}*' for w in palabras])
            else:
                query = f'workoutName:*{cadena}*'
            results = searcher.search(parser.parse(query), limit=100)
            ids = [r['idWorkout'] for r in results]
        rutinas = list(Workout.objects.filter(id__in=ids).select_related())
    else:
        rutinas = list(Workout.objects.all().select_related())
        ids = [r.id for r in rutinas]
    
    if order == 'name':
        rutinas = sorted(rutinas, key=lambda x: x.workoutName.lower())
    elif order == 'popularity':
        recent_period = now() - timedelta(days=14)
        for rutina in rutinas:
            rutina.recent_likes = Favourite.objects.filter(workout=rutina, date_added__gte=recent_period).count()
        rutinas = sorted(rutinas, key=lambda x: getattr(x, 'recent_likes', 0), reverse=True)
    elif order == 'likes_count':
        rutinas = sorted(rutinas, key=lambda x: x.likes_count, reverse=True)
    elif order == 'creationDate':
        rutinas = sorted(rutinas, key=lambda x: x.creationDate, reverse=True)
    
    if user and user.is_authenticated:
        favoritos = set(Favourite.objects.filter(user=user, workout_id__in=ids).values_list('workout_id', flat=True))
        for rutina in rutinas:
            rutina.is_favourite = rutina.id in favoritos
    
    return rutinas

if __name__ == "__main__":
    # Calcula la ruta absoluta a la carpeta backend
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # .../backend/main/search
    BACKEND_DIR = os.path.dirname(os.path.dirname(BASE_DIR))  # .../backend

    if BACKEND_DIR not in sys.path:
        sys.path.insert(0, BACKEND_DIR)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WorkoutRS.settings')
    import django
    django.setup()
    almacenar_datos()
