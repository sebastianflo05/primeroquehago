"""Esqueleto ejecutable para la clase de dashboards.

OBJETIVO DIDACTICO
==================
Este archivo contiene la estructura que reciben los estudiantes. La aplicacion
funciona desde el principio, pero los KPIs comunicativos, las graficas y la
vista ejecutiva quedan como bloques TODO para que el docente los programe en
vivo.

La clase sigue este orden:

    datos -> filtros -> KPIs -> graficas -> color -> interpretacion -> GitHub

Para ejecutar:

    streamlit run app.py

Cuando guardes el archivo, Streamlit detectara el cambio y recargara la pagina.

COMO ENCONTRAR CADA BLOQUE
=========================
En Visual Studio Code presiona Ctrl+F (Windows) o Cmd+F (macOS) y busca:

    DOCENTE-XX

Estos marcadores son mas confiables que los numeros de linea, porque las lineas
cambian conforme se escribe codigo.

ALCANCE DE ESTA SESION
======================
En esta clase se trabajan KPIs, graficas, color, storytelling y GitHub.
Feature engineering, modelos y clustering se entregan como modulos avanzados
comentados, pero no se programan durante estas dos horas.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ==============================================================================
# 1. RUTAS Y CONFIGURACION
# ==============================================================================
# Path(__file__) representa este archivo.
# .resolve().parent obtiene la carpeta del proyecto sin depender de la
# carpeta desde la que se ejecuto el comando. Esto evita errores al desplegar
# desde GitHub en Streamlit Community Cloud.
APP_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = APP_DIR / "data" / "ejemplo_estudiantes.csv"


# ==============================================================================
# 2. PALETA TOMADA DE LA GUIA PDF
# ==============================================================================
# El color debe tener significado:
# - Azul: informacion principal.
# - Gris: contexto.
# - Naranja: atencion.
# - Rojo: problema serio.
# - Verde: resultado favorable.
#
# En la clase usaremos estas constantes dentro de las graficas. De esta manera
# un mismo color conserva el mismo significado en todo el dashboard.
COLOR_PRIMARY = "#2563EB"
COLOR_CONTEXT = "#64748B"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#DC2626"
COLOR_SUCCESS = "#16A34A"

COLOR_PALETTE = [
    COLOR_PRIMARY,
    COLOR_WARNING,
    COLOR_CONTEXT,
    COLOR_SUCCESS,
    COLOR_DANGER,
]

# Esta paleta sirve para comprobar si las graficas siguen funcionando cuando
# se imprimen o proyectan en blanco y negro.
GRAYSCALE_PALETTE = [
    "#111827",
    "#4B5563",
    "#6B7280",
    "#9CA3AF",
    "#D1D5DB",
]


# ==============================================================================
# 3. CONFIGURACION DE STREAMLIT
# ==============================================================================
# set_page_config debe aparecer antes que cualquier elemento visible de la app.
st.set_page_config(
    page_title="Esqueleto de dashboard",
    layout="wide",
    initial_sidebar_state="auto",
)

st.title("Dashboard de analisis de datos")
st.caption("Esqueleto para construir las visualizaciones durante la clase")


# ==============================================================================
# 4. FUNCIONES DE CARGA Y PREPARACION
# ==============================================================================
@st.cache_data(show_spinner=False)
def load_default_data(path: Path) -> pd.DataFrame:
    """Lee el CSV incluido y guarda el resultado en cache.

    Streamlit ejecuta el archivo completo cada vez que el usuario interactua.
    El cache evita leer el mismo CSV desde disco en cada clic.
    """

    return pd.read_csv(path)


def prepare_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Aplica una preparacion pequena y facil de explicar.

    1. Copia los datos para no modificar el objeto original.
    2. Normaliza nombres de columnas.
    3. Convierte columnas que parecen fechas.
    """

    prepared = raw_df.copy()
    prepared.columns = [
        str(column).strip().lower().replace(" ", "_").replace("-", "_")
        for column in prepared.columns
    ]

    date_tokens = ("fecha", "date")
    for column in prepared.columns:
        if any(token in column for token in date_tokens):
            converted = pd.to_datetime(prepared[column], errors="coerce")
            if converted.notna().mean() >= 0.7:
                prepared[column] = converted

    return prepared


# ==============================================================================
# 5. CARGA DEL CSV
# ==============================================================================
# El cargador permite trabajar con el CSV de cada equipo. Si no se sube ningun
# archivo, la app usa el ejemplo academico incluido en el repositorio.
uploaded_file = st.sidebar.file_uploader(
    "CSV del proyecto",
    type=["csv"],
)

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
else:
    raw_df = load_default_data(DEFAULT_DATA_PATH)

df = prepare_data(raw_df)


# ==============================================================================
# 6. PERFIL DE COLUMNAS
# ==============================================================================
# Detectamos tipos porque el tipo de variable determina que grafica usar:
# - Numerica: histograma, boxplot, dispersion.
# - Categorica: barras, filtros, comparaciones.
# - Fecha: linea temporal.
numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
datetime_columns = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
categorical_columns = [
    column
    for column in df.columns
    if column not in numeric_columns and column not in datetime_columns
]


# ==============================================================================
# 7. CONTROLES GLOBALES
# ==============================================================================
st.sidebar.markdown("### Vista del dashboard")

# Este interruptor se utilizara durante la clase para hacer la prueba de
# accesibilidad e impresion en blanco y negro.
grayscale_mode = st.sidebar.toggle(
    "Modo blanco y negro",
    value=False,
)

active_palette = GRAYSCALE_PALETTE if grayscale_mode else COLOR_PALETTE

# Estas variables empiezan vacias. Cada TODO guardara aqui su figura para que
# posteriormente pueda reutilizarse en la vista ejecutiva sin repetir codigo.
histogram_figure = None
bar_figure = None
scatter_figure = None
time_figure = None
accessible_bar_figure = None

st.sidebar.markdown("### Filtro global")

if categorical_columns:
    filter_column = st.sidebar.selectbox(
        "Columna para filtrar",
        options=["Sin filtro"] + categorical_columns,
    )
else:
    filter_column = "Sin filtro"
    st.sidebar.caption("No se detectaron columnas categoricas.")

filtered_df = df.copy()

if filter_column != "Sin filtro":
    available_values = sorted(
        filtered_df[filter_column].dropna().astype(str).unique()
    )
    selected_values = st.sidebar.multiselect(
        "Valores incluidos",
        options=available_values,
        default=available_values,
    )
    filtered_df = filtered_df[
        filtered_df[filter_column].astype(str).isin(selected_values)
    ]

if filtered_df.empty:
    st.warning("No hay registros con los filtros actuales.")
    st.stop()


# ==============================================================================
# 8. ESTRUCTURA GENERAL
# ==============================================================================
# Las pestanas separan tres momentos:
# - Datos: comprobar que el CSV esta bien cargado.
# - Graficas: construir visualizaciones durante la clase.
# - Dashboard: seleccionar los resultados que se van a comunicar.
data_tab, charts_tab, dashboard_tab = st.tabs(
    ["Datos", "Graficas de clase", "Dashboard final"]
)


# ==============================================================================
# 9. PESTANA DE DATOS - YA ESTA COMPLETA
# ==============================================================================
with data_tab:
    st.subheader("Revision inicial")

    # Estos son indicadores TECNICOS de calidad de datos. Ya vienen completos
    # porque permiten comprobar que el CSV se cargo correctamente.
    # Los KPIs COMUNICATIVOS se construyen en la vista ejecutiva.
    kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
    kpi_1.metric("Registros", f"{len(filtered_df):,}")
    kpi_2.metric("Columnas", len(filtered_df.columns))
    kpi_3.metric("Faltantes", int(filtered_df.isna().sum().sum()))
    kpi_4.metric("Variables numericas", len(numeric_columns))

    st.dataframe(filtered_df.head(20), width="stretch")

    type_summary = pd.DataFrame(
        {
            "tipo": ["Numericas", "Categoricas", "Fechas"],
            "columnas": [
                ", ".join(numeric_columns) or "Ninguna",
                ", ".join(categorical_columns) or "Ninguna",
                ", ".join(datetime_columns) or "Ninguna",
            ],
        }
    )
    st.dataframe(type_summary, width="stretch", hide_index=True)


# ==============================================================================
# 10. PESTANA DE GRAFICAS - AQUI SE CODIFICA EN VIVO
# ==============================================================================
with charts_tab:
    st.subheader("Construccion de graficas")

    # --------------------------------------------------------------------------
    # DOCENTE-02 | TODO 1: HISTOGRAMA
    # --------------------------------------------------------------------------
    # Pregunta: Como se distribuye una variable numerica?
    # Grafica: Histograma.
    # Color: Un solo color principal porque no hay una segunda categoria.
    if numeric_columns:
        histogram_column = st.selectbox(
            "Variable para el histograma",
            options=numeric_columns,
            key="skeleton_histogram_column",
        )

        # DOCENTE - PEGAR DEBAJO DE ESTE COMENTARIO:
        # 1. Calculo de la mediana.
        # 2. px.histogram(...).
        # 3. st.plotly_chart(...).
        st.info(
            "TODO 1: construir un histograma con px.histogram() y aplicar "
            "active_palette[0] como color principal."
        )
    else:
        st.info("El CSV no contiene variables numericas.")

    st.divider()

    # --------------------------------------------------------------------------
    # DOCENTE-03 | TODO 2: BARRAS ORDENADAS
    # --------------------------------------------------------------------------
    # Pregunta: Cuantos casos hay en cada categoria?
    # Grafica: Barras horizontales ordenadas.
    # Regla: Si solo mostramos una medida, un color es suficiente.
    if categorical_columns:
        bar_column = st.selectbox(
            "Variable para las barras",
            options=categorical_columns,
            key="skeleton_bar_column",
        )

        # DOCENTE - PEGAR DEBAJO DE ESTE COMENTARIO:
        # 1. value_counts() para contar categorias.
        # 2. sort_values() para facilitar la comparacion.
        # 3. px.bar(..., orientation="h").
        st.info(
            "TODO 2: contar categorias con value_counts(), ordenar y construir "
            "barras horizontales con px.bar()."
        )
    else:
        st.info("El CSV no contiene variables categoricas.")

    st.divider()

    # --------------------------------------------------------------------------
    # DOCENTE-04 | TODO 3: RELACION ENTRE DOS VARIABLES
    # --------------------------------------------------------------------------
    # Pregunta: Existe relacion entre dos variables numericas?
    # Grafica: Dispersion.
    # Advertencia: Correlacion no significa causalidad.
    if len(numeric_columns) >= 2:
        scatter_x = st.selectbox(
            "Variable X",
            options=numeric_columns,
            key="skeleton_scatter_x",
        )
        scatter_y_options = [
            column for column in numeric_columns if column != scatter_x
        ]
        scatter_y = st.selectbox(
            "Variable Y",
            options=scatter_y_options,
            key="skeleton_scatter_y",
        )

        # DOCENTE - PEGAR DEBAJO DE ESTE COMENTARIO:
        # 1. Eliminar faltantes de X y Y.
        # 2. Calcular correlacion como referencia.
        # 3. Construir px.scatter(...) con transparencia.
        st.info(
            "TODO 3: construir una dispersion con px.scatter(), usar "
            "transparencia y calcular la correlacion solo como referencia."
        )

    st.divider()

    # --------------------------------------------------------------------------
    # DOCENTE-05 | TODO 4: SERIE TEMPORAL
    # --------------------------------------------------------------------------
    # Pregunta: Como cambia una medida a traves del tiempo?
    # Grafica: Linea.
    # Regla: El eje X debe representar el tiempo en orden.
    if datetime_columns and numeric_columns:
        date_column = st.selectbox(
            "Columna de fecha",
            options=datetime_columns,
            key="skeleton_date_column",
        )
        time_value = st.selectbox(
            "Medida temporal",
            options=numeric_columns,
            key="skeleton_time_value",
        )

        # DOCENTE - PEGAR DEBAJO DE ESTE COMENTARIO:
        # 1. Agrupar los registros de una misma fecha.
        # 2. Ordenar cronologicamente.
        # 3. Construir px.line(..., markers=True).
        st.info(
            "TODO 4: agrupar por fecha, ordenar y construir una linea con "
            "px.line()."
        )

    st.divider()

    # --------------------------------------------------------------------------
    # DOCENTE-06 | TODO 5: COLOR + PATRONES
    # --------------------------------------------------------------------------
    # Pregunta: Como distinguimos grupos sin depender solamente del color?
    # Solucion: combinar color con pattern_shape, marcadores o estilos de linea.
    if len(categorical_columns) >= 2:
        comparison_group = st.selectbox(
            "Categoria principal",
            options=categorical_columns,
            key="skeleton_comparison_group",
        )
        comparison_series = st.selectbox(
            "Categoria para color y patron",
            options=[
                column
                for column in categorical_columns
                if column != comparison_group
            ],
            key="skeleton_comparison_series",
        )

        # DOCENTE - PEGAR DEBAJO DE ESTE COMENTARIO:
        # 1. Contar combinaciones de las dos categorias.
        # 2. Usar color y pattern_shape con la MISMA variable.
        # 3. Probar el resultado con el modo blanco y negro.
        st.info(
            "TODO 5: crear barras agrupadas con color y pattern_shape. "
            "Despues activar el modo blanco y negro para comprobar la lectura."
        )


# ==============================================================================
# 11. DASHBOARD FINAL - SE COMPLETA AL CERRAR LA CLASE
# ==============================================================================
with dashboard_tab:
    st.subheader("Vista ejecutiva")

    # --------------------------------------------------------------------------
    # DOCENTE-01 | KPIs COMUNICATIVOS
    # --------------------------------------------------------------------------
    # Un KPI no es solo un numero grande. Debe orientar una decision.
    # Ejemplos:
    # - Finanzas: ingreso total, margen, variacion contra presupuesto.
    # - Biomedicina: pacientes, tasa de respuesta, eventos adversos.
    # - Educacion: matricula, promedio, porcentaje de aprobacion.
    # - Humanidades: documentos analizados, temas, periodo cubierto.
    #
    # DOCENTE - PEGAR DEBAJO DE ESTE COMENTARIO:
    # Crear columnas con st.columns() y mostrar 3 o 4 st.metric().
    st.info(
        "TODO KPI: sustituir este mensaje por indicadores que respondan "
        "la pregunta del proyecto."
    )

    # --------------------------------------------------------------------------
    # DOCENTE-07 | STORYTELLING Y VISTA EJECUTIVA
    # --------------------------------------------------------------------------
    # La vista final debe contener:
    # 1. KPIs que orientan.
    # 2. Una grafica principal.
    # 3. Una grafica de apoyo.
    # 4. Hallazgo + evidencia + limitacion.
    st.info(
        "TODO STORYTELLING: traer aqui solamente las graficas que respondan "
        "la pregunta analitica principal."
    )

    st.markdown("### Interpretacion")
    st.text_area(
        "Escribe el hallazgo, la evidencia y una limitacion",
        placeholder=(
            "Hallazgo: ...\n"
            "Evidencia: ...\n"
            "Limitacion: estos datos muestran asociacion, no causalidad."
        ),
        height=130,
    )

    st.markdown("### Revision antes de publicar")
    st.checkbox("La pregunta analitica es clara.", key="check_question")
    st.checkbox("Las graficas corresponden al tipo de dato.", key="check_charts")
    st.checkbox("El color tiene un significado consistente.", key="check_color")
    st.checkbox(
        "Las graficas se entienden en blanco y negro.",
        key="check_grayscale",
    )
    st.checkbox("La interpretacion incluye una limitacion.", key="check_limit")
