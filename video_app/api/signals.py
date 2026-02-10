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
    Enqueues HLS processing on creation and thumbnail generation when missing.
    
    Args:
        sender: Model class (Video)
        instance: Video instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    queue = django_rq.get_queue('default', autocommit=True)
    
    if created:
        queue.enqueue(process_video_to_hls, video_id= instance.id)
    
    if not instance.thumbnail:
        queue.enqueue(generate_thumbnail_for_video, instance.id, instance.video_file.path)

@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    Signal handler triggered after a Video instance is deleted.
    Removes associated HLS directories from the filesystem.
    
    Args:
        sender: Model class (Video)
        instance: Video instance that was deleted
        **kwargs: Additional keyword arguments
        
    Note:
        File cleanup for video_file and thumbnail is handled by django-cleanup.
    """
    video_id = instance.id
    hls_dir = os.path.join(getattr(settings, "MEDIA_ROOT", ""), 'hls', str(video_id))
    
    try:
        if os.path.exists(hls_dir):
            shutil.rmtree(hls_dir)
    except Exception:
        pass