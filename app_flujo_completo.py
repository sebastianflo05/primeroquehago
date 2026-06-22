"""Aplicacion principal de la plantilla Streamlit.

================================================================================
PROPOSITO DE ESTE ARCHIVO
================================================================================
app.py es el "guion" del dashboard. Define:

  1. La estructura de la pagina (sidebar, pestañas, layout).
  2. La CARGA de datos (que archivo se usa).
  3. Los FILTROS que el usuario puede aplicar.
  4. Que GRAFICAS y TABLAS se muestran en cada pestana.
  5. Como se CONECTAN los componentes: carga -> filtra -> analiza -> grafica.

La logica PESADA (modelos, graficas, limpieza) vive en los otros archivos:
  - data_loader.py: carga y limpieza de datos.
  - analytics.py: estadistica, modelo, clustering.
  - visualizations.py: graficas Plotly.
  - config.py: configuracion general (titulos, colores, rutas).

================================================================================
ORDEN DE CLASE RECOMENDADO
================================================================================
1. Ejecutar la app y recorrer las pestañas (sin codigo).
2. Explicar la estructura: sidebar -> filtros -> pestanas.
3. Abrir app.py y mostrar el flujo de arriba a abajo.
4. En cada pestana, mostrar que archivo contiene la logica correspondiente.
5. Modificar config.py para cambiar titulo y colores en vivo.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Streamlit puede ejecutar este archivo desde distintas carpetas. Agregar su
# propio directorio a sys.path permite importar los modulos vecinos de forma
# predecible sin depender de la terminal desde la que se lanzo el comando.
MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import analytics
import data_loader
import visualizations as viz
from config import APP_SUBTITLE, APP_TITLE, DEFAULT_DATA_PATH, PREVIEW_ROWS


# ==============================================================================
# CONFIGURACION DE LA PAGINA
# ==============================================================================
# st.set_page_config() es SIEMPRE la primera instruccion de Streamlit.
# Si se coloca despues de cualquier otro comando de Streamlit, falla.
#
# Opciones:
#   page_title: titulo que aparece en la pestana del navegador.
#   layout="wide": usa todo el ancho de la pantalla (vs "centered").
#   initial_sidebar_state: la barra lateral comienza abierta.

st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# BLOQUE 1: CARGA DE DATOS
# ==============================================================================
# El usuario puede:
#   a) Subir su propio CSV desde la barra lateral.
#   b) Usar el dataset de ejemplo (DEFAULT_DATA_PATH en config.py).
#
# La funcion data_loader.prepare_dataset() aplica limpieza basica:
# - Normaliza nombres de columnas.
# - Detecta y convierte fechas.
#
# Pregunta para clase: "?Que pasa si subimos un CSV con columnas nuevas?"
# (R: la app se adapta automaticamente porque perfilamos las columnas
#  en tiempo real con profile_columns()).

def load_dataset() -> pd.DataFrame:
    """Carga el CSV de ejemplo o el archivo subido por el usuario."""

    uploaded_file = st.sidebar.file_uploader(
        "CSV del proyecto",
        type=["csv"],
    )

    if uploaded_file is not None:
        raw_df = data_loader.load_csv_from_upload(uploaded_file)
    else:
        raw_df = data_loader.load_csv_from_path(DEFAULT_DATA_PATH)

    return data_loader.prepare_dataset(raw_df)


# ==============================================================================
# BLOQUE 2: FILTROS
# ==============================================================================
# Filtro global en la barra lateral: permite seleccionar una columna
# categorica y elegir que valores incluir.
#
# Logica:
#   - Si no hay columnas categoricas, no mostramos filtro.
#   - Si el usuario selecciona "Sin filtro", mostramos todo.
#   - Si selecciona valores, filtramos el DataFrame.
#
# Referencia: guia de color -> "KPIs: datos filtrados"

def apply_sidebar_filters(df: pd.DataFrame, categorical_columns: list[str]) -> pd.DataFrame:
    """Aplica un filtro global sencillo para mantener la plantilla manejable."""

    filtered = df.copy()

    st.sidebar.markdown("### Filtro global")
    if not categorical_columns:
        st.sidebar.caption("No hay columnas categoricas disponibles.")
        return filtered

    filter_column = st.sidebar.selectbox(
        "Columna para filtrar",
        options=["Sin filtro"] + categorical_columns,
    )

    if filter_column == "Sin filtro":
        return filtered

    available_values = sorted(filtered[filter_column].dropna().astype(str).unique())
    selected_values = st.sidebar.multiselect(
        "Valores incluidos",
        options=available_values,
        default=available_values,
    )

    if selected_values:
        filtered = filtered[filtered[filter_column].astype(str).isin(selected_values)]

    return filtered


# ==============================================================================
# BLOQUE 3: INDICADORES (KPIs)
# ==============================================================================
# Los KPIs (Key Performance Indicators) son numeros grandes que resumen
# el estado de los datos. Deben ser:
#   - Claros (que significa el numero).
#   - Relevantes (responde una pregunta importante).
#   - Accionables (sugiere una decision).
#
# KPIs actuales:
#   - Registros: total de filas.
#   - Columnas: total de columnas.
#   - Faltantes promedio: % de valores faltantes.
#   - Promedio de la primera variable numerica.
#
# Los estudiantes pueden cambiar estos KPIs para su proyecto.
# Referencia: guia de color -> "KPIs: usar color con moderacion"

def render_kpis(df: pd.DataFrame, numeric_columns: list[str]) -> None:
    """Muestra indicadores generales en la vista ejecutiva."""

    total_rows = len(df)
    total_columns = len(df.columns)
    missing_pct = float(df.isna().mean().mean() * 100) if total_rows else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registros", f"{total_rows:,}")
    col2.metric("Columnas", total_columns)
    col3.metric("Faltantes promedio", f"{missing_pct:.1f}%")

    if numeric_columns:
        first_numeric = numeric_columns[0]
        col4.metric(
            f"Promedio {first_numeric}",
            f"{df[first_numeric].mean():.2f}",
        )
    else:
        col4.metric("Variables numericas", 0)


# ==============================================================================
# BLOQUE 4: INICIO DE LA APP (FLUJO PRINCIPAL)
# ==============================================================================
# A partir de aqui, el codigo se ejecuta SECUENCIALMENTE en cada
# interaccion del usuario con Streamlit.

# 4.1 Cargar datos.
df = load_dataset()

# 4.2 Perfilar columnas (detectar tipos).
profile = data_loader.profile_columns(df)

# 4.3 Aplicar filtros de la barra lateral.
filtered_df = apply_sidebar_filters(df, profile.categorical)

# 4.4 Re-perfilar despues del filtro (pueden haber cambiado los tipos).
filtered_profile = data_loader.profile_columns(filtered_df)

# 4.5 Titulo y subtitulo del dashboard.
st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

# 4.6 Si el filtro dejo cero registros, mostrar advertencia y detener.
if filtered_df.empty:
    st.warning("No hay registros con los filtros actuales.")
    st.stop()

# 4.7 Crear las pestanas del dashboard.
# Cada pestana representa una etapa del flujo analitico:
#   Datos -> Estadistica -> Features -> Modelo -> Clustering -> Dashboard
tabs = st.tabs(
    [
        "Datos",
        "Estadistica",
        "Feature engineering",
        "Modelo",
        "Clustering",
        "Dashboard",
    ]
)


# ==============================================================================
# PESTANA 1: DATOS
# ==============================================================================
# Muestra una vista general del dataset: KPIs, primeras filas, tipos de
# columnas y valores faltantes.
#
# Esta pestana es el "control de calidad" inicial.
# Pregunta: "?Que debemos revisar antes de modelar?"
# - ?Cuantos registros tenemos?
# - ?Hay valores faltantes?
# - ?Los tipos de datos son correctos?
# - ?Hay columnas que no necesitamos?

with tabs[0]:
    st.subheader("Vista general del dataset")
    render_kpis(filtered_df, filtered_profile.numeric)

    left, right = st.columns([1.2, 1])
    with left:
        st.dataframe(filtered_df.head(PREVIEW_ROWS), width="stretch")

    with right:
        type_table = pd.DataFrame(
            {
                "tipo": ["numericas", "categoricas", "fechas", "booleanas"],
                "columnas": [
                    ", ".join(filtered_profile.numeric) or "N/A",
                    ", ".join(filtered_profile.categorical) or "N/A",
                    ", ".join(filtered_profile.datetime) or "N/A",
                    ", ".join(filtered_profile.boolean) or "N/A",
                ],
            }
        )
        st.dataframe(type_table, width="stretch", hide_index=True)

    st.subheader("Valores faltantes")
    st.dataframe(
        data_loader.missing_values_table(filtered_df),
        width="stretch",
        hide_index=True,
    )


# ==============================================================================
# PESTANA 2: ESTADISTICA DESCRIPTIVA
# ==============================================================================
# Aqui exploramos los datos:
# - Variables numericas: histograma + boxplot + tabla descriptiva.
# - Variables categoricas: grafica de barras con frecuencias.
# - Correlacion entre variables numericas.
#
# Referencia: guia de graficos
#   - 1 numerica + distribucion -> Histograma
#   - 1 numerica + dispersion -> Boxplot
#   - 3+ numericas + correlacion -> Heatmap
#   - 1 categorica + frecuencia -> Barras

with tabs[1]:
    st.subheader("Estadistica descriptiva")

    if filtered_profile.numeric:
        numeric_column = st.selectbox(
            "Variable numerica",
            options=filtered_profile.numeric,
            key="numeric_for_stats",
        )

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                viz.numeric_histogram(filtered_df, numeric_column),
                use_container_width=True,
                key="stats_numeric_histogram",
            )
        with col2:
            st.plotly_chart(
                viz.numeric_boxplot(filtered_df, numeric_column),
                use_container_width=True,
                key="stats_numeric_boxplot",
            )

        st.dataframe(
            analytics.describe_numeric_columns(filtered_df, filtered_profile.numeric),
            width="stretch",
            hide_index=True,
        )

        if len(filtered_profile.numeric) >= 2:
            st.plotly_chart(
                viz.correlation_heatmap(filtered_df, filtered_profile.numeric),
                use_container_width=True,
                key="stats_correlation_heatmap",
            )
    else:
        st.info("El dataset no tiene columnas numericas.")

    if filtered_profile.categorical:
        categorical_column = st.selectbox(
            "Variable categorica",
            options=filtered_profile.categorical,
            key="categorical_for_stats",
        )
        st.plotly_chart(
            viz.category_bar_chart(filtered_df, categorical_column),
            use_container_width=True,
            key="stats_category_bar",
        )


# ==============================================================================
# PESTANA 3: FEATURE ENGINEERING
# ==============================================================================
# Creamos variables derivadas a partir de columnas de fecha.
# Esto permite que el modelo detecte patrones temporales.
#
# Si el dataset no tiene fechas, mostramos un mensaje informativo.
# En un proyecto real, los estudiantes pueden agregar aqui otras
# transformaciones: proporciones, agregados, interacciones, etc.

with tabs[2]:
    st.subheader("Variables derivadas")

    if filtered_profile.datetime:
        selected_dates = st.multiselect(
            "Columnas de fecha",
            options=filtered_profile.datetime,
            default=filtered_profile.datetime,
        )
        featured_df = analytics.add_date_features(filtered_df, selected_dates)
    else:
        selected_dates = []
        featured_df = filtered_df.copy()
        st.info("No se detectaron columnas de fecha.")

    new_columns = [column for column in featured_df.columns if column not in filtered_df.columns]

    st.write("Columnas nuevas:", ", ".join(new_columns) if new_columns else "Ninguna")
    st.dataframe(featured_df.head(PREVIEW_ROWS), width="stretch")


# ==============================================================================
# PESTANA 4: MODELO SUPERVISADO
# ==============================================================================
# Entrena un Random Forest para clasificacion o regresion.
#
# Flujo:
#   1. Elegir variable objetivo (lo que queremos predecir).
#   2. Elegir variables predictoras (con que informacion predecimos).
#   3. Presionar "Entrenar modelo".
#   4. Revisar metricas y grafica de importancia.
#
# Preguntas clave para clase:
#   - "?Podemos predecir X con estas variables?"
#   - "?Que variables son las mas importantes?"
#   - "?El modelo generaliza o solo memoriza?"
#   - "?La metrica elegida corresponde al costo real del error?"
#
# Ver tambien: manual_profesores.md -> Bloque 5. Modelos supervisados

with tabs[3]:
    st.subheader("Modelo supervisado")

    # Usamos las features de fecha (si existen) para el modelo.
    model_df = analytics.add_date_features(filtered_df, filtered_profile.datetime)
    model_profile = data_loader.profile_columns(model_df)

    candidate_columns = (
        model_profile.numeric
        + model_profile.categorical
        + model_profile.boolean
    )
    candidate_targets = [column for column in candidate_columns if column in model_df.columns]

    if len(candidate_targets) < 2:
        st.info("Se necesitan al menos dos columnas utiles para entrenar un modelo.")
    else:
        target_column = st.selectbox(
            "Variable objetivo",
            options=candidate_targets,
            index=len(candidate_targets) - 1,
        )

        feature_options = [column for column in candidate_columns if column != target_column]
        default_features = feature_options[: min(8, len(feature_options))]
        feature_columns = st.multiselect(
            "Variables predictoras",
            options=feature_options,
            default=default_features,
        )

        enough_target_values = model_df[target_column].dropna().nunique() >= 2
        enough_features = len(feature_columns) >= 1

        if st.button("Entrenar modelo", type="primary") and enough_features and enough_target_values:
            result = analytics.train_supervised_model(
                model_df,
                target_column=target_column,
                feature_columns=feature_columns,
            )

            metric_col, importance_col = st.columns([1, 1.2])
            with metric_col:
                st.markdown(f"Tipo de problema: `{result.problem_type}`")
                st.dataframe(result.metrics, width="stretch", hide_index=True)

                if result.confusion is not None:
                    st.markdown("Matriz de confusion")
                    st.dataframe(result.confusion, width="stretch")

            with importance_col:
                st.plotly_chart(
                    viz.feature_importance_bar(result.feature_importance),
                    use_container_width=True,
                    key="model_feature_importance",
                )

            if result.problem_type == "regression":
                st.plotly_chart(
                    viz.prediction_scatter(result.predictions),
                    use_container_width=True,
                    key="model_prediction_scatter",
                )
            else:
                st.dataframe(
                    result.predictions.head(PREVIEW_ROWS),
                    width="stretch",
                    hide_index=True,
                )
        elif not enough_target_values:
            st.warning("La variable objetivo necesita al menos dos valores distintos.")
        elif not enough_features:
            st.warning("Selecciona al menos una variable predictora.")


# ==============================================================================
# PESTANA 5: CLUSTERING
# ==============================================================================
# Agrupa observaciones similares usando K-Means.
#
# Flujo:
#   1. Elegir variables para clusterizar.
#   2. Elegir numero de clusters (k).
#   3. Presionar "Calcular clusters".
#   4. Revisar el perfil de cada cluster.
#
# Interpretacion en clase:
#   - Los clusters NO son verdades absolutas; dependen de las variables
#     seleccionadas y del escalamiento.
#   - La silueta ayuda a elegir k, pero el contexto es mas importante.
#   - Nombrar los clusters ayuda a comunicar los hallazgos.
#
# Ver: manual_profesores.md -> Bloque 6. Clustering

with tabs[4]:
    st.subheader("Clustering")

    cluster_df = analytics.add_date_features(filtered_df, filtered_profile.datetime)
    cluster_profile = data_loader.profile_columns(cluster_df)
    cluster_candidates = (
        cluster_profile.numeric
        + cluster_profile.categorical
        + cluster_profile.boolean
    )

    if len(cluster_candidates) < 2:
        st.info("Se necesitan al menos dos columnas para formar clusters.")
    else:
        default_cluster_features = cluster_candidates[: min(5, len(cluster_candidates))]
        cluster_features = st.multiselect(
            "Variables para clusterizar",
            options=cluster_candidates,
            default=default_cluster_features,
        )
        n_clusters = st.slider("Numero de clusters", min_value=2, max_value=8, value=3)

        if st.button("Calcular clusters", type="primary") and len(cluster_features) >= 2:
            cluster_result = analytics.run_clustering(
                cluster_df,
                feature_columns=cluster_features,
                n_clusters=n_clusters,
            )

            if cluster_result.silhouette is not None:
                st.metric("Silueta", f"{cluster_result.silhouette:.3f}")

            st.dataframe(
                cluster_result.profile,
                width="stretch",
                hide_index=True,
            )

            numeric_for_scatter = [
                column
                for column in cluster_features
                if pd.api.types.is_numeric_dtype(cluster_result.data_with_clusters[column])
            ]

            if len(numeric_for_scatter) >= 2:
                st.plotly_chart(
                    viz.cluster_scatter(
                        cluster_result.data_with_clusters,
                        x_column=numeric_for_scatter[0],
                        y_column=numeric_for_scatter[1],
                    ),
                    use_container_width=True,
                    key="cluster_scatter",
                )
            else:
                st.dataframe(
                    cluster_result.data_with_clusters.head(PREVIEW_ROWS),
                    width="stretch",
                )
        elif len(cluster_features) < 2:
            st.warning("Selecciona al menos dos variables para clustering.")


# ==============================================================================
# PESTANA 6: DASHBOARD (VISTA EJECUTIVA)
# ==============================================================================
# Esta es la pestana de PRESENTACION. Debe responder:
#   - ?Cual es el hallazgo principal?
#   - ?Que datos se estan mostrando?
#   - ?Que decision podria tomarse con esta informacion?
#
# A diferencia de las pestanas anteriores (que son exploratorias),
# esta pestana debe CONTAR UNA HISTORIA.
#
# Los estudiantes deben personalizar esta pestana para su proyecto:
#   - Cambiar KPIs.
#   - Elegir las graficas que mejor comunican su hallazgo.
#   - Agregar interpretaciones en texto.
#
# Referencia: guia de color -> "Checklist visual antes de entregar"

with tabs[5]:
    st.subheader("Vista ejecutiva")
    render_kpis(filtered_df, filtered_profile.numeric)

    chart_col, table_col = st.columns([1.2, 1])

    with chart_col:
        if filtered_profile.numeric:
            dashboard_numeric = st.selectbox(
                "Metrica principal",
                options=filtered_profile.numeric,
                key="dashboard_metric",
            )
            st.plotly_chart(
                viz.numeric_histogram(filtered_df, dashboard_numeric),
                use_container_width=True,
                key="dashboard_numeric_histogram",
            )

    with table_col:
        if filtered_profile.categorical:
            dashboard_category = st.selectbox(
                "Dimension de comparacion",
                options=filtered_profile.categorical,
                key="dashboard_category",
            )
            st.plotly_chart(
                viz.category_bar_chart(filtered_df, dashboard_category, top_n=10),
                use_container_width=True,
                key="dashboard_category_bar",
            )

    st.subheader("Datos filtrados")
    st.dataframe(filtered_df.head(PREVIEW_ROWS), width="stretch")
