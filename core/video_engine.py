import re, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
from .storage import ensure_output_dir

W,H = 1080,1920

def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def _wrap(draw, text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0,0), test, font=font)[2] <= max_width:
            line = test
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    return lines

def _extract_scenes(text):
    headings = re.split(r"(?im)(?=^#{1,4}\s*(?:scene\s*\d+|\d+\.?\s*scene))", text)
    chunks = [x.strip() for x in headings if x.strip()]
    if len(chunks) <= 1:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks = paragraphs[:12]
    return chunks[:12] or [text[:1200]]

def _make_frame(title, body, index, total, landscape=False):
    width, height = (1920,1080) if landscape else (1080,1920)
    im = Image.new("RGB", (width,height), (13,14,19))
    d = ImageDraw.Draw(im)
    # restrained cinematic gradient
    for y in range(height):
        t = y / max(height-1,1)
        color = (int(13+20*t), int(14+4*t), int(20+10*t))
        d.line((0,y,width,y), fill=color)
    d.rectangle((70,90,width-70,height-90), outline=(176,126,52), width=4)
    d.text((110,130), "VYRON STUDIOS", font=_font(34,True), fill=(218,177,98))
    d.text((110,height-170), f"SCENE {index+1:02d} / {total:02d}", font=_font(28,True), fill=(218,177,98))
    title_font = _font(64 if landscape else 58, True)
    body_font = _font(38 if landscape else 34)
    maxw = width-220
    title_lines = _wrap(d, title[:180], title_font, maxw)
    y = height*0.27
    for line in title_lines[:3]:
        d.text((110,y), line, font=title_font, fill=(255,255,255))
        y += 82
    y += 35
    body_clean = re.sub(r"[*#`]", "", body)
    body_lines = _wrap(d, body_clean[:950], body_font, maxw)
    for line in body_lines[:12]:
        d.text((110,y), line, font=body_font, fill=(210,211,218))
        y += 54
    return im

def render_video(text, layout, seconds_per_scene, fps, audio_bytes=None, audio_name=None):
    outdir = ensure_output_dir()
    landscape = layout.startswith("Landscape")
    width,height = (1920,1080) if landscape else (1080,1920)
    scenes = _extract_scenes(text)
    scenes = scenes[:10]
    tmp_video = outdir / "vyron_silent.mp4"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    writer = imageio_ffmpeg.write_frames(
        str(tmp_video), (width,height), fps=fps, codec="libx264",
        quality=7, pix_fmt_in="rgb24", pix_fmt_out="yuv420p",
        macro_block_size=1
    )
    writer.send(None)
    try:
        for i, chunk in enumerate(scenes):
            lines = [x.strip(" -\t") for x in chunk.splitlines() if x.strip()]
            title = re.sub(r"[*#]", "", lines[0])[:100] if lines else f"Scene {i+1}"
            body = " ".join(re.sub(r"[*#]", "", x) for x in lines[1:]) or chunk
            frame = _make_frame(title, body, i, len(scenes), landscape)
            for _ in range(int(seconds_per_scene*fps)):
                writer.send(frame.tobytes())
    finally:
        writer.close()
    final_path = outdir / "vyron_video.mp4"
    if audio_bytes:
        suffix = Path(audio_name or "narration.mp3").suffix.lower()
        if suffix not in [".mp3", ".wav", ".m4a"]:
            suffix = ".mp3"
        audio_path = outdir / ("narration" + suffix)
        audio_path.write_bytes(audio_bytes)
        cmd = [ffmpeg, "-y", "-i", str(tmp_video), "-i", str(audio_path),
               "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
               "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(final_path)]
        subprocess.run(cmd, check=True, capture_output=True)
    else:
        tmp_video.replace(final_path)
    return str(final_path)

def make_srt(text, seconds_per_scene):
    scenes = _extract_scenes(text)
    def stamp(sec):
        h = sec // 3600; m = (sec % 3600) // 60; s = sec % 60
        return f"{h:02d}:{m:02d}:{s:02d},000"
    blocks=[]
    for i, scene in enumerate(scenes[:12]):
        clean = re.sub(r"[*#`]", "", scene)
        clean = re.sub(r"\s+", " ", clean).strip()[:220]
        start=i*seconds_per_scene; end=(i+1)*seconds_per_scene
        blocks.append(f"{i+1}\n{stamp(start)} --> {stamp(end)}\n{clean}")
    return "\n\n".join(blocks)
