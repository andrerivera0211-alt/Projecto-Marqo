# Proyecto Marqo — Búsqueda Vectorial Semántica

Repositorio grupal para el desarrollo del proyecto basado en **Marqo**, motor de búsqueda vectorial end-to-end (documents-in, documents-out).

## Estructura del repositorio

```
proyecto-marqo/
├── README.md                  # Este archivo
├── .gitignore                 # Archivos/carpetas ignoradas por Git
├── requirements.txt           # Dependencias de Python
├── docker-compose.yml         # Levanta el contenedor de Marqo localmente
├── docs/                      # Documentación técnica del proyecto
│   ├── 01_descripcion_tecnica.md
│   └── 02_mecanismos_indexacion.md
├── src/                       # Código fuente de la aplicación
│   ├── __init__.py
│   ├── config.py              # Configuración (URL del cliente, índices, etc.)
│   ├── ingest.py               # Carga/indexación de documentos en Marqo
│   └── search.py               # Funciones de búsqueda/consulta
├── notebooks/                 # Notebooks de exploración y pruebas
├── data/                      # Datos de entrada (no se sube a git, ver .gitignore)
├── tests/                     # Pruebas unitarias
│   └── test_search.py
└── .github/workflows/         # CI/CD (GitHub Actions)
    └── ci.yml
```

##  Cómo levantar el entorno

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/<organizacion>/proyecto-marqo.git
   cd proyecto-marqo
   ```

2. Levantar Marqo localmente con Docker:
   ```bash
   docker-compose up -d
   ```

3. Crear entorno virtual e instalar dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate   # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Probar la conexión:
   ```bash
   python src/ingest.py
   ```

##  Flujo de trabajo en equipo (Git)

- `main`: rama estable, solo se actualiza vía Pull Request aprobado.
- `develop`: rama de integración del equipo.
- `feature/<nombre>`: una rama por funcionalidad/persona (ej. `feature/ingesta-pdfs`).

##  Documentación

Ver carpeta [`docs/`](./docs) para el informe técnico (definición, origen, paradigma e indexación interna).
