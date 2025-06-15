import numpy as np
from scipy.sparse import coo_matrix
from lightfm import LightFM

print("[TEST] Iniciando test mínimo de LightFM...")
users, items = 10, 10
X = coo_matrix(np.random.randint(0, 2, size=(users, items)))
model = LightFM(no_components=2)
try:
    model.fit(X, epochs=1)
    print("[SUCCESS] LightFM minimal fit successful.")
except Exception as e:
    print(f"[ERROR] LightFM minimal fit failed: {e}")
    import traceback
    traceback.print_exc()

print("[TEST] LightFM escalado: probando tamaños crecientes...")
for size in [10, 25, 50, 100, 200, 4000]:
    print(f"\n[TEST] Probando matriz de tamaño {size}x{size}...")
    X = coo_matrix(np.random.randint(0, 2, size=(size, size)))
    model = LightFM(no_components=2)
    try:
        model.fit(X, epochs=1)
        print(f"[SUCCESS] LightFM fit OK para tamaño {size}x{size}")
    except Exception as e:
        print(f"[ERROR] LightFM fit falló para tamaño {size}x{size}: {e}")
        import traceback
        traceback.print_exc()
        break
print("\n[TEST] Finalizado test escalado LightFM.")
