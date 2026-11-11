"""Paso 2 del video: graba la app pública con Playwright, un clip por escena (2 a 6), con la duración de la narración.

    uv run --no-project --with playwright python grabar.py

Lee salidas/tiempos.json (de narrar.py) y guarda salidas/grabacion.webm (una sola toma) y salidas/grabacion.json (en qué segundo empieza cada escena). Las escenas 1 y 7 (portada y cierre)
son cuadros fijos que arma montar.py.
"""
import json
import shutil
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

AQUI = Path(__file__).parent
SALIDAS = AQUI / "salidas"
URL = "https://wawa-yawar.streamlit.app/~/+/"   # la app sin el marco de Streamlit Cloud
W, H = 1920, 1080


def duraciones():
    t = json.loads((SALIDAS / "tiempos.json").read_text(encoding="utf-8"))
    return [fin - ini for ini, fin in t["escenas"]]


def esperar_app(page):
    page.goto(URL, wait_until="domcontentloaded", timeout=120_000)
    page.get_by_role("tab", name="Un niño").wait_for(timeout=180_000)
    page.wait_for_timeout(2500)


def suave(page, y, pasos=30):
    """Desplaza la página poco a poco hasta y (px), para que se vea natural en el video."""
    actual = page.evaluate("() => document.querySelector('section.main, [data-testid=stMain], main').scrollTop || window.scrollY")
    for k in range(1, pasos + 1):
        page.mouse.wheel(0, (y - actual) / pasos)
        page.wait_for_timeout(25)


def escena_2(page):   # El Perú: gráfico por altitud
    page.get_by_role("tab", name="El Perú").click()
    page.get_by_text("Por altitud", exact=True).wait_for()
    page.wait_for_timeout(1500)
    suave(page, 300)
    graf = page.locator(".js-plotly-plot").first.bounding_box()
    for k in range(6):
        page.mouse.move(graf["x"] + graf["width"] * (0.2 + 0.12 * k), graf["y"] + graf["height"] * 0.6, steps=15)
        page.wait_for_timeout(700)


def escena_3(page):   # encabezado
    page.get_by_role("tab", name="Un niño").click()
    page.mouse.move(W / 2, 300)
    page.mouse.wheel(0, -4000)
    page.wait_for_timeout(500)
    page.mouse.move(W * 0.3, 180, steps=25)


def escena_4(page):   # Un niño
    page.wait_for_timeout(800)
    page.get_by_text("Norma vigente (RM 251-2024)").first.hover()


def escena_5(page):   # Revisa tu padrón
    page.get_by_role("tab", name="Revisa tu padrón").click()
    page.wait_for_timeout(800)
    sel = page.locator("[data-testid=stSelectbox]").first
    sel.click()
    page.wait_for_timeout(600)
    page.get_by_role("option", name="Cajamarca (valle)").click()
    page.get_by_text("cambian de diagnóstico").first.wait_for(timeout=30_000)
    page.wait_for_timeout(2500)
    suave(page, 450)
    page.wait_for_timeout(2500)
    page.get_by_role("button", name="Descargar reporte (Excel)").scroll_into_view_if_needed()
    page.get_by_role("button", name="Descargar reporte (Excel)").hover()


def escena_6(page):   # mapa
    page.get_by_role("tab", name="El Perú").click()
    page.wait_for_timeout(1000)
    mapa = page.frame_locator("iframe[title*='streamlit_folium'], iframe").last
    mapa.locator(".leaflet-container").wait_for(timeout=30_000)
    caja = page.locator("iframe").last.bounding_box()
    # Puno queda al sureste del centro del mapa
    page.mouse.move(caja["x"] + caja["width"] * 0.4, caja["y"] + caja["height"] * 0.5, steps=20)
    page.wait_for_timeout(500)
    page.mouse.move(caja["x"] + caja["width"] * 0.62, caja["y"] + caja["height"] * 0.72, steps=30)


ESCENAS = {2: escena_2, 3: escena_3, 4: escena_4, 5: escena_5, 6: escena_6}


def main():
    """Una sola grabación continua; guarda en qué segundo empieza cada escena para que montar.py la corte."""
    SALIDAS.mkdir(exist_ok=True)
    durs = duraciones()
    tmp = SALIDAS / "tmp_grabacion"
    with sync_playwright() as pw:
        nav = pw.chromium.launch()
        ctx = nav.new_context(viewport={"width": W, "height": H}, record_video_dir=str(tmp),
                              record_video_size={"width": W, "height": H}, locale="es-PE")
        t0 = time.time()   # el video empieza con la página
        page = ctx.new_page()
        esperar_app(page)
        marcas = {}
        for n, accion in ESCENAS.items():
            inicio = time.time()
            marcas[n] = {"inicio": inicio - t0, "dur": durs[n - 1]}
            accion(page)
            resto = durs[n - 1] + 0.3 - (time.time() - inicio)
            if resto > 0:
                page.wait_for_timeout(resto * 1000)
            print(f"escena {n}: {marcas[n]}", flush=True)
        ctx.close()
        nav.close()
    shutil.move(next(tmp.glob("*.webm")), SALIDAS / "grabacion.webm")
    shutil.rmtree(tmp)
    (SALIDAS / "grabacion.json").write_text(json.dumps(marcas, indent=1), encoding="utf-8")

if __name__ == "__main__":
    main()
