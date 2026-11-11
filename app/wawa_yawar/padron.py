"""Lectura y revisión del padrón de tamizajes de un establecimiento de salud."""

import io

import pandas as pd

from .criterios import cambio, diagnosticar

ALIAS = {
    "hemoglobina_g_dl": ["hemoglobina_g_dl", "hemoglobina", "hb", "hgb", "hb_g_dl", "hemoglobina (g/dl)"],
    "edad_meses": ["edad_meses", "edad", "edad (meses)", "meses"],
    "altitud_m": ["altitud_m", "altitud", "altura", "msnm", "altitud (m)"],
}


def normalizar(df):
    """Encuentra las columnas de hemoglobina, edad y altitud aunque tengan otro nombre."""
    cols = {str(c).strip().lower(): c for c in df.columns}
    ren = {}
    for destino, opciones in ALIAS.items():
        encontrada = next((cols[o] for o in opciones if o in cols), None)
        if encontrada is None:
            raise ValueError(f"No encuentro la columna de {destino.split('_')[0]}. "
                             f"Nombres aceptados: {', '.join(opciones)}")
        ren[encontrada] = destino
    df = df.rename(columns=ren)
    for c in ALIAS:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "."), errors="coerce")
    return df


def revisar(df):
    df = normalizar(df.copy())
    valido = df.hemoglobina_g_dl.between(4, 20) & df.edad_meses.between(6, 59) & df.altitud_m.between(0, 5000)
    df["observacion"] = ""
    df.loc[~valido, "observacion"] = "Revisar datos: hemoglobina 4–20 g/dL, edad 6–59 meses, altitud 0–5000 m"
    ok = df[valido]
    r = diagnosticar(ok.hemoglobina_g_dl, ok.altitud_m, ok.edad_meses)
    si_no = {True: "Sí", False: "No"}
    df.loc[valido, "hb_corregida_anterior"] = r["hb_ajustada_363"]
    df.loc[valido, "hb_corregida_vigente"] = r["hb_ajustada_oms"]
    df.loc[valido, "anemia_norma_anterior"] = pd.Series(r["anemia_363"], index=ok.index).map(si_no)
    df.loc[valido, "anemia_norma_vigente"] = pd.Series(r["anemia_oms"], index=ok.index).map(si_no)
    df.loc[valido, "cambio"] = cambio(r["anemia_363"], r["anemia_oms"])
    return df


def excel(df, resumen):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        resumen.to_excel(w, sheet_name="Resumen", index=False)
        df.to_excel(w, sheet_name="Padrón revisado", index=False)
        df[df.cambio.isin(["Ahora con anemia", "Ahora sin anemia"])].to_excel(w, sheet_name="Cambian", index=False)
    return buf.getvalue()
