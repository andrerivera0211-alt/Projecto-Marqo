"""Carga / indexación de documentos en Marqo."""
import marqo
from config import MARQO_URL, INDEX_NAME


def get_client() -> marqo.Client:
    return marqo.Client(url=MARQO_URL)


def crear_indice(client: marqo.Client, index_name: str = INDEX_NAME):
    try:
        client.create_index(index_name)
        print(f"Índice '{index_name}' creado correctamente.")
    except Exception as e:
        print(f"El índice ya podría existir o ocurrió un error: {e}")


def indexar_documentos(client: marqo.Client, documentos: list, index_name: str = INDEX_NAME):
    resultado = client.index(index_name).add_documents(documentos, tensor_fields=["texto"])
    return resultado


if __name__ == "__main__":
    client = get_client()
    crear_indice(client)

    documentos_ejemplo = [
        {"_id": "1", "texto": "Marqo es un motor de búsqueda vectorial."},
        {"_id": "2", "texto": "HNSW es un algoritmo de búsqueda aproximada de vecinos."},
    ]
    resultado = indexar_documentos(client, documentos_ejemplo)
    print(resultado)
