''' recommender_final.py: Sistema híbrido para Workout-RS v3
Incluye:
 - LightFM con user_features de perfil de salud
 - Content-Based para ejercicios y rutinas
 - ALS CF para ejercicios y rutinas
 - Penalizaciones suaves basadas en HealthProfile adaptadas a categorías reales
 - Adaptación de cold-start para nuevos usuarios
 - Caché de recomendaciones en BBDD con TTL
'''

# --- SILENCIAR WARNINGS DE THREADING Y OPENBLAS ANTES DE IMPORTAR NUMPY, LIGHTFM, IMPLICIT ---
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
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

import pandas as pd
import numpy as np
import scipy.sparse as sp
from scipy.sparse import hstack, vstack, csr_matrix
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from implicit.als import AlternatingLeastSquares
from lightfm import LightFM
from lightfm.data import Dataset as LFDataset
import datetime
import pytz
import faulthandler; faulthandler.enable(all_threads=True)


# --------------------------------------------------
# 0. Configuración general
# --------------------------------------------------
WEIGHTS_DEFAULT = {'lightfm': 0.4, 'content': 0.3, 'als': 0.3}
WEIGHTS_COLD    = {'lightfm': 0.6, 'content': 0.4, 'als': 0.0}
COLD_THRESHOLD  = 5   # mín interacciones para no ser cold
CACHE_TTL_HOURS = 6   # caducidad de caché

# Penalizaciones adaptadas a tus categorías:
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

PENALTIES = {
    'age_hi': {
        'threshold': 75,
        'delta': 0.3,
        'cats': ['Cardio,Ejercicios/Pliamétricos','Cardio,Correr']
    },
    'cardio_zero': {
        'cardio_vig_level': 0,
        'delta': 0.2,
        'cats': CARDIO_CATS
    },
    'bmi_obese': {
        'bmi_cat': 'obese',
        'delta': 0.2,
        'cats': ['Cardio,Correr','Cardio,Deporte/Entrenamiento']
    },
    'strength_zero': {
        'strength_level': 0,
        'delta': 0.2,
        'cats': ['Solo entrenamiento de fuerza','Entrenamiento en circuito']
    }
}

# --------------------------------------------------
# 1. Content-Based Ejercicio & Rutina
# --------------------------------------------------
# A) Ejercicio

def get_exercise_content_matrix():
    ex_qs = Exercise.objects.prefetch_related('priMuscles','secMuscles')
    df_ex = read_frame(ex_qs, fieldnames=['id','exerciseName','exerciseCategory','equipment','likes_count'])
    # Texto, músculos y equipo
    X_text_ex = TfidfVectorizer(max_features=500,ngram_range=(1,2)).fit_transform(
        df_ex['exerciseName'] + ' ' + df_ex['exerciseCategory'].fillna('')
    )
    X_mus_ex = MultiLabelBinarizer(sparse_output=True).fit_transform(
        [[m.name for m in ex.priMuscles.all()]+[m.name for m in ex.secMuscles.all()] for ex in ex_qs]
    )
    X_eq_ex = MultiLabelBinarizer(sparse_output=True).fit_transform(
        df_ex['equipment'].fillna('').str.split(', ')
    )
    X_cb_ex = hstack([X_text_ex,X_mus_ex,X_eq_ex])
    sim_ex  = cosine_similarity(X_cb_ex,X_cb_ex)
    return df_ex, X_cb_ex, sim_ex

# B) Rutina

def get_workout_content_matrix():
    wk_qs = Workout.objects.all()
    df_wk = read_frame(wk_qs, fieldnames=['id','workoutName','workoutCategory','level','gender','bodyPart','likes_count'])
    X_text_wk = TfidfVectorizer(max_features=300,ngram_range=(1,1)).fit_transform(
        df_wk['workoutName'] + ' ' + df_wk['workoutCategory'].fillna('') + ' ' + df_wk['bodyPart'].fillna('')
    )
    X_lvl = MultiLabelBinarizer(sparse_output=True).fit_transform(df_wk['level'].fillna('').str.split(', '))
    X_gen = MultiLabelBinarizer(sparse_output=True).fit_transform(df_wk['gender'].fillna('').str.split(', '))
    # Agregar vectores de ejercicios por rutina
    df_ex, X_cb_ex, _ = get_exercise_content_matrix()
    agg = []
    for wk in wk_qs:
        ids = [we.exercise.id for we in WorkoutExercise.objects.filter(workout=wk)]
        idxs = [df_ex.index[df_ex['id'] == ex_id][0] for ex_id in ids if ex_id in set(df_ex['id'])]
        if idxs:
            submat = X_cb_ex[idxs]
            mean_vec = submat.sum(axis=0) / submat.shape[0]
            agg.append(csr_matrix(mean_vec))
        else:
            agg.append(csr_matrix((1, X_cb_ex.shape[1])))
    X_ex_agg = vstack(agg)
    X_cb_wk  = hstack([X_text_wk, X_lvl, X_gen, X_ex_agg])
    sim_wk   = cosine_similarity(X_cb_wk, X_cb_wk)
    return df_wk, X_cb_wk, sim_wk


# --------------------------------------------------
# 2. ALS Collaborative Filtering
# --------------------------------------------------
def build_interactions(model, field):
    """
    Construye la matriz usuario×ítem y devuelve también los mapeos de usuario e ítem.
    """
    # 1) ContentType para el modelo (Exercise o Workout)
    ct = ContentType.objects.get_for_model(model)

    # 2) Vistas
    qs_v = ViewLog.objects.filter(content_type=ct).values('user_id', 'object_id', 'timestamp')
    df_v = pd.DataFrame.from_records(qs_v).rename(columns={'object_id': field})
    df_v['weight'] = 1.0

    # 3) Favoritos
    fav_filter = {f'{field}__isnull': False}
    qs_f = Favourite.objects.filter(**fav_filter).values('user_id', field, 'date_added')
    df_f = pd.DataFrame.from_records(qs_f).rename(columns={'date_added': 'timestamp'})
    df_f['weight'] = 5.0

    # 4) Comentarios
    qs_c = Comment.objects.filter(**fav_filter).values('user_id', field, 'date_added')
    df_c = pd.DataFrame.from_records(qs_c).rename(columns={'date_added': 'timestamp'})
    df_c['weight'] = 3.0

    # 5) Unir y aplicar decaimiento
    df = pd.concat([df_v, df_f, df_c], ignore_index=True)
    # FILTRO RADICAL: eliminar user_id=0 en todos los pasos
    df = df[df['user_id'] != 0]
    now = timezone.now()
    df['timestamp'] = df['timestamp'].apply(lambda x: x.replace(tzinfo=pytz.UTC) if x.tzinfo is None else x)
    df['days'] = (now - df['timestamp']).dt.days.clip(lower=0)
    df['w_dec'] = df['weight'] * np.exp(-0.001 * df['days'])

    # 6) Mapear usuarios e ítems a índices consecutivos
    user_ids = [id_ for id_ in df['user_id'].unique() if id_ != 0]
    item_ids = df[field].unique()
    user_mapping = {id_: idx for idx, id_ in enumerate(user_ids)}
    # --- FIX: build both item_id->idx and idx->item_id mappings ---
    item_mapping_id2idx = {id_: idx for idx, id_ in enumerate(item_ids)}
    item_mapping_idx2id = {idx: id_ for idx, id_ in enumerate(item_ids)}

    df['user_idx'] = df['user_id'].map(user_mapping)
    df['item_idx'] = df[field].map(item_mapping_id2idx)

    n_users = len(user_mapping)
    n_items = len(item_mapping_id2idx)

    rows = df['user_idx'].values
    cols = df['item_idx'].values
    data = df['w_dec'].values

    mat = sp.coo_matrix((data, (rows, cols)), shape=(n_users, n_items))
    # Return both mappings for flexibility
    return mat, user_mapping, item_mapping_idx2id, item_mapping_id2idx

def build_all_interactions():
    # Unpack both mappings
    mat_ex, user_mapping_ex, item_mapping_ex_idx2id, item_mapping_ex_id2idx = build_interactions(Exercise, 'exercise_id')
    mat_wk, user_mapping_wk, item_mapping_wk_idx2id, item_mapping_wk_id2idx = build_interactions(Workout, 'workout_id')
    als_ex = AlternatingLeastSquares(factors=50, regularization=0.01, iterations=20)
    als_wk = AlternatingLeastSquares(factors=30, regularization=0.01, iterations=15)
    als_ex.fit(mat_ex.T)
    als_wk.fit(mat_wk.T)
    # Return both idx2id and id2idx for each
    return als_ex, als_wk, mat_ex, mat_wk, user_mapping_ex, user_mapping_wk, item_mapping_ex_idx2id, item_mapping_wk_idx2id, item_mapping_ex_id2idx, item_mapping_wk_id2idx

# --------------------------------------------------
# 3. LightFM con user_features de HealthProfile
# --------------------------------------------------
# Ajuste robusto para usuarios con interacciones reales

def build_lightfm_features(user_mapping, ex_ids, wk_ids):
    lf = LFDataset()
    from django.contrib.auth.models import User
    # Los usuarios de LightFM serán los índices 0..N-1
    num_users = len(user_mapping)
    user_indices = list(range(num_users))
    # Invertir el mapping para ir de idx a user_id
    idx_to_uid = {idx: uid for uid, idx in user_mapping.items()}
    # Construir features para cada idx en orden
    user_features_dict = {}
    all_user_features = set()
    profiles = HealthProfile.objects.filter(user_id__in=list(user_mapping.keys())).exclude(user_id=0)
    for prof in profiles:
        idx = user_mapping[prof.user_id]
        f=[]
        if prof.date_of_birth:
            age=(datetime.date.today()-prof.date_of_birth).days//365; f.append(f"age:{min(age//10*10,70)}")
        f.append(f"gender:{prof.gender}")
        if prof.height_cm and prof.weight_kg:
            bmi=float(prof.weight_kg)/(prof.height_cm/100)**2
            f.append(f"bmi:{int(bmi//5*5)}")
        all_user_features.update(f)
        user_features_dict[idx] = f
    # Para cada idx, poner sus features o [] si no hay datos
    ufs = [(idx, user_features_dict.get(idx, [])) for idx in user_indices]
    # Construir features de ítem (ejercicios y rutinas)
    item_features_ex = set()
    item_features_wk = set()
    from main.models.exercise import Exercise
    from main.models.workout import Workout
    ex_qs = Exercise.objects.filter(id__in=ex_ids)
    for ex in ex_qs:
        item_features_ex.add(f"cat:{ex.exerciseCategory}")
        item_features_ex.update([f"mus:{m.name}" for m in ex.priMuscles.all()])
    wk_qs = Workout.objects.filter(id__in=wk_ids)
    for wk in wk_qs:
        item_features_wk.add(f"cat:{wk.workoutCategory}")
        item_features_wk.add(f"lvl:{wk.level}")
        item_features_wk.add(f"bp:{wk.bodyPart}")
    all_item_features = list(item_features_ex | item_features_wk)
    all_user_features = list(all_user_features)
    print(f"[DEBUG] build_lightfm_features: fit users={user_indices}, items={ex_ids+wk_ids}, user_features={all_user_features}, item_features={all_item_features}")
    lf.fit(users=user_indices, items=ex_ids+wk_ids, user_features=all_user_features, item_features=all_item_features)
    print(f"[DEBUG] build_lightfm_features: ufs (primeros 10)={ufs[:10]}")
    return lf, user_indices, ex_ids, wk_ids, ufs

# item_features ejercicio y rutina
def get_item_features(ex_qs,wk_qs):
    ifs_ex = [(ex.id,[f"cat:{ex.exerciseCategory}"]+[f"mus:{m.name}" for m in ex.priMuscles.all()]) for ex in ex_qs]
    ifs_wk = [(wk.id,[f"cat:{wk.workoutCategory}",f"lvl:{wk.level}",f"bp:{wk.bodyPart}"]) for wk in wk_qs]
    return ifs_ex, ifs_wk

def train_lightfm_model(inter_ex, inter_wk, ufs, ifs_ex, ifs_wk):
    lf = LightFM(loss='warp',no_components=30,learning_rate=0.05)
    # LightFM
    (inter_ex,_) = lf.build_interactions([(u,e,1.0) for u,e,_ in inter_ex.nonzero()])
    (inter_wk,_) = lf.build_interactions([(u,w,1.0) for u,w,_ in inter_wk.nonzero()])
    uf = lf.build_user_features(ufs)
    ife_ex = lf.build_item_features(ifs_ex)
    ife_wk = lf.build_item_features(ifs_wk)
    model_lf = LightFM(loss='warp',no_components=30,learning_rate=0.05)
    model_lf.fit(inter_ex,user_features=uf,item_features=ife_ex,epochs=10)
    model_lf.fit(inter_wk,user_features=uf,item_features=ife_wk,epochs=10)
    return model_lf

# --------------------------------------------------
# 4. Penalización y pesos cold-start
# --------------------------------------------------

def get_weights(user_id):
    count = mat_ex.tocsr()[user_id].getnnz()
    return WEIGHTS_COLD if count < COLD_THRESHOLD else WEIGHTS_DEFAULT


def penalize(profile, item, score, is_ex):
    """
    Aplica penalizaciones suaves según HealthProfile,
    pero respeta objetivos del usuario evitando penalizar si coincide el objetivo.
    """
    # Recogemos los objetivos del usuario
    user_goals = {g.name for g in profile.goals.all()}

    # 1) Edad avanzada: no hacer ejercicios muy intensos de pliométricos o carrera
    if profile.date_of_birth:
        age = (datetime.date.today() - profile.date_of_birth).days // 365
        if age >= PENALTIES['age_hi']['threshold'] and \
           getattr(item, 'exerciseCategory', None) in PENALTIES['age_hi']['cats']:
            score -= PENALTIES['age_hi']['delta']

    # 2) Nivel cero de cardio vigoroso: penalizar ejercicios de cardio salvo si el usuario 
    # busca mejorar la resistencia
    if profile.cardio_vig_level == PENALTIES['cardio_zero']['cardio_vig_level'] and is_ex:
        cat = item.exerciseCategory
        cardio_goals = {'Mejora de la resistencia', 'Pérdida de peso', 'Mantenimiento de la salud',
                        'Mejorar la salud mental'}
        # penalizamos solo si no coincide con sus objetivos
        if cat in PENALTIES['cardio_zero']['cats'] and not (user_goals & cardio_goals):
            score -= PENALTIES['cardio_zero']['delta']

    # 3) IMC elevado: penalizar cardio intenso salvo objetivos de pérdida de peso
    if profile.height_cm and profile.weight_kg:
        bmi = float(profile.weight_kg) / ((profile.height_cm/100)**2)
        if bmi >= 30 and is_ex:
            cat = item.exerciseCategory
            cardio_weight_loss_goals = {'Pérdida de peso'}
            if cat in PENALTIES['bmi_obese']['cats'] and not (user_goals & cardio_weight_loss_goals):
                score -= PENALTIES['bmi_obese']['delta']

    # 4) Nivel cero de fuerza: penalizar rutinas de fuerza salvo si busca aumentar fuerza o ganancia muscular
    if not is_ex and profile.strength_level == PENALTIES['strength_zero']['strength_level']:
        cat = item.workoutCategory
        strength_goals = {'Aumentar la fuerza', 'Ganancia muscular', 'Preparación deportiva'}
        if cat in PENALTIES['strength_zero']['cats'] and not (user_goals & strength_goals):
            score -= PENALTIES['strength_zero']['delta']

    return max(score, 0)

def recommend_exercises(user_id, base_ex_id=None, top_n=10):
    """
    Recommends exercises for a user. Accepts top_n as the number of recommendations to return (default 10).
    The previous argument 'k' is replaced by 'top_n' for clarity and compatibility with test scripts.
    """
    k = top_n  # for backward compatibility with internal code
    print(f"[DEBUG] >>>>> recommend_exercises ENTRANDO: user_id={user_id} (type={type(user_id)})")
    print(f"[DEBUG] >>>>> recommend_exercises globals antes de entrar: {globals().keys()}")
    global mat_ex_global, als_ex, model_lf, uf, ife_ex, ex_ids, df_ex, sim_ex, ex_qs, user_mapping_global
    print(f"[DEBUG] recommend_exercises INICIO: user_id={user_id}, base_ex_id={base_ex_id}, top_n={top_n}")
    # ...existing code, replacing all 'k' with 'top_n' where it controls the number of results...
    if 'mat_ex_global' not in globals() or mat_ex_global is None or mat_ex_global.shape[0] == 0:
        print(f"[DEBUG] mat_ex_global no inicializada o vacía (en recommend_exercises). type={type(mat_ex_global)}, shape={getattr(mat_ex_global, 'shape', None)}")
        top = df_ex.sort_values('likes_count', ascending=False).head(top_n)
        print(f"[DEBUG] Top populares IDs: {list(top['id'])}")
        return top[['id','exerciseName']]
    cutoff = timezone.now() - datetime.timedelta(hours=CACHE_TTL_HOURS)
    cached = RecommendCache.objects.filter(user_id=user_id, item_type='exercise', recommended_at__gte=cutoff)
    if cached.exists():
        ids = [c.item_id for c in cached.order_by('-score')[:top_n]]
        print(f"[DEBUG] Recomendaciones en caché para user_id={user_id}: {ids}")
        return df_ex[df_ex['id'].isin(ids)][['id','exerciseName']]
    try:
        profile = HealthProfile.objects.get(user_id=user_id)
        print(f"[DEBUG] HealthProfile encontrado para user_id={user_id}")
    except Exception as e:
        print(f"[DEBUG] No se pudo obtener HealthProfile para user_id={user_id}: {e}. Devolviendo populares.")
        top = df_ex.sort_values('likes_count', ascending=False).head(top_n)
        return top[['id','exerciseName']]
    if user_id not in user_mapping_global:
        print(f"[DEBUG] user_id={user_id} NO está en user_mapping_global. Devolviendo populares.")
        top = df_ex.sort_values('likes_count', ascending=False).head(top_n)
        return top[['id','exerciseName']]
    mapped_uid = user_mapping_global[user_id]
    print(f"[DEBUG] user_id={user_id} está en mapping global con mapped_uid={mapped_uid}")
    w = get_weights(mapped_uid)
    print(f"[DEBUG] Pesos usados: {w}")
    cb = np.zeros(df_ex.shape[0])
    if base_ex_id:
        idx = df_ex.index[df_ex['id']==base_ex_id][0]; cb = sim_ex[idx]
        print(f"[DEBUG] base_ex_id={base_ex_id} encontrado, idx={idx}, sim_ex shape={sim_ex.shape}")
    cf = np.zeros(df_ex.shape[0])
    # ALS recommend: user_items debe ser una matriz de 1 fila (del usuario)
    try:
        user_items_row = mat_ex_global[mapped_uid]
        als_indices, als_scores = als_ex.recommend(userid=0, user_items=user_items_row, N=df_ex.shape[0])
        print(f"[DEBUG] ALS recommend raw output (first 10): {als_indices[:10]}, {als_scores[:10]}")
        for idx_in_matrix, sc in zip(als_indices, als_scores):
            try:
                # Map ALS index to exercise ID using item_mapping_ex
                if idx_in_matrix in item_mapping_ex:
                    ex_id = item_mapping_ex[idx_in_matrix]
                    # Ensure the exercise ID exists in df_ex
                    if ex_id in df_ex['id'].values:
                        idx = df_ex.index[df_ex['id'] == ex_id][0]
                        cf[idx] = sc
                    else:
                        print(f"[DEBUG] ALS mapped ex_id={ex_id} not found in df_ex")
                else:
                    print(f"[DEBUG] ALS idx_in_matrix={idx_in_matrix} not found in item_mapping_ex")
            except Exception as e:
                print(f"[DEBUG] Error assigning ALS score idx_in_matrix={idx_in_matrix}: {e}")
                continue
    except Exception as e:
        print(f"[ERROR] ALS recommend falló para user_id={user_id}: {e}")
        cf = np.zeros(df_ex.shape[0])
    # ...existing code continues...
    try:
        lf_sc = model_lf.predict(mapped_uid, np.arange(len(ex_ids)), user_features=uf, item_features=ife_ex)
        print(f"[DEBUG] LightFM predict ejecutado para mapped_uid={mapped_uid}")
    except Exception as e:
        print(f"[DEBUG] Error en LightFM predict: {e}")
        lf_sc = np.zeros(df_ex.shape[0])
    print(f"[DEBUG] ALS scores (first 10): {cf[:10]}")
    print(f"[DEBUG] LightFM scores (first 10): {lf_sc[:10]}")
    print(f"[DEBUG] Content-Based scores (first 10): {cb[:10]}")
    final = w['content']*cb + w['als']*cf + w['lightfm']*lf_sc
    print(f"[DEBUG] Final scores (first 10): {final[:10]}")
    for i, ex_id in enumerate(df_ex['id']):
        before = final[i]
        final[i] = penalize(profile, ex_qs.get(id=ex_id), final[i], True)
        if final[i] != before:
            print(f"[DEBUG] Penalización aplicada a ex_id={ex_id}: antes={before}, después={final[i]}")
    top = np.argsort(-final)[:top_n]
    print(f"[DEBUG] Top indices: {top}")
    print(f"[DEBUG] Top exercise IDs: {[df_ex.iloc[i]['id'] for i in top]}")
    results = df_ex.loc[top, ['id','exerciseName']]
    RecommendCache.objects.filter(user_id=user_id, item_type='exercise').delete()
    RecommendCache.objects.bulk_create([
        RecommendCache(user_id=user_id,item_type='exercise',item_id=r['id'],score=final[i])
        for i,r in enumerate(results.to_dict('records'))
    ])
    print(f"[DEBUG] recommend_exercises FIN para user_id={user_id}")
    return results

def recommend_workouts(user_id, base_wk_id=None, k=10):
    global mat_wk_global, als_wk, model_lf, uf, ife_wk, wk_ids, df_wk, sim_wk, wk_qs, user_mapping_global
    if 'mat_wk_global' not in globals() or mat_wk_global is None or mat_wk_global.shape[0] == 0:
        top = df_wk.sort_values('likes_count', ascending=False).head(k)
        return top[['id','workoutName']]
    cutoff = timezone.now() - datetime.timedelta(hours=CACHE_TTL_HOURS)
    cached = RecommendCache.objects.filter(user_id=user_id, item_type='workout', recommended_at__gte=cutoff)
    if cached.exists():
        ids = [c.item_id for c in cached.order_by('-score')[:k]]
        return df_wk[df_wk['id'].isin(ids)][['id','workoutName']]
    profile = HealthProfile.objects.get(user_id=user_id)
    if user_id not in user_mapping_global:
        top = df_wk.sort_values('likes_count', ascending=False).head(k)
        return top[['id','workoutName']]
    mapped_uid = user_mapping_global[user_id]
    w = get_weights(mapped_uid)
    cb = np.zeros(df_wk.shape[0])
    if base_wk_id:
        idx = df_wk.index[df_wk['id']==base_wk_id][0]; cb = sim_wk[idx]
    cf = np.zeros(df_wk.shape[0])
    for wid,sc in als_wk.recommend(mapped_uid, mat_wk_global.tocsr(), N=df_wk.shape[0]):
        try:
            cf[df_wk.index[df_wk['id']==wid][0]] = sc
        except Exception:
            continue
    lf_sc = model_lf.predict(mapped_uid, np.arange(len(wk_ids)), user_features=uf, item_features=ife_wk)
    final = w['content']*cb + w['als']*cf + w['lightfm']*lf_sc
    for i, wk_id in enumerate(df_wk['id']):
        final[i] = penalize(profile, wk_qs.get(id=wk_id), final[i], False)
    top = np.argsort(-final)[:k]
    results = df_wk.loc[top, ['id','workoutName']]
    RecommendCache.objects.filter(user_id=user_id, item_type='workout').delete()
    RecommendCache.objects.bulk_create([
        RecommendCache(user_id=user_id,item_type='workout',item_id=r['id'],score=final[i])
        for i,r in enumerate(results.to_dict('records'))
    ])
    return results

# --------------------------------------------------
# Inicialización global del sistema de recomendación
# --------------------------------------------------

def init_recommender():
    print("[DEBUG] >>>>> ENTRANDO EN init_recommender() <<<<<")
    import sys
    sys.stdout.flush()
    try:
        global df_ex, X_cb_ex, sim_ex, ex_qs, ex_ids
        global df_wk, X_cb_wk, sim_wk, wk_qs, wk_ids
        global als_ex, als_wk, mat_ex, mat_wk
        global model_lf, uf, ife_ex, ife_wk
        global user_mapping_global, item_mapping_ex, item_mapping_wk
        global mat_ex_global, mat_wk_global
        ex_qs = Exercise.objects.prefetch_related('priMuscles','secMuscles')
        df_ex, X_cb_ex, sim_ex = get_exercise_content_matrix()
        ex_ids = df_ex['id'].tolist()
        wk_qs = Workout.objects.all()
        df_wk, X_cb_wk, sim_wk = get_workout_content_matrix()
        wk_ids = df_wk['id'].tolist()
        print("[DEBUG] --- INICIALIZANDO ALS ---")
        sys.stdout.flush()
        global item_mapping_ex, item_mapping_wk, item_mapping_ex_id2idx, item_mapping_wk_id2idx
        als_ex, als_wk, mat_ex, mat_wk, user_mapping_ex, user_mapping_wk, item_mapping_ex_idx2id, item_mapping_wk_idx2id, item_mapping_ex_id2idx, item_mapping_wk_id2idx = build_all_interactions()
        item_mapping_ex = item_mapping_ex_idx2id
        item_mapping_wk = item_mapping_wk_idx2id
        # item_mapping_ex_id2idx and item_mapping_wk_id2idx are set by build_all_interactions
        print("[DEBUG] ALS inicializado correctamente.")
        sys.stdout.flush()
        user_ids_ex = set(uid for uid in user_mapping_ex.keys() if uid != 0)
        user_ids_wk = set(uid for uid in user_mapping_wk.keys() if uid != 0)
        user_ids_all = (user_ids_ex | user_ids_wk)
        from django.contrib.auth.models import User
        from main.models.users import HealthProfile
        existing_user_ids = set(User.objects.filter(id__in=user_ids_all).values_list('id', flat=True))
        profile_user_ids = set(HealthProfile.objects.filter(user_id__in=existing_user_ids).values_list('user_id', flat=True))
        valid_user_ids = [uid for uid in sorted(user_ids_all & existing_user_ids & profile_user_ids)
                          if (uid in user_mapping_ex or uid in user_mapping_wk) and uid != 0]
        user_mapping_global = {uid: idx for idx, uid in enumerate(valid_user_ids)}
        print(f"[DEBUG] Usuarios con interacciones (EX): {sorted(user_ids_ex)}")
        print(f"[DEBUG] Usuarios con interacciones (WK): {sorted(user_ids_wk)}")
        print(f"[DEBUG] Usuarios válidos en mapping global: {sorted(user_mapping_global.keys())}")
        def remap_matrix(mat, user_mapping_local, user_mapping_global):
            row_map = [user_mapping_global[uid] for uid in user_mapping_local.keys() if uid in user_mapping_global]
            if not row_map:
                return sp.coo_matrix((0, mat.shape[1]))
            mat = mat.tocsr()[row_map]
            return mat
        mat_ex_remap = remap_matrix(mat_ex, user_mapping_ex, user_mapping_global)
        mat_wk_remap = remap_matrix(mat_wk, user_mapping_wk, user_mapping_global)
        global mat_ex_global, mat_wk_global
        mat_ex_global = mat_ex_remap
        mat_wk_global = mat_wk_remap
        print(f"[DEBUG] mat_ex_global inicializada: type={type(mat_ex_global)}, shape={getattr(mat_ex_global, 'shape', None)}")
        print(f"[DEBUG] mat_wk_global inicializada: type={type(mat_wk_global)}, shape={getattr(mat_wk_global, 'shape', None)}")
        print(f"[DEBUG] user_mapping_global keys={list(user_mapping_global.keys())}")
        # --- INICIALIZANDO LIGHTFM ---
        print("[DEBUG] --- INICIALIZANDO LIGHTFM ---")
        sys.stdout.flush()
        lf_dataset, users, ex_ids_lf, wk_ids_lf, ufs = build_lightfm_features(user_mapping_global, ex_ids, wk_ids)
        ifs_ex, ifs_wk = get_item_features(ex_qs, wk_qs)
        uf = lf_dataset.build_user_features(ufs)
        ife_ex = lf_dataset.build_item_features(ifs_ex)
        ife_wk = lf_dataset.build_item_features(ifs_wk)
        # --- REDUCE LightFM COMPLEXITY FOR DEBUGGING ---
        model_lf = LightFM(loss='warp', no_components=8, learning_rate=0.03)
        # --- DEBUG: REDUCE DATA SIZE FOR LIGHTFM ---
        # Limit to first 50 users and 50 items for debugging OOM errors
        n_users = min(mat_ex_global.shape[0], 50)
        n_items = min(mat_ex_global.shape[1], 50)
        mat_ex_small = mat_ex_global[:n_users, :n_items]
        uf_small = uf[:n_users, :]
        ife_ex_small = ife_ex[:n_items, :]
        print(f"[DEBUG] LightFM debug: mat_ex_small.shape={mat_ex_small.shape}, uf_small.shape={uf_small.shape}, ife_ex_small.shape={ife_ex_small.shape}")
        sys.stdout.flush()
        print("1")
        try:
            if mat_ex_small.dtype != np.float32:
                mat_ex_small = mat_ex_small.astype(np.float32)
            if uf_small.dtype != np.float32:
                uf_small = uf_small.astype(np.float32)
            if ife_ex_small.dtype != np.float32:
                ife_ex_small = ife_ex_small.astype(np.float32)

            print(f"[CHECK] mat_ex_small.dtype={mat_ex_small.dtype}, uf_small.dtype={uf_small.dtype}, ife_ex_small.dtype={ife_ex_small.dtype}")

            model_lf.fit(mat_ex_small.tocoo(), user_features=uf_small, item_features=ife_ex_small, epochs=1, num_threads=1, verbose=False)
            print("[DEBUG] LightFM fit (small) completed successfully.")
            sys.stdout.flush()
        except Exception as e:
            print("3")
            print(f"[ERROR] LightFM fit (small) failed: {e}")
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
        # --- END DEBUG BLOCK ---

        # --- ORIGINAL FULL FIT (may OOM) ---
        print("[DEBUG] Antes de model_lf.fit(mat_ex_global)")
        sys.stdout.flush()
        try:
            model_lf.fit(mat_ex_global.tocoo(), user_features=uf, item_features=ife_ex, epochs=3)
            print("[DEBUG] Después de model_lf.fit(mat_ex_global)")
            sys.stdout.flush()
            model_lf.fit(mat_wk_global.tocoo(), user_features=uf, item_features=ife_wk, epochs=3)
            print("[DEBUG] Después de model_lf.fit(mat_wk_global)")
            sys.stdout.flush()
        except Exception as e:
            print(f"[ERROR] LightFM fit failed: {e}")
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
        print(f"[DEBUG] >>>>> SALIENDO DE init_recommender() <<<<<")
        sys.stdout.flush()
    except Exception as e:
        print(f"[DEBUG] Error en init_recommender: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        # NO raise, para que el script de test nunca termine abruptamente
        return

# Llamar a la inicialización al importar el módulo (opcional, o hacerlo desde un comando)
try:
    init_recommender()
except Exception as e:
    print(f"[WARN] No se pudo inicializar el recomendador: {e}")
    import traceback
    traceback.print_exc()


# Puedes implementar un comando manage.py para recálculo masivo offline:
# loop sobre usuarios activos, llama a recommend_* y almacena caché.

# Fin de recommender_final.py

# Instrucciones para probar el módulo:
# 1. Ejecuta 'python manage.py shell' y luego:
#    from main.recommendations import recommendations
#    recommendations.init_recommender()  # (si no se inicializó solo)
#    recommendations.recommend_exercises(user_id=1)
#    recommendations.recommend_workouts(user_id=1)
# 2. Crea un comando Django para recalcular recomendaciones masivas si lo necesitas.
# 3. Revisa la tabla RecommendCache para ver los resultados almacenados.

# --- VALIDACIÓN Y GUARDADO ROBUSTO DE MATRICES REALES PARA DEBUG ---
import numpy as np
import scipy.sparse as sp
def check_matrix(name, mat):
    try:
        print(f"[VALIDATE] {name}: type={type(mat)}, shape={getattr(mat, 'shape', None)}, dtype={getattr(mat, 'dtype', None)}")
        if mat is None:
            print(f"[VALIDATE] {name}: matriz es None")
            return
        if hasattr(mat, 'shape') and (mat.shape[0] == 0 or mat.shape[1] == 0):
            print(f"[VALIDATE] {name}: matriz vacía (alguna dimensión es 0)")
            return
        if sp.issparse(mat):
            arr = mat.data
        else:
            arr = np.asarray(mat)
        if arr.size == 0:
            print(f"[VALIDATE] {name}: matriz/data vacía")
            return
        print(f"[VALIDATE] {name}: min={arr.min()}, max={arr.max()}")
        print(f"[VALIDATE] {name}: has_nan={np.isnan(arr).any()}, has_inf={np.isinf(arr).any()}")
    except Exception as e:
        print(f"[VALIDATE][ERROR] {name}: {e}")
# Validar tras remap de matriz
check_matrix('mat_ex_global', mat_ex_global)
# Validar tras crear user features
check_matrix('uf', uf)
# Validar tras crear item features
check_matrix('ife_ex', ife_ex)
try:
    sp.save_npz('mat_ex_global_debug.npz', mat_ex_global)
    np.save('uf_debug.npy', uf)
    np.save('ife_ex_debug.npy', ife_ex)
    print('[VALIDATE] Matrices guardadas para test externo.')
except Exception as e:
    print(f"[VALIDATE][ERROR] al guardar matrices: {e}")
