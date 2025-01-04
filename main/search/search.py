import time
from tkinter import *
from tkinter import messagebox
import os, shutil, sys
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import query
from tkinter import messagebox
from whoosh import index

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WorkoutRS.settings')

import django
django.setup()

from main.models import Exercise, Workout
from main.scrapping.scrapping import extraer_rutinas_y_ejercicios

 
def almacenar_datos():

    esquema_rutina = Schema(
        nombre=TEXT(stored=True, phrase=True),
        categoria=KEYWORD(stored=True, commas=True, lowercase=True),
        nivel=KEYWORD(stored=True, commas=True, lowercase=True),
        genero=KEYWORD(stored=True, commas=True, lowercase=True),
        partes_cuerpo=KEYWORD(stored=True, commas=True, lowercase=True),
        descripcion=TEXT(stored=True, phrase=True),
        ejercicios1=STORED,
        ejercicios2=STORED,
        ejercicios3=STORED,
        ejercicios4=STORED,
        ejercicios5=STORED,
        ejercicios6=STORED,
        ejercicios7=STORED
    )

    esquema_ejercicio = Schema(
        id=ID(stored=True, unique=True),
        nombre=TEXT(stored=True, phrase=True),
        categoria=KEYWORD(stored=True, commas=True, lowercase=True),
        musculoPri=KEYWORD(stored=True, commas=True, lowercase=True),
        musculoSec=KEYWORD(stored=True, commas=True, lowercase=True),
        video=TEXT(stored=True, phrase=False),
        instrucciones=TEXT(stored=True, phrase=True),
        etiquetas=KEYWORD(stored=True, commas=True, lowercase=True)
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
            id=str(ejercicio.idExercise),  # Acceder al id del ejercicio
            nombre=str(ejercicio.exerciseName),
            categoria=str(ejercicio.exerciseCategory),
            musculoPri=[str(musculo.name) for musculo in ejercicio.priMuscles.all()],  # Obtener los músculos primarios
            musculoSec=[str(musculo.name) for musculo in ejercicio.secMuscles.all()],  # Obtener los músculos secundarios
            video=str(ejercicio.video) if ejercicio.video else '',  # Verificar si hay video
            instrucciones=str(ejercicio.instructions) if ejercicio.instructions else '',  # Verificar si hay instrucciones
            etiquetas=str(ejercicio.tags) if ejercicio.tags else ''  # Verificar si hay etiquetas
        )
        print(f"Se ha añadido el ejercicio {ejercicio.exerciseName} al índice")

    # Añadir rutinas al índice
    for rutina in lista_rutinas:
        writer_rutina.add_document(
            nombre=str(rutina.workoutName),
            categoria=str(rutina.workoutCategory),
            nivel=str(rutina.level),
            genero=str(rutina.gender),
            partes_cuerpo=str(rutina.bodyPart),
            descripcion=str(rutina.description) if rutina.description else '',  # Verificar si hay descripción
            ejercicios1=[str(ejercicio.idExercise) for ejercicio in rutina.day1.all()],
            ejercicios2=[str(ejercicio.idExercise) for ejercicio in rutina.day2.all()],
            ejercicios3=[str(ejercicio.idExercise) for ejercicio in rutina.day3.all()],
            ejercicios4=[str(ejercicio.idExercise) for ejercicio in rutina.day4.all()],
            ejercicios5=[str(ejercicio.idExercise) for ejercicio in rutina.day5.all()],
            ejercicios6=[str(ejercicio.idExercise) for ejercicio in rutina.day6.all()],
            ejercicios7=[str(ejercicio.idExercise) for ejercicio in rutina.day7.all()]
        )
        print(f"Se ha añadido la rutina {rutina.workoutName} al índice")
    # Commit writers
    writer_ejercicio.commit()
    writer_rutina.commit()

    messagebox.showinfo("Fin de indexado", f"Se han indexado los {len(lista_ejercicios)} ejercicios y {len(lista_rutinas)} rutinas")


def ej_buscar_nombre_decripcion():
    def mostrar_lista(event):
        ix=open_dir("IndexEjercicio")
        with ix.searcher() as searcher:
            query = MultifieldParser(["nombre","descripcion"], ix.schema).parse(f'"{en.get()}"')

            results = searcher.search(query, limit=10)
            listar_titulo_introduccion(results)
    
    v = Toplevel()
    v.title("Busqueda por Título o Introducción")
    l = Label(v, text="Introduzca las palabras a buscar:")
    l.pack(side=LEFT)
    en = Entry(v)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)
        

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
    almacenar_datos()
