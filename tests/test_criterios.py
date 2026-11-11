"""Las fórmulas de wawa_yawar reproducen, niño por niño, la hemoglobina ajustada del INEI (ENDES 2025).

Requiere los microdatos en datos/originales (python scripts/obtener_datos.py).
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from wawa_yawar.criterios import diagnosticar

ORIGINALES = Path(__file__).resolve().parent.parent / "data" / "originales"


def leer(nombre, columnas=None):
    pyreadstat = pytest.importorskip("pyreadstat")
    rutas = list(ORIGINALES.glob(f"modulo_*/**/{nombre}"))
    if not rutas:
        pytest.skip("Faltan los microdatos de la ENDES 2025")
    df, _ = pyreadstat.read_sav(rutas[0], usecols=columnas)
    return df.rename(columns=str.upper)


def test_reproduce_hc56_y_hc56a():
    r6 = leer("RECH6_2025.sav")
    r0 = leer("RECH0_2025.sav", ["HHID", "HV040"])
    d = r6.merge(r0, on="HHID", how="left", validate="m:1")
    d = d[d.HC53.notna() & d.HC56.notna() & d.HC56A.notna() & d.HC1.between(6, 59)]
    r = diagnosticar(d.HC53 / 10, d.HV040, d.HC1)
    assert len(d) > 5000
    assert np.array_equal(r["hb_ajustada_363"] * 10, d.HC56.to_numpy())
    assert np.array_equal(r["hb_ajustada_oms"] * 10, d.HC56A.to_numpy())


def test_casos_simples():
    # A nivel del mar no hay ajuste: solo cambia el corte para menores de 24 meses
    r = diagnosticar(10.7, 0, 12)
    assert r["anemia_363"] and not r["anemia_oms"]
    # A 24 meses o más el corte es el mismo (11,0)
    r = diagnosticar(10.7, 0, 30)
    assert r["anemia_363"] and r["anemia_oms"]
