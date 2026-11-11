# Wawa Yawar

*Wawa yawar*: "la sangre del niño", en quechua.

> **Estado: en desarrollo.** Proyecto final de la Diplomatura de Especialización en Ciencia de Datos para las Ciencias Sociales y la Gestión Pública (Q-Lab PUCP), [issue #204](https://github.com/d2cml-ai/Data-Science-Python/issues/204). Presentación: miércoles 11 de noviembre de 2026. Las secciones marcadas *(en construcción)* se completan antes de esa fecha.

## Entregables

| Entregable | Enlace |
|---|---|
| Demo (URL pública) | **https://wawa-yawar.streamlit.app/** |
| Video de respaldo (60–90 s) | *(en construcción)* |
| Código de la app | [`app/app.py`](app/app.py) |
| Criterios de diagnóstico | [`app/wawa_yawar/criterios.py`](app/wawa_yawar/criterios.py) |
| Revisión del padrón | [`app/wawa_yawar/padron.py`](app/wawa_yawar/padron.py) |
| Cuántos niños cambian de diagnóstico | [`scripts/reclasificacion.py`](scripts/reclasificacion.py) |
| Pruebas | [`tests/`](tests/) (contra la ENDES y del padrón) |
| Conversaciones con usuarios | [`docs/research/`](docs/research/README.md) |
| Diagrama de arquitectura | [`docs/arquitectura.md`](docs/arquitectura.md) |

## 1. One-liner

**Ayudamos a los puestos de salud de la sierra y la selva alta a diagnosticar la anemia infantil con la norma vigente: la app corrige la hemoglobina según la altitud y revisa todo su padrón de tamizajes.**

## 2. Founder

*(Foto: en construcción.)*

**Fiorella Ampuero.** Trabajo en investigación para el desarrollo, con interés en el desarrollo infantil temprano. En la Tarea 3 del curso recalculé la anemia infantil de la ENDES 2025 con los dos criterios del MINSA y validé mis cifras contra las publicadas por el INEI ([anemia-altitud-peru](https://github.com/fampueroc/anemia-altitud-peru)). Este es un proyecto personal: no representa a mi empleador.

**Cómo cubro el equipo con agentes de IA** *(en construcción)*:

| Rol | Quién lo hace |
|---|---|
| Producto | Yo: conversaciones con usuarios, priorización del flujo, criterios clínicos de las normas |
| Ingeniería | Claude Code, con mi revisión y pruebas automáticas contra los microdatos del INEI |
| Diseño | *(en construcción)* |
| Ventas | *(en construcción)* |

## 3. Problema *(en construcción)*

En abril de 2024 el MINSA adoptó la guía de la OMS para diagnosticar anemia (RM 251-2024-MINSA). Cambiaron dos cosas a la vez: la fórmula que ajusta la hemoglobina según la altitud y el punto de corte para niñas y niños de 6 a 23 meses.

Con los microdatos de la ENDES 2025, la anemia en niñas y niños de 6 a 35 meses pasa de **43,4 %** (criterio anterior, RM 363-2022) a **34,9 %** (criterio vigente). Pero el cambio no es parejo: **sube entre 7 y 11 puntos entre 500 y 2499 m y baja entre 14 y 34 puntos por encima de 3000 m** ([análisis de la Tarea 3](https://github.com/fampueroc/anemia-altitud-peru)). Hay niños que antes no figuraban con anemia y ahora sí, y otros al revés. Del diagnóstico depende el seguimiento que recibe cada niño.

- **Quién lo sufre:** *(en construcción: el rol preciso, a partir de las conversaciones)* quienes hacen el tamizaje de hemoglobina en los establecimientos del primer nivel de atención por encima de los 500 m, y quienes consolidan esas cifras en las redes de salud y las DIRESA.
- **Cuánto le cuesta, en diagnósticos que cambian** ([`scripts/reclasificacion.py`](scripts/reclasificacion.py), ENDES 2025, niñas y niños de 6 a 35 meses, IC 95 % con el diseño muestral):

  | Dónde | Cambia de diagnóstico | Ahora con anemia | Ahora sin anemia |
  |---|---:|---:|---:|
  | Perú | 12,1 % (11,3–12,9) | 1,8 % | 10,3 % |
  | 500–999 m | 9,4 % | 8,2 % | 1,2 % |
  | 1000–2499 m | 9,4 % | 8,9 % | 0,5 % |
  | 3500 m o más | 24,5 % | 0,0 % | 24,5 % |
  | Puno | 22,9 % | 1,8 % | 21,1 % |

  Es decir, **en el Perú, 1 de cada 8 niños cambia de diagnóstico con la norma vigente**, y la dirección depende de la altitud. Es descriptivo: no dice cuál norma es la correcta. Tablas completas: [`reclasificacion_altitud_2025.csv`](data/procesados/reclasificacion_altitud_2025.csv) y [`reclasificacion_departamento_2025.csv`](data/procesados/reclasificacion_departamento_2025.csv).
- **Cuánto le cuesta, en horas:** *(en construcción: con las conversaciones)*.
- **Cómo lo resuelve hoy:** *(en construcción: con las conversaciones)*.
- **Evidencia:** notas de 3 conversaciones con usuarios potenciales en [`docs/research/`](docs/research/README.md).

## 4. Solución e insight *(en construcción)*

- **Un niño:** se ingresa la hemoglobina, la edad y la altitud, y la app da el diagnóstico con los dos criterios y la hemoglobina ajustada.
- **Revisa tu padrón:** el establecimiento sube su Excel o CSV de tamizajes, y la app reclasifica a cada niño, pone primero a los que cambian de diagnóstico y descarga un reporte en Excel. Los padrones de ejemplo ([Puno](data/ejemplo/padron_puno.csv) y [Cajamarca, valle](data/ejemplo/padron_cajamarca.csv)) son 60 niños reales de la ENDES 2025, con códigos ficticios ([`scripts/padron_ejemplo.py`](scripts/padron_ejemplo.py)). En Puno, 10 de 60 niños dejan de tener anemia; en el valle de Cajamarca, 5 de 60 pasan a tenerla.
- **El Perú:** un gráfico por altitud y un mapa de Folium, con la ENDES, de dónde y cuánto cambia el diagnóstico.

**Insight:** el criterio nuevo no "baja la anemia" en todo el país; mueve el diagnóstico en las dos direcciones según la altitud. Sin una herramienta, ese cambio no se ve en el padrón del establecimiento.

## 5. Why now *(en construcción)*

- La norma cambió en 2024 y el ajuste por altitud es una fórmula cuadrática que no se calcula a mano en un puesto de salud.
- La ENDES publica la hemoglobina ajustada con los dos criterios (HC56 y HC56A), lo que permite validar la herramienta niño por niño contra el INEI.

## 6. Demo *(en construcción)*

- **URL pública:** https://wawa-yawar.streamlit.app/ (Streamlit Community Cloud)
- **Video de respaldo:** *(en construcción).*
- **Correr en local:**

  ```bash
  uv sync
  uv run streamlit run app/app.py
  ```

- **Validación:** `uv run pytest` comprueba que las fórmulas de [`app/wawa_yawar/criterios.py`](app/wawa_yawar/criterios.py) reproducen, niño por niño, la hemoglobina ajustada que publica el INEI en la ENDES 2025 (variables HC56 y HC56A). Los microdatos se bajan con `uv run python scripts/obtener_datos.py`.
- **Capturas del flujo principal:** *(en construcción, en `docs/capturas/`).*
- **Arquitectura:** [`docs/arquitectura.md`](docs/arquitectura.md).
- **Modelos y APIs:** no usamos un LLM ni APIs de pago. El diagnóstico aplica las fórmulas oficiales de las dos normas, que son deterministas y están validadas contra el INEI; un modelo probabilístico no aporta aquí y podría equivocarse. Además, los datos del padrón no salen hacia terceros.

## 7. Modelo de negocio *(en construcción)*

Propuesta inicial, por validar con las conversaciones (máximo tres planes):

| Plan | Para quién | Qué incluye | Precio |
|---|---|---|---|
| Gratis | Cualquier establecimiento | Diagnóstico de un niño a la vez | S/ 0 |
| Establecimiento | Puesto o centro de salud | Revisa tu padrón | *(en construcción)* |
| Red / DIRESA | Redes de salud y DIRESA | Varios establecimientos y reporte consolidado | *(en construcción)* |

**Costo por usuario:** sin tokens ni APIs de pago; solo el servidor. Monto y margen de contribución: *(en construcción)*.

## 8. Herramientas del curso

**Dentro del producto** (lo que usa el personal de salud):

| Herramienta | Sesión | Archivo | Por qué esta |
|---|---|---|---|
| Dashboard en Streamlit | 05 | [`app/app.py`](app/app.py) | Quien la usa es personal de salud, no programador: necesita un formulario y un botón para subir su padrón. |
| Mapa con Folium | 06 | [`app/app.py`](app/app.py) (pestaña "El Perú") | El problema es territorial: el cambio de diagnóstico depende de la altitud donde vive el niño. |

**Para preparar los datos:**

| Herramienta | Sesión | Archivo | Para qué |
|---|---|---|---|
| Descarga de datos públicos | 03 | [`scripts/obtener_datos.py`](scripts/obtener_datos.py) | Baja los microdatos de la ENDES 2025 del portal del INEI. |
| GeoPandas | 06 | [`scripts/preparar_mapa.py`](scripts/preparar_mapa.py) | Arma los 26 ámbitos que usa el INEI (con Lima Metropolitana y Lima Provincias por separado) a partir de los límites provinciales. |

**Para el video de respaldo** *(en construcción)*: narración con mi voz clonada (texto a tu voz, sesión 15) y subtítulos con Whisper (sesión 13), con el mismo flujo del reel de la Tarea 3.

## 9. Qué hizo el agente *(en construcción)*

Claude Code (Anthropic) generó el código base de la app y de las pruebas a partir de los scripts de la Tarea 3, bajo mi revisión. Detalle por archivo: *(en construcción)*.

## Estructura del repo

```
app/                    # app de Streamlit
  wawa_yawar/          # criterios de diagnóstico (RM 363-2022 y RM 251-2024)
data/                   # resultados agregados de la ENDES y límites departamentales
  originales/           # microdatos del INEI (no se suben; ver scripts/obtener_datos.py)
docs/                   # arquitectura, capturas y research/ con las 3 conversaciones
scripts/                # descarga y procesamiento de la ENDES
tests/                  # pruebas de los criterios contra la ENDES
```

## Fuentes

- INEI, ENDES 2025 y 2024, microdatos (módulos 1629 y 1638).
- RM 363-2022-MINSA y RM 251-2024-MINSA.
- Límites departamentales: INEI (2007), vía [juaneladio/peru-geojson](https://github.com/juaneladio/peru-geojson) (MPL-2.0).

## Licencia

[MIT](LICENSE).
