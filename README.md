# Esqueleto de dashboard para estudiantes

Este proyecto contiene solamente el material que se utiliza durante la sesion
de dashboards. La solucion terminada del docente no esta incluida.

## Lo que se construira en clase

1. KPIs que orienten una decision.
2. Histograma para estudiar una distribucion.
3. Barras ordenadas para comparar categorias.
4. Dispersion para explorar una relacion.
5. Linea para revisar cambios en el tiempo.
6. Color y patrones que funcionen tambien en blanco y negro.
7. Vista ejecutiva con hallazgo, evidencia y limitacion.
8. Commits, push y despliegue desde GitHub.

## Ejecutar el proyecto

```bash
python -m venv .venv
```

macOS o Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\activate
```

Instalar y ejecutar:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Como trabajar con el codigo

En Visual Studio Code usa `Ctrl+F` en Windows o `Cmd+F` en macOS y busca los
marcadores:

```text
DOCENTE-01
DOCENTE-02
DOCENTE-03
DOCENTE-04
DOCENTE-05
DOCENTE-06
DOCENTE-07
```

Cada marcador explica:

- la pregunta que se desea responder;
- el tipo de dato requerido;
- el lugar exacto donde se agregara codigo;
- la razon para elegir la grafica o el color.

## Modulos avanzados

La carpeta `modulos_avanzados/` contiene ejemplos comentados de feature
engineering, modelos supervisados y clustering. Son material de consulta y no
forman parte de la programacion en vivo de esta sesion.

El docente conserva una copia con exactamente la misma estructura. En esa copia
privada, `app.py` contiene los marcadores resueltos; en esta entrega permanecen
como ejercicios.

## GitHub en una frase

- `commit`: guarda una version identificada en tu computadora.
- `push`: envia tus commits a GitHub.
- `branch`: crea una linea de trabajo separada para experimentar.

Consulta `EJEMPLOS_POR_DISCIPLINA.md` para adaptar preguntas, KPIs y graficas a
tu area.
