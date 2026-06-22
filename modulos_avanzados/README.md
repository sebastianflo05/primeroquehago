# Modulos avanzados

Estos archivos muestran como se implementan otras etapas del analisis:

- `app_flujo_completo.py`: interfaz completa que conecta todos los modulos.
- `analytics.py`: estadistica, feature engineering, modelo y clustering.
- `data_loader.py`: carga, limpieza y deteccion de tipos.
- `visualizations.py`: funciones reutilizables para graficas.
- `config.py`: titulos, rutas, colores y semilla aleatoria.

No se importan desde el esqueleto de la clase. Se incluyen para que el
estudiante pueda leerlos despues y reconocer el flujo completo sin que el
docente tenga que cubrirlos en las dos horas disponibles.

Para explorar la version completa despues de la clase:

```bash
streamlit run modulos_avanzados/app_flujo_completo.py
```

En particular, la seccion de clustering explica:

1. por que se escalan las variables;
2. como K-Means asigna observaciones;
3. que significa el coeficiente de silueta;
4. como se construye un perfil de cada grupo;
5. por que los clusters no deben interpretarse como verdades absolutas.
