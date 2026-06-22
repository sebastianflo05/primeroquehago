"""Configuracion central de la plantilla.

================================================================================
PROPOSITO DE ESTE ARCHIVO
================================================================================
Este archivo concentra TODAS las constantes que usa el dashboard. La razon
didactica es simple: si los estudiantes solo modifican UN archivo para adaptar
el dashboard a sus datos, que sea este.

Que pueden cambiar aqui:
- El titulo y subtitulo del dashboard.
- La ruta al archivo CSV de su equipo.
- La paleta de colores (referencia: guia_color_visualizacion_datos.md).
- El numero de filas que se muestran en las vistas previas.
- La semilla aleatoria para reproducibilidad de modelos.

Que NO deben cambiar aqui (sin entenderlo primero):
- El nombre de las variables (APP_TITLE, COLOR_PRIMARY, etc.)
  porque se importan desde otros archivos y cambiarlos romperia todo.
"""

from pathlib import Path

# ==============================================================================
# TITULO Y SUBTITULO
# ==============================================================================
# Cada equipo debe cambiar APP_TITLE por el tema de su proyecto.
# Ejemplo: "Dashboard de rendimiento academico", "Analisis de ventas 2026".
APP_TITLE = "Plantilla de dashboard para analisis de datos"

# Texto corto que aparece debajo del titulo. Explica que hace el dashboard.
# Ejemplo: "Exploracion de calificaciones, modelo de aprobacion y perfiles de estudiantes".
APP_SUBTITLE = "Exploracion, modelo supervisado, clustering y visualizacion ejecutiva"

# ==============================================================================
# DATOS
# ==============================================================================
# Ruta al archivo CSV que se carga por defecto.
# La app tambien permite subir un CSV manualmente desde la barra lateral.
# Para cambiar de dataset: poner el archivo en la carpeta data/ y actualizar
# esta ruta. Ejemplo: "data/calificaciones_2026.csv"
DEFAULT_DATA_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "ejemplo_estudiantes.csv"
)

# ==============================================================================
# PALETA DE COLORES
# ==============================================================================
# Estos colores se aplican a TODAS las graficas del dashboard.
# La eleccion de colores sigue los criterios de la guia de color:
# Ver: guia_color_visualizacion_datos.md -> seccion "Colores recomendados"
#
# Logica de la paleta:
#   COLOR_PRIMARY (azul)  -> informacion principal, barras, KPIs.
#   COLOR_SECONDARY (verde) -> resultado positivo, exito, secundario.
#   COLOR_WARNING (naranja) -> alerta, atencion, valores cerca del limite.
#   COLOR_DANGER (rojo)   -> problema, riesgo, valores criticos.
#   COLOR_NEUTRAL (gris)  -> ejes, contexto, texto secundario, datos de referencia.
#
# Los estudiantes pueden cambiar los valores HEX siempre que mantengan
# el significado de cada color consistente en todo el dashboard.

COLOR_PRIMARY = "#2563eb"    # Azul
COLOR_SECONDARY = "#16a34a"  # Verde
COLOR_WARNING = "#f59e0b"    # Naranja
COLOR_DANGER = "#dc2626"     # Rojo
COLOR_NEUTRAL = "#64748b"    # Gris

# ==============================================================================
# VISTA PREVIA
# ==============================================================================
# Numero maximo de filas que se muestran en las tablas de vista previa.
# No es necesario mostrar 1000 filas en pantalla; con 20 basta para que
# los estudiantes sepan como se ven los datos.
PREVIEW_ROWS = 20

# ==============================================================================
# REPRODUCIBILIDAD
# ==============================================================================
# Semilla fija para los modelos de Machine Learning.
# Esto asegura que cada vez que se ejecute el dashboard con los mismos datos,
# los resultados del modelo y clustering sean identicos.
# Explicacion en clase: "Si no fijamos la semilla, cada vez que entrenemos
# el modelo obtendriamos resultados ligeramente distintos por el muestreo
# aleatorio de train_test_split y la inicializacion del Random Forest."
RANDOM_STATE = 42

# ==============================================================================
# MODELOS GUARDADOS (AVANZADO)
# ==============================================================================
# Para cargar modelos pre-entrenados en lugar de entrenar cada vez.
# Esto es util cuando:
#   - El modelo tarda en entrenar y se quiere mostrar resultados rapido.
#   - Se quiere comparar un modelo guardado contra uno recien entrenado.
#   - Se uso un modelo complejo (XGBoost, redes neuronales) entrenado fuera
#     del dashboard y se quiere cargar el resultado.
#
# Para activar: descomentar y apuntar a un archivo .pkl
# MODEL_PATH = "modelos/modelo_entrenado.pkl"
# MODEL_PATH = None  # <- mantener en None si se entrena en vivo
