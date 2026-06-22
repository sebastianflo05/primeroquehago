"""Funciones analiticas: estadistica, features, modelo y clustering.

================================================================================
PROPOSITO DE ESTE ARCHIVO
================================================================================
Contiene toda la logica de analisis de datos que NO es carga de datos NI
visualizacion. Esto incluye:

  - Estadistica descriptiva (tabla resumen de columnas numericas).
  - Feature engineering (creacion de variables derivadas de fechas).
  - Modelo supervisado (Random Forest para clasificacion o regresion).
  - Clustering (K-Means con perfil de clusters).

Las funciones estan escritas para ser DIDACTICAS, no optimas en produccion.
Priorizamos claridad sobre velocidad, y devolvemos DataFrames que se pueden
mostrar directamente en Streamlit.

================================================================================
ORDEN DE LAS SECCIONES (seguir este orden en clase)
================================================================================
1. Estadistica descriptiva       -> ?Que dicen los datos por si solos?
2. Feature engineering           -> ?Que nuevas variables podemos crear?
3. Modelo supervisado            -> ?Podemos predecir algo?
4. Clustering                    -> ?Hay grupos naturales en los datos?

Este orden refleja el flujo analitico recomendado en el manual del profesor.

ALCANCE DE LA SESION DE DASHBOARDS
==================================
Este modulo se entrega como referencia avanzada, pero NO se programa durante
la sesion de dos horas sobre KPIs, graficas, color, storytelling y GitHub.
Los comentarios permiten que estudiantes de distintas carreras reconozcan:

  - que entra al algoritmo,
  - que transformaciones se realizan,
  - que resultado devuelve,
  - que limitaciones deben mencionar.

El dashboard principal puede funcionar sin modificar este archivo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    silhouette_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config import RANDOM_STATE


# ==============================================================================
# TIPOS AUXILIARES
# ==============================================================================

ProblemType = Literal["classification", "regression"]


# ==============================================================================
# DATACLASSES DE RESULTADOS
# ==============================================================================
# Usamos dataclasses para agrupar los resultados de cada operacion.
# Esto es mejor que devolver tuplas porque:
#   1. Tiene nombres claros (result.metrics, no result[0]).
#   2. Es facil agregar nuevos campos sin romper codigo existente.
#   3. Streamlit puede mostrar dataclasses directamente.

@dataclass
class ModelResult:
    """Paquete con todo lo necesario para interpretar el modelo.

    Atributos:
        problem_type: "classification" o "regression".
        metrics: DataFrame con metricas de evaluacion.
        feature_importance: DataFrame con importancia de cada variable.
        predictions: DataFrame con valor real vs prediccion.
        confusion: Matriz de confusion (solo clasificacion) o None.
    """

    problem_type: ProblemType
    metrics: pd.DataFrame
    feature_importance: pd.DataFrame
    predictions: pd.DataFrame
    confusion: pd.DataFrame | None


@dataclass
class ClusterResult:
    """Paquete con resultados de clustering.

    Atributos:
        data_with_clusters: DataFrame original + columna "cluster".
        profile: DataFrame con perfil promedio de cada cluster.
        silhouette: Coeficiente de silueta (calidad de clusters) o None.
    """

    data_with_clusters: pd.DataFrame
    profile: pd.DataFrame
    silhouette: float | None


# ==============================================================================
# 1. FEATURE ENGINEERING: VARIABLES DERIVADAS DE FECHAS
# ==============================================================================
# Por que crear features de fecha?
# - Una fecha como "2026-03-15" no es util para un modelo matematico.
# - Pero "mes=3" o "dia_semana=0" si lo son: el modelo puede detectar
#   patrones como "en diciembre las ventas suben" o "los lunes hay mas errores".
#
# Que creamos:
#   Para cada columna de fecha "fecha_inscripcion", creamos:
#   - fecha_inscripcion_anio: el anio (2025, 2026...).
#   - fecha_inscripcion_mes: el mes (1-12).
#   - fecha_inscripcion_dia_semana: dia de la semana (0=lunes, 6=domingo).

def add_date_features(df: pd.DataFrame, date_columns: list[str]) -> pd.DataFrame:
    """Agrega columnas derivadas de fechas (anio, mes, dia_semana)."""
    featured = df.copy()

    for column in date_columns:
        if column not in featured.columns:
            continue

        dates = pd.to_datetime(featured[column], errors="coerce")
        featured[f"{column}_anio"] = dates.dt.year
        featured[f"{column}_mes"] = dates.dt.month
        featured[f"{column}_dia_semana"] = dates.dt.dayofweek

    return featured


# ==============================================================================
# 2. MODELO SUPERVISADO
# ==============================================================================

def infer_problem_type(target: pd.Series) -> ProblemType:
    """Decide si el problema es clasificacion o regresion.

    Regla:
    - Si la variable es numerica Y tiene mas de 10 valores unicos -> regresion.
    - En cualquier otro caso -> clasificacion.

    Esta es una regla SIMPLIFICADA para propositos didacticos.
    En la practica, la decision depende del significado del negocio,
    no solo de los datos.
    """
    unique_values = target.dropna().nunique()
    is_numeric = pd.api.types.is_numeric_dtype(target)

    if is_numeric and unique_values > 10:
        return "regression"

    return "classification"


def _split_columns_by_type(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Separa columnas numericas y categoricas para preprocesamiento."""
    numeric_features = df.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = [
        column for column in df.columns if column not in numeric_features
    ]
    return numeric_features, categorical_features


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """Crea el preprocesador de datos para modelos y clustering.

    Que hace el preprocesador:
    1. Columnas numericas:
       - Imputa valores faltantes con la mediana.
       - Escala con StandardScaler (media=0, desviacion=1).
    2. Columnas categoricas:
       - Imputa valores faltantes con la moda (valor mas frecuente).
       - One-hot encoding: convierte cada categoria en una columna binaria.
    3. El resto de columnas se descartan (remainder="drop").

    Por que es necesario?
    - Los modelos de sklearn no aceptan valores faltantes.
    - Los modelos basados en distancia (K-Means, SVM) necesitan
      variables en la misma escala.
    - sklearn solo trabaja con numeros; las categorias hay que
      convertirlas a numeros (one-hot encoding).
    """
    numeric_features, categorical_features = _split_columns_by_type(X)

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
    )


def _get_feature_names(preprocessor: ColumnTransformer) -> list[str]:
    """Obtiene nombres de columnas despues del one-hot encoding.

    Despues de one-hot encoding, una columna "color" con valores
    ["rojo", "verde", "azul"] se convierte en tres columnas:
    ["color_azul", "color_rojo", "color_verde"].

    Esta funcion recupera esos nombres para que la grafica de
    importancia de variables tenga etiquetas legibles.
    """
    try:
        return preprocessor.get_feature_names_out().tolist()
    except Exception:
        return [f"feature_{idx}" for idx in range(len(preprocessor.transformers_))]


def train_supervised_model(
    df: pd.DataFrame,
    target_column: str,
    feature_columns: list[str],
) -> ModelResult:
    """Entrena un modelo supervisado (Random Forest) y evalua.

    ============================================================================
    FLUJO DEL MODELO (explicar paso a paso en clase)
    ============================================================================
    1. Separar X (predictoras) y y (objetivo).
    2. Dividir en entrenamiento (75%) y prueba (25%).
       - Entrenamiento: el modelo "aprende" de estos datos.
       - Prueba: evaluamos que tan bien aprendio con datos NUEVOS.
       (Pregunta clave: "?Por que no evaluamos con los mismos datos
        de entrenamiento?" -> porque el modelo podria solo memorizar).
    3. Crear preprocesador (imputacion + escalamiento + one-hot).
    4. Elegir modelo segun el tipo de problema:
       - CLASIFICACION: RandomForestClassifier.
       - REGRESION: RandomForestRegressor.
    5. Entrenar (fit) y predecir (predict).
    6. Evaluar con metricas apropiadas.
    7. Calcular importancia de variables.
    8. Devolver todo en un ModelResult.

    ============================================================================
    POR QUE RANDOM FOREST?
    ============================================================================
    - Funciona bien con datos mixtos (numericos y categoricos).
    - No requiere escalamiento de variables (aunque igual escalamos
      por compatibilidad con el pipeline).
    - Da importancia de variables "out of the box".
    - Es robusto a valores atipicos y faltantes.
    - Es facil de explicar en clase: "un bosque de muchos arboles de decision".
    """
    modeling_df = df[feature_columns + [target_column]].dropna(subset=[target_column])
    X = modeling_df[feature_columns]
    y = modeling_df[target_column]

    problem_type = infer_problem_type(y)

    # Estratificacion: para clasificacion, mantener la proporcion de
    # clases en entrenamiento y prueba. Si hay 80% "Si" y 20% "No",
    # ambos conjuntos deben tener esa misma proporcion.
    stratify = y if problem_type == "classification" and y.nunique() > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    preprocessor = build_preprocessor(X_train)

    if problem_type == "classification":
        model = RandomForestClassifier(
            n_estimators=200,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
        )
    else:
        model = RandomForestRegressor(
            n_estimators=200,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
        )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    if problem_type == "classification":
        metrics = pd.DataFrame(
            {
                "metrica": ["accuracy", "f1_macro"],
                "valor": [
                    accuracy_score(y_test, y_pred),
                    f1_score(y_test, y_pred, average="macro", zero_division=0),
                ],
            }
        )
        # Matriz de confusion: muestra donde el modelo acierta y donde se equivoca.
        # Las filas son valores REALES, las columnas son PREDICCIONES.
        # La diagonal son aciertos; fuera de la diagonal son errores.
        labels = sorted(pd.Series(y_test).astype(str).unique().tolist())
        confusion = pd.DataFrame(
            confusion_matrix(y_test.astype(str), pd.Series(y_pred).astype(str), labels=labels),
            index=[f"real_{label}" for label in labels],
            columns=[f"pred_{label}" for label in labels],
        )
    else:
        rmse = mean_squared_error(y_test, y_pred) ** 0.5
        metrics = pd.DataFrame(
            {
                "metrica": ["mae", "rmse", "r2"],
                "valor": [
                    mean_absolute_error(y_test, y_pred),
                    rmse,
                    r2_score(y_test, y_pred),
                ],
            }
        )
        confusion = None

    # Importancia de variables (feature importance).
    # Random Forest mide que tan util fue cada variable para reducir
    # la impureza en los arboles de decision.
    feature_names = _get_feature_names(pipeline.named_steps["preprocessor"])
    importances = pipeline.named_steps["model"].feature_importances_

    feature_importance = (
        pd.DataFrame({"feature": feature_names, "importancia": importances})
        .sort_values("importancia", ascending=False)
        .head(15)
        .reset_index(drop=True)
    )

    predictions = pd.DataFrame(
        {
            "valor_real": y_test.reset_index(drop=True),
            "prediccion": pd.Series(y_pred),
        }
    )

    return ModelResult(
        problem_type=problem_type,
        metrics=metrics.round(4),
        feature_importance=feature_importance,
        predictions=predictions,
        confusion=confusion,
    )


# ==============================================================================
# 3. CLUSTERING (K-MEANS)
# ==============================================================================
# MODULO AVANZADO - NO SE PROGRAMA EN LA SESION DE DASHBOARDS.
#
# Por que K-Means?
# - Es el algoritmo de clustering mas intuitivo.
# - La idea es simple: cada punto pertenece al cluster cuyo centro
#   esta mas cercano.
# - Limitacion: asume que los clusters son esfericos y de tamano similar.
#
# Preguntas para clase:
# - "?Cuantos clusters elegir?" -> la silueta ayuda, pero el contexto
#   del negocio es mas importante.
# - "?Por que escalamos las variables?" -> K-Means usa distancia euclidiana;
#   si una variable va de 0 a 1 y otra de 0 a 1000, la segunda domina
#
# Ejemplos por disciplina:
# - Finanzas: agrupar clientes por frecuencia, gasto y morosidad.
# - Biomedicina: explorar perfiles de pacientes por mediciones comparables.
# - Educacion: encontrar perfiles de participacion y rendimiento.
# - Humanidades: agrupar documentos por frecuencias de temas ya cuantificadas.
#
# Precaucion:
# Un cluster no es una etiqueta verdadera ni una causa. Es una agrupacion
# matematica que cambia cuando cambian las variables, la escala o el valor de k.

def run_clustering(
    df: pd.DataFrame,
    feature_columns: list[str],
    n_clusters: int,
) -> ClusterResult:
    """Ejecuta K-Means y perfila los clusters resultantes."""
    cluster_df = df[feature_columns].copy()
    preprocessor = build_preprocessor(cluster_df)
    X_processed = preprocessor.fit_transform(cluster_df)

    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=RANDOM_STATE,
        n_init=10,
    )
    labels = kmeans.fit_predict(X_processed)

    data_with_clusters = df.copy()
    data_with_clusters["cluster"] = labels

    # Coeficiente de silueta: mide que tan separados estan los clusters.
    # Rango de -1 a 1:
    #   > 0.5: los clusters estan bien separados.
    #   0 a 0.5: clusters con algo de superposicion.
    #   < 0: las observaciones estan en el cluster equivocado.
    silhouette = None
    if n_clusters > 1 and len(set(labels)) > 1 and len(labels) > n_clusters:
        silhouette = float(silhouette_score(X_processed, labels))

    # Perfil de clusters: calculamos el promedio (numericas) y la moda
    # (categoricas) para cada cluster. Esto permite "nombrar" los clusters.
    # Ejemplo:
    #   Cluster 0: promedio_alto en calificaciones, moda aprobacion="Si".
    #   -> Podemos llamarlo "Rendimiento alto".
    profile_rows = []
    for cluster_id in sorted(data_with_clusters["cluster"].unique()):
        subset = data_with_clusters[data_with_clusters["cluster"] == cluster_id]
        row = {
            "cluster": cluster_id,
            "registros": len(subset),
            "porcentaje": round(len(subset) / len(data_with_clusters) * 100, 2),
        }
        for column in feature_columns:
            if pd.api.types.is_numeric_dtype(subset[column]):
                row[f"{column}_promedio"] = round(subset[column].mean(), 3)
            else:
                mode = subset[column].mode(dropna=True)
                row[f"{column}_moda"] = mode.iloc[0] if not mode.empty else None

        profile_rows.append(row)

    profile = pd.DataFrame(profile_rows)

    return ClusterResult(
        data_with_clusters=data_with_clusters,
        profile=profile,
        silhouette=silhouette,
    )


# ==============================================================================
# 4. ESTADISTICA DESCRIPTIVA
# ==============================================================================
# Tabla compacta con los principales estadisticos descriptivos.
# Usamos pandas .describe() que ya calcula:
#   count, mean, std, min, 25%, 50%, 75%, max.
#
# Por que esta tabla?
# - Antes de modelar, hay que entender los datos.
# - La media sin la desviacion estandar puede enganar.
# - Los percentiles muestran la distribucion completa.

def describe_numeric_columns(df: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
    """Tabla compacta con estadisticos descriptivos de columnas numericas.

    Muestra: count, mean, std, min, 25%, 50%, 75%, max.
    """
    if not numeric_columns:
        return pd.DataFrame()

    return (
        df[numeric_columns]
        .describe()
        .T[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
        .round(3)
        .reset_index()
        .rename(columns={"index": "columna"})
    )
