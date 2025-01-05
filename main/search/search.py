import time
from tkinter import *
from tkinter import messagebox
import os, shutil, sys
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from whoosh import query
from tkinter import messagebox
from whoosh.analysis import KeywordAnalyzer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WorkoutRS.settings')

import django
django.setup()

from main.models import Exercise, Workout
from main.scrapping.scrapping import extraer_rutinas_y_ejercicios

 
def almacenar_datos():

    esquema_rutina = Schema(
        workoutName=TEXT(stored=True, phrase=True),
        workoutCategory=TEXT(analyzer=KeywordAnalyzer(), stored=True),
        level=KEYWORD(stored=True, commas=True, lowercase=True),
        gender=KEYWORD(stored=True, commas=True, lowercase=True),
        bodyPart=TEXT(analyzer=KeywordAnalyzer(), stored=True),
        description=TEXT(stored=True, phrase=True),
        day1=STORED,
        day2=STORED,
        day3=STORED,
        day4=STORED,
        day5=STORED,
        day6=STORED,
        day7=STORED
    )

    esquema_ejercicio = Schema(
        idExercise=ID(stored=True, unique=True),
        exerciseName=TEXT(stored=True, phrase=True),
        exerciseCategory=TEXT(analyzer=KeywordAnalyzer(), stored=True),
        priMuscles=TEXT(analyzer=KeywordAnalyzer(), stored=True),
        secMuscles=TEXT(analyzer=KeywordAnalyzer(), stored=True),
        video=TEXT(stored=True, phrase=False),
        instructions=TEXT(stored=True, phrase=True),
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

    # Añadir ejercicios al índice
    for ejercicio in lista_ejercicios:
        writer_ejercicio.add_document(
            idExercise=str(ejercicio.idExercise),  # Acceder al id del ejercicio
            exerciseName=str(ejercicio.exerciseName),
            exerciseCategory=str(ejercicio.exerciseCategory),
            priMuscles=",".join([str(musculo.name) for musculo in ejercicio.priMuscles.all()]),
            secMuscles=",".join([str(musculo.name) for musculo in ejercicio.secMuscles.all()]),
            video=str(ejercicio.video) if ejercicio.video else '',  # Verificar si hay video
            instructions=str(ejercicio.instructions) if ejercicio.instructions else '',  # Verificar si hay instrucciones
        )
        print(f"Se ha añadido el ejercicio {ejercicio.exerciseName} al índice")

    # Añadir rutinas al índice
    for rutina in lista_rutinas:
        writer_rutina.add_document(
            workoutName=str(rutina.workoutName),
            workoutCategory=str(rutina.workoutCategory),
            level=str(rutina.level),
            gender=str(rutina.gender),
            bodyPart=str(rutina.bodyPart),
            description=str(rutina.description) if rutina.description else '',  # Verificar si hay descripción
            day1=[str(ejercicio.idExercise) for ejercicio in rutina.day1.all()],
            day2=[str(ejercicio.idExercise) for ejercicio in rutina.day2.all()],
            day3=[str(ejercicio.idExercise) for ejercicio in rutina.day3.all()],
            day4=[str(ejercicio.idExercise) for ejercicio in rutina.day4.all()],
            day5=[str(ejercicio.idExercise) for ejercicio in rutina.day5.all()],
            day6=[str(ejercicio.idExercise) for ejercicio in rutina.day6.all()],
            day7=[str(ejercicio.idExercise) for ejercicio in rutina.day7.all()]
        )
        print(f"Se ha añadido la rutina {rutina.workoutName} al índice")
    # Commit writers
    writer_ejercicio.commit()
    writer_rutina.commit()
    
    mensaje = f"Se han añadido {len(lista_ejercicios)} ejercicios y {len(lista_rutinas)} rutinas a los índices"
    
    return mensaje


def ej_buscar_nombre_instrucciones(cadena):
    try:
        ix = open_dir("IndexEjercicio")
    except IndexError:
        return []  # Devuelve una lista vacía si no se puede abrir el índice

    with ix.searcher() as searcher:
        query = MultifieldParser(["exerciseName", "instructions"], ix.schema).parse(f'"{cadena}"')
        results = searcher.search(query, limit=100)
        result_list = [dict(result) for result in results]
        
    return result_list


def ej_buscar(name, cat, muscle):
    try:
        ix = open_dir("IndexEjercicio")
    except Exception as e:
        print(f"Error opening index: {e}")
        return []

    with ix.searcher() as searcher:
        fields = ["exerciseName", "exerciseCategory", "priMuscles", "secMuscles"]
        parser = MultifieldParser(fields, schema=ix.schema, group=OrGroup)

        # Construye la consulta de forma dinámica
        query_parts = []
        if name:
            query_parts.append(f'(exerciseName:"{name}" OR exerciseName:*"{name}"*)')
        if cat:
            query_parts.append(f'(exerciseCategory:"{cat}" OR exerciseCategory:*"{cat}"*)')
        if muscle:
            query_parts.append(f'((priMuscles:*"{muscle}"* OR secMuscles:"{muscle}") OR (priMuscles:"{muscle}" OR secMuscles:"{muscle}"))')

        # Combina las partes de la consulta
        if query_parts:
            query_string = " AND ".join(query_parts)
        else:
            query_string = "*:*"  # Devuelve todos los documentos si no hay términos de búsqueda

        try:
            query = parser.parse(query_string)
            results = searcher.search(query, limit=100)
            result_list = [dict(result) for result in results]
            return result_list
        except Exception as e:
            print(f"Error parsing query: {e}")
            return []


def ru_buscar(name, cat, level, gender):
    try:
        ix = open_dir("IndexRutina")
    except Exception as e:
        print(f"Error opening index: {e}")
        return []

    with ix.searcher() as searcher:
        fields = ["workoutName", "workoutCategory", "level", "gender"]
        parser = MultifieldParser(fields, schema=ix.schema, group=OrGroup)

        # Construye la consulta de forma dinámica
        query_parts = []
        if name:
            query_parts.append(f'(workoutName:"{name}"* OR workoutName:"{name}")')
        if cat:
            query_parts.append(f'(workoutCategory:"{cat}" OR workoutCategory:*"{cat}"*)')
        if level:
            query_parts.append(f'level:{level}')
        if gender:
            query_parts.append(f'gender:{gender}')

        # Combina las partes de la consulta
        if query_parts:
            query_string = " AND ".join(query_parts)
        else:
            query_string = "*:*"  # Devuelve todos los documentos si no hay términos de búsqueda

        try:
            query = parser.parse(query_string)
            print(f"Constructed query: {query}")
            results = searcher.search(query, limit=100)
            result_list = [dict(result) for result in results]
            print(f"Search results: {len(result_list)}")
            return result_list
        except Exception as e:
            print(f"Error parsing query: {e}")
            return []
    
def ru_buscar_nombre_descripcion(cadena):
    try:
        ix = open_dir("IndexRutina")
    except IndexError:
        return []

    with ix.searcher() as searcher:
        query = MultifieldParser(["workoutName", "description"], ix.schema).parse(f'"{cadena}"*')
        results = searcher.search(query, limit=100)
        result_list = [dict(result) for result in results]
        
    return result_list

    
def buscar_caracteristicas_titulo():
    def mostrar_lista(event):
        ix=open_dir("Index")      
        with ix.searcher() as searcher:
            lista_caracteristicas = [i.decode('utf-8') for i in searcher.lexicon('caracteristicas')]
            entrada = str(en.get().lower())
            if entrada not in lista_caracteristicas:
                messagebox.showinfo("Error", "El criterio de búsqueda no es una característica existente\nLas características existentes son: " + ",".join(lista_caracteristicas))
                return
            query = QueryParser("titulo", ix.schema).parse('caracteristicas:'+ entrada +' '+str(en1.get()))
            print('caracteristicas:'+ entrada +' '+str(en1.get()))
            print(query)
            results = searcher.search(query, limit=10)
            listar_rutinas(results)
    
    v = Toplevel()
    v.title("Busqueda por Características y título")
    l = Label(v, text="Introduzca característica a buscar:")
    l.pack(side=LEFT)

    
    ix=open_dir("Index")      
    with ix.searcher() as searcher:
        lista_caracteristicas = [i.decode('utf-8') for i in searcher.lexicon('caracteristicas')]
    
    en = Spinbox(v, values=lista_caracteristicas, state="readonly")
    en.pack(side=LEFT)

    l1 = Label(v, text="Introduzca Título")
    l1.pack(side=LEFT)
    en1 = Entry(v)
    en1.pack(side=LEFT)

    en1.bind("<Return>", mostrar_lista)


def listar_titulo_introduccion(results):      
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in results:
        s = 'TÍTULO: ' + row['titulo']
        lb.insert(END, s)       
        s = "INTRODUCCIÓN: " + row['introduccion']
        lb.insert(END, s)
        lb.insert(END,"------------------------------------------------------------------------\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

    
def ventana_principal():
        
    def listar_rutinas():
        ix=open_dir("IndexRutina")
        with ix.searcher() as searcher:
            results = searcher.search(query.Every(),limit=None)
            listado_rutinas(results) 

    def listar_ejercicios():
        ix=open_dir("IndexEjercicio")
        with ix.searcher() as searcher:
            results = searcher.search(query.Every(),limit=None)
            listado_rutinas(results) 

    
    root = Tk()
    menubar = Menu(root)
    
    datosmenu = Menu(menubar, tearoff=0)
    datosmenu.add_command(label="Cargar", command=cargar)
    datosmenu.add_command(label="Listar rutinas", command=listar_rutinas)
    datosmenu.add_command(label="Listar ejercicios", command=listar_ejercicios)

    datosmenu.add_separator()   

    datosmenu.add_command(label="Salir", command=root.quit)
    
    menubar.add_cascade(label="Datos", menu=datosmenu)
    
    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Título o Introducción", command=buscar_titulo_introduccion)
    buscarmenu.add_command(label="Características y Título", command=buscar_caracteristicas_titulo)

    menubar.add_cascade(label="Buscar", menu=buscarmenu)
        
    root.config(menu=menubar)
    root.mainloop()

    

if __name__ == "__main__":
    # ru_buscar(name="Single", cat="Thighs", level="aaa", bodyPart="bbb", gender="male")
    ej_buscar(name="", cat="Running", muscle="")
    # almacenar_datos()
