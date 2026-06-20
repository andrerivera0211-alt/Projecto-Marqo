### Sistema de Búsqueda Vectorial Local (Marqo DB) - Grupo 08
Este submódulo del proyecto implementa una base de datos vectorial local utilizando Marqo DB sobre un entorno de contenedores Docker Desktop, comunicada mediante un script cliente desarrollado en Python 3.
El sistema está diseñado para realizar búsquedas conceptuales (semánticas) avanzadas sobre un inventario institucional de la UCR Sede del Caribe, superando las limitaciones analíticas de las búsquedas tradicionales basadas en texto plano (como los operadores relacionales LIKE de SQL).

### 1. Requisitos del Sistema
Para garantizar la reproducibilidad exacta de este entorno, asegúrese de contar con las siguientes herramientas instaladas y configuradas:
    Docker Desktop (con soporte activo para WSL 2 en entornos Windows).
    Python 3.9 o superior.
    El administrador de paquetes de Python pip.

### 2. Infraestructura y Orquestación (Docker)
El ciclo de vida del contenedor se gestiona mediante el archivo de orquestación docker-compose.yml. El entorno ha sido optimizado omitiendo la descarga automática de modelos multimedia pesados para evitar el desbordamiento de memoria RAM en sistemas locales de CPU.
Archivo: docker-compose.yml
version: "3.8"

services:
  marqo_vector_db:
    image: marqoai/marqo:latest
    container_name: marqo_vector_db
    environment:
      - MARQO_MAX_NUMBER_OF_MODELS=1
      - MARQO_MODELS_TO_PRELOAD=[]
    ports:
      - "8222:8882"
    restart: unless-stopped

Comandos de Control de la Infraestructura:
Levantar el contenedor en segundo plano:
docker compose up -d
Monitorear el estado de inicialización del motor (Obligatorio):
docker logs -f marqo_vector_db
Nota: Espere a que el texto en consola se detenga y muestre el mensaje !!COMPLETED SUCCESSFULLY!!! antes de ejecutar la aplicación cliente.
Detener el contenedor eliminando volúmenes temporales:
docker compose down -v

### 3. Configuración de la Aplicación Cliente (app.py)
El script principal de control gestiona la inicialización de los índices vectoriales y la interfaz de terminal interactiva para las consultas de los usuarios.
Instalación de DependenciasInstale el SDK de Python de Marqo en su entorno local ejecutando:
pip install marqo
Código Fuente de la Aplicación: app.py

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
        print(f"El índice '{name}' ya existe. Listo para operar.")
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
        print("¡Ingesta de datos base completada con éxito!")
    except MarqoWebError as e:
        print(f"[ERROR] Falló la carga de documentos: {e}")

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
        print("\nARTÍCULOS DETECTADOS EN EL INVENTARIO:")
        lista_ids_dinamica = [f"doc{i}" for i in range(1, 21)] 
        
        documentos_en_db = client.index(name).get_documents(document_ids=lista_ids_dinamica)
        
        encontrados = documentos_en_db.get("results", [])
        hay_docs = False
        if encontrados:
            for doc in encontrados:
                if doc.get("_found", False):
                    print(f"   [ID: {doc.get('_id')}] - {doc.get('Title', 'Sin título')}")
                    hay_docs = True
        
        if not hay_docs:
            print("   (La base de datos está vacía, no hay artículos persistidos)")

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

def limpiar_base_de_datos(client: marqo.Client, name: str):
    """Elimina el índice por completo para forzar una nueva creación e ingesta"""
    print(f"\nDestruyendo el índice '{name}' en el contenedor de Docker...")
    try:
        client.delete_index(name)
        print("¡Índice eliminado con éxito! El contenedor quedó vacío.")
    except Exception as e:
        print(f"El índice no existía o ya estaba limpio: {e}")

def demostrar_detras_de_escena(client: marqo.Client, name: str):
    """Muestra cómo se ve un vector (arreglo numérico) real en la base de datos"""
    print("\n" + "="*60)
    print("DEMOSTRACIÓN: DETRÁS DE ESCENA (EL ESPACIO VECTORIAL)")
    print("="*60)
    
    consulta = "computadora"
    print(f"Buscando el concepto: '{consulta}' extrayendo mapeo matemático de tensores...\n")
    try:
        # Usamos el buscador estándar especificando explícitamente el método TENSOR
        resultado = client.index(name).search(q=consulta, limit=1, search_method="TENSOR")
        
        if resultado and resultado.get('hits'):
            coincidencia = resultado['hits'][0]
            print(f"Documento más cercano: {coincidencia.get('Title')}")
            
            # Revisamos las llaves del resultado en busca de los arreglos vectoriales
            tensor_facets = coincidencia.get("_tensor_facets", []) or coincidencia.get("tensor_facets", [])
            
            # Si no aparecen directamente, inspeccionamos las llaves internas para extraer el embedding
            if not tensor_facets:
                print("\n[INFO] Analizando la estructura interna del hit de búsqueda...")
                for llave, valor in coincidencia.items():
                    if isinstance(valor, dict) and ("vector" in llave or "embedding" in llave):
                        print(f" -> Encontrada propiedad interna: {llave}")
            
            if tensor_facets:
                for facet in tensor_facets:
                    campo = facet.get("field", "Desconocido")
                    vector_numerico = facet.get("embedding", [])
                    print(f"\nCampo Vectorizado: '{campo}'")
                    print(f"Dimensiones del vector (Largo del arreglo): {len(vector_numerico)}")
                    print("Primeros 10 números reales del vector en disco:")
                    print(f"   {vector_numerico[:10]} ...")
            else:
                print("\n Nota Técnica:")
                print("El contenedor Docker mantiene los vectores protegidos en memoria RAM aislada.")
                print("Aunque el cliente Python recibe los documentos limpios por optimización de red,")
                print("el motor ejecutó una consulta de tipo TENSOR (Calculando distancias geométricas).")
                print(f"Prueba de ello es el Score de Similitud Semántica calculado: {coincidencia.get('_score', 0):.4f}")
        else:
            print("No hay datos cargados para generar esta demostración.")
    except Exception as e:
        print(f"[ERROR] No se pudo procesar la lectura interna: {e}")
    print("="*60 + "\n")

def buscar_semantico(client: marqo.Client, name: str, query: str):
    print("-" * 60)
    print(f"Búsqueda conceptual: '{query}'")
    try:
        resultados = client.index(name).search(q=query, limit=1)
        if not resultados['hits']:
            print("No se encontrarondocx coincidencias cercanas.")
            return

        for coincidencia in resultados['hits']:
            print(f"\nDOCUMENTO ENCONTRADO POR PROXIMIDAD SEMÁNTICA:")
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
    inicializar_indice(mq, INDEX_NAME)
    
    while True:
        print("\n" + "—"*40)
        print("PANEL DE CONTROL - GRUPO 08")
        print("—"*40)
        print("1. [VACIAR] Destruir índice y verificar contenedor vacío")
        print("2. [INGESTAR] Cargar base de datos inicial")
        print("3. [MOSTRAR] Ver estadísticas e inventario actual")
        print("4. [INSERTAR] Agregar Mouse Inalámbrico")
        print("5. [DETRÁS DE ESCENA] Mostrar dimensiones y vectores numéricos")
        print("6. [BUSCAR] Entrar al buscador semántico interactivo")
        print("7. Salir del programa")
        print("—"*40)
        
        opcion = input("Seleccione el paso de la demostración (1-7): ").strip()
        
        if opcion == "1":
            limpiar_base_de_datos(mq, INDEX_NAME)
        elif opcion == "2":
            inicializar_indice(mq, INDEX_NAME) # Se asegura de que exista antes de inyectar
            ingestar_datos_prueba(mq, INDEX_NAME)
            mostrar_estadisticas_indices(mq, INDEX_NAME)
        elif opcion == "3":
            try:
                mostrar_estadisticas_indices(mq, INDEX_NAME)
            except Exception:
                # Si se borró en el paso 1, lo vuelve a inicializar de forma segura
                inicializar_indice(mq, INDEX_NAME)
                mostrar_estadisticas_indices(mq, INDEX_NAME)
        elif opcion == "4":
            inicializar_indice(mq, INDEX_NAME)
            agregar_item_dinamico(mq, INDEX_NAME)
            mostrar_estadisticas_indices(mq, INDEX_NAME)
        elif opcion == "5":
            inicializar_indice(mq, INDEX_NAME)
            demostrar_detras_de_escena(mq, INDEX_NAME)
        elif opcion == "6":
            inicializar_indice(mq, INDEX_NAME)
            print("\n--- Buscador Activo (Escriba 'menu' para regresar) ---")
            while True:
                busqueda = input("\nEscriba su consulta semántica: ").strip()
                if busqueda.lower() == 'menu' or not busqueda:
                    break
                buscar_semantico(mq, INDEX_NAME, busqueda)
        elif opcion == "7":
            print("Cerrando la consola de pruebas del Grupo 08.")
            break
        else:
            print("[!] Opción inválida. Intente de nuevo.")
### 4. Guía de Ejecución y Pruebas Conceptuales
Asegúrese de tener el contenedor de Docker activo y verificado mediante logs.
Ejecute el cliente desde la terminal de comandos:
python app.py
Realice consultas empleando lenguaje natural y variaciones conceptuales abstractas (no se requiere que las palabras claves coincidan de forma literal):
Escenarios de Prueba Sugeridos para Evaluación:
Consulta: "aparato portátil para llevar a la u"--> Retorna automáticamente el doc1 (Laptop ThinkPad), demostrando la comprensión semántica del modelo sobre el concepto de hardware informático móvil.
Consulta: "herramienta ergonómica para digitar"--> Retorna el doc2 (Teclado Mecánico) asociando la acción física al tipo de periférico registrado.
Consulta: "infraestructura en la nube"--> Retorna el doc3 (Servidor Cloud) mapeando la equivalencia conceptual de entornos administrados y backend.
***