# Video de respaldo

Video horizontal (1920×1080) de 60 a 90 segundos: la app pública grabada en uso, narrada con mi voz clonada y con subtítulos. Todo corre en local; no se usa ninguna API de pago.

| Archivo | Qué hace |
|---|---|
| [`guion.json`](guion.json) | Narración de cada escena, qué se ve en pantalla y la fuente de cada cifra |
| [`narrar.py`](narrar.py) | Voz clonada (Qwen3-TTS) y subtítulos palabra por palabra (Whisper), con `reel.py` de la [Tarea 3](https://github.com/fampueroc/anemia-altitud-peru/tree/main/reel) (sesión 15) |
| [`grabar.py`](grabar.py) | Graba https://wawa-yawar.streamlit.app/ con Playwright, una acción por escena y con la duración de la narración |
| [`montar.py`](montar.py) | Une portada, grabación, cierre y créditos; dibuja los subtítulos y el aviso «Voz generada con IA» |

## Uso

```bash
cd video
PY=../../anemia-altitud-peru/reel/.venv/Scripts/python.exe   # entorno de la Tarea 3 (torch, qwen-tts, faster-whisper)
$PY narrar.py --voz ../../anemia-altitud-peru/reel/recursos/mi_voz_2.ogg
uv run --no-project --with playwright python -m playwright install chromium   # una sola vez
uv run --no-project --with playwright python grabar.py
$PY montar.py
```

Las salidas (`salidas/`: audio, grabación y video) no se suben al repositorio; el video final está enlazado en el README principal.
