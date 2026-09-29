#!/usr/bin/env python3
"""video_analizador: transcribe el audio (faster-whisper) y hace OCR de los
fotogramas (Tesseract) de un video; genera TXT, JSON, SRT y VTT con tiempos."""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, difflib
from pathlib import Path

def ts(sec, sep=","):
    ms = int(round(sec * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"

def hms(sec): return ts(sec, ".")[:-4]

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit(f"Error ejecutando {cmd[0]}:\n{r.stderr[-800:]}")
    return r

def has_audio(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                        "stream=index", "-of", "csv=p=0", str(video)], capture_output=True, text=True)
    return bool(r.stdout.strip())

def duration(video):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)])
    return float(r.stdout.strip())

# ---------------------------------------------------------------- AUDIO
def do_audio(video, wav, args):
    """Devuelve (segmentos, estado)."""
    segs, status = [], "ok"
    from faster_whisper import WhisperModel
    from faster_whisper.audio import decode_audio
    model = None
    try:
        model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type,
                             download_root=args.model_dir, local_files_only=args.offline)
    except Exception as e:
        status = f"SIN_TRANSCRIPCION: no se pudo cargar el modelo '{args.model}' ({type(e).__name__}: {str(e)[:150]})"
        print("AVISO:", status, file=sys.stderr)
    if model:
        it, info = model.transcribe(str(wav), language=None if args.lang == "auto" else args.lang,
                                    vad_filter=True, beam_size=5, condition_on_previous_text=False)
        for s in it:
            segs.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip()})
        print(f"  idioma: {info.language} (p={info.language_probability:.2f})", file=sys.stderr)
        return segs, status
    # Respaldo: solo detección de voz (Silero VAD incluido en faster-whisper)
    from faster_whisper.vad import get_speech_timestamps
    audio = decode_audio(str(wav), sampling_rate=16000)
    for t in get_speech_timestamps(audio):
        segs.append({"start": round(t["start"] / 16000, 3), "end": round(t["end"] / 16000, 3),
                     "text": "[voz detectada - sin transcripción]"})
    return segs, status

# ---------------------------------------------------------------- OCR
def norm(t): return re.sub(r"\s+", " ", re.sub(r"[^\wáéíóúñü]+", " ", t.lower())).strip()

def ocr_frame(path, lang, minconf):
    import cv2, pytesseract
    img = cv2.imread(str(path))
    if img is None: return []
    h, w = img.shape[:2]
    if w < 1600:  # ampliar mejora la lectura de texto pequeño
        f = 1600 / w; img = cv2.resize(img, None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    d = pytesseract.image_to_data(gray, lang=lang, config="--oem 1 --psm 11", output_type=pytesseract.Output.DICT)
    lines = {}
    for i, txt in enumerate(d["text"]):
        txt = txt.strip()
        try: conf = float(d["conf"][i])
        except ValueError: continue
        if not txt or conf < minconf: continue
        k = (d["block_num"][i], d["par_num"][i], d["line_num"][i])
        lines.setdefault(k, []).append(txt)
    out = [" ".join(v) for v in lines.values()]
    return [l for l in out if len(re.findall(r"\w", l)) >= 3]

def do_ocr(video, workdir, args, dur):
    frames = Path(workdir) / "frames"; frames.mkdir()
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vf", f"fps=1/{args.ocr_interval}",
         "-q:v", "2", str(frames / "f_%06d.jpg")])
    files = sorted(frames.glob("f_*.jpg"))
    lang = args.ocr_lang
    tracks = []  # {text,start,end,norm}
    for i, f in enumerate(files):
        t0 = i * args.ocr_interval; t1 = min(t0 + args.ocr_interval, dur)
        for line in ocr_frame(f, lang, args.min_conf):
            n = norm(line)
            if not n: continue
            for tr in tracks:  # fusionar con el mismo texto visto justo antes
                if tr["end"] >= t0 - 1e-6 and difflib.SequenceMatcher(None, tr["norm"], n).ratio() >= 0.85:
                    tr["end"] = t1; break
            else:
                tracks.append({"text": line, "start": round(t0, 3), "end": round(t1, 3), "norm": n})
    for tr in tracks: tr.pop("norm")
    return tracks

# ---------------------------------------------------------------- SALIDAS
def write_subs(items, base, key="text"):
    with open(f"{base}.srt", "w", encoding="utf-8") as f:
        for i, s in enumerate(items, 1):
            f.write(f"{i}\n{ts(s['start'])} --> {ts(s['end'])}\n{s[key]}\n\n")
    with open(f"{base}.vtt", "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for s in items: f.write(f"{ts(s['start'], '.')} --> {ts(s['end'], '.')}\n{s[key]}\n\n")

def main():
    ap = argparse.ArgumentParser(prog="video_analizador", description=__doc__)
    ap.add_argument("video"); ap.add_argument("-o", "--salida", help="carpeta de salida (def: <video>_analisis)")
    ap.add_argument("--lang", default="es", help="idioma de voz: es, en, ... o auto (def: es)")
    ap.add_argument("--model", default=os.environ.get("VA_MODEL", "small"),
                    help="modelo Whisper (tiny/base/small/medium/large-v3) o ruta local (def: small)")
    ap.add_argument("--model-dir", default=os.environ.get("VA_MODEL_DIR"), help="carpeta de caché de modelos")
    ap.add_argument("--offline", action="store_true", help="no descargar modelos")
    ap.add_argument("--device", default="auto", help="auto/cpu/cuda"); ap.add_argument("--compute-type", default="auto")
    ap.add_argument("--ocr-lang", default="spa+eng", help="idiomas Tesseract (def: spa+eng)")
    ap.add_argument("--ocr-interval", type=float, default=1.0, help="segundos entre fotogramas OCR (def: 1)")
    ap.add_argument("--min-conf", type=float, default=60, help="confianza mínima OCR 0-100 (def: 60)")
    ap.add_argument("--no-audio", action="store_true"); ap.add_argument("--no-ocr", action="store_true")
    args = ap.parse_args()
    for b in ("ffmpeg", "ffprobe", "tesseract"):
        if not shutil.which(b): sys.exit(f"Falta '{b}' en el PATH.")
    video = Path(args.video)
    if not video.is_file(): sys.exit(f"No existe el archivo: {video}")
    out = Path(args.salida or f"{video.with_suffix('')}_analisis"); out.mkdir(parents=True, exist_ok=True)
    dur = duration(video); base = str(out / video.stem)
    res = {"video": str(video.resolve()), "duracion_s": round(dur, 3), "idioma": args.lang,
           "audio": [], "texto_en_pantalla": [], "estado_audio": "omitido", "estado_ocr": "omitido"}
    with tempfile.TemporaryDirectory() as tmp:
        if not args.no_audio:
            if has_audio(video):
                wav = out / f"{video.stem}_audio.wav"
                print("[1/3] Extrayendo audio y transcribiendo...", file=sys.stderr)
                run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
                res["audio"], res["estado_audio"] = do_audio(video, wav, args)
            else: res["estado_audio"] = "el video no tiene pista de audio"
        if not args.no_ocr:
            print("[2/3] OCR de fotogramas...", file=sys.stderr)
            res["texto_en_pantalla"] = do_ocr(video, tmp, args, dur); res["estado_ocr"] = "ok"
    print("[3/3] Escribiendo resultados...", file=sys.stderr)
    write_subs(res["audio"], base + "_audio"); write_subs(res["texto_en_pantalla"], base + "_ocr")
    Path(base + "_resultado.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    # informe combinado, ordenado por tiempo
    ev = [(s["start"], s["end"], "AUDIO", s["text"]) for s in res["audio"]] + \
         [(s["start"], s["end"], "TEXTO EN PANTALLA", s["text"]) for s in res["texto_en_pantalla"]]
    ev.sort()
    lines = [f"INFORME DE ANÁLISIS: {video.name}", f"Duración: {hms(dur)}", f"Estado audio: {res['estado_audio']}",
             f"Estado OCR: {res['estado_ocr']}", "=" * 60, ""]
    for a, b, k, t in ev:
        lines += [f"TIEMPO:\n[{hms(a)} - {hms(b)}]", f"{k}:", t, ""]
    lines += ["=" * 60, "TRANSCRIPCIÓN COMPLETA (AUDIO):", " ".join(s["text"] for s in res["audio"]), "",
              "TODO EL TEXTO EN PANTALLA (único):"] + list(dict.fromkeys(s["text"] for s in res["texto_en_pantalla"]))
    Path(base + "_informe.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nListo. Archivos en: {out.resolve()}", file=sys.stderr)
    for p in sorted(out.iterdir()): print(" ", p)

if __name__ == "__main__": main()
