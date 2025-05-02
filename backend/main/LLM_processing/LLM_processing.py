import mariadb
from transformers import pipeline
import torch

equipment_options = [
    "Casa", "Gimnasio", "AireLibre", "Mancuernas", "Barras", "Máquinas",
    "BandasElásticas", "Kettlebell", "TRX", "Banco", "Esterilla",
    "CuerdaSaltadora", "BalónMedicinal"
]

# Cargamos el pipeline para completar textos
generator = pipeline('text2text-generation', model='t5-small')

def generar_equipamiento(nombre, instrucciones):
    prompt = f"Ejercicio: {nombre}\nInstrucciones: {instrucciones}\n\n¿De qué equipos se necesita para realizar este ejercicio? Devuelve los equipos necesarios."
    result = generator(prompt, max_length=50)
    print(f"Prompt: {prompt}")
    print(f"Resultado: {result}")
    return result[0]['generated_text']

# Conexión a la base de datos MariaDB
conn = mariadb.connect(
    user="usuario", 
    password="1234", 
    host="localhost", 
    port=3306, 
    database="workoutrs_db"
)
cursor = conn.cursor()

# Obtener ejercicios que no tienen equipamiento asignado
cursor.execute("SELECT id, exerciseName, instructions FROM main_exercise WHERE equipment IS NULL OR equipment = ''")
ejercicios = cursor.fetchall()

# Actualizar cada ejercicio con el equipamiento necesario
for eid, nombre, instrucciones in ejercicios:
    try:
        equipamiento = generar_equipamiento(nombre, instrucciones)
        print(f"{nombre} → {equipamiento}")
        cursor.execute(
            "UPDATE main_exercise SET equipment = ? WHERE id = ?",
            (equipamiento, eid)
        )
    except Exception as e:
        print(f"Error con ejercicio {eid}: {e}")

# Confirmar los cambios en la base de datos
conn.commit()
conn.close()