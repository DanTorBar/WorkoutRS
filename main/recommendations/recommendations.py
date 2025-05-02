''' recommender_final.py: Sistema híbrido para Workout-RS v3
Incluye:
 - LightFM con user_features de perfil de salud
 - Content-Based para ejercicios y rutinas
 - ALS CF para ejercicios y rutinas
 - Penalizaciones suaves basadas en HealthProfile adaptadas a categorías reales
 - Adaptación de cold-start para nuevos usuarios
 - Caché de recomendaciones en BBDD con TTL
'''

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

# B) Rutina
wk_qs = Workout.objects.all()
df_wk = read_frame(wk_qs, fieldnames=['id','workoutName','workoutCategory','level','gender','bodyPart','likes_count'])
X_text_wk = TfidfVectorizer(max_features=300,ngram_range=(1,1)).fit_transform(
    df_wk['workoutName'] + ' ' + df_wk['workoutCategory'].fillna('') + ' ' + df_wk['bodyPart'].fillna('')
)
X_lvl = MultiLabelBinarizer(sparse_output=True).fit_transform(df_wk['level'].fillna('').str.split(', '))
X_gen = MultiLabelBinarizer(sparse_output=True).fit_transform(df_wk['gender'].fillna('').str.split(', '))
# Agregar vectores de ejercicios por rutina
agg = []
for wk in wk_qs:
    # ids de los ejercicios en la rutina
    ids = [we.exercise.id for we in WorkoutExercise.objects.filter(workout=wk)]
    # índices en df_ex
    idxs = [df_ex.index[df_ex['id'] == ex_id][0] for ex_id in ids if ex_id in set(df_ex['id'])]
    if idxs:
        submat = X_cb_ex[idxs]               # sparse shape (n_items, F)
        mean_vec = submat.sum(axis=0) / submat.shape[0]  # numpy.matrix (1, F)
        agg.append(csr_matrix(mean_vec))     # convierto a csr_matrix 1×F
    else:
        # rutina sin ejercicios, vector cero
        agg.append(csr_matrix((1, X_cb_ex.shape[1])))

# Apilo todas las rutinas en una sola matriz
X_ex_agg = vstack(agg)             # ahora sí son todas 2D sparse
X_cb_wk  = hstack([X_text_wk, X_lvl, X_gen, X_ex_agg])
sim_wk   = cosine_similarity(X_cb_wk, X_cb_wk)


# --------------------------------------------------
# 2. ALS Collaborative Filtering
# --------------------------------------------------
def build_interactions(model, field):
    """
    Construye la matriz usuario×ítem reemplazando django_pandas.read_frame
    por pandas.DataFrame.from_records y mapeando IDs a índices.
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
    now = timezone.now()
    df['timestamp'] = df['timestamp'].apply(lambda x: x.replace(tzinfo=pytz.UTC) if x.tzinfo is None else x)
    df['days'] = (now - df['timestamp']).dt.days.clip(lower=0)
    df['w_dec'] = df['weight'] * np.exp(-0.001 * df['days'])

    # 6) Mapear usuarios e ítems a índices consecutivos
    user_mapping = {id_: idx for idx, id_ in enumerate(df['user_id'].unique())}
    item_mapping = {id_: idx for idx, id_ in enumerate(df[field].unique())}

    df['user_idx'] = df['user_id'].map(user_mapping)
    df['item_idx'] = df[field].map(item_mapping)

    n_users = len(user_mapping)
    n_items = len(item_mapping)

    rows = df['user_idx'].values
    cols = df['item_idx'].values
    data = df['w_dec'].values

    return sp.coo_matrix((data, (rows, cols)), shape=(n_users, n_items))

mat_ex = build_interactions(Exercise,'exercise_id')
mat_wk = build_interactions(Workout, 'workout_id')
als_ex = AlternatingLeastSquares(factors=50,regularization=0.01,iterations=20)
als_wk = AlternatingLeastSquares(factors=30,regularization=0.01,iterations=15)
als_ex.fit(mat_ex.T); als_wk.fit(mat_wk.T)

# --------------------------------------------------
# 3. LightFM con user_features de HealthProfile
# --------------------------------------------------
lf    = LFDataset()
users = [p.user_id for p in HealthProfile.objects.all()]
ex_ids= df_ex['id'].tolist(); wk_ids = df_wk['id'].tolist()
# user_features
ufs = []
for prof in HealthProfile.objects.all():
    f=[]
    if prof.date_of_birth:
        age=(datetime.date.today()-prof.date_of_birth).days//365; f.append(f"age:{min(age//10*10,70)}")
    f.append(f"gender:{prof.gender}")
    if prof.height_cm and prof.weight_kg:
        bmi=float(prof.weight_kg)/(prof.height_cm/100)**2
        cat='normal' if bmi<25 else 'overweight' if bmi<30 else 'obese'
        f.append(f"bmi:{cat}")
    f += [f"neat:{prof.neat_level}",f"cardio_mod:{prof.cardio_mod_level}",f"cardio_vig:{prof.cardio_vig_level}",f"strength:{prof.strength_level}"]
    f += [f"goal:{g.name}" for g in prof.goals.all()]+[f"cond:{c.name}" for c in prof.conditions.all()]
    f += [f"equip:{e.name}" for e in prof.equipment.all()]
    if prof.environment: f.append(f"env:{prof.environment}")
    ufs.append((prof.user_id,f))
# item_features ejercicio y rutina
ifs_ex = [(ex.id,[f"cat:{ex.exerciseCategory}"]+[f"mus:{m.name}" for m in ex.priMuscles.all()]) for ex in ex_qs]
ifs_wk = [(wk.id,[f"cat:{wk.workoutCategory}",f"lvl:{wk.level}",f"bp:{wk.bodyPart}"]) for wk in wk_qs]
lf.fit(users,ex_ids+wk_ids, user_features=set(f for _,fl in ufs for f in fl), item_features=set(f for _,fl in ifs_ex+ifs_wk for f in fl))
(inter_ex,_) = lf.build_interactions([(u,e,1.0) for u,e,_ in mat_ex.nonzero()])
(inter_wk,_) = lf.build_interactions([(u,w,1.0) for u,w,_ in mat_wk.nonzero()])
uf = lf.build_user_features(ufs)
ife_ex = lf.build_item_features(ifs_ex)
ife_wk = lf.build_item_features(ifs_wk)
model_lf = LightFM(loss='warp',no_components=30,learning_rate=0.05)
model_lf.fit(inter_ex,user_features=uf,item_features=ife_ex,epochs=10)
model_lf.fit(inter_wk,user_features=uf,item_features=ife_wk,epochs=10)

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

    # 2) Nivel cero de cardio vigoroso: penalizar ejercicios de cardio salvo si el usuario busca mejorar la resistencia
    if profile.cardio_vig_level == PENALTIES['cardio_zero']['cardio_vig_level'] and is_ex:
        cat = item.exerciseCategory
        cardio_goals = {'Mejora de la resistencia', 'Pérdida de peso', 'Mantenimiento de la salud', 'Mejorar la salud mental'}
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

def recommend_exercises(user_id, base_ex_id=None, k=10):
    # comprobar caché válida
    cutoff = timezone.now() - datetime.timedelta(hours=CACHE_TTL_HOURS)
    cached = RecommendCache.objects.filter(user_id=user_id, item_type='exercise', recommended_at__gte=cutoff)
    if cached.exists():
        ids = [c.item_id for c in cached.order_by('-score')[:k]]
        return df_ex[df_ex['id'].isin(ids)][['id','exerciseName']]

    profile = HealthProfile.objects.get(user_id=user_id)
    w       = get_weights(user_id)
    # Content-Based
    cb = np.zeros(df_ex.shape[0])
    if base_ex_id:
        idx = df_ex.index[df_ex['id']==base_ex_id][0]; cb = sim_ex[idx]
    # ALS CF
    cf = np.zeros(df_ex.shape[0])
    for eid,sc in als_ex.recommend(user_id, mat_ex.tocsr(), N=df_ex.shape[0]):
        cf[df_ex.index[df_ex['id']==eid][0]] = sc
    # LightFM
    lf_sc = model_lf.predict(user_id, np.arange(len(ex_ids)), user_features=uf, item_features=ife_ex)
    # combinar scores\    final = w['content']*cb + w['als']*cf + w['lightfm']*lf_sc
    # penalizar
    for i, ex_id in enumerate(df_ex['id']):
        final[i] = penalize(profile, ex_qs.get(id=ex_id), final[i], True)
    # top-k
    top = np.argsort(-final)[:k]
    results = df_ex.loc[top, ['id','exerciseName']]
    # actualizar caché
    RecommendCache.objects.filter(user_id=user_id, item_type='exercise').delete()
    RecommendCache.objects.bulk_create([
        RecommendCache(user_id=user_id,item_type='exercise',item_id=r['id'],score=final.iloc[i])
        for i,r in enumerate(results.to_dict('records'))
    ])
    return results


def recommend_workouts(user_id, base_wk_id=None, k=10):
    cutoff = timezone.now() - datetime.timedelta(hours=CACHE_TTL_HOURS)
    cached = RecommendCache.objects.filter(user_id=user_id, item_type='workout', recommended_at__gte=cutoff)
    if cached.exists():
        ids = [c.item_id for c in cached.order_by('-score')[:k]]
        return df_wk[df_wk['id'].isin(ids)][['id','workoutName']]

    profile = HealthProfile.objects.get(user_id=user_id)
    w       = get_weights(user_id)
    # CB
    cb = np.zeros(df_wk.shape[0])
    if base_wk_id:
        idx = df_wk.index[df_wk['id']==base_wk_id][0]; cb = sim_wk[idx]
    # ALS CF
    cf = np.zeros(df_wk.shape[0])
    for wid,sc in als_wk.recommend(user_id, mat_wk.tocsr(), N=df_wk.shape[0]):
        cf[df_wk.index[df_wk['id']==wid][0]] = sc
    # LF
    lf_sc = model_lf.predict(user_id, np.arange(len(wk_ids)), user_features=uf, item_features=ife_wk)
    # combinar\    final = w['content']*cb + w['als']*cf + w['lightfm']*lf_sc
    # penalizar rutinass
    for i, wk_id in enumerate(df_wk['id']):
        final[i] = penalize(profile, wk_qs.get(id=wk_id), final[i], False)
    top = np.argsort(-final)[:k]
    results = df_wk.loc[top, ['id','workoutName']]
    # caché
    RecommendCache.objects.filter(user_id=user_id, item_type='workout').delete()
    RecommendCache.objects.bulk_create([
        RecommendCache(user_id=user_id,item_type='workout',item_id=r['id'],score=final.iloc[i])
        for i,r in enumerate(results.to_dict('records'))
    ])
    return results

# Puedes implementar un comando manage.py para recálculo masivo offline:
# loop sobre usuarios activos, llama a recommend_* y almacena caché.

# Fin de recommender_final.py
