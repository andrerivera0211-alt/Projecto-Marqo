"""Funciones de búsqueda/consulta sobre el índice de Marqo."""
from config import INDEX_NAME
from ingest import get_client


def buscar(consulta: str, index_name: str = INDEX_NAME, limite: int = 5):
    client = get_client()
    resultados = client.index(index_name).search(q=consulta, limit=limite)
    return resultados


if __name__ == "__main__":
    resultados = buscar("algoritmo de búsqueda de vecinos cercanos")
    for hit in resultados.get("hits", []):
        print(hit)
