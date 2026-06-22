# Ejemplos de dashboard por disciplina

No copies un ejemplo literalmente. Primero identifica la pregunta que deseas
responder y despues sustituye los nombres de las columnas por los de tu CSV.

## Finanzas y administracion

**Pregunta:** ¿Como cambian los ingresos y que categorias concentran el gasto?

- KPIs: ingreso total, gasto total, margen y variacion contra presupuesto.
- Linea: ingreso o gasto por mes.
- Barras: gasto por categoria, sucursal o producto.
- Dispersion: riesgo contra rendimiento, o ingreso contra costo.
- Color: azul para informacion principal y naranja para desviaciones que
  requieren atencion.
- Limitacion: una variacion historica no garantiza el comportamiento futuro.

## Biomedicina y ciencias de la salud

**Pregunta:** ¿Como se distribuye una medicion y que grupos presentan
diferencias?

- KPIs: pacientes analizados, medicion promedio o mediana, faltantes y tasa de
  respuesta.
- Histograma: edad, biomarcador, presion o tiempo de recuperacion.
- Boxplot: medicion por tratamiento o grupo.
- Barras: participantes por diagnostico o resultado.
- Color: evitar depender solo de rojo y verde; usar etiquetas y patrones.
- Limitacion: una asociacion observacional no demuestra efecto clinico.

No incluyas nombres, expedientes ni otros identificadores personales en un
repositorio publico.

## Educacion

**Pregunta:** ¿Que patrones de rendimiento y participacion aparecen en el
grupo?

- KPIs: estudiantes, promedio, porcentaje de aprobacion y asistencia.
- Histograma: calificacion final.
- Barras: estudiantes por programa, grupo o modalidad.
- Dispersion: horas de estudio contra calificacion.
- Linea: asistencia o promedio por periodo.
- Color: reservar un color de atencion para riesgo academico, sin etiquetar a
  personas como problema.
- Limitacion: el dashboard describe patrones y no explica por si solo sus
  causas.

## Humanidades y ciencias sociales

**Pregunta:** ¿Que temas, periodos o fuentes dominan el corpus?

- KPIs: documentos, autores o fuentes, periodo cubierto y porcentaje
  clasificado.
- Barras: documentos por tema, archivo, region o categoria.
- Linea: publicaciones o menciones por año.
- Histograma: extension de textos, fecha o frecuencia de una medida.
- Heatmap: coocurrencia de temas cuando existe una matriz numerica adecuada.
- Color: usar tonos sobrios y destacar solo el tema central.
- Limitacion: convertir textos en conteos pierde matices del contexto.

## Ingenieria, ambiente y operaciones

**Pregunta:** ¿Como cambia el desempeño y donde aparecen fallas o consumos
atipicos?

- KPIs: produccion, eficiencia, consumo, fallas y tiempo fuera de servicio.
- Linea: medicion de sensor o produccion a traves del tiempo.
- Barras: fallas por equipo, planta o tipo.
- Dispersion: temperatura contra consumo, carga contra eficiencia.
- Histograma: duracion de procesos o mediciones de calidad.
- Color: azul para operacion normal, naranja para cercania a un limite y rojo
  solo para una condicion realmente critica.
- Limitacion: revisar calibracion, frecuencia de muestreo y periodos faltantes.

## Plantilla para cualquier carrera

Completa estas frases antes de programar:

```text
El usuario necesita decidir ______________________________________________.
El KPI principal sera __________________ porque ___________________________.
La grafica principal sera ______________ porque permite comparar/ver ______.
El color principal significa _____________________________________________.
La principal limitacion de los datos es _________________________________.
```
