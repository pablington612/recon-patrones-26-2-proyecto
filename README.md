# Proyecto final Reconocimiento de Patrones 2026-2

Predicción de `TVT` (profundidad vertical verdadera) en pozos horizontales, usando los datos de la competencia de Kaggle [rogii-wellbore-geology-prediction](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction).

<details>
<summary><strong>Detalles del proyecto e instalación</strong></summary>

## Estructura

```
proyecto/
├── README.md            # el reporte del proyecto (ver abajo)
├── requirements.txt       # dependencias
├── datos/descargar.py   # descarga los datos con la API de Kaggle
├── libretas/
│   ├── 01-exploracion.ipynb
│   ├── 02-validacion-y-linea-base.ipynb
│   ├── 03-modelos.ipynb
│   └── 04-envio-final.ipynb
├── src/                 # funciones reutilizables (atributos, validación, modelos)
├── experimentos.csv     # bitácora: un renglón por experimento
└── leaderboard/         # capturas de la tabla y de envíos
```

## Requisitos

- Python 3.14 (el entorno del proyecto se creó con esta versión)
- Git
- Una cuenta de Kaggle

## Instalación

1. Clona el repositorio y entra a la carpeta:

   ```bash
   git clone <URL-del-repositorio>
   cd recon-patrones-26-2-proyecto
   ```

2. Crea y activa un entorno virtual:

   ```bash
   python -m venv .venv
   ```

   - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
   - Windows (Git Bash): `source .venv/Scripts/activate`
   - macOS / Linux: `source .venv/bin/activate`

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Credenciales de Kaggle

Los datos se descargan con `kagglehub`, que necesita credenciales.

1. Entra a la [página de la competencia](https://www.kaggle.com/competitions/rogii-wellbore-geology-prediction) y acepta las reglas (*Join Competition*). Sin esto la descarga falla con error 403.
2. En Kaggle ve a *Settings → API* y genera un token.
3. Copia la plantilla y llénala:

   ```bash
   cp .env.example .env      # en PowerShell: Copy-Item .env.example .env
   ```

## Descarga de datos (manual)

La libreta descarga los datos automáticamente la primera vez. Para hacerlo antes:

```bash
python datos/descargar.py
```

Los archivos quedan en la caché de `kagglehub` (`~/.cache/kagglehub`), fuera del repositorio. El script imprime la ruta.

## Ejecutar las libretas

### Desde un IDE

**VS Code**
1. Instala las extensiones *Python* y *Jupyter*.
2. Abre la carpeta del proyecto y luego `libretas/01-exploracion.ipynb`.
3. Arriba a la derecha pulsa *Select Kernel → Python Environments* y elige `.venv`.
4. Pulsa *Run All* o ejecuta celda por celda con `Shift+Enter`.

**PyCharm**
1. Abre la carpeta y configura el intérprete: *Settings → Python Interpreter → Add → Existing* y elige `.venv`.
2. Abre la libreta y ejecuta las celdas.

### Desde el navegador

Con el entorno activado, instala JupyterLab (no está en `requirements.txt`) y ábrelo desde la raíz del proyecto:

```bash
pip install jupyterlab
jupyter lab
```

Se abrirá el navegador (o copia la URL con el token que aparece en la terminal). Abre `libretas/01-exploracion.ipynb`. Si te pide kernel, elige *Python 3*.

> Tip: si `.venv` no aparece como kernel, regístralo con
> `python -m ipykernel install --user --name recon-patrones`.

## Problemas comunes

- **403 / Forbidden al descargar**: no aceptaste las reglas de la competencia, o el usuario/token en `.env` son incorrectos.
- **`ModuleNotFoundError`**: el kernel no es el de `.venv`; selecciónalo de nuevo.
- **Credenciales no encontradas**: verifica que `.env` exista en la raíz del proyecto y tenga ambos valores.
</details>