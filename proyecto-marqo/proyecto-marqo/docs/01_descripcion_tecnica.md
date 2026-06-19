# 1.1 Descripción técnica de Marqo

## Definición formal
Marqo es un motor de búsqueda vectorial de extremo a extremo ("documents-in,
documents-out"): a diferencia de un vector store puro, Marqo genera él mismo
los embeddings a partir de documentos crudos (texto o imágenes) usando
modelos transformer, y se encarga de indexarlos y de responder búsquedas
semánticas a través de una única API.

## Origen
- Fundado a mediados de 2022 en Melbourne, Australia.
- Fundadores: Tom Hamer (CEO, ex-ingeniero de bases de datos en AWS) y
  Jesse Clark (CTO, ex-científico de Machine Learning en la división de
  robótica de Amazon).
- Posteriormente trasladó su sede principal a San Francisco, EE. UU.

## Paradigma
Vector database / motor de búsqueda semántica multimodal (texto + imágenes
vía modelos como CLIP), pensado originalmente para casos de uso de
Retrieval Augmented Generation (RAG) y búsqueda semántica de e-commerce.

## Lenguaje de desarrollo base
Según el repositorio oficial (github.com/marqo-ai/marqo):
- **Python: 94.2%** — capa de API, orquestación e inferencia de modelos.
- **Java: 5%** — integración con el motor de indexación vectorial
  subyacente (OpenSearch en la v1).
- Otros: 0.8%.

## Nota importante sobre el estado actual del proyecto
El repositorio open source de Marqo está oficialmente **deprecado** (no
recibe más actualizaciones). La empresa giró su modelo de negocio hacia una
plataforma comercial de "AI-native ecommerce search & product discovery"
("Commerce Superintelligence") orientada a grandes retailers, y ya no se
posiciona como una vector database de propósito general. Esto es relevante
para justificar la elección de la herramienta en el proyecto y para evaluar
riesgos de mantenimiento a futuro.


## Fuente:

Repositorio de GITHUB De Marqo : https://github.com/marqo-ai/marqo
