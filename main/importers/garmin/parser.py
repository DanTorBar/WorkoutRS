import json
from datetime import datetime, timedelta
from collections import defaultdict
from io import TextIOWrapper

def parse_datetime(s):
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")

def parse_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

def start_of_week(dt):
    return dt - timedelta(days=dt.weekday())

def parse_garmin_export(zip_file):
    data = {}

    # 1. Datos del perfil
    profile_path = "DI_CONNECT/DI-Connect-User/xxx@gmail.com_0_userProfile.json"
    try:
        with zip_file.open(profile_path) as f:
            profile = json.load(f)
            data["name"] = profile.get("displayName")
            data["birth_date"] = profile.get("birthDate")
            data["height"] = profile.get("height")  # en cm
            data["weight"] = profile.get("weight")  # en kg
            data["gender"] = profile.get("gender")  # MALE/FEMALE
    except KeyError:
        print(f"[WARN] No se encontró el archivo de perfil: {profile_path}")

    # 2. Datos de actividad resumida
    activity_path = "DI_CONNECT/DI-Connect-Fitness/xxx@gmail.com_0_summarizedActivities.json"
    try:
        with zip_file.open(activity_path) as f:
            activities = json.load(f)
    except KeyError:
        print(f"[WARN] No se encontró el archivo de actividades: {activity_path}")
        activities = []

    # 3. Agregar métricas semanales por tipo de actividad
    weekly = defaultdict(lambda: defaultdict(float))  # {week_start: {tipo: minutos}}

    for act in activities:
        dt = parse_datetime(act["startTimeGmt"])
        week = start_of_week(dt)
        duration_min = parse_float(act.get("duration", 0)) / 60.0
        activity_type = act.get("activityType", "unknown").lower()

        if duration_min > 0:
            if "run" in activity_type:
                weekly[week]["vigorous"] += duration_min
            elif "walk" in activity_type or "hike" in activity_type:
                weekly[week]["neat"] += duration_min
            elif "bike" in activity_type or "cycling" in activity_type or "elliptical" in activity_type:
                weekly[week]["moderate"] += duration_min
            elif "strength" in activity_type or "functional" in activity_type or "weight" in activity_type:
                weekly[week]["strength"] += duration_min
            else:
                weekly[week]["neat"] += duration_min  # Consideramos el resto como NEAT por defecto

    # 4. Tomar promedio de las últimas 4 semanas (si hay suficientes)
    weeks = sorted(weekly.keys())[-4:]
    n = len(weeks) or 1

    def avg_minutes(key):
        return sum(weekly[w][key] for w in weeks) / n

    data["imported_neat_min"] = int(avg_minutes("neat"))
    data["imported_cardio_mod_min"] = int(avg_minutes("moderate"))
    data["imported_cardio_vig_min"] = int(avg_minutes("vigorous"))
    data["imported_strength_min"] = int(avg_minutes("strength"))

    return data
