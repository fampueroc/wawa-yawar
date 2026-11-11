"""Paso 1 del video: guion.json -> narración con la voz clonada, tiempos por escena y subtítulos.

Reutiliza reel.py de la Tarea 3 (anemia-altitud-peru/reel, copiado de la sesión 15: Qwen3-TTS + Whisper)
y corre con el entorno de esa carpeta:

    ../../anemia-altitud-peru/reel/.venv/Scripts/python.exe narrar.py --voz ../../anemia-altitud-peru/reel/recursos/mi_voz_2.ogg

Guarda en salidas/: narracion.wav, escena_N.wav, tiempos.json (inicio y fin de cada escena y palabras) y video.srt.
"""
import argparse
import json
import sys
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI.parents[1] / "anemia-altitud-peru" / "reel"))
import reel  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument("--voz", required=True)
p.add_argument("--velocidad", type=float, default=1.08)
a = p.parse_args()

salidas = AQUI / "salidas"
salidas.mkdir(exist_ok=True)
guion = json.loads((AQUI / "guion.json").read_text(encoding="utf-8"))

voz = reel.Voz(a.voz)
print("referencia:", voz.texto_ref, flush=True)
nar = reel.narrar(voz, guion, velocidad=a.velocidad)
print("duración:", round(nar.duracion, 1), "s; WER:", [round(e["wer"], 2) for e in guion["escenas"]], flush=True)
reel.subtitulos(nar, guion)

reel.sf.write(salidas / "narracion.wav", nar.audio, nar.sr)
for i, (ini, fin) in enumerate(nar.escenas, 1):
    reel.sf.write(salidas / f"escena_{i}.wav", nar.audio[int(ini * nar.sr):int(fin * nar.sr)], nar.sr)
reel.a_srt(nar, salidas / "video.srt")
(salidas / "tiempos.json").write_text(json.dumps({
    "duracion": nar.duracion, "escenas": nar.escenas, "palabras": nar.palabras,
    "wer": [e["wer"] for e in guion["escenas"]],
}, ensure_ascii=False, indent=1), encoding="utf-8")
print("listo:", salidas, flush=True)
