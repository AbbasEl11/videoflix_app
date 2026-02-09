from video_app.models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .tasks import process_video_to_hls, generate_thumbnail_for_video
import django_rq, os, shutil
from django.conf import settings

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal handler triggered after a Video instance is saved.
    Enqueues background tasks for video processing and thumbnail generation.
    
    Args:
        sender: Model class (Video)
        instance: Video instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(process_video_to_hls, video_id= instance.id)
        queue.enqueue(generate_thumbnail_for_video, instance, instance.video_file.path)

@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    Signal handler triggered after a Video instance is deleted.
    Removes associated video files, thumbnails, and HLS directories.
    
    Args:
        sender: Model class (Video)
        instance: Video instance that was deleted
        **kwargs: Additional keyword arguments
    """
    video_id = instance.id

    if getattr(instance, "video_file", None) and instance.video_file:
        try: 
            if os.path.exists(instance.video_file.path):
                os.remove(instance.video_file.path)
        except Exception:
            pass

    if getattr(instance, "thumbnail", None) and instance.thumbnail:
        try: 
            if os.path.exists(instance.thumbnail.path):
                os.remove(instance.thumbnail.path)
        except Exception:
            pass

    hls_dir = os.path.join(getattr(settings, "MEDIA_ROOT", ""), 'hls', str(video_id))
    try:
        if os.path.exists(hls_dir):
            shutil.rmtree(hls_dir)
    except Exception:
        pass