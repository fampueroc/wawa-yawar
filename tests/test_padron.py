"""Revisión del padrón: columnas con otros nombres, comas decimales, filas con errores y reporte en Excel."""

import io

import pandas as pd
import pytest

from wawa_yawar.padron import excel, revisar


def test_revisa_padron_con_otros_nombres_y_errores():
    df = pd.DataFrame({"Código": ["A", "B", "C"], "Hb": ["10,8", "13.8", "99"],
                       "Edad": [14, 14, 20], "Altura": [700, 3825, 3000]})
    r = revisar(df)
    # A: 700 m y 14 meses. Norma anterior sin ajuste (< 1000 m): 10,8 < 11,0 -> anemia.
    #    Norma vigente: 10,8 - 0,41 = 10,3 < 10,5 -> anemia.
    assert r.loc[0, "cambio"] == "Anemia con ambos"
    # B: el caso de Puno de la pestaña "Un niño"
    assert r.loc[1, "cambio"] == "Ahora sin anemia"
    # C: hemoglobina imposible -> no se diagnostica, se marca para revisar
    assert r.loc[2, "observacion"].startswith("Revisar datos")
    assert pd.isna(r.loc[2, "cambio"])


def test_falta_una_columna():
    with pytest.raises(ValueError, match="altitud"):
        revisar(pd.DataFrame({"hb": [11.0], "edad": [12]}))


def test_reporte_excel():
    r = revisar(pd.DataFrame({"hb": [11.0, 13.8], "edad": [12, 14], "altitud": [800, 3825]}))
    hojas = pd.ExcelFile(io.BytesIO(excel(r, pd.DataFrame({"Indicador": ["x"], "Valor": [1]})))).sheet_names
    assert hojas == ["Resumen", "Padrón revisado", "Cambian"]
