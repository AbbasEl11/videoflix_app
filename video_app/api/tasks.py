import os, subprocess, django_rq

from pathlib import Path

from django.conf import settings
from ..models import Video


HLS_VARIANTS = [
    {"name": "360p", "height": 360, "v_bitrate": "800k", "maxrate": "856k", "bufsize": "1200k", "bandwidth": 900000},
    {"name": "480p", "height": 480, "v_bitrate": "1400k", "maxrate": "1498k", "bufsize": "2100k", "bandwidth": 1600000},
    {"name": "720p", "height": 720, "v_bitrate": "2800k", "maxrate": "2996k", "bufsize": "4200k", "bandwidth": 3200000},
    {"name": "1080p", "height": 1080, "v_bitrate": "5000k", "maxrate": "5350k", "bufsize": "7500k", "bandwidth": 5800000},
]

def process_video_to_hls(video_id: int):
    video = Video.objects.get(id=video_id)
    input_path = Path(video.video_file.path)

    output_root = Path(getattr(settings, 'MEDIA_ROOT')) / 'hls' / str(video.id)
    output_root.mkdir(parents=True, exist_ok=True)

    queue = django_rq.get_queue('default', autocommit=True)

    jobs = []


    for v in HLS_VARIANTS:
        job = queue.enqueue(
            process_single_variant,
            video_id=video.id,
            input_path=str(input_path),
            output_root=str(output_root),
            variant_config=v
        )
        jobs.append(job)
        print(f"Enqueued {v['name']} for video ID {video.id}: {job.id}")

    queue.enqueue(
        create_master_playlist,
        video_id=video.id,
        output_root=str(output_root),
        depends_on=jobs
    )

    return {"video_id": video.id, "variants_enqueued": len(jobs)}

def process_single_variant(
    video_id: int,
    input_path: str,
    output_root: str,
    variant_config: dict
):

    print(f"Processing {variant_config['name']} for video {video_id}...")
    
    variant_dir = Path(output_root) / variant_config["name"]
    variant_dir.mkdir(parents=True, exist_ok=True)

    playlist_path = transcode_variant_to_hls(
        input_path=Path(input_path),
        output_dir=variant_dir,
        height=variant_config["height"],
        v_bitrate=variant_config["v_bitrate"],
        maxrate=variant_config["maxrate"],
        bufsize=variant_config["bufsize"]
    )

    print(f"Completed {variant_config['name']} for video {video_id}")
    
    return {
        "name": variant_config["name"],
        "height": variant_config["height"],
        "bandwidth": variant_config["bandwidth"],
        "playlist_rel": f"{variant_config['name']}/{Path(playlist_path).name}"
    }


def create_master_playlist(video_id: int, output_root: str):

    print(f"Creating master playlist for video {video_id}...")
    
    output_root_path = Path(output_root)
    created_variants = []
    
    for v in HLS_VARIANTS:
        variant_dir = output_root_path / v["name"]
        playlist_path = variant_dir / "index.m3u8"
        
        if playlist_path.exists():
            created_variants.append({
                "name": v["name"],
                "height": v["height"],
                "bandwidth": v["bandwidth"],
                "playlist_rel": f"{v['name']}/index.m3u8"
            })
    
    master_path = write_master_playlist(output_root_path, created_variants)
    
    print(f"Master playlist created for video {video_id}: {master_path}")
    
    return {
        "video_id": video_id,
        "master_playlist": str(master_path),
        "variants": created_variants
    }

def transcode_variant_to_hls(
    input_path: Path,
    output_dir: Path,
    height: int,
    v_bitrate: str,
    maxrate: str,
    bufsize: str,
    hls_time: int = 4
):

    variant_playlist = output_dir / "index.m3u8"
    segment_pattern = output_dir / "seg_%05d.ts"

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vf",
        f"scale=-2:{height}",
        "-c:v",
        "libx264",
        "-preset",
        "faster",  
        "-profile:v",
        "high", 
        "-level",
        "4.0",
        "-crf",
        "23", 
        "-g",
        str(hls_time * 25),  
        "-keyint_min",
        str(hls_time * 25),
        "-sc_threshold",
        "0",
        "-b:v",
        v_bitrate,
        "-maxrate",
        maxrate,
        "-bufsize",
        bufsize,
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-ac",
        "2",
        "-ar",
        "48000",
        "-hls_time",
        str(hls_time),
        "-hls_playlist_type",
        "vod",
        "-hls_segment_filename",
        str(segment_pattern),
        "-movflags",
        "+faststart",
        "-threads",
        "0",
        str(variant_playlist),
    ]

    run_ffmpeg(cmd)
    return str(variant_playlist)

def write_master_playlist(output_root: Path, variants: list):
    master_path = output_root / "master.m3u8"

    lines = ["#EXTM3U", "#EXT-X-VERSION:3"]

    for v in sorted(variants, key=lambda x: x["height"]):
        lines.append(f'#EXT-X-STREAM-INF:BANDWIDTH={v["bandwidth"]},RESOLUTION=1920x{v["height"]}')
        lines.append(v["playlist_rel"])
    
    master_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(master_path)

def run_ffmpeg(cmd: list):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=os.environ.copy())
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: (code {p.returncode}) {p.stderr}")