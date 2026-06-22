"""Carga y preparacion de datos.

================================================================================
PROPOSITO DE ESTE ARCHIVO
================================================================================
Separa la logica de lectura y limpieza de datos de la interfaz visual.
La app principal (app.py) decide QUÉ mostrar; este modulo decide CÓMO
leer, limpiar y preparar los datos.

Esto sigue el principio de responsabilidad unica: cada archivo hace UNA cosa.
Si los estudiantes necesitan cambiar como se lee el CSV (encoding, separador,
manejo de errores), saben que deben mirar aqui y no en app.py.

================================================================================
CONCEPTOS PARA EXPLICAR EN CLASE
================================================================================
1. "Los datos nunca llegan limpios" -> siempre revisar tipos, faltantes, nombres.
2. "Cache" en Streamlit -> @st.cache_data evita recargar el CSV en cada clic.
3. "Perfil de columnas" -> clasificar columnas por tipo es el primer paso
   para saber que grafica usar (ver guia de graficos).
4. "Nombres consistentes" -> espacios, mayusculas y guiones causan errores
   silenciosos al seleccionar columnas por nombre en el codigo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO

import pandas as pd
import streamlit as st


# ==============================================================================
# PERFIL DE COLUMNAS
# ==============================================================================
# Esta estructura guarda los nombres de columnas agrupadas por tipo.
# La usamos en toda la app para saber:
#   - que columnas mostrar en selectores de graficas,
#   - que columnas pueden entrar al modelo,
#   - que columnas pueden usarse como filtros.
#
# Es como un "inventario" de los datos antes de empezar a analizar.

@dataclass
class ColumnProfile:
    """Resumen de tipos de columnas detectadas en el dataset.

    Atributos:
        numeric: columnas numericas (int, float).
        categorical: columnas de texto o categoria (object, string).
        datetime: columnas de fecha (datetime64).
        boolean: columnas verdadero/falso (bool).
    """

    numeric: list[str]
    categorical: list[str]
    datetime: list[str]
    boolean: list[str]


# ==============================================================================
# CARGA DE DATOS
# ==============================================================================

@st.cache_data(show_spinner=False)
def load_csv_from_path(path: str) -> pd.DataFrame:
    """Lee un CSV desde una ruta local.

    Por que usar cache:
    - Streamlit ejecuta el script completo en cada interaccion.
    - Sin cache, leeriamos el CSV desde disco en cada clic.
    - Con @st.cache_data, solo se lee UNA vez y se reusa hasta que el
      archivo cambie.

    Pregunta para clase:
    "?Que pasaria si el CSV tiene 2 millones de filas y no usamos cache?"
    (R: la app se volveria muy lenta porque leería el archivo en cada clic).
    """
    return pd.read_csv(path)


def load_csv_from_upload(uploaded_file: BinaryIO) -> pd.DataFrame:
    """Lee un CSV que el usuario sube desde la interfaz de Streamlit.

    Diferencia con load_csv_from_path:
    - load_csv_from_path: recibe un string (ruta).
    - load_csv_from_upload: recibe un objeto de archivo binario.
    Ambas devuelven un DataFrame porque pandas.read_csv acepta ambos.
    """
    return pd.read_csv(uploaded_file)


# ==============================================================================
# LIMPIEZA DE COLUMNAS
# ==============================================================================

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza nombres de columnas: minusculas, sin espacios ni guiones.

    Por que es necesario:
    - Los CSV suelen tener nombres como "Calificacion Final" o "Edad-del-Estudiante".
    - En Python, los espacios y guiones causan errores: df["Calificacion Final"] funciona,
      pero es facil olvidar el nombre exacto.
    - Al normalizar a "calificacion_final", el codigo es mas predecible.

    Que hace esta funcion:
    1. Convierte a minusculas.
    2. Reemplaza espacios por guion bajo.
    3. Reemplaza guiones por guion bajo.

    Ejemplo:
        "Calificacion Final" -> "calificacion_final"
        "Fecha-Nacimiento" -> "fecha_nacimiento"
    """
    cleaned = df.copy()
    cleaned.columns = [
        str(col).strip().lower().replace(" ", "_").replace("-", "_")
        for col in cleaned.columns
    ]
    return cleaned


def parse_possible_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Intenta convertir a datetime las columnas con nombres de fecha.

    Estrategia:
    No revisamos TODAS las columnas (seria lento y arriesgado).
    Solo revisamos aquellas cuyo nombre contenga palabras clave:
    "fecha", "date", "dia", "day", "mes", "month".

    Si la columna parece una fecha y al menos el 70% de sus valores
    se pueden convertir, aplicamos la conversion.

    Por que 70%?
    - Si solo el 10% de los valores son fechas validas, probablemente
      la columna no es una fecha (o tiene datos muy sucios).
    - Si el 90% se convierte, podemos recuperar los pocos errores con coerce.
    """
    parsed = df.copy()
    date_tokens = ("fecha", "date", "dia", "day", "mes", "month")

    for column in parsed.columns:
        lower_name = str(column).lower()
        looks_like_date = any(token in lower_name for token in date_tokens)

        if looks_like_date and not pd.api.types.is_numeric_dtype(parsed[column]):
            converted = pd.to_datetime(parsed[column], errors="coerce")
            success_rate = converted.notna().mean()
            if success_rate >= 0.7:
                parsed[column] = converted

    return parsed


# ==============================================================================
# PERFILAMIENTO
# ==============================================================================

def profile_columns(df: pd.DataFrame) -> ColumnProfile:
    """Clasifica cada columna del dataset por su tipo de dato.

    Esta funcion es clave porque:
    - Las columnas numericas van a histogramas, boxplots, scatter, correlacion.
    - Las columnas categoricas van a graficas de barras, filtros, grupos.
    - Las columnas de fecha van a lineas de tiempo y feature engineering.
    - Las columnas booleanas van a modelos como variables dummy.

    Referencia: guia_color_visualizacion_datos.md -> "Guia de graficos segun tipo de datos"

    Logica de clasificacion:
    1. Numeric: pandas detecta automaticamente (int64, float64).
    2. Datetime: pandas detecta (datetime64[ns]).
    3. Boolean: pandas detecta (bool).
    4. Categorica: TODO lo que no es ninguno de los anteriores.
       Esto incluye object, string y cualquier otro tipo no numerico.
    """
    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    datetime = df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns.tolist()
    boolean = df.select_dtypes(include=["bool"]).columns.tolist()

    categorical = [
        column
        for column in df.columns
        if column not in numeric and column not in datetime and column not in boolean
    ]

    return ColumnProfile(
        numeric=numeric,
        categorical=categorical,
        datetime=datetime,
        boolean=boolean,
    )


def missing_values_table(df: pd.DataFrame) -> pd.DataFrame:
    """Tabla de valores faltantes: cuantos y que porcentaje por columna.

    Uso en clase:
    - Las columnas con muchos faltantes (>50%) probablemente no sirven.
    - Las columnas con pocos faltantes (<5%) se pueden imputar.
    - Los faltantes no son siempre "malos": a veces indican que un evento
      no aplica (ej: "fecha_baja" solo aplica si el estudiante se dio de baja).
    """
    total_missing = df.isna().sum()
    percent_missing = (total_missing / len(df)).fillna(0) * 100

    summary = pd.DataFrame(
        {
            "columna": total_missing.index,
            "faltantes": total_missing.values,
            "porcentaje_faltante": percent_missing.round(2).values,
        }
    )
    return summary.sort_values("porcentaje_faltante", ascending=False)


# ==============================================================================
# PREPARACION COMPLETA
# ==============================================================================

def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Preparacion inicial que aplica a TODOS los datasets.

    Pasos:
    1. Normalizar nombres de columnas.
    2. Detectar y convertir fechas.

    Nota para clase:
    Esta funcion se ejecuta automaticamente al cargar los datos.
    Si los estudiantes quieren agregar mas pasos de limpieza
    (ej: eliminar columnas innecesarias, filtrar filas), pueden
    agregarlos aqui o en app.py segun prefieran.
    """
    prepared = clean_column_names(df)
    prepared = parse_possible_dates(prepared)
    return prepared
