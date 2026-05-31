# exa-MINADO - Buscador de temario (PDF / DOCX)

<img width="1200" height="655" alt="exa-MINADO" src="https://github.com/user-attachments/assets/d1e480a3-a005-4398-a354-5588fa7a02a8" />

Herramienta mínima en Python para indexar apuntes en PDF y DOCX y buscarlos con una caja flotante (Tkinter). El extractor se ejecuta una vez; el buscador lee `db.json` al instante.

## Estructura del proyecto

```
.
├── run_app.py        # Punto de entrada (venv + buscador)
├── extractor.py      # Lee temarios/ y genera db.json
├── buscador.py       # Interfaz de búsqueda flotante
├── visor.py          # Abre PDF/DOCX en la página indicada
├── db.json           # Base de datos (generada automáticamente)
├── temarios/         # Coloca aquí tus PDF y DOCX
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.10 o superior
- Tkinter (suele venir con Python en Linux/Windows)

## Instalación y arranque

En la carpeta del proyecto, con un solo comando:

```bash
python run_app.py
```

`run_app.py` crea el entorno virtual `.venv` si no existe, instala las dependencias de `requirements.txt` y abre el buscador. Si falta `db.json`, ejecuta antes el extractor de forma automática.

Dependencias Python: `pymupdf`, `python-docx`, `pytesseract`, `Pillow`.

**PDF solo con imágenes (escaneados):** hace falta [Tesseract](https://github.com/tesseract-ocr/tesseract) en el sistema:

```bash
# Linux (Debian/Ubuntu)
sudo apt install tesseract-ocr tesseract-ocr-spa

# Windows: instalador desde UB Mannheim (incluir idioma Spanish)
```

El extractor detecta páginas con poco texto y aplica OCR automáticamente. Está optimizado para **diapositivas UF1465** (una imagen PNG 1376×768 por página, fondo claro). Los **`.png` sueltos** en `temarios/` también se indexan con OCR (Tesseract). Instala `tesseract-ocr-spa` para castellano.

Instalación manual (opcional):

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux:    source .venv/bin/activate
pip install -r requirements.txt -q
python buscador.py
```

## Uso

### 1. Preparar el temario

Copia tus archivos `.pdf`, `.docx` e imágenes `.png` en la carpeta `temarios/`.

### 2. Generar la base de datos

```bash
python run_app.py extract
```

También vale `python3 extractor.py`: si usas el Python del sistema, el script se relanza solo con `.venv` cuando existe.

No ejecutes el extractor con `python3` a mano sin haber creado antes el entorno (`python run_app.py` o `python run_app.py extract`).

Esto crea o actualiza `db.json` con entradas como:

```json
[
  {
    "archivo": "Tema1_Intro.pdf",
    "pagina": 5,
    "texto": "el polimorfismo consiste en..."
  },
  {
    "archivo": "Ejercicios_JDBC.docx",
    "pagina": 2,
    "texto": "la conexion se realiza mediante..."
  }
]
```

Vuelve a ejecutar el extractor cuando añadas o cambies archivos en `temarios/`.

### 3. Abrir el buscador

```bash
python run_app.py
```

También puedes lanzar `python buscador.py` dentro del `.venv` activado. Si no existe `db.json`, `run_app.py` intentará generarlo; si falla, ejecuta `python extractor.py` tras colocar archivos en `temarios/`.

## Interfaz del buscador

| Acción | Comportamiento |
|--------|----------------|
| **Enter** | Busca y muestra resultados con enlaces al temario |
| **Clic** en `archivo  p.N` (azul subrayado) | Abre el PDF en la página N (Evince, Okular, Atril, navegador…) |
| **Doble clic** en un resultado | Copia el texto del párrafo al portapapeles |
| **Esc** | Cierra la aplicación al instante |
| **Cerrar ventana** | Cierra el buscador (también al cerrar la terminal) |

La ventana permanece siempre visible (`topmost`). Usa la barra de título del sistema para moverla; al cerrar la terminal, la aplicación se cierra con ella.

## Algoritmo de búsqueda

- La consulta se pasa a minúsculas y se divide en palabras.
- Un párrafo coincide solo si **todas** las palabras aparecen en su texto (orden irrelevante).
- Ejemplo: `herencia interfaz` devuelve párrafos que contienen ambas palabras.

## Notas

- En DOCX, `pagina` se aproxima según saltos de página del documento; en PDF corresponde al número de página real.
- El extractor también indexa tablas de los DOCX (celdas unidas con ` | `).
- Los PDF escaneados, diapositivas en imagen o **PNG** tardan más (OCR). Regenera con `python run_app.py extract` tras cambiar el temario.
- En **DOCX**, el clic abre el archivo; el número de página del índice es orientativo (Word/LibreOffice no reciben página por línea de comandos).
- En **Windows**, la página exacta en PDF funciona mejor con [SumatraPDF](https://www.sumatrapdfreader.org/) instalado.
- `db.json` puede crecer mucho con temarios grandes; conviene regenerarlo solo cuando cambie el material.
