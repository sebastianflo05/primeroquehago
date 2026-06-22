"""Visualizaciones reutilizables para el dashboard.

================================================================================
PROPOSITO DE ESTE ARCHIVO
================================================================================
Todas las graficas de Plotly viven aqui, separadas de la logica de la app.
Esto permite que los estudiantes modifiquen o agreguen una grafica sin tener
que entender todo app.py.

CADA grafica en este archivo fue elegida por una razon especifica segun el
tipo de dato que muestra. Ver la guia de color y graficos para la justificacion
completa: guia_color_visualizacion_datos.md -> "Guia de graficos segun tipo de datos"

================================================================================
GUIA RAPIDA: QUE GRAFICA USAR SEGUN TUS DATOS
================================================================================
| Que quieres mostrar           | Tipo de variable     | Grafica que usamos aqui |
|-------------------------------|----------------------|-------------------------|
| Distribucion de un valor      | 1 numerica           | Histograma              |
| Dispersion y valores atipicos | 1 numerica           | Boxplot                 |
| Frecuencia de categorias      | 1 categorica         | Barras horizontales     |
| Correlacion entre numericas   | 2+ numericas         | Mapa de calor           |
| Importancia del modelo        | features + peso      | Barras de importancia   |
| Prediccion vs realidad        | 2 numericas          | Dispersion (scatter)    |
| Agrupacion por clusters       | 2 numericas + grupo  | Dispersion coloreada    |

================================================================================
PALETA DE COLORES
================================================================================
Todas las graficas usan los colores definidos en config.py.
Si cambias un color en config.py, se actualiza automaticamente en todas las
graficas. Esto sigue el principio de la guia de color: "un color debe significar
lo mismo en todo el dashboard".

Ver: guia_color_visualizacion_datos.md -> seccion "Mantener consistencia"
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px

from config import COLOR_PRIMARY, COLOR_SECONDARY


# ==============================================================================
# 1 NUMERICA -> HISTOGRAMA
# ==============================================================================
# Por que histograma? (ver guia de graficos: "Distribucion de un valor")
# - Muestra la forma de la distribucion: simetrica, sesgada, multimodal.
# - Revela valores extremos y concentraciones.
# - Facil de interpretar para audiencias no tecnicas.
#
# Por que 24 bins?
# - Muy pocos bins (ej: 5) esconden la forma de la distribucion.
# - Muchos bins (ej: 100) muestran ruido que confunde.
# - 24 es un balance razonable para datasets de tamano pequeno a mediano.

def numeric_histogram(df: pd.DataFrame, column: str):
    """Histograma para revisar la distribucion de una variable numerica."""
    return px.histogram(
        df,
        x=column,
        nbins=24,
        color_discrete_sequence=[COLOR_PRIMARY],
        title=f"Distribucion de {column}",
    )


# ==============================================================================
# 1 NUMERICA -> BOXPLOT
# ==============================================================================
# Por que boxplot? (ver guia: "Resumir distribucion por grupo")
# - Muestra mediana, cuartiles y valores atipicos en una sola grafica.
# - Complementa al histograma: el histograma muestra la FORMA, el boxplot
#   muestra la DISPERSION y los VALORES EXTREMOS.
#
# La opcion points="outliers" resalta los valores atipicos.
# Pregunta para clase: "?Que consideramos un valor atipico en un boxplot?"
# (R: valores que caen fuera de 1.5 * rango intercuartil)

def numeric_boxplot(df: pd.DataFrame, column: str):
    """Boxplot para detectar dispersion y posibles valores atipicos."""
    return px.box(
        df,
        y=column,
        points="outliers",
        color_discrete_sequence=[COLOR_SECONDARY],
        title=f"Variabilidad de {column}",
    )


# ==============================================================================
# 1 CATEGORICA -> BARRAS HORIZONTALES
# ==============================================================================
# Por que barras horizontales? (ver guia: "Comparar grupos", "Ranking")
# - Las barras horizontales son mas faciles de leer cuando las etiquetas
#   de categoria son largas (el texto se lee de izquierda a derecha).
# - Ordenar por frecuencia ayuda a identificar rapidamente las categorias
#   mas y menos comunes.
#
# Por que top_n=15?
# - Mas de 15 categorias en una grafica de barras se vuelve ilegible.
# - Si hay mas de 15, conviene agrupar las restantes como "Otros".
#   (Ver guia de color: "Errores frecuentes -> Demasiadas categorias")

def category_bar_chart(df: pd.DataFrame, column: str, top_n: int = 15):
    """Grafica de barras para las categorias mas frecuentes."""
    counts = (
        df[column]
        .astype(str)
        .value_counts(dropna=False)
        .head(top_n)
        .rename_axis(column)
        .reset_index(name="conteo")
    )
    return px.bar(
        counts,
        x="conteo",
        y=column,
        orientation="h",
        color_discrete_sequence=[COLOR_PRIMARY],
        title=f"Frecuencia de {column}",
    )


# ==============================================================================
# 2+ NUMERICAS -> MAPA DE CALOR (HEATMAP)
# ==============================================================================
# Por que heatmap? (ver guia: "Correlacion entre muchas numericas")
# - Resumen visual de correlaciones en una sola tabla coloreada.
# - Los colores claros/oscuros muestran la fuerza de la correlacion.
# - Usamos la escala RdBu_r (rojo-azul) porque es una paleta divergente:
#   - Rojo: correlacion negativa.
#   - Azul: correlacion positiva.
#   - Blanco: sin correlacion.
# - zmin=-1, zmax=1: fija la escala de correlacion de -1 a 1.
# - text_auto: muestra el valor numerico dentro de cada celda.
#
# Referencia: guia de color -> "Paleta divergente"

def correlation_heatmap(df: pd.DataFrame, numeric_columns: list[str]):
    """Mapa de calor de correlaciones entre variables numericas."""
    corr = df[numeric_columns].corr(numeric_only=True)

    return px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Correlacion entre variables numericas",
    )


# ==============================================================================
# FEATURES DEL MODELO -> BARRAS DE IMPORTANCIA
# ==============================================================================
# Por que barras? (ver guia: "Ranking u orden")
# - La importancia de variables es inherentemente un ranking.
# - Las barras horizontales ordenadas permiten ver de un vistazo
#   cuales variables contribuyen mas al modelo.
# - Solo mostramos las 15 mas importantes (top de analytics.py).
#
# Interpretacion en clase:
# - "importancia" NO significa causalidad. Solo indica que la variable
#   fue util para hacer predicciones en ESTE modelo con ESTOS datos.
# - Una variable con baja importancia no es "inutil"; podria ser util
#   en otro modelo o con otra transformacion.

def feature_importance_bar(feature_importance: pd.DataFrame):
    """Grafica de importancia de variables del modelo supervisado."""
    return px.bar(
        feature_importance.sort_values("importancia"),
        x="importancia",
        y="feature",
        orientation="h",
        color_discrete_sequence=[COLOR_PRIMARY],
        title="Variables mas influyentes del modelo",
    )


# ==============================================================================
# 2 NUMERICAS (REAL VS PREDICCION) -> SCATTER
# ==============================================================================
# Por que scatter? (ver guia: "Relacion entre dos numericas")
# - Muestra la relacion entre el valor real y la prediccion.
# - Si el modelo es bueno, los puntos deben alinearse cerca de la
#   diagonal y = x (aunque no dibujamos la linea explicitamente).
# - Puntos lejos de la diagonal son errores de prediccion.
#
# Esta grafica solo se muestra para problemas de regresion.
# Para clasificacion usamos una tabla de predicciones.

def prediction_scatter(predictions: pd.DataFrame):
    """Comparacion entre valor real y prediccion para regresion."""
    return px.scatter(
        predictions,
        x="valor_real",
        y="prediccion",
        color_discrete_sequence=[COLOR_PRIMARY],
        title="Valor real vs. prediccion",
    )


# ==============================================================================
# 2 NUMERICAS + CLUSTER -> SCATTER COLOREADO
# ==============================================================================
# Por que scatter coloreado? (ver guia: "Clusters o grupos naturales")
# - Permite ver como se separan los clusters en el espacio 2D.
# - Cada color representa un cluster diferente.
# - Usamos la paleta cualitativa Set2 de Plotly (8 colores suaves).
#
# Limitacion: solo muestra 2 dimensiones. Los clusters se calculan
# con mas variables pero solo podemos visualizar 2 a la vez.
# Por eso permitimos elegir que columnas graficar.

def cluster_scatter(df: pd.DataFrame, x_column: str, y_column: str):
    """Dispersion 2D coloreada por cluster."""
    return px.scatter(
        df,
        x=x_column,
        y=y_column,
        color=df["cluster"].astype(str),
        title=f"Clusters segun {x_column} y {y_column}",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
