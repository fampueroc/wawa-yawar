# Hemo-Altura

> **Estado: en desarrollo.** Proyecto final de la Diplomatura de Ciencia de Datos para las Ciencias Sociales y la Gestión Pública (Q-Lab PUCP), [issue #204](https://github.com/d2cml-ai/Data-Science-Python/issues/204). Presentación: miércoles 11 de noviembre de 2026. Las secciones marcadas *(en construcción)* se completan antes de esa fecha.

## 1. One-liner

**Hacemos el diagnóstico de anemia infantil con el criterio vigente para los puestos de salud y las DIRESA de la sierra y la selva alta del Perú, mediante una app que ajusta la hemoglobina por altitud, reclasifica el padrón de tamizajes del establecimiento y muestra qué niños cambian de diagnóstico.**

## 2. Founder

**Fiorella Ampuero.** Trabajo en investigación para el desarrollo, con interés en el desarrollo infantil temprano. En la Tarea 3 del curso recalculé la anemia infantil de la ENDES 2025 con los dos criterios del MINSA y validé mis cifras contra las publicadas por el INEI ([anemia-altitud-peru](https://github.com/fampueroc/anemia-altitud-peru)). Es un proyecto personal: no representa a mi empleador.

## 3. Problema *(en construcción)*

En abril de 2024 el MINSA adoptó la guía de la OMS para diagnosticar anemia (RM 251-2024-MINSA). Cambiaron dos cosas a la vez: la fórmula que ajusta la hemoglobina según la altitud y el punto de corte para niñas y niños de 6 a 23 meses.

Con los microdatos de la ENDES 2025, la anemia en niñas y niños de 6 a 35 meses pasa de **43,4 %** (criterio anterior, RM 363-2022) a **34,9 %** (criterio vigente). Pero el cambio no es parejo: **sube entre 7 y 11 puntos entre 500 y 2499 m y baja entre 14 y 34 puntos por encima de 3000 m** ([análisis de la Tarea 3](https://github.com/fampueroc/anemia-altitud-peru)). Es decir, hay niños que antes no figuraban con anemia y ahora sí, y otros al revés. De ese diagnóstico depende quién recibe suplementación con hierro.

- **Quién lo sufre:** el personal de los puestos de salud que hace el tamizaje, los equipos de las DIRESA que consolidan las cifras y, al final, las familias.
- **Cuánto le cuesta:** *(en construcción: con la ENDES, cuántos niños cambian de diagnóstico por franja de altitud).*
- **Cómo lo resuelve hoy:** *(en construcción: con las conversaciones con usuarios).*

Notas de las conversaciones con usuarios potenciales: [`docs/research/`](docs/research/).

## 4. Solución e insight *(en construcción)*

- **Un niño:** se ingresa la hemoglobina, la edad y la altitud, y la app da el diagnóstico con los dos criterios y la hemoglobina ajustada.
- **Revisa tu padrón:** el establecimiento sube su Excel o CSV de tamizajes y la app reclasifica a cada niño, marca quién cambia de diagnóstico y descarga un reporte.
- **El Perú:** un mapa y una tabla, con la ENDES, de dónde y cuánto cambia el diagnóstico.

**Insight:** el criterio nuevo no "baja la anemia" en todo el país; mueve el diagnóstico en las dos direcciones según la altitud. Sin una herramienta, ese cambio no se ve en el padrón del establecimiento.

## 5. Why now *(en construcción)*

- La norma cambió en 2024 y el ajuste por altitud es una fórmula que no se calcula a mano en un puesto de salud.
- La ENDES publica la hemoglobina ajustada con los dos criterios (HC56 y HC56A), lo que permite validar la herramienta niño por niño.

## 6. Demo *(en construcción)*

- **URL pública:** *(pendiente, Streamlit Community Cloud).*
- **Correr en local:**

  ```bash
  uv sync
  uv run streamlit run app.py
  ```

- **Validación:** `uv run pytest` comprueba que las fórmulas de [`hemo_altura/criterios.py`](hemo_altura/criterios.py) reproducen, niño por niño, la hemoglobina ajustada que publica el INEI en la ENDES 2025 (variables HC56 y HC56A). Los microdatos se bajan con `uv run python scripts/obtener_datos.py`.
- Capturas, diagrama de arquitectura y modelos o APIs: *(pendiente).*

## 7. Modelo de negocio *(en construcción)*

Propuesta inicial, por validar con las conversaciones: licencia anual por DIRESA o red de salud, y versión gratuita para un niño a la vez. Precio y costo por usuario: *(pendiente).*

## 8. Herramientas del curso

| Herramienta | Sesión | Archivo |
|---|---|---|
| Dashboard en Streamlit | 05 | [`app.py`](app.py) |
| Mapa con Folium | 06 | *(en construcción)* |

## 9. Qué hizo el agente *(en construcción)*

Claude Code (Anthropic) generó el código base de la app y de las pruebas a partir de los scripts de la Tarea 3, bajo mi revisión. Detalle por archivo: *(pendiente).*

## Fuentes

- INEI, ENDES 2025 y 2024, microdatos (módulos 1629 y 1638).
- RM 363-2022-MINSA y RM 251-2024-MINSA.
- Límites departamentales: INEI (2007), vía [juaneladio/peru-geojson](https://github.com/juaneladio/peru-geojson) (MPL-2.0).

## Licencia

[MIT](LICENSE).
