"""Paso 3 del video: une portada, grabación de la app, cierre, narración y subtítulos en salidas/wawa_yawar.mp4.

    ../../anemia-altitud-peru/reel/.venv/Scripts/python.exe montar.py

Usa salidas/narracion.wav y tiempos.json (narrar.py) y salidas/grabacion.webm y grabacion.json (grabar.py).
Los subtítulos y el aviso de voz con IA se dibujan con Pillow, cuadro por cuadro, como en el reel de la Tarea 3.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI.parents[1] / "anemia-altitud-peru" / "reel"))
import reel  # noqa: E402

SALIDAS = Path(os.environ.get("SALIDAS", AQUI / "salidas"))
W, H, FPS = 1920, 1080, 30
FONDO, TEXTO, SUAVE, ACENTO = "#1C1A17", "#F7F3EC", "#B8AE9F", "#F08A4B"
CREDITOS = 5.0
FF = reel.FFMPEG

guion = json.loads((AQUI / "guion.json").read_text(encoding="utf-8"))
tiempos = json.loads((SALIDAS / "tiempos.json").read_text(encoding="utf-8"))
marcas = json.loads((SALIDAS / "grabacion.json").read_text(encoding="utf-8"))
escenas = tiempos["escenas"]
palabras = [tuple(p) for p in tiempos["palabras"]]

# Whisper escribe mal el nombre y algunas palabras; el texto correcto es el del guion. Las cifras van en número.
CORRECCIONES = [
    (["Guagua", "y", "Aguar"], "Wawa Yawar"),
    (["Sierra", "Alta,"], "sierra alta,"),
    (["Valle"], "valle"),
    (["IN", "-A."], "INEI."),
    (["guaguayawar.streamlit.app"], "wawa-yawar.streamlit.app"),
    (["seis", "a", "treinta", "y", "cinco"], "6 a 35"),
    (["catorce"], "14"),
    (["tres", "mil", "ochocientos", "veinticinco"], "3825"),
    (["trece", "coma", "ocho"], "13,8"),
    (["cinco", "pasan"], "5 pasan"),
]


def corregir(palabras):
    salida, i = [], 0
    while i < len(palabras):
        for malas, buena in CORRECCIONES:
            if [p[2] for p in palabras[i:i + len(malas)]] == malas:
                salida.append((palabras[i][0], palabras[i + len(malas) - 1][1], buena))
                i += len(malas)
                break
        else:
            salida.append(palabras[i])
            i += 1
    return salida


palabras = corregir(palabras)
total = tiempos["duracion"] + CREDITOS


def tarjeta(lineas):
    """Cuadro fijo: lista de (texto, fuente, tamaño, peso, color, espacio después), centrado en vertical."""
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    filas = [(t, reel._fuente(f, s, p), c, g) for t, f, s, p, c, g in lineas]
    alto = sum(f.size * 1.25 + g for _, f, _, g in filas)   # 1,25: Oswald es más alta que su tamaño nominal
    y = (H - alto) / 2
    for t, f, c, g in filas:
        d.text((160, y), t, font=f, fill=c)
        y += f.size * 1.25 + g
    return img


portada = tarjeta([
    ("Wawa Yawar", "Oswald", 150, 700, TEXTO, 50),
    ("Diagnóstico de anemia infantil con la norma vigente", "PublicSans", 54, 700, ACENTO, 14),
    ("RM 251-2024-MINSA: nuevo ajuste de la hemoglobina por altitud", "PublicSans", 44, 500, TEXTO, 0),
])
cierre = tarjeta([
    ("Pruébala", "Oswald", 110, 600, TEXTO, 20),
    ("wawa-yawar.streamlit.app", "PublicSans", 76, 700, ACENTO, 30),
    ("Código: github.com/fampueroc/wawa-yawar", "PublicSans", 44, 500, SUAVE, 0),
])
creditos = tarjeta([("Créditos", "Oswald", 90, 600, TEXTO, 30)]
                   + [(c, "PublicSans", 42, 500, TEXTO, 18) for c in guion["creditos"]])

# --------------------------------------------------------------------------- tramos de la línea de tiempo
# La narración es: INICIO, escena 1, PAUSA, escena 2, PAUSA, ..., escena 7, FINAL. Cada escena dura hasta que empieza la otra.
cortes = [0.0] + [escenas[i][0] - reel.PAUSA for i in range(1, len(escenas))] + [tiempos["duracion"], total]


class Grabacion:
    """Lee la grabación a 30 fps, siempre hacia adelante (las escenas están en orden), sin cargarla entera."""

    def __init__(self, ruta):
        self.proc = subprocess.Popen([FF, "-v", "error", "-i", str(ruta), "-r", str(FPS), "-vf", f"scale={W}:{H}",
                                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.i, self.actual = -1, None

    def __getitem__(self, k):
        while self.i < k:
            crudo = self.proc.stdout.read(W * H * 3)
            if len(crudo) < W * H * 3:
                break   # se acabó: se queda el último cuadro
            self.actual, self.i = crudo, self.i + 1
        return Image.frombytes("RGB", (W, H), self.actual)


grab = Grabacion(SALIDAS / "grabacion.webm")


def fondo(t):
    k = next(i for i in range(len(cortes) - 1) if cortes[i] <= t < cortes[i + 1]) if t < total else len(cortes) - 2
    n = k + 1   # número de escena; el último tramo son los créditos
    if n == 1:
        return portada
    if n == 7:
        return cierre
    if n == 8:
        return creditos
    cuadro = int((marcas[str(n)]["inicio"] + t - cortes[k]) * FPS)
    return grab[cuadro]


bloques = reel._bloques(palabras, max_palabras=7, max_letras=48)
fsub = reel._fuente("PublicSans", 46, 700)
faviso = reel._fuente("PublicSans", 24, 700)


def cuadro(t):
    img = fondo(t).copy()
    d = ImageDraw.Draw(img)
    # aviso de voz con IA, siempre visible
    aviso = "VOZ GENERADA CON IA"
    x1 = W - 40
    x0 = x1 - d.textlength(aviso, font=faviso) - 36
    d.rounded_rectangle((x0, 30, x1, 74), radius=22, fill="#000000")
    d.text((x0 + 18, 52), aviso, font=faviso, fill="#FFFFFF", anchor="lm")
    # subtítulo con la palabra actual resaltada
    b = next((b for b in bloques if b[0][0] - 0.1 <= t <= b[-1][1] + 0.25), None)
    if b:
        texto = " ".join(p[2] for p in b)
        w = d.textlength(texto, font=fsub)
        x, y = (W - w) / 2, H - 150
        d.rounded_rectangle((x - 30, y - 20, x + w + 30, y + fsub.size + 26), radius=24, fill="#000000")
        for ini, fin, palabra in b:
            d.text((x, y), palabra, font=fsub, fill=reel.SUB_ACTIVA if ini <= t <= fin + 0.05 else "#FFFFFF")
            x += d.textlength(palabra + " ", font=fsub)
    return img


wav = SALIDAS / "narracion.wav"
salida = SALIDAS / "wawa_yawar.mp4"
cmd = [FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-i", str(wav), "-af", f"apad,loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium",
       "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
       "-t", f"{total:.2f}", "-movflags", "+faststart", str(salida)]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for k in range(int(total * FPS)):
    proc.stdin.write(cuadro(k / FPS).tobytes())
proc.stdin.close()
proc.wait()
reel.a_srt(reel.Narracion(np.zeros(1), 1, escenas, palabras), SALIDAS / "wawa_yawar.srt")
portada.save(SALIDAS / "portada.png")
print(f"listo: {salida} ({total:.1f} s)")
