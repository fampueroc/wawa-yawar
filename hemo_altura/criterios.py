"""Diagnóstico de anemia en niñas y niños de 6 a 59 meses con los dos criterios del MINSA.

- RM 363-2022-MINSA: ajuste por altitud CDC (1989) desde 1000 m; anemia si Hb ajustada < 11,0 g/dL.
- RM 251-2024-MINSA (guía OMS 2024): ajuste (g/L) = 0,0056384·m + 0,0000003·m² desde 500 m;
  anemia si Hb ajustada < 10,5 g/dL (6-23 meses) o < 11,0 g/dL (24-59 meses).

Las fórmulas son las mismas que usa el INEI en la ENDES: en tests/test_criterios.py se comprueba que
reproducen, niño por niño, las variables HC56 y HC56A (hemoglobina ajustada) de los microdatos.
La hemoglobina se trabaja en décimas de g/dL y se trunca, como en la ENDES.
"""

import numpy as np


def ajuste_363(altitud_m):
    """Ajuste por altitud de la RM 363-2022 (CDC 1989), en décimas de g/dL."""
    m = np.asarray(altitud_m, dtype=float)
    a = m / 1000 * 3.3
    return np.where(m >= 1000, (-0.032 * a + 0.022 * a**2) * 10, 0.0)


def ajuste_oms(altitud_m):
    """Ajuste por altitud de la RM 251-2024 (OMS 2024), en décimas de g/dL (equivale a g/L)."""
    m = np.asarray(altitud_m, dtype=float)
    return np.where(m >= 500, 0.0056384 * m + 0.0000003 * m**2, 0.0)


def corte_oms(edad_meses):
    """Punto de corte de la RM 251-2024, en décimas de g/dL."""
    return np.where(np.asarray(edad_meses) < 24, 105, 110)


def diagnosticar(hb_g_dl, altitud_m, edad_meses):
    """Diagnóstico con los dos criterios. Acepta números o arreglos.

    Devuelve un dict con la hemoglobina ajustada (g/dL) y si hay anemia con cada criterio.
    """
    hb = np.round(np.asarray(hb_g_dl, dtype=float) * 10)  # décimas de g/dL
    hb_363 = np.floor(hb - ajuste_363(altitud_m))
    hb_oms = np.floor(hb - ajuste_oms(altitud_m))
    return {
        "hb_ajustada_363": hb_363 / 10,
        "hb_ajustada_oms": hb_oms / 10,
        "anemia_363": hb_363 < 110,
        "anemia_oms": hb_oms < corte_oms(edad_meses),
    }


def cambio(anemia_363, anemia_oms):
    """Etiqueta del cambio de diagnóstico al pasar de la RM 363-2022 a la RM 251-2024."""
    a, b = np.asarray(anemia_363, bool), np.asarray(anemia_oms, bool)
    return np.select(
        [a & b, ~a & ~b, ~a & b, a & ~b],
        ["Anemia con ambos", "Sin anemia con ambos", "Ahora con anemia", "Ahora sin anemia"],
        default="",
    )
