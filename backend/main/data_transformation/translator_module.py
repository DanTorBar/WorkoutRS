import requests
from dotenv import load_dotenv
import os
import deepl

load_dotenv()

api_key = os.getenv("DEEPL_API_KEY")
deepl_client = deepl.DeepLClient(api_key)

def manual_translate(term):
    translations = {
        "Thighs": "Muslos",
        "Chest": "Pecho",
        "Forearms": "Antebrazos",
        "Trapezius": "Trapecios",
        "Back": "Espalda",
        "Abdominals": "Abdominales",
        "Triceps": "Tríceps",
        "Calves": "Gemelos",
        "Biceps": "Bíceps",
        "Lower Back": "Zona lumbar",
        "Shoulders": "Hombros",
        "Walking": "Caminar",
        "Fitness Machines": "Máquinas de fitness",
        "Running": "Correr",
        "Cycling": "Ciclismo",
        "Drills/Plyometrics": "Ejercicios/Pliometría",
        "Aerobics/Dancing": "Aeróbicos/Baile",
        "Yoga/Pilates": "Yoga/Pilates",
        "Sports/Cross Training": "Deportes/Entrenamiento cruzado",
        "Workout Programs/Videos": "Programas de entrenamiento/Vídeos",
        "Rehabilitation Exercises": "Ejercicios de rehabilitación",
        "Cardio": "Cardio",
        "Anterior Deltoids": "Deltoides anteriores",
        "Biceps Femoris (Hamstrings)": "Bíceps femoral (isquiotibiales)",
        "Brachialis": "Braquial anterior",
        "Deltoids": "Deltoides",
        "Forearm Extensors": "Extensores del antebrazo",
        "Forearm Flexors": "Flexores del antebrazo",
        "Gastrocnemius": "Gemelos (Gastrocnemio)",
        "Gluteus Maximus": "Glúteo mayor",
        "Inner Quadriceps": "Cuádriceps internos",
        "Intercostals": "Intercostales",
        "Latissimus Dorsi": "Dorsales",
        "Lower Pectorals": "Pectorales inferiores",
        "Lower Rectus Abdominis": "Abdomen inferior",
        "Medial Deltoids": "Deltoides medios",
        "N/A": "N/A",
        "Obliques": "Oblicuos",
        "Outer Quadriceps": "Cuádriceps externos",
        "Pectorals": "Pectorales",
        "Quadriceps": "Cuádriceps",
        "Rear Deltoids": "Deltoides posteriores",
        "Rectus Abdominis": "Recto abdominal",
        "Soleus": "Sóleo",
        "Spinal Erectors": "Erectores espinales",
        "Upper Pectorals": "Pectorales superiores",
        "Upper Rectus Abdominis": "Abdomen superior",
        "Yoga": "Yoga",
        "Strength & Cardio Combined": "Fuerza y cardio combinados",
        "Cardio Training Only": "Solo entrenamiento de cardio",
        "Pilates": "Pilates",
        "Strength Training Only": "Solo entrenamiento de fuerza",
        "Running & Race Training": "Entrenamiento de carrera y competición",
        "Toning": "Tonificación",
        "Circuit Training": "Entrenamiento en circuito",
        "Stretching": "Estiramientos",
        "Beginner": "Principiante",
        "Advanced": "Avanzado",
        "Intermediate": "Intermedio",
        "Both": "Ambos",
        "Men": "Hombres",
        "Women": "Mujeres",
        "Total Body Cardio": "Cardio de cuerpo completo",
        "Abs": "Abdominales"
    }

    return translations.get(term.strip(), None)


def translate_text(text, target_lang="ES"):
    # Primero intenta la traducción manual
    manual = manual_translate(text)
    if manual:
        return manual

    try:
        response = deepl_client.translate_text(
            text,
            target_lang=target_lang,
            source_lang="EN",
        )
        return response.text

    except deepl.exceptions.DeepLException as e:
        print(f"Error al traducir '{text}': {e}")
        return text