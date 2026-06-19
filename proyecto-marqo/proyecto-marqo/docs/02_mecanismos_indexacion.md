# 1.2 Mecanismos de indexación interna

Marqo no implementa su propio algoritmo de búsqueda aproximada de vecinos
(ANN) desde cero: delega esa función en un motor vectorial subyacente, que
cambió entre las dos generaciones del producto.

## Marqo 1 (versión open source clásica)
- Backend: **OpenSearch**, usando el motor **Lucene**.
- Los índices Lucene se componen de segmentos inmutables que se crean y
  fusionan (merge) a medida que se agregan documentos, lo que generaba
  consumo de recursos impredecible durante cargas masivas de datos.
- Algoritmo de indexación: **HNSW** (Hierarchical Navigable Small World)
  exclusivamente. No usa IVF.
- Parámetros por defecto ajustados por el equipo de Marqo tras pruebas
  internas: `efConstruction = 512`, `M = 16`, `efSearch = 2000` (buen
  balance entre recall y latencia).

## Marqo 2 (rediseño arquitectónico)
- Ante limitaciones de rendimiento de OpenSearch/Lucene en cargas de
  e-commerce a gran escala, el equipo evaluó varios motores: Milvus, Vespa,
  OpenSearch gestionado por AWS, Weaviate, Redis y Qdrant.
- Resultado: eligieron **Vespa** como nuevo backend tras benchmarks
  internos (p. ej., con 50M de vectores, Vespa mostró latencias p50 de
  16ms frente a 140ms de Milvus en infraestructura equivalente).
- Vespa también es un motor basado en grafos **HNSW** (tampoco usa IVF),
  pero con una arquitectura de nodos distribuidos en C++ que permite
  mutaciones (updates/deletes) y sharding horizontal sin los cuellos de
  botella de los segmentos inmutables de Lucene.

## Conclusión: ¿HNSW, IVF o combinación?
Marqo usa **exclusivamente HNSW** en ambas arquitecturas (v1 y v2). No
implementa IVF (Inverted File Index), que es típico de motores orientados a
clustering por celdas como Faiss. Los vectores se cargan en memoria nativa
(in-memory graph) para minimizar la latencia de recorrido del grafo,
mientras que la persistencia y segmentación en disco quedan delegadas al
motor subyacente (Lucene en v1, Vespa en v2). Además, Marqo soporta
sharding horizontal del índice para escalar a cientos de millones de
documentos.

## Fuentes
Blog oficial: https://www.marqo.ai/blog/what-is-marqo
Blog oficial: https://www.marqo.ai/blog/understanding-recall-in-
- Repositorio de Marqo: github.com/marqo-ai/marqo
