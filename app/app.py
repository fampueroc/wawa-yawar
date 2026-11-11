"""Wawa Yawar: diagnóstico de anemia infantil con el criterio vigente y el anterior.

Uso:
    streamlit run app/app.py
"""

import streamlit as st

from wawa_yawar.criterios import cambio, diagnosticar

st.set_page_config(page_title="Wawa Yawar", layout="wide")

st.title("Wawa Yawar")
st.markdown(
    "Diagnóstico de anemia en niñas y niños de 6 a 59 meses con el criterio vigente "
    "(**RM 251-2024-MINSA**, guía OMS 2024) y el anterior (**RM 363-2022-MINSA**), "
    "con el ajuste por la altitud donde vive el niño."
)
st.caption("Versión en desarrollo · Proyecto personal del curso de Data Science con Python (Q-Lab PUCP). "
           "No reemplaza el criterio del personal de salud.")

tab_nino, tab_padron, tab_peru = st.tabs(["Un niño", "Revisa tu padrón", "El Perú"])

with tab_nino:
    c1, c2, c3 = st.columns(3)
    hb = c1.number_input("Hemoglobina observada (g/dL)", 5.0, 20.0, 13.8, step=0.1, format="%.1f")
    edad = c2.number_input("Edad (meses)", 6, 59, 14)
    altitud = c3.number_input("Altitud donde vive (m s. n. m.)", 0, 5000, 3825, step=5)

    r = diagnosticar(hb, altitud, edad)
    a363, aoms = bool(r["anemia_363"]), bool(r["anemia_oms"])
    k1, k2 = st.columns(2)
    k1.metric("RM 363-2022 (anterior)", "Anemia" if a363 else "Sin anemia",
              f"Hb ajustada {float(r['hb_ajustada_363']):.1f} g/dL", delta_color="off")
    k2.metric("RM 251-2024 (vigente)", "Anemia" if aoms else "Sin anemia",
              f"Hb ajustada {float(r['hb_ajustada_oms']):.1f} g/dL", delta_color="off")
    st.info(f"Cambio de diagnóstico: **{cambio(a363, aoms)}**")

with tab_padron:
    st.write("En construcción: sube el Excel o CSV de tamizajes del establecimiento y la app reclasifica a cada niño.")

with tab_peru:
    st.write("En construcción: cuántos niños cambian de diagnóstico con el criterio nuevo, por altitud (ENDES 2025).")
