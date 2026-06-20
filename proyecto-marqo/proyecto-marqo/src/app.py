import marqo
from marqo.errors import MarqoWebError
import logging

# Silencia las advertencias visuales de discrepancia de versiones en la consola
logging.getLogger("marqo").setLevel(logging.ERROR)

def conectar_marqo(url: str, api_key: str) -> marqo.Client:
    print(f"Conectando al cliente local de Marqo ({url})...")
    client = marqo.Client(url=url, api_key=api_key)
    
    # PARCHE DE RED: Forzamos al SDK a operar en modo puramente Open Source / Local
    client.config.is_cloud = False
    if hasattr(client.config, 'instance_mapping'):
        client.config.instance_mapping.is_cloud = False
        
    return client

def inicializar_indice(client: marqo.Client, name: str) -> bool:
    try:
        client.get_index(name)
        print(f"El índice '{name}' ya existe. Saltando creación.")
        return False
    except Exception:
        print(f"El índice no existe. Creando índice vectorial '{name}'...")
        try:
            client.create_index(
                index_name=name, 
                model="hf/all_datasets_v4_MiniLM-L6"
            )
            print("¡Índice creado con éxito!")
            return True
        except MarqoWebError as e:
            print(f"[ERROR CRÍTICO] No se pudo crear el índice: {e}")
            exit(1)

def ingestar_datos_prueba(client: marqo.Client, name: str):
    dataset = [
        {
            "_id": "doc1",
            "Title": "Laptop ThinkPad",
            "Description": "Computadora portátil de alta gama ideal para desarrollo de software y bases de datos relacionales."
        },
        {
            "_id": "doc2",
            "Title": "Teclado Mecánico",
            "Description": "Dispositivo periférico de entrada con switches ergonómicos para programadores y escritores."
        },
        {
            "_id": "doc3",
            "Title": "Servidor Cloud",
            "Description": "Infraestructura administrada en la nube para el despliegue de contenedores Docker y backend."
        }
    ]
    
    print("\nIniciando conversión de texto a vectores (Embeddings)...")
    try:
        client.index(name).add_documents(dataset, tensor_fields=["Title", "Description"])
        print("¡Ingesta completada con éxito!")
    except MarqoWebError as e:
        print(f"[ERROR] Falló la carga de documentos: {e}")

# ==========================================
# 
# ==========================================

def mostrar_estadisticas_indices(client: marqo.Client, name: str):
    """Muestra los contadores y el contenido real guardado en el contenedor de Docker"""
    print("\n" + "="*50)
    print("ESTADO ACTUAL DEL CONTENEDOR EN DOCKER:")
    try:
        # 1. Obtener contadores matemáticos
        stats = client.index(name).get_stats()
        print(f" -> Número de Documentos Persistidos: {stats.get('numberOfDocuments', 0)}")
        print(f" -> Número de Vectores Generados: {stats.get('numberOfVectors', 0)}")
        print(f" -> Estado del Índice Vectorial: {stats.get('indexStatus', 'N/A')}")
        
        # 2. Recuperar y mostrar los datos reales almacenados de forma dinámica
        print("\n ARTÍCULOS DETECTADOS EN EL INVENTARIO:")
        
        lista_ids_dinamica = [f"doc{i}" for i in range(1, 21)] 
        
        documentos_en_db = client.index(name).get_documents(
            document_ids=lista_ids_dinamica
        )
        
        # Filtramos solo los que sí existen de verdad en el contenedor
        encontrados = documentos_en_db.get("results", [])
        if encontrados:
            for doc in encontrados:
                if doc.get("_found", False): # Solo si el documento existe en el Docker
                    print(f"   [ID: {doc.get('_id')}] - {doc.get('Title', 'Sin título')}")
        else:
            print("   (No se pudieron leer detalles de los artículos o está vacío)")

    except Exception as e:
        print(f"[ERROR] No se pudieron leer las estadísticas: {e}")
    print("="*50 + "\n")

def agregar_item_dinamico(client: marqo.Client, name: str):
    """Inserta un nuevo periférico en vivo para demostrar la ingesta dinámica"""
    print("\nInsertando nuevo hardware al inventario...")
    nuevo_articulo = [
        {
            "_id": "doc4",
            "Title": "Mouse Óptico Inalámbrico",
            "Description": "Dispositivo apuntador con sensor de alta precisión ideal para diseñadores y navegación ergonómica sin cables."
        }
    ]
    try:
        client.index(name).add_documents(nuevo_articulo, tensor_fields=["Title", "Description"])
        print("¡Éxito! 'Mouse Óptico Inalámbrico' (doc4) ha sido indexado y vectorizado en caliente.")
    except Exception as e:
        print(f"[ERROR] No se pudo agregar el documento: {e}")

# ==========================================

def buscar_semantico(client: marqo.Client, name: str, query: str):
    print("-" * 60)
    print(f"Búsqueda conceptual: '{query}'")
    try:
        resultados = client.index(name).search(q=query, limit=1)
        if not resultados['hits']:
            print("No se encontraron coincidencias cercanas.")
            return

        for coincidencia in resultados['hits']:
            print(f"\n DOCUMENTO ENCONTRADO POR PROXIMIDAD SEMÁNTICA:")
            print(f"ID: {coincidencia['_id']}")
            print(f"Título: {coincidencia.get('Title', 'N/A')}")
            print(f"Descripción: {coincidencia.get('Description', 'N/A')}")
            print(f"Score de Similitud: {coincidencia.get('_score', 'N/A'):.4f}")
    except MarqoWebError as e:
        print(f"[ERROR] No se pudo procesar la consulta: {e}")
    print("-" * 60)

if __name__ == "__main__":
    CONFIG_URL = 'http://127.0.0.1:8222'
    CONFIG_KEY = 'marqo-secret-key-2026'
    INDEX_NAME = "inventario-ucr"
    
    mq = conectar_marqo(CONFIG_URL, CONFIG_KEY)
    es_nuevo = inicializar_indice(mq, INDEX_NAME)
    
    if es_nuevo:
        ingestar_datos_prueba(mq, INDEX_NAME)
    else:
        try:
            estado_docs = mq.index(INDEX_NAME).get_stats()
            if estado_docs.get("numberOfDocuments", 0) == 0:
                print("¡Alerta! El índice está vacío en el contenedor. Forzando ingesta...")
                ingestar_datos_prueba(mq, INDEX_NAME)
            else:
                print("Usando datos persistidos previamente en el contenedor.")
        except Exception:
            ingestar_datos_prueba(mq, INDEX_NAME)
            
    # -------------------------------------------------------------
    #
    # -------------------------------------------------------------
    #     
    # mostrar_estadisticas_indices(mq, INDEX_NAME)
    # agregar_item_dinamico(mq, INDEX_NAME)
    
    # -------------------------------------------------------------
        
    print("\n--- Sistema de Búsqueda Vectorial Listo ---")
    while True:
        busqueda = input("\nEscriba lo que quiere buscar (para terminar escriba 'salir'): ").strip()
        if busqueda.lower() == 'salir' or not busqueda:
            print("Cerrando el explorador de vectores")
            break
        buscar_semantico(mq, INDEX_NAME, busqueda)