"""Wawa Yawar: diagnóstico de anemia infantil con el criterio vigente y el anterior.

Uso:
    uv run streamlit run app/app.py
"""

import json
from pathlib import Path

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

from wawa_yawar.criterios import cambio, diagnosticar
from wawa_yawar.padron import excel, revisar

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
NARANJA, AZUL = "#c2410c", "#1d4ed8"

st.set_page_config(page_title="Wawa Yawar", layout="wide")

st.title("Wawa Yawar")
st.markdown(
    "Diagnóstico de anemia en niñas y niños de 6 a 59 meses con la norma vigente "
    "(**RM 251-2024-MINSA**, guía OMS 2024) y la anterior (**RM 363-2022-MINSA**), "
    "con la hemoglobina corregida según la altitud donde vive el niño."
)
st.caption("Proyecto personal del curso de Ciencia de Datos (Q-Lab PUCP). No reemplaza el criterio del personal de salud.")


def num(v, d=1):
    return f"{v:.{d}f}".replace(".", ",")


@st.cache_data
def cargar_peru():
    alt = pd.read_csv(DATA / "procesados" / "reclasificacion_altitud_2025.csv")
    dep = pd.read_csv(DATA / "procesados" / "reclasificacion_departamento_2025.csv")
    geo = json.loads((DATA / "ambitos.geojson").read_text(encoding="utf-8"))
    return alt, dep, geo


tab_nino, tab_padron, tab_peru = st.tabs(["Un niño", "Revisa tu padrón", "El Perú"])

# --------------------------------------------------------------------------- un niño
with tab_nino:
    c1, c2, c3 = st.columns(3)
    hb = c1.number_input("Hemoglobina observada (g/dL)", 4.0, 20.0, 13.8, step=0.1, format="%.1f")
    edad = c2.number_input("Edad (meses)", 6, 59, 14)
    altitud = c3.number_input("Altitud donde vive (m s. n. m.)", 0, 5000, 3825, step=5)

    r = diagnosticar(hb, altitud, edad)
    a363, aoms = bool(r["anemia_363"]), bool(r["anemia_oms"])
    k1, k2 = st.columns(2)
    k1.metric("Norma anterior (RM 363-2022)", "Anemia" if a363 else "Sin anemia")
    k1.caption(f"Hemoglobina corregida por altitud: **{num(float(r['hb_ajustada_363']))} g/dL** (corte: 11,0)")
    k2.metric("Norma vigente (RM 251-2024)", "Anemia" if aoms else "Sin anemia")
    k2.caption(f"Hemoglobina corregida por altitud: **{num(float(r['hb_ajustada_oms']))} g/dL** "
               f"(corte: {'10,5' if edad < 24 else '11,0'})")
    etiqueta = str(cambio(a363, aoms))
    if etiqueta in ("Ahora con anemia", "Ahora sin anemia"):
        st.warning(f"**{etiqueta}**: el diagnóstico cambia con la norma vigente.")
    else:
        st.success(f"**{etiqueta}**: el diagnóstico no cambia.")
    with st.expander("¿Cómo se calcula?"):
        st.markdown(
            "- **Norma anterior:** a la hemoglobina se le resta el ajuste CDC (1989) desde 1000 m; "
            "anemia si queda < 11,0 g/dL.\n"
            "- **Norma vigente:** se resta 0,0056384·m + 0,0000003·m² (g/L) desde 500 m; anemia si queda "
            "< 10,5 g/dL en 6–23 meses o < 11,0 g/dL en 24–59 meses.\n"
            "- Son las mismas fórmulas del INEI: reproducen niño por niño la hemoglobina ajustada de la ENDES 2025."
        )

# --------------------------------------------------------------------------- padrón
with tab_padron:
    st.markdown("Sube el padrón de tamizajes del establecimiento (CSV o Excel) con tres columnas: "
                "**hemoglobina** (g/dL), **edad** (meses) y **altitud** (m) donde vive cada niño.")
    c1, c2 = st.columns([2, 1])
    archivo = c1.file_uploader("Padrón", type=["csv", "xlsx"], label_visibility="collapsed")
    ejemplo = c2.selectbox("…o prueba con un ejemplo", ["", "Puno", "Cajamarca (valle)"],
                           help="60 niños reales de la ENDES 2025 (datos públicos y anónimos) con códigos ficticios. Cajamarca (valle): niños que viven entre 500 y 2499 m.")
    df, nombre = None, ""
    try:
        if archivo is not None:
            df = pd.read_csv(archivo) if archivo.name.endswith(".csv") else pd.read_excel(archivo)
            nombre = archivo.name
        elif ejemplo:
            nombre = f"padron_{ejemplo.split()[0].lower()}.csv"
            df = pd.read_csv(DATA / "ejemplo" / nombre)
        if df is not None:
            df = revisar(df)
    except ValueError as e:
        st.error(str(e))
        df = None

    if df is not None:
        ok = df[df.observacion == ""]
        n = len(ok)
        con_ant, con_vig = int((ok.anemia_norma_anterior == "Sí").sum()), int((ok.anemia_norma_vigente == "Sí").sum())
        ahora_con, ahora_sin = int((ok.cambio == "Ahora con anemia").sum()), int((ok.cambio == "Ahora sin anemia").sum())
        m = st.columns(4)
        m[0].metric("Niños revisados", n, f"{len(df) - n} con datos por revisar" if len(df) > n else None,
                    delta_color="off")
        m[1].metric("Con anemia: norma anterior → vigente", f"{con_ant} → {con_vig}")
        m[2].metric("Ahora con anemia", ahora_con)
        m[3].metric("Ahora sin anemia", ahora_sin)
        if ahora_con or ahora_sin:
            st.warning(f"**{ahora_con + ahora_sin} de {n} niños cambian de diagnóstico** con la norma vigente. "
                       "Están primero en la tabla.")

        orden = {"Ahora con anemia": 0, "Ahora sin anemia": 1, "Anemia con ambos": 2, "Sin anemia con ambos": 3}
        vista = df.assign(_o=df.cambio.map(orden).fillna(-1)).sort_values("_o", kind="stable").drop(columns="_o")

        def color(fila):
            c = {"Ahora con anemia": "background-color: #fde2d4", "Ahora sin anemia": "background-color: #dbe6fd"}
            return [c.get(fila.cambio, "")] * len(fila)

        decimal = st.column_config.NumberColumn
        st.dataframe(vista.style.apply(color, axis=1), hide_index=True, use_container_width=True, column_config={
            "codigo": "Código", "observacion": "Observación", "cambio": "Cambio de diagnóstico",
            "hemoglobina_g_dl": decimal("Hb observada (g/dL)", format="%.1f"),
            "edad_meses": decimal("Edad (meses)", format="%d"),
            "altitud_m": decimal("Altitud (m)", format="%d"),
            "hb_corregida_anterior": decimal("Hb corregida, norma anterior", format="%.1f"),
            "hb_corregida_vigente": decimal("Hb corregida, norma vigente", format="%.1f"),
            "anemia_norma_anterior": "Anemia, norma anterior", "anemia_norma_vigente": "Anemia, norma vigente",
        })

        resumen = pd.DataFrame({
            "Indicador": ["Archivo", "Niños revisados", "Con datos por revisar",
                          "Con anemia, norma anterior (RM 363-2022)", "Con anemia, norma vigente (RM 251-2024)",
                          "Ahora con anemia", "Ahora sin anemia"],
            "Valor": [nombre, n, len(df) - n, con_ant, con_vig, ahora_con, ahora_sin],
        })
        st.download_button("Descargar reporte (Excel)", excel(vista, resumen),
                           file_name=f"reporte_{Path(nombre).stem}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.caption("El padrón se procesa en memoria y no se guarda.")

# --------------------------------------------------------------------------- Perú
with tab_peru:
    alt, dep, geo = cargar_peru()
    peru = alt[alt.dominio == "Perú"].iloc[0]
    st.markdown(
        f"Con los microdatos de la **ENDES 2025** (INEI), **{num(peru.cambia)} % de las niñas y niños de 6 a 35 "
        f"meses cambia de diagnóstico** con la norma vigente (IC 95 %: {num(peru.cambia_li)}–{num(peru.cambia_ls)}): "
        f"{num(peru.ahora_sin)} % deja de tener anemia y {num(peru.ahora_con)} % pasa a tenerla. "
        "La dirección depende de la altitud."
    )
    franjas = alt[alt.dominio != "Perú"]
    fig = go.Figure()
    for col, nombre_serie, color_serie in [("ahora_con", "Ahora con anemia", NARANJA),
                                          ("ahora_sin", "Ahora sin anemia", AZUL)]:
        fig.add_bar(x=franjas.dominio, y=franjas[col], name=nombre_serie, marker_color=color_serie,
                    error_y=dict(type="data", symmetric=False, array=franjas[f"{col}_ls"] - franjas[col],
                                 arrayminus=franjas[col] - franjas[f"{col}_li"].clip(lower=0)))
    fig.update_layout(barmode="group", yaxis_title="% de niños de 6 a 35 meses", xaxis_title="Altitud donde vive",
                      legend=dict(orientation="h", y=1.12), margin=dict(t=30, b=10), height=520)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Por altitud")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Por departamento")
        valores = dep.set_index("dominio")
        for f in geo["features"]:
            fila = valores.loc[f["properties"]["ambito"]]
            f["properties"]["texto"] = (f"{num(fila.cambia)} % cambia de diagnóstico "
                                        f"({num(fila.ahora_con)} % ahora con anemia, {num(fila.ahora_sin)} % ahora sin)")
        mapa = folium.Map(location=[-9.6, -75.0], zoom_start=5, tiles="OpenStreetMap")
        folium.Choropleth(geo_data=geo, data=dep, columns=["dominio", "cambia"], key_on="feature.properties.ambito",
                          fill_color="OrRd", fill_opacity=0.8, line_opacity=0.4,
                          legend_name="% que cambia de diagnóstico").add_to(mapa)
        folium.GeoJson(geo, style_function=lambda _: {"fillOpacity": 0, "weight": 0},
                       tooltip=folium.GeoJsonTooltip(["ambito", "texto"], aliases=["", ""])).add_to(mapa)
        st_folium(mapa, height=520, use_container_width=True, returned_objects=[])
    st.caption("Fuente: INEI, ENDES 2025, microdatos. Cálculo propio con el diseño muestral de la encuesta; reproduce "
               "las cifras de anemia que publica el INEI. Lima Metropolitana y Lima Provincias van por separado. "
               "Es descriptivo: muestra cuánto cambia la clasificación, no cuál criterio es mejor.")
