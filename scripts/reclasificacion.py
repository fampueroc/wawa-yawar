"""¿Cuántos niños cambian de diagnóstico al pasar de la RM 363-2022 a la RM 251-2024? ENDES 2025.

Población: niñas y niños de 6 a 35 meses, residentes que durmieron en el hogar la noche anterior
(HV103 = 1), con hemoglobina medida: la misma del indicador que publica el INEI.

Para cada dominio (Perú, franja de altitud, ámbito departamental) estima, con el diseño muestral de
la ENDES (estratos HV022, conglomerados HV001, ponderador HV005, linealización de Taylor):
- % de niños que pasan a tener anemia ("ahora con anemia"),
- % de niños que dejan de tenerla ("ahora sin anemia"),
- % que cambia de diagnóstico en cualquier dirección.

El diagnóstico usa app/wawa_yawar/criterios.py, el mismo código de la app, y se comprueba que
coincide con las variables HC57 y HC57A del INEI.

Uso:
    uv run python scripts/reclasificacion.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "app"))
from wawa_yawar.criterios import diagnosticar  # noqa: E402

ORIGINALES = RAIZ / "data" / "originales"
PROCESADOS = RAIZ / "data" / "procesados"
Z = 1.96

DEPARTAMENTOS = {
    1: "Amazonas", 2: "Áncash", 3: "Apurímac", 4: "Arequipa", 5: "Ayacucho",
    6: "Cajamarca", 7: "Callao", 8: "Cusco", 9: "Huancavelica", 10: "Huánuco",
    11: "Ica", 12: "Junín", 13: "La Libertad", 14: "Lambayeque", 15: "Lima Provincias",
    16: "Loreto", 17: "Madre de Dios", 18: "Moquegua", 19: "Pasco", 20: "Piura",
    21: "Puno", 22: "San Martín", 23: "Tacna", 24: "Tumbes", 25: "Ucayali",
    26: "Lima Metropolitana",
}
FRANJAS = [0, 500, 1000, 2500, 3000, 3500, 10000]


def leer(nombre, columnas=None):
    ruta = next(ORIGINALES.glob(f"modulo_*/**/{nombre}"))
    df, _ = pyreadstat.read_sav(ruta, usecols=columnas)
    return df.rename(columns=str.upper)


def cargar():
    r6 = leer("RECH6_2025.sav")
    r1 = leer("RECH1_2025.sav", ["HHID", "HVIDX", "HV103"])
    r0 = leer("RECH0_2025.sav", ["HHID", "HV001", "HV005", "HV022", "HV024", "HV040", "UBIGEO"])
    r6["HC0"] = pd.to_numeric(r6["HC0"])
    r1["HVIDX"] = pd.to_numeric(r1["HVIDX"])
    d = (r6.merge(r1, left_on=["HHID", "HC0"], right_on=["HHID", "HVIDX"], how="left", validate="1:1")
           .merge(r0, on="HHID", how="left", validate="m:1"))
    d["AMBITO"] = np.where(d.UBIGEO.str[:4] == "1501", 26, d.HV024).astype(int)
    d = d[(d.HV103 == 1) & d.HC1.between(6, 35) & d.HC53.notna()].copy()

    r = diagnosticar(d.HC53 / 10, d.HV040, d.HC1)
    d["anemia_363"] = r["anemia_363"].astype(float)
    d["anemia_oms"] = r["anemia_oms"].astype(float)
    assert (d.anemia_363 == (d.HC57 <= 3)).all(), "No coincide con HC57 del INEI"
    assert (d.anemia_oms == (d.HC57A <= 3)).all(), "No coincide con HC57A del INEI"
    d["ahora_con"] = ((d.anemia_363 == 0) & (d.anemia_oms == 1)).astype(float)
    d["ahora_sin"] = ((d.anemia_363 == 1) & (d.anemia_oms == 0)).astype(float)
    d["cambia"] = d.ahora_con + d.ahora_sin
    return d


def proporcion(d, y, dominio):
    """Proporción ponderada en un dominio y su error estándar (linealización de Taylor)."""
    w = d.HV005 * dominio
    total = w.sum()
    p = (w * d[y]).sum() / total
    z = w * (d[y] - p) / total
    psu = pd.DataFrame({"h": d.HV022, "c": d.HV001, "z": z}).groupby(["h", "c"]).z.sum().reset_index()
    var = 0.0
    for _, g in psu.groupby("h"):
        n = len(g)
        if n > 1:
            var += n / (n - 1) * ((g.z - g.z.mean()) ** 2).sum()
    return p, np.sqrt(var)


def fila(d, nombre, dom):
    f = {"dominio": nombre, "n": int(dom.sum())}
    for y in ["anemia_363", "anemia_oms", "ahora_con", "ahora_sin", "cambia"]:
        p, se = proporcion(d, y, dom)
        f[y], f[f"{y}_li"], f[f"{y}_ls"] = 100 * p, 100 * (p - Z * se), 100 * (p + Z * se)
    return f


def tabla(d):
    filas = [fila(d, "Perú", pd.Series(1.0, index=d.index))]
    for a, b in zip(FRANJAS[:-1], FRANJAS[1:]):
        nombre = f"{a}–{b - 1} m" if b < 10000 else f"{a} m o más"
        filas.append(fila(d, nombre, d.HV040.between(a, b - 1).astype(float)) | {"desde": a, "hasta": b})
    altitud = pd.DataFrame(filas)
    deps = pd.DataFrame([fila(d, n, (d.AMBITO == c).astype(float)) for c, n in DEPARTAMENTOS.items()])
    return altitud, deps


if __name__ == "__main__":
    d = cargar()
    altitud, deps = tabla(d)
    altitud.round(2).to_csv(PROCESADOS / "reclasificacion_altitud_2025.csv", index=False, encoding="utf-8")
    deps.round(2).to_csv(PROCESADOS / "reclasificacion_departamento_2025.csv", index=False, encoding="utf-8")
    cols = ["dominio", "n", "anemia_363", "anemia_oms", "ahora_con", "ahora_con_li", "ahora_con_ls",
            "ahora_sin", "ahora_sin_li", "ahora_sin_ls", "cambia", "cambia_li", "cambia_ls"]
    pd.set_option("display.width", 250)
    print(altitud[cols].round(1).to_string(index=False))
    print()
    print(deps[cols].sort_values("cambia", ascending=False).round(1).to_string(index=False))
