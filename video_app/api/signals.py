from video_app.models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .tasks import process_video_to_hls
import django_rq, os, shutil
from django.conf import settings

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        print("Video created, enqueueing processing task.")
        print(f"Video ID: {instance.id}, Video Path: {instance.video_file.path}")

        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(process_video_to_hls, video_id= instance.id)

@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    video_id = instance.id

    if getattr(instance, "video_file", None) and instance.video_file:
        try: 
            if os.path.exists(instance.video_file.path):
                os.remove(instance.video_file.path)
        except Exception:
            pass

    if getattr(instance, "thumbnail_url", None) and instance.thumbnail_url:
        try: 
            if os.path.exists(instance.thumbnail_url.path):
                os.remove(instance.thumbnail_url.path)
        except Exception:
            pass

    hls_dir = os.path.join(getattr(settings, "MEDIA_ROOT", ""), 'hls', str(video_id))
    try:
        if os.path.exists(hls_dir):
            shutil.rmtree(hls_dir)
    except Exception:
        pass