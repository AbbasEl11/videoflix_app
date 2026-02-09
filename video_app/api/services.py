from ..models import Video

def list_videos_queryset():
    """
    Retrieve all videos ordered by creation date descending.
    
    Returns:
        QuerySet: Video queryset ordered by newest first
    """
    return Video.objects.all().order_by('-created_at')

def get_video_by_id(video_id: int) -> Video:
    """
    Retrieve a single video by its ID.
    
    Args:
        video_id: Primary key of the video
        
    Returns:
        Video: Video instance
        
    Raises:
        Video.DoesNotExist: If video with given ID doesn't exist
    """
    return Video.objects.get(id=video_id)