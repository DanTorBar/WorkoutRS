import os
import sys
import traceback

# Añadir el directorio raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Configurar Django antes de importar cualquier módulo que lo use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WorkoutRS.settings')
try:
    import django
    django.setup()
except Exception as e:
    print("[ERROR] No se pudo configurar Django:", e)
    traceback.print_exc()
    sys.exit(1)

print("[TEST] Iniciando test robusto de recomendador...")
sys.stdout.flush()

try:
    from backend.main.recommendations import recommendations_old
    # Borrar la caché de recomendaciones antes de cada test
    from main.models.recommendations import RecommendCache
except Exception as e:
    print("[ERROR] No se pudo importar recommendations o RecommendCache:", e)
    traceback.print_exc()
    sys.exit(1)

try:
    print("[TEST] Llamando a init_recommender()...")
    sys.stdout.flush()
    recommendations_old.init_recommender()
    print("[TEST] init_recommender() completado.")
    sys.stdout.flush()
except Exception as e:
    print("[ERROR] Fallo en init_recommender:", e)
    traceback.print_exc()
    sys.exit(2)

# --- SIEMPRE PROBAR ESTOS IDS, AUNQUE EL MAPPING ESTÉ VACÍO ---
forced_user_ids = [1, 3, 609, 610, 9999]

# Obtener user_ids del mapping si existen
user_ids = []
try:
    if hasattr(recommendations_old, 'user_id_mapping'):
        user_ids = list(recommendations_old.user_id_mapping.keys())
    elif hasattr(recommendations_old, 'user_ids'):
        user_ids = list(recommendations_old.user_ids)
    print(f"[TEST] user_ids detectados: {user_ids[:10]} ... (total: {len(user_ids)})")
    sys.stdout.flush()
except Exception as e:
    print("[WARN] No se pudo obtener user_ids:", e)
    sys.stdout.flush()

# Unir ambos (sin duplicados)
user_ids = list(dict.fromkeys(user_ids + forced_user_ids))

print(f"[TEST] user_ids a probar: {user_ids}")
sys.stdout.flush()

if not user_ids:
    print("[ERROR] No hay ningún user_id para probar. El test NO se ejecutará.")
    sys.exit(3)

print("[TEST] INICIO del bucle de recomendaciones")
sys.stdout.flush()

try:
    for idx, uid in enumerate(user_ids):
        print(f"\n==============================\n[TEST] ({idx+1}/{len(user_ids)}) Recomendando ejercicios para user_id={uid} (type={type(uid)})...")
        sys.stdout.flush()
        try:
            uid_int = int(uid)
            # Borrar caché para este usuario antes de recomendar
            RecommendCache.objects.filter(user_id=uid_int, item_type='exercise').delete()
            print(f"[DEBUG] Caché de recomendaciones borrada para user_id={uid_int}")
            print(f"[DEBUG] Antes de recommend_exercises({uid_int}, top_n=5) (type={type(uid_int)})")
            sys.stdout.flush()
            recs = recommendations_old.recommend_exercises(uid_int, top_n=5)
            print(f"[DEBUG] Después de recommend_exercises({uid_int}), resultado: {recs}")
            sys.stdout.flush()
            if recs is None or len(recs) == 0:
                print(f"[WARN] No se obtuvieron recomendaciones para user_id={uid_int}.")
            else:
                print(f"[OK] Recomendaciones para user_id={uid_int}: {recs}")
            sys.stdout.flush()
        except Exception as e:
            print(f"[ERROR] Fallo recomendando para user_id={uid}:", e)
            traceback.print_exc()
            sys.stdout.flush()
except Exception as e:
    print("[FATAL] Excepción inesperada en el bucle de recomendaciones:", e)
    traceback.print_exc()
    sys.stdout.flush()

print("[TEST] FIN del bucle de recomendaciones")
print("[TEST] Script finalizado.")
sys.stdout.flush()
