import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

from django.utils import timezone
from django_pandas.io import read_frame
from django.contrib.contenttypes.models import ContentType
from main.models.exercise import Exercise
from main.models.workout import Workout, WorkoutExercise
from main.models.social import Favourite, Comment
from main.models.users import HealthProfile
from main.models.logs import ViewLog
from main.models.recommendations import RecommendCache
from main.recommendations.recommendation_cache import get_cached_recommendations, CACHE_TTL_HOURS

import pandas as pd
import numpy as np
import scipy.sparse as sp
from scipy.sparse import hstack, vstack, csr_matrix
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from implicit.als import AlternatingLeastSquares
import datetime
import pytz

# --------------------------------------------------
# 0. Configuración general
# --------------------------------------------------
WEIGHTS_DEFAULT = {'als': 0.3, 'content': 0.7}
WEIGHTS_COLD    = {'als': 0.0, 'content': 1.0}
COLD_THRESHOLD  = 5      # umbral de interacciones para cold-start
CACHE_TTL_HOURS = 6      # caducidad de caché en horas

# Penalizaciones básicas según categorías (igual que antes)
CARDIO_CATS = [
    'Cardio,Caminar','Cardio,Máquinas de fitness','Cardio,Correr','Cardio,Ciclismo',
    'Cardio,Ejercicios/Pliamétricos','Cardio,Aerobic/Baile','Cardio,Yoga/Pilates',
    'Cardio,Deporte/Entrenamiento','Cardio,Programas/Vídeos de entrenamiento',
    'Cardio,Programas de entrenamiento/Vídeos','Cardio,Ejercicios de rehabilitación'
]
STRENGTH_CATS = [
    # categorías de rutinas de fuerza intensas para penalizar si strength_level=0
    'Solo entrenamiento de fuerza','Entrenamiento en circuito'
]
# Mapeo de condiciones a categorías de ejercicio/rutina a penalizar
# AJUSTAR: completa con los nombres de Condition.name que uses y las categorías de ítems que conviene penalizar.
CONDITION_PENALTIES = {
    # Hipertensión: evitar cardio muy intenso y ejercicios de alta presión arterial
    'hipertensión': {
        'exercise_cats': ['Cardio,Correr', 'Cardio,Ejercicios/Pliométricos', 'Cardio,Ciclismo'],
        'workout_cats': ['Entrenamiento en circuito'],
        'delta': 0.3
    },
    # Asma: evitar cardio de alta intensidad y ambientes polvorientos
    'asma': {
        'exercise_cats': ['Cardio,Correr', 'Cardio,Ejercicios/Pliométricos'],
        'workout_cats': ['Entrenamiento en circuito'],
        'delta': 0.2
    },
    # Dolor de rodilla: evitar saltos y ejercicios de impacto
    'dolor de rodilla': {
        'exercise_cats': ['Cardio,Correr', 'Cardio,Ejercicios/Pliométricos', 'Cardio,Aerobic/Baile'],
        'workout_cats': ['Entrenamiento en circuito'],
        'delta': 0.3
    },
    # Osteoporosis: evitar ejercicios de impacto y saltos
    'osteoporosis': {
        'exercise_cats': ['Cardio,Correr', 'Cardio,Ejercicios/Pliométricos', 'Cardio,Deporte/Entrenamiento'],
        'workout_cats': ['Entrenamiento en circuito'],
        'delta': 0.3
    },
    # Embarazo: evitar ejercicios de impacto y rutinas de alta intensidad
    'embarazo': {
        'exercise_cats': ['Cardio,Correr', 'Cardio,Ejercicios/Pliométricos', 'Cardio,Aerobic/Baile'],
        'workout_cats': ['Entrenamiento en circuito', 'Solo entrenamiento de fuerza'],
        'delta': 0.4
    },
    # Enfermedad cardíaca: evitar cardio intenso y rutinas de fuerza máxima
    'enfermedad cardíaca': {
        'exercise_cats': ['Cardio,Correr', 'Cardio,Ejercicios/Pliométricos', 'Cardio,Ciclismo'],
        'workout_cats': ['Entrenamiento en circuito', 'Solo entrenamiento de fuerza'],
        'delta': 0.4
    },
    # Artritis: evitar ejercicios de impacto y movimientos repetitivos de articulaciones afectadas
    'artritis': {
        'exercise_cats': ['Cardio,Correr', 'Cardio,Ejercicios/Pliométricos'],
        'workout_cats': ['Entrenamiento en circuito'],
        'delta': 0.2
    },
    # Sobrepeso: evitar ejercicios de alto impacto al inicio
    'sobrepeso': {
        'exercise_cats': ['Cardio,Correr', 'Cardio,Ejercicios/Pliométricos'],
        'workout_cats': [],
        'delta': 0.2
    },
}

# Penalización por falta de equipamiento:
EQUIPMENT_PENALTY_DELTA = 0.2  # restar 0.2 si el ejercicio requiere equipamiento que el usuario NO tiene
# Penalización por entorno no disponible:
ENV_PENALTY_DELTA = 0.2       # restar si el ítem requiere entorno no en profile.environment
# Penalización por exceso de actividad: si imported minutos altos, reducir más de lo necesario
# Por ejemplo, si el usuario ya hace mucho cardio vigoroso, penalizar cardio adicional:
EXCESS_ACTIVITY_PENALTY = {
    'cardio_vig': {
        'threshold_min': 150,   # minutos/semana umbral
        'exercise_cats': CARDIO_CATS,
        'delta': 0.1
    },
    'cardio_mod': {
        'threshold_min': 300,
        'exercise_cats': CARDIO_CATS,
        'delta': 0.1
    },
    # Puedes añadir para strength: aunque no hay imported_strength_min, se podría usar strength_level o neat_level
}

# Penalizaciones adicionales por edad, nivel de fuerza/cardiovascular, IMC, etc.
PENALTIES = {
    'age_hi': {
        'threshold': 65,
        'cats': CARDIO_CATS,
        'delta': 0.2
    },
    'cardio_zero': {
        'cardio_vig_level': 0,
        'cats': CARDIO_CATS,
        'delta': 0.2
    },
    'bmi_obese': {
        'cats': CARDIO_CATS,
        'delta': 0.1
    }
}

# --------------------------------------------------
# Funciones de Content-Based
# --------------------------------------------------
def get_exercise_content_matrix():
    """
    Construye df_ex con campos clave y X_cb_ex: matriz CSR de features de ejercicio.
    """
    ex_qs = Exercise.objects.prefetch_related('priMuscles','secMuscles')
    df_ex = read_frame(ex_qs, fieldnames=['id','exerciseName','exerciseCategory','equipment','likes_count'])
    # Texto + categoría
    X_text_ex = TfidfVectorizer(max_features=500, ngram_range=(1,2)).fit_transform(
        df_ex['exerciseName'].fillna('') + ' ' + df_ex['exerciseCategory'].fillna('')
    )
    # Músculos primarios/secundarios
    X_mus_ex = MultiLabelBinarizer(sparse_output=True).fit_transform(
        [[m.name for m in ex.priMuscles.all()]+[m.name for m in ex.secMuscles.all()] for ex in ex_qs]
    )
    # Equipamiento necesario (campo texto, ej. "mancuernas, banda")
    X_eq_ex = MultiLabelBinarizer(sparse_output=True).fit_transform(
        df_ex['equipment'].fillna('').str.split(', ')
    )
    X_cb_ex = hstack([X_text_ex, X_mus_ex, X_eq_ex]).tocsr()
    return df_ex, X_cb_ex

def get_workout_content_matrix(X_cb_ex, df_ex):
    """
    Construye df_wk con campos clave y X_cb_wk: matriz CSR de features de rutina.
    Agrega vectores de ejercicios incluidos.
    """
    wk_qs = Workout.objects.all()
    df_wk = read_frame(wk_qs, fieldnames=['id','workoutName','workoutCategory','level','gender','bodyPart','likes_count'])
    X_text_wk = TfidfVectorizer(max_features=300, ngram_range=(1,1)).fit_transform(
        df_wk['workoutName'].fillna('') + ' ' +
        df_wk['workoutCategory'].fillna('') + ' ' +
        df_wk['bodyPart'].fillna('')
    )
    X_lvl = MultiLabelBinarizer(sparse_output=True).fit_transform(df_wk['level'].fillna('').str.split(', '))
    X_gen = MultiLabelBinarizer(sparse_output=True).fit_transform(df_wk['gender'].fillna('').str.split(', '))
    # Agregar vectores de ejercicios por rutina
    agg = []
    id2idx_ex = {eid: idx for idx, eid in enumerate(df_ex['id'])}
    for wk in wk_qs:
        ids = [we.exercise.id for we in WorkoutExercise.objects.filter(workout=wk)]
        idxs = [id2idx_ex[ex_id] for ex_id in ids if ex_id in id2idx_ex]
        if idxs:
            submat = X_cb_ex[idxs]
            mean_vec = submat.sum(axis=0) / submat.shape[0]
            agg.append(csr_matrix(mean_vec))
        else:
            agg.append(csr_matrix((1, X_cb_ex.shape[1])))
    X_ex_agg = vstack(agg)
    X_cb_wk = hstack([X_text_wk, X_lvl, X_gen, X_ex_agg]).tocsr()
    return df_wk, X_cb_wk

# --------------------------------------------------
# Penalizaciones avanzadas usando HealthProfile completo
# --------------------------------------------------
def penalize(profile: HealthProfile, item, score: float, is_ex: bool):
    """
    Ajusta score según diversas condiciones del perfil:
      - Edad avanzada
      - Niveles de cardio/strength
      - IMC alto
      - Objetivos
      - Condiciones médicas (profile.conditions)
      - Equipamiento disponible (profile.equipment)
      - Entorno disponible (profile.environment)
      - Actividad importada (imported_*_min)
    item: instancia de Exercise o Workout según is_ex.
    """
    sc = score
    user_goals = set(profile.get_goals_list())

    # --- Edad avanzada ---
    if profile.date_of_birth:
        age = (datetime.date.today() - profile.date_of_birth).days // 365
        cfg = PENALTIES.get('age_hi')
        if cfg and age >= cfg['threshold']:
            cat = getattr(item, 'exerciseCategory', None) if is_ex else getattr(item, 'workoutCategory', None)
            if cat in cfg['cats']:
                sc -= cfg['delta']

    # --- Nivel cero cardio ---
    if is_ex and getattr(profile, 'cardio_vig_level', None) is not None:
        cfg = PENALTIES.get('cardio_zero')
        if cfg and profile.cardio_vig_level == cfg['cardio_vig_level']:
            cat = item.exerciseCategory
            cardio_goals = {'Mejora de la resistencia', 'Pérdida de peso', 'Mantenimiento de la salud', 'Mejorar la salud mental'}
            if cat in cfg['cats'] and not (user_goals & cardio_goals):
                sc -= cfg['delta']

    # --- IMC alto ---
    if is_ex and getattr(profile, 'height_cm', None) and getattr(profile, 'weight_kg', None):
        bmi = float(profile.weight_kg) / ((profile.height_cm/100)**2)
        if bmi >= 30:
            cfg = PENALTIES.get('bmi_obese')
            if cfg:
                cat = item.exerciseCategory
                cardio_weight_loss_goals = {'Pérdida de peso'}
                if cat in cfg['cats'] and not (user_goals & cardio_weight_loss_goals):
                    sc -= cfg['delta']

    # --- Condiciones médicas específicas ---
    # Por cada condition en profile.conditions, si existe en CONDITION_PENALTIES:
    for name in profile.get_conditions_list():
        name = name.lower()
        if name in CONDITION_PENALTIES:
            cfg = CONDITION_PENALTIES[name]
            delta = cfg.get('delta', 0)
            if is_ex:
                cat = getattr(item, 'exerciseCategory', None)
                if cat in cfg.get('exercise_cats', []):
                    sc -= delta
            else:
                cat = getattr(item, 'workoutCategory', None)
                if cat in cfg.get('workout_cats', []):
                    sc -= delta

    # --- Equipamiento disponible ---
    # Si es ejercicio y requiere equipamiento que el usuario no tiene, penalizar
    if is_ex:
        user_equip = {e.lower() for e in profile.get_equipment_list()}
        reqs = []
        if getattr(item, 'equipment', None):
            reqs = [s.strip().lower() for s in item.equipment.split(',') if s.strip()]
        if reqs:
            missing = [r for r in reqs if r not in user_equip]
            if missing:
                sc -= EQUIPMENT_PENALTY_DELTA

    # --- Entorno disponible ---
    if not is_ex:
        if hasattr(item, 'environment'):
            user_env = {e.lower() for e in profile.get_environment_list()}
            try:
                wk_envs = {e.name.lower() for e in item.environment.all()}
            except:
                wk_envs = set()
            if wk_envs and not (wk_envs & user_env):
                sc -= ENV_PENALTY_DELTA

    # --- Actividad importada (minutos semanales) ---
    # Ejemplo: si usuario ya hace mucho cardio vigoroso, penalizar más cardio
    if is_ex:
        cat = getattr(item, 'exerciseCategory', None)
        cfg = EXCESS_ACTIVITY_PENALTY.get('cardio_vig')
        if cfg and getattr(profile, 'imported_cardio_vig_min', None) is not None:
            if profile.imported_cardio_vig_min >= cfg['threshold_min']:
                if cat in cfg['exercise_cats']:
                    sc -= cfg['delta']
        cfg2 = EXCESS_ACTIVITY_PENALTY.get('cardio_mod')
        if cfg2 and getattr(profile, 'imported_cardio_mod_min', None) is not None:
            if profile.imported_cardio_mod_min >= cfg2['threshold_min']:
                if cat in cfg2['exercise_cats']:
                    sc -= cfg2['delta']
        # Podrías añadir lógica similar para neat_level o strength, si tuvieras imported_strength_min.
    else:
        # Para rutinas, se podría penalizar si imported_* min alto en la categoría correspondiente
        pass

    # --- Asegurar no negativo ---
    if sc < 0:
        sc = 0.0
    return sc

# --------------------------------------------------
# Construcción de interacciones alineadas con df_ex/df_wk
# --------------------------------------------------
def build_interactions_exercise(df_ex):
    """
    Construye matriz (n_users x n_items) para ejercicios, alineada a df_ex.
    Devuelve mat_ex (COO), user_mapping_ex (user_id->idx),
            item_mapping_ex_id2idx (exercise_id->idx), item_mapping_ex_idx2id.
    """
    ct = ContentType.objects.get_for_model(Exercise)
    records = []
    # Vistas
    qs_v = ViewLog.objects.filter(content_type=ct).values('user_id','object_id','timestamp')
    for rec in qs_v:
        records.append((rec['user_id'], rec['object_id'], rec['timestamp'], 1.0))
    # Favoritos
    qs_f = Favourite.objects.filter(exercise_id__isnull=False).values('user_id','exercise_id','date_added')
    for rec in qs_f:
        records.append((rec['user_id'], rec['exercise_id'], rec['date_added'], 5.0))
    # Comentarios
    qs_c = Comment.objects.filter(exercise_id__isnull=False).values('user_id','exercise_id','date_added')
    for rec in qs_c:
        records.append((rec['user_id'], rec['exercise_id'], rec['date_added'], 3.0))
    # Filtrar y decaimiento
    df_records = []
    set_eids = set(df_ex['id'])
    now = timezone.now()
    for uid, eid, ts, weight in records:
        if uid == 0 or eid not in set_eids:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=pytz.UTC)
        days = (now - ts).days
        w = weight * np.exp(-0.001 * max(days, 0))
        df_records.append((uid, eid, w))
    if not df_records:
        # Sin interacciones: matriz vacía
        user_mapping_ex = {}
        item_mapping_ex_id2idx = {eid: idx for idx, eid in enumerate(df_ex['id'])}
        item_mapping_ex_idx2id = {idx: eid for eid, idx in item_mapping_ex_id2idx.items()}
        mat = sp.coo_matrix((0, len(item_mapping_ex_id2idx)), shape=(0, len(item_mapping_ex_id2idx)))
        return mat, {}, item_mapping_ex_id2idx, item_mapping_ex_idx2id
    df_int = pd.DataFrame(df_records, columns=['user_id','exercise_id','w_dec'])
    user_ids = sorted(df_int['user_id'].unique())
    user_mapping_ex = {uid: idx for idx, uid in enumerate(user_ids)}
    item_mapping_ex_id2idx = {eid: idx for idx, eid in enumerate(df_ex['id'])}
    item_mapping_ex_idx2id = {idx: eid for eid, idx in item_mapping_ex_id2idx.items()}
    rows, cols, data = [], [], []
    for _, row in df_int.iterrows():
        uid, eid, w = row['user_id'], row['exercise_id'], row['w_dec']
        uidx = user_mapping_ex[uid]
        iidx = item_mapping_ex_id2idx[eid]
        rows.append(uidx); cols.append(iidx); data.append(w)
    mat = sp.coo_matrix((np.array(data, dtype=np.float32), (np.array(rows), np.array(cols))),
                        shape=(len(user_mapping_ex), len(item_mapping_ex_id2idx)))
    return mat, user_mapping_ex, item_mapping_ex_id2idx, item_mapping_ex_idx2id

def build_interactions_workout(df_wk):
    """
    Similar a build_interactions_exercise pero para Workout.
    """
    ct = ContentType.objects.get_for_model(Workout)
    records = []
    qs_v = ViewLog.objects.filter(content_type=ct).values('user_id','object_id','timestamp')
    for rec in qs_v:
        records.append((rec['user_id'], rec['object_id'], rec['timestamp'], 1.0))
    qs_f = Favourite.objects.filter(workout_id__isnull=False).values('user_id','workout_id','date_added')
    for rec in qs_f:
        records.append((rec['user_id'], rec['workout_id'], rec['date_added'], 5.0))
    qs_c = Comment.objects.filter(workout_id__isnull=False).values('user_id','workout_id','date_added')
    for rec in qs_c:
        records.append((rec['user_id'], rec['workout_id'], rec['date_added'], 3.0))
    df_records = []
    set_wids = set(df_wk['id'])
    now = timezone.now()
    for uid, wid, ts, weight in records:
        if uid == 0 or wid not in set_wids:
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=pytz.UTC)
        days = (now - ts).days
        w = weight * np.exp(-0.001 * max(days, 0))
        df_records.append((uid, wid, w))
    if not df_records:
        user_mapping_wk = {}
        item_mapping_wk_id2idx = {wid: idx for idx, wid in enumerate(df_wk['id'])}
        item_mapping_wk_idx2id = {idx: wid for wid, idx in item_mapping_wk_id2idx.items()}
        mat = sp.coo_matrix((0, len(item_mapping_wk_id2idx)), shape=(0, len(item_mapping_wk_id2idx)))
        return mat, {}, item_mapping_wk_id2idx, item_mapping_wk_idx2id
    df_int = pd.DataFrame(df_records, columns=['user_id','workout_id','w_dec'])
    user_ids = sorted(df_int['user_id'].unique())
    user_mapping_wk = {uid: idx for idx, uid in enumerate(user_ids)}
    item_mapping_wk_id2idx = {wid: idx for idx, wid in enumerate(df_wk['id'])}
    item_mapping_wk_idx2id = {idx: wid for wid, idx in item_mapping_wk_id2idx.items()}
    rows, cols, data = [], [], []
    for _, row in df_int.iterrows():
        uid, wid, w = row['user_id'], row['workout_id'], row['w_dec']
        uidx = user_mapping_wk[uid]
        iidx = item_mapping_wk_id2idx[wid]
        rows.append(uidx); cols.append(iidx); data.append(w)
    mat = sp.coo_matrix((np.array(data, dtype=np.float32), (np.array(rows), np.array(cols))),
                        shape=(len(user_mapping_wk), len(item_mapping_wk_id2idx)))
    return mat, user_mapping_wk, item_mapping_wk_id2idx, item_mapping_wk_idx2id

# --------------------------------------------------
# Variables globales a llenar en init_recommender
# --------------------------------------------------
# Para ejercicios:
#   df_ex, X_cb_ex, item_cb_norms_ex_global, pos_ex_in_df,
#   mat_ex, user_mapping_ex, item_mapping_ex_id2idx, item_mapping_ex_idx2id,
#   user_factors_ex_global, item_factors_ex_global
# Para rutinas:
#   df_wk, X_cb_wk, item_cb_norms_wk_global, pos_wk_in_df,
#   mat_wk, user_mapping_wk, item_mapping_wk_id2idx, item_mapping_wk_idx2id,
#   user_factors_wk_global, item_factors_wk_global

def init_recommender():
    """
    Inicializa matrices de contenido, entrena ALS y precomputa factores y normas.
    Llamar al arrancar la app o en manage.py shell antes de recomendar.
    """
    global df_ex, X_cb_ex, item_cb_norms_ex_global, pos_ex_in_df
    global mat_ex, user_mapping_ex, item_mapping_ex_id2idx, item_mapping_ex_idx2id, user_factors_ex_global, item_factors_ex_global

    global df_wk, X_cb_wk, item_cb_norms_wk_global, pos_wk_in_df
    global mat_wk, user_mapping_wk, item_mapping_wk_id2idx, item_mapping_wk_idx2id, user_factors_wk_global, item_factors_wk_global

    print("[DEBUG] Iniciando init_recommender()")
    # 1) Content-Based ejercicios
    df_ex, X_cb_ex = get_exercise_content_matrix()
    pos_ex_in_df = {eid: pos for pos, eid in enumerate(df_ex['id'])}
    globals()['pos_ex_in_df'] = pos_ex_in_df

    # 2) Content-Based rutinas (usa X_cb_ex y df_ex)
    df_wk, X_cb_wk = get_workout_content_matrix(X_cb_ex, df_ex)
    pos_wk_in_df = {wid: pos for pos, wid in enumerate(df_wk['id'])}
    globals()['pos_wk_in_df'] = pos_wk_in_df

    # 3) ALS para ejercicios
    mat_ex, user_mapping_ex, item_mapping_ex_id2idx, item_mapping_ex_idx2id = build_interactions_exercise(df_ex)
    globals()['mat_ex'] = mat_ex
    globals()['user_mapping_ex'] = user_mapping_ex
    globals()['item_mapping_ex_id2idx'] = item_mapping_ex_id2idx
    globals()['item_mapping_ex_idx2id'] = item_mapping_ex_idx2id
    if mat_ex.shape[0] > 0 and mat_ex.shape[1] > 0:
        als_ex = AlternatingLeastSquares(factors=50, regularization=0.01, iterations=20)
        als_ex.fit(mat_ex.T)
        user_factors_ex_global = als_ex.user_factors
        item_factors_ex_global = als_ex.item_factors
    else:
        user_factors_ex_global = np.zeros((0, 50))
        item_factors_ex_global = np.zeros((len(df_ex), 50))
    globals()['user_factors_ex_global'] = user_factors_ex_global
    globals()['item_factors_ex_global'] = item_factors_ex_global

    # 4) ALS para rutinas
    mat_wk, user_mapping_wk, item_mapping_wk_id2idx, item_mapping_wk_idx2id = build_interactions_workout(df_wk)
    globals()['mat_wk'] = mat_wk
    globals()['user_mapping_wk'] = user_mapping_wk
    globals()['item_mapping_wk_id2idx'] = item_mapping_wk_id2idx
    globals()['item_mapping_wk_idx2id'] = item_mapping_wk_idx2id
    if mat_wk.shape[0] > 0 and mat_wk.shape[1] > 0:
        als_wk = AlternatingLeastSquares(factors=30, regularization=0.01, iterations=15)
        als_wk.fit(mat_wk.T)
        user_factors_wk_global = als_wk.user_factors
        item_factors_wk_global = als_wk.item_factors
    else:
        user_factors_wk_global = np.zeros((0, 30))
        item_factors_wk_global = np.zeros((len(df_wk), 30))
    globals()['user_factors_wk_global'] = user_factors_wk_global
    globals()['item_factors_wk_global'] = item_factors_wk_global

    # 5) Precompute normas de content-based
    item_cb_norms_ex_global = np.sqrt(X_cb_ex.multiply(X_cb_ex).sum(axis=1)).A1
    item_cb_norms_wk_global = np.sqrt(X_cb_wk.multiply(X_cb_wk).sum(axis=1)).A1
    globals()['item_cb_norms_ex_global'] = item_cb_norms_ex_global
    globals()['item_cb_norms_wk_global'] = item_cb_norms_wk_global

    print("[DEBUG] init_recommender completado")

# --------------------------------------------------
# Funciones auxiliares para content-based
# --------------------------------------------------
def get_user_interactions_weights_ex(user_id):
    """
    Devuelve lista de (pos_en_df_ex, peso) para ejercicios del usuario, según ViewLog/Favourite/Comment con decaimiento.
    """
    now = timezone.now()
    records = []
    from django.contrib.contenttypes.models import ContentType
    ct = ContentType.objects.get_for_model(Exercise)
    # Vistas
    qs_v = ViewLog.objects.filter(content_type=ct, user_id=user_id).values('object_id','timestamp')
    for rec in qs_v:
        eid = rec['object_id']; ts = rec['timestamp']
        if eid in pos_ex_in_df:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=pytz.UTC)
            days = (now - ts).days
            w = 1.0 * np.exp(-0.001 * max(days,0))
            records.append((pos_ex_in_df[eid], w))
    # Favoritos
    qs_f = Favourite.objects.filter(exercise_id__isnull=False, user_id=user_id).values('exercise_id','date_added')
    for rec in qs_f:
        eid = rec['exercise_id']; ts = rec['date_added']
        if eid in pos_ex_in_df:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=pytz.UTC)
            days = (now - ts).days
            w = 5.0 * np.exp(-0.001 * max(days,0))
            records.append((pos_ex_in_df[eid], w))
    # Comentarios
    qs_c = Comment.objects.filter(exercise_id__isnull=False, user_id=user_id).values('exercise_id','date_added')
    for rec in qs_c:
        eid = rec['exercise_id']; ts = rec['date_added']
        if eid in pos_ex_in_df:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=pytz.UTC)
            days = (now - ts).days
            w = 3.0 * np.exp(-0.001 * max(days,0))
            records.append((pos_ex_in_df[eid], w))
    from collections import defaultdict
    agg = defaultdict(float)
    for pos, w in records:
        agg[pos] += w
    return list(agg.items())

def get_user_interactions_weights_wk(user_id):
    """
    Devuelve lista de (pos_en_df_wk, peso) para rutinas del usuario.
    """
    now = timezone.now()
    records = []
    from django.contrib.contenttypes.models import ContentType
    ct = ContentType.objects.get_for_model(Workout)
    # Vistas
    qs_v = ViewLog.objects.filter(content_type=ct, user_id=user_id).values('object_id','timestamp')
    for rec in qs_v:
        wid = rec['object_id']; ts = rec['timestamp']
        if wid in pos_wk_in_df:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=pytz.UTC)
            days = (now - ts).days
            w = 1.0 * np.exp(-0.001 * max(days,0))
            records.append((pos_wk_in_df[wid], w))
    # Favoritos
    qs_f = Favourite.objects.filter(workout_id__isnull=False, user_id=user_id).values('workout_id','date_added')
    for rec in qs_f:
        wid = rec['workout_id']; ts = rec['date_added']
        if wid in pos_wk_in_df:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=pytz.UTC)
            days = (now - ts).days
            w = 5.0 * np.exp(-0.001 * max(days,0))
            records.append((pos_wk_in_df[wid], w))
    # Comentarios
    qs_c = Comment.objects.filter(workout_id__isnull=False, user_id=user_id).values('workout_id','date_added')
    for rec in qs_c:
        wid = rec['workout_id']; ts = rec['date_added']
        if wid in pos_wk_in_df:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=pytz.UTC)
            days = (now - ts).days
            w = 3.0 * np.exp(-0.001 * max(days,0))
            records.append((pos_wk_in_df[wid], w))
    from collections import defaultdict
    agg = defaultdict(float)
    for pos, w in records:
        agg[pos] += w
    return list(agg.items())

# --------------------------------------------------
# Recomendaciones
# --------------------------------------------------
def recommend_exercises(user_id, top_n=10):
    cached = get_cached_recommendations(user_id, 'exercise', top_n)
    if cached is not None:
        return cached
    try:
        df_ex
    except NameError:
        from main.recommendations.recommender import init_recommender
        init_recommender()
    # Si usuario no en mapping de ALS-interacciones, devolvemos populares
    if user_id not in user_mapping_ex:
        top = df_ex.sort_values('likes_count', ascending=False).head(top_n)
        return top[['id','exerciseName']]

    # Cold-start check
    mapped = user_mapping_ex[user_id]
    if mapped >= mat_ex.shape[0]:
        count = 0
    else:
        count = mat_ex.tocsr()[mapped].getnnz()
    weights = WEIGHTS_COLD if count < COLD_THRESHOLD else WEIGHTS_DEFAULT

    # CF score alineado con catálogo completo
    n_items_ex = len(df_ex)
    score_cf = np.zeros(n_items_ex, dtype=np.float32)
    if mapped < user_factors_ex_global.shape[0]:
        uf = user_factors_ex_global[mapped]
        for als_idx, eid in item_mapping_ex_idx2id.items():
            pos = pos_ex_in_df.get(eid)
            if pos is not None:
                score_cf[pos] = item_factors_ex_global[als_idx].dot(uf)

    # Content-based personalizado
    uw = get_user_interactions_weights_ex(user_id)
    if not uw:
        score_cb = np.zeros(n_items_ex, dtype=np.float32)
    else:
        pos_list, ws = zip(*uw)
        Xsub = X_cb_ex[list(pos_list)]
        u_cb_feat = Xsub.T.dot(np.array(ws, dtype=np.float32))
        norm_u = np.linalg.norm(u_cb_feat)
        if norm_u > 0:
            raw = X_cb_ex.dot(u_cb_feat)
            score_cb = raw / (norm_u * (item_cb_norms_ex_global + 1e-8))
        else:
            score_cb = np.zeros(n_items_ex, dtype=np.float32)

    final = weights['als'] * score_cf + weights['content'] * score_cb

    # Aplicar penalizaciones avanzadas
    try:
        profile = HealthProfile.objects.get(user_id=user_id)
    except:
        profile = None
    scored = []
    for pos, sc in enumerate(final):
        if profile:
            ex_id = df_ex.iloc[pos]['id']
            try:
                item = Exercise.objects.get(id=ex_id)
            except Exercise.DoesNotExist:
                scored.append((pos, sc))
                continue
            sc2 = penalize(profile, item, sc, True)
        else:
            sc2 = sc
        scored.append((pos, sc2))
    scored.sort(key=lambda x: -x[1])
    top = scored[:top_n]
    ids = [df_ex.iloc[pos]['id'] for pos, _ in top]
    names = [df_ex.iloc[pos]['exerciseName'] for pos, _ in top]
    RecommendCache.objects.filter(user_id=user_id, item_type='exercise').delete()
    for pos, sc in top:
        RecommendCache.objects.create(
            user_id=user_id, item_type='exercise',
            item_id=df_ex.iloc[pos]['id'], score=sc
        )
    return pd.DataFrame({'id': ids, 'exerciseName': names})

def recommend_workouts(user_id, top_n=10):
    cached = get_cached_recommendations(user_id, 'workout', top_n)
    if cached is not None:
        return cached
    try:
        df_wk
    except NameError:
        from main.recommendations.recommender import init_recommender
        init_recommender()
    if user_id not in user_mapping_wk:
        top = df_wk.sort_values('likes_count', ascending=False).head(top_n)
        return top[['id','workoutName']]

    mapped = user_mapping_wk[user_id]
    if mapped >= mat_wk.shape[0]:
        count = 0
    else:
        count = mat_wk.tocsr()[mapped].getnnz()
    weights = WEIGHTS_COLD if count < COLD_THRESHOLD else WEIGHTS_DEFAULT

    # CF score
    n_items_wk = len(df_wk)
    score_cf = np.zeros(n_items_wk, dtype=np.float32)
    if mapped < user_factors_wk_global.shape[0]:
        uf = user_factors_wk_global[mapped]
        for als_idx, wid in item_mapping_wk_idx2id.items():
            pos = pos_wk_in_df.get(wid)
            if pos is not None:
                score_cf[pos] = item_factors_wk_global[als_idx].dot(uf)

    # Content-based personalizado
    uw = get_user_interactions_weights_wk(user_id)
    if not uw:
        score_cb = np.zeros(n_items_wk, dtype=np.float32)
    else:
        pos_list, ws = zip(*uw)
        Xsub = X_cb_wk[list(pos_list)]
        u_cb_feat = Xsub.T.dot(np.array(ws, dtype=np.float32))
        norm_u = np.linalg.norm(u_cb_feat)
        if norm_u > 0:
            raw = X_cb_wk.dot(u_cb_feat)
            score_cb = raw / (norm_u * (item_cb_norms_wk_global + 1e-8))
        else:
            score_cb = np.zeros(n_items_wk, dtype=np.float32)

    final = weights['als'] * score_cf + weights['content'] * score_cb

    # Penalizaciones avanzadas
    try:
        profile = HealthProfile.objects.get(user_id=user_id)
    except:
        profile = None
    scored = []
    for pos, sc in enumerate(final):
        if profile:
            wk_id = df_wk.iloc[pos]['id']
            try:
                item = Workout.objects.get(id=wk_id)
            except Workout.DoesNotExist:
                scored.append((pos, sc))
                continue
            sc2 = penalize(profile, item, sc, False)
        else:
            sc2 = sc
        scored.append((pos, sc2))
    scored.sort(key=lambda x: -x[1])
    top = scored[:top_n]
    ids = [df_wk.iloc[pos]['id'] for pos, _ in top]
    names = [df_wk.iloc[pos]['workoutName'] for pos, _ in top]
    RecommendCache.objects.filter(user_id=user_id, item_type='workout').delete()
    for pos, sc in top:
        RecommendCache.objects.create(
            user_id=user_id, item_type='workout',
            item_id=df_wk.iloc[pos]['id'], score=sc
        )
    return pd.DataFrame({'id': ids, 'workoutName': names})

# Uso:
#   from main.recommendations.recommender_extended import init_recommender, recommend_exercises, recommend_workouts
#   init_recommender()
#   df_rec = recommend_exercises(user_id=..., top_n=10)
#   df_rec_wk = recommend_workouts(user_id=..., top_n=10)
