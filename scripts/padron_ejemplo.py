"""Arma padrones de tamizaje de ejemplo con niños reales de la ENDES 2025 (datos públicos y anónimos).

Cada padrón toma una muestra aleatoria (semilla fija) de niñas y niños de 6 a 35 meses de un
departamento, con su hemoglobina observada (HC53), su edad (HC1) y la altitud de su conglomerado
(HV040). El código de cada niño es ficticio y no se guarda ningún otro dato de la encuesta.

Uso:
    uv run python scripts/padron_ejemplo.py
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
from reclasificacion import cargar  # noqa: E402

DESTINO = RAIZ / "data" / "ejemplo"
PADRONES = {"puno": 21, "cajamarca": 6}  # código del ámbito departamental
N = 60

if __name__ == "__main__":
    DESTINO.mkdir(parents=True, exist_ok=True)
    d = cargar()
    for nombre, codigo in PADRONES.items():
        m = d[d.AMBITO == codigo].sample(N, random_state=20261111)
        p = m.assign(
            hemoglobina_g_dl=(m.HC53 / 10).round(1),
            edad_meses=m.HC1.astype(int),
            altitud_m=m.HV040.astype(int),
        )[["hemoglobina_g_dl", "edad_meses", "altitud_m"]].reset_index(drop=True)
        p.insert(0, "codigo", [f"{nombre[:3].upper()}-{i:03d}" for i in range(1, N + 1)])
        p.to_csv(DESTINO / f"padron_{nombre}.csv", index=False, encoding="utf-8")
        print(nombre, len(p), "niños; altitud", p.altitud_m.min(), "–", p.altitud_m.max(), "m")
