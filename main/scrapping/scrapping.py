# encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
import re, os, ssl, sys, django
import requests
import socket
from datetime import datetime

from main.models.exercise import Exercise, Muscle
from main.models.workout import Workout, WorkoutExercise

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WorkoutRS.settings")

import django

django.setup()

from django.contrib.auth.models import User
from main.LLM_processing.translator_module import translate_text

# lineas para evitar error SSL
if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
    ssl, "_create_unverified_context", None
):
    ssl._create_default_https_context = ssl._create_unverified_context


def store_exercise(
    id_, exerciseName, exerciseCategory, priMuscles, secMuscles, video, instructions
):
    exerciseName_es = translate_text(exerciseName)
    exerciseCategory_es = translate_text(exerciseCategory)
    instructions_es = translate_text(instructions)
    
    print(exerciseName_es)

    primary_muscles = [
        Muscle.objects.get_or_create(name=translate_text(muscle))[0] for muscle in priMuscles.split(",")
    ]
    secondary_muscles = [
        Muscle.objects.get_or_create(name=translate_text(muscle))[0] for muscle in secMuscles.split(",")
    ]

    exercise, created = Exercise.objects.get_or_create(
        id=id_,
        defaults={
            "exerciseName": exerciseName_es,
            "exerciseCategory": exerciseCategory_es,
            "video": video,
            "instructions": instructions_es,
            "likes_count": 0,
        },
    )
    if created:
        print(exercise.__dict__)
        exercise.priMuscles.set(primary_muscles)
        exercise.secMuscles.set(secondary_muscles)
        exercise.save()

    #     print(f"Ejercicio '{exerciseName}' creado.")
    # else:
    #     print(f"Ejercicio '{exerciseName}' ya existía.")


def store_workout(
    workoutName, workoutCategory, level, gender, bodyPart, description, days
):
    workoutName_es = translate_text(workoutName)
    workoutCategory_es = translate_text(workoutCategory)
    level_es = translate_text(level)
    gender_es = translate_text(gender)
    description_es = translate_text(description)

    workout, _ = Workout.objects.get_or_create(
        workoutName=workoutName_es,
        defaults={
            "workoutCategory": workoutCategory_es,
            "level": level_es,
            "gender": gender_es,
            "description": description_es,
            "bodyPart": bodyPart,
            "creator_id": User.objects.get(username="admin").id,
            "creationDate": datetime.now(),
            "likes_count": 0,            
        },
    )

    workout.creator_id = User.objects.get(username="admin").id

    for day, exercises in enumerate(days, start=1):
        for exercise_id in exercises:
            exercise = Exercise.objects.get(id=exercise_id)
            WorkoutExercise.objects.get_or_create(
                workout=workout, exercise=exercise, day=day
            )

    workout.save()
    print(f"Rutina '{workoutName}' almacenada.")
    print(workout.__dict__)
    # print("Día 1: ", workout.dia_1.all())
    # print("Día 2: ", workout.dia_2.all())
    # print("Día 3: ", workout.dia_3.all())
    # print("Día 4: ", workout.dia_4.all())
    # print("Día 5: ", workout.dia_5.all())
    # print("Día 6: ", workout.dia_6.all())
    # print("Día 7: ", workout.dia_7.all())
    print("---------------------")


def extraer_rutinas_y_ejercicios():
    import locale  # para activar las fechas en formato español

    locale.setlocale(locale.LC_TIME, "es_ES")

    id_exercises = set()  # Conjunto para almacenar los IDs de los ejercicios

    url = "https://www.fitclick.com/workout_plans"

    headers = {
        "Host": "www.fitclick.com",
        "Cookie": "_ga=GA1.2.589040901.1735386370; _gid=GA1.2.89931548.1735386370; __eoi=ID=9a5a5c78ad0fe67a:T=1735386397:RT=1735386397:S=AA-AfjYEJhhoaAL6B_GDISCIAc49; _gat=1",
        "Content-Length": "247838",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Accept-Language": "es-ES,es;q=0.9",
        "Origin": "https://www.fitclick.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.fitclick.com/workout_plans",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=0, i",
    }
    with open("main/scrapping/data/request_body.txt", "r") as file:
        body = file.read()

    try:
        # Realizar la solicitud POST
        response = requests.post(url, headers=headers, data=body, timeout=50)
        # response.raise_for_status()  # Esto lanzará una excepción si la solicitud no fue exitosa

        # PRUEBA
        with open("main/scrapping/data/request.html", "r") as file:
            respuesta = file.read()
        
        # Comprobar si la solicitud fue exitosa
        if response.status_code == 200 or respuesta:
            s = BeautifulSoup(respuesta, "lxml")
            l = s.find("table", class_="MainLeftContentColWidth").find_all_next(
                "td", attrs={"valign": "bottom"}
            )
            l = l[:-1]
            i = 0
            
            print("Cantidad de rutinas a procesar: ", len(l))

            workout_l = []
            exercise_l = []

            for r in l:
                i += 1
                link = r.find_next("td", attrs={"valign": "bottom"}).find_next("a")[
                    "href"
                ]

                try:
                    req = urllib.request.Request(
                        "https://www.fitclick.com" + link,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36"
                        },
                    )

                    # Intentar abrir la URL con un reintento en caso de timeout
                    try:
                        f = urllib.request.urlopen(req, timeout=10)
                    except urllib.error.URLError as e:
                        if isinstance(e.reason, socket.timeout):
                            print(
                                f"Timeout al procesar el enlace {link}, reintentando..."
                            )
                            f = urllib.request.urlopen(req, timeout=10)
                        else:
                            raise

                    s = BeautifulSoup(f, "lxml")

                    workoutName = (
                        s.find("div", class_="pageTitle")
                        .find_next("h1")
                        .strong.string.strip()
                    )

                    if s.find(
                        "div",
                        class_="CustomWorkoutDetailsLabel",
                        string=re.compile("Workout Category:"),
                    ):
                        workoutCategory = (
                            s.find(
                                "div",
                                class_="CustomWorkoutDetailsLabel",
                                string=re.compile("Workout Category:"),
                            )
                            .parent.find_next("div", class_="CustomWorkoutDetailsData")
                            .span.string.strip()
                        )
                    else:
                        workoutCategory = "N/A"

                    if s.find(
                        "div",
                        class_="CustomWorkoutDetailsLabel",
                        string=re.compile("Experience Level:"),
                    ):
                        level = (
                            s.find(
                                "div",
                                class_="CustomWorkoutDetailsLabel",
                                string=re.compile("Experience Level:"),
                            )
                            .parent.find_next("div", class_="CustomWorkoutDetailsData")
                            .string.strip()
                        )
                    else:
                        level = "N/A"

                    if s.find(
                        "div",
                        class_="CustomWorkoutDetailsLabel",
                        string=re.compile("Target Gender:"),
                    ):
                        gender = (
                            s.find(
                                "div",
                                class_="CustomWorkoutDetailsLabel",
                                string=re.compile("Target Gender:"),
                            )
                            .parent.find_next("div", class_="CustomWorkoutDetailsData")
                            .string.strip()
                        )
                    else:
                        gender = "N/A"

                    if s.find(
                        "div",
                        class_="CustomWorkoutDetailsLabel",
                        string=re.compile("Body Parts:"),
                    ):
                        bodyPart = (
                            s.find(
                                "div",
                                class_="CustomWorkoutDetailsLabel",
                                string=re.compile("Body Parts:"),
                            )
                            .parent.find_next("div", class_="CustomWorkoutDetailsData")
                            .string.strip()
                        )
                        bodyPart = ",".join([translate_text(p.strip()) for p in bodyPart.split(",")])
                    else:
                        bodyPart = "N/A"

                    if s.find("div", class_="CustomWorkoutDescriptionContent CmsHtml"):
                        if s.find(
                            "div", class_="CustomWorkoutDescriptionContent CmsHtml"
                        ).string:
                            description = s.find("div", class_="CustomWorkoutDescriptionContent CmsHtml").decode_contents().strip()
                    else:
                        description = "N/A"

                    exercises_workout = [[] for _ in range(7)]

                    days = s.find_all("div", class_="CustomDay")

                    for day in days:
                        numday = int(
                            day.find("div", class_="DayNum")
                            .a["name"]
                            .replace("day", "")
                            .strip()
                        )

                        if day.find_next("div", class_="divStrength"):
                            ejsFuerza = day.find_next(
                                "div", class_="divStrength"
                            ).find_all("td", class_="Ex_Name")
                        else:
                            ejsFuerza = []

                        if day.find_next("div", class_="divCardio"):
                            ejsCardio = day.find_next(
                                "div", class_="divCardio"
                            ).find_all("td", class_="Cdo_Name")
                        else:
                            ejsCardio = []

                        listaEjs = ejsFuerza + ejsCardio

                        for ej in listaEjs:
                            if ej.find("a"):
                                link = ej.find("a")["href"]
                                try:
                                    req = urllib.request.Request(
                                        "https://www.fitclick.com" + link,
                                        headers={
                                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36"
                                        },
                                    )

                                    # Intentar abrir la URL con un reintento en caso de timeout
                                    try:
                                        f = urllib.request.urlopen(req, timeout=10)
                                    except urllib.error.URLError as e:
                                        if isinstance(e.reason, socket.timeout):
                                            print(
                                                f"Timeout al procesar el enlace {link}, reintentando..."
                                            )
                                            f = urllib.request.urlopen(req, timeout=10)
                                        else:
                                            raise

                                    s = BeautifulSoup(f, "lxml")

                                    match = re.search(r"eqID=(\d+)", link)
                                    if match:
                                        id_ = match.group(1)

                                    exerciseName = (
                                        s.find("div", class_="pageTitle")
                                        .find_next("h1")
                                        .string.strip()
                                    )

                                    exerciseCategory = "N/A"

                                    if s.find("div", class_="MiscTextSmall"):
                                        info = s.select(
                                            'div[style="float:left;width:550px;"] a'
                                        )
                                        if info:
                                            exerciseCategories = []
                                            for link in info:
                                                exerciseCategories.append(
                                                    link.text.strip()
                                                )
                                            exerciseCategory = ",".join(
                                                exerciseCategories
                                            )

                                    if s.find(
                                        "span",
                                        string=re.compile("Primary Muscles Trained:"),
                                    ):
                                        priMuscles = (
                                            s.find(
                                                "span",
                                                string=re.compile(
                                                    "Primary Muscles Trained:"
                                                ),
                                            )
                                            .parent.find_next("a")
                                            .text.strip()
                                        )
                                    else:
                                        priMuscles = "N/A"

                                    if s.find(
                                        "span",
                                        string=re.compile("Secondary Muscles Trained:"),
                                    ):
                                        secMuscles = (
                                            s.find(
                                                "span",
                                                string=re.compile(
                                                    "Secondary Muscles Trained:"
                                                ),
                                            )
                                            .parent.find_next("a")
                                            .text.strip()
                                        )
                                    else:
                                        secMuscles = "N/A"

                                    embed = s.find("embed")
                                    if embed:
                                        video = embed["src"]

                                    if s.find(
                                        "div",
                                        class_="hLower",
                                        string=re.compile("Instructions:"),
                                    ):
                                        instructions = (
                                            s.find(
                                                "div",
                                                class_="hLower",
                                                string=re.compile("Instructions:"),
                                            )
                                            .parent.find_next("div", class_="CmsHtml")
                                            .get_text(separator="\n")
                                            .strip()
                                        )
                                    else:
                                        instructions = "N/A"

                                    if id_ not in id_exercises:
                                        store_exercise(
                                            id_,
                                            exerciseName,
                                            exerciseCategory,
                                            priMuscles,
                                            secMuscles,
                                            video,
                                            instructions,
                                        )
                                        exercise_l.append(
                                            (
                                                id_,
                                                exerciseName,
                                                exerciseCategory,
                                                priMuscles,
                                                secMuscles,
                                                video,
                                                instructions,
                                            )
                                        )
                                        id_exercises.add(id_)

                                    exercises_workout[numday - 1].append(id_)

                                except Exception as e:
                                    print(f"Error al procesar el enlace {link}: {e}")

                    workout_l.append(
                        (
                            workoutName,
                            workoutCategory,
                            level,
                            gender,
                            bodyPart,
                            description,
                            exercises_workout[0],
                            exercises_workout[1],
                            exercises_workout[2],
                            exercises_workout[3],
                            exercises_workout[4],
                            exercises_workout[5],
                            exercises_workout[6],
                        )
                    )
                    store_workout(
                        workoutName,
                        workoutCategory,
                        level,
                        gender,
                        bodyPart,
                        description,
                        exercises_workout,
                    )
                    print(
                        "Se han cargado "
                        + str(i)
                        + " rutinas de un total de "
                        + str(len(l))
                    )

                except Exception as e:
                    print(f"Error al procesar la rutina {link}: {e}")

        else:
            print(f"Error: {response.status_code}")

    except requests.RequestException as e:
        print(f"Error en la solicitud POST: {e}")

    print("Datos de rutinas y ejercicios almacenados en la base de datos.")


if __name__ == "__main__":
    extraer_rutinas_y_ejercicios()
