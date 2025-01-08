from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def calcular_similitud(items, id_item, campos):
    """
    Calcula la similitud entre un ítem específico y el resto de los ítems.

    :param items: Lista de diccionarios con los datos de los ítems.
    :param id_item: ID del ítem base para las recomendaciones.
    :param campos: Lista de campos a usar para la comparación.
    :return: Lista de ítems similares ordenados por similitud.
    """
    # Crear una lista de textos combinando los valores de los campos seleccionados
    textos = [
        " ".join(str(item[campo]) for campo in campos if item.get(campo)) 
        for item in items
    ]

    # Vectorizar los textos
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(textos)

    # Calcular la matriz de similitud
    similitudes = cosine_similarity(X)

    # Encontrar el índice del ítem base
    idx_base = next(i for i, item in enumerate(items) if item["id"] == id_item)

    # Ordenar ítems por similitud con el ítem base
    similares = sorted(
        enumerate(similitudes[idx_base]),
        key=lambda x: x[1],
        reverse=True
    )

    # Excluir el ítem base y devolver los más similares
    recomendaciones = [
        items[i] for i, sim in similares if i != idx_base
    ]
    return recomendaciones
