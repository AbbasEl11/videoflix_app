from pathlib import Path
from django.conf import settings

def get_hls_root_dir(video_id: int) -> Path:
    """
    Get the root HLS directory path for a video.
    
    Args:
        video_id: Video ID
        
    Returns:
        Path: Root HLS directory path
    """
    return Path(getattr(settings, "MEDIA_ROOT")) / "hls" / str(video_id)

def get_hls_variant_dir(video_id: int, resolution: str) -> Path:
    """
    Get the HLS variant directory path for a specific resolution.
    
    Args:
        video_id: Video ID
        resolution: Resolution string (e.g., '480p', '720p', '1080p')
        
    Returns:
        Path: Variant directory path
    """
    return get_hls_root_dir(video_id) / resolution

def get_hls_playlist_path(video_id: int, resolution: str) -> Path:
    """
    Get the HLS playlist file path for a specific resolution.
    
    Args:
        video_id: Video ID
        resolution: Resolution string
        
    Returns:
        Path: Playlist file path
    """
    return get_hls_variant_dir(video_id, resolution) / "index.m3u8"

def get_hls_segment_path(video_id: int, resolution: str, segment: str) -> Path:
    """
    Get the HLS segment file path.
    
    Args:
        video_id: Video ID
        resolution: Resolution string
        segment: Segment filename
        
    Returns:
        Path: Segment file path
    """
    return get_hls_variant_dir(video_id, resolution) / segment