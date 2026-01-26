from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at', 'has_thumbnail')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description', 'category')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Video Informationen', {
            'fields': ('title', 'description', 'category')
        }),
        ('Dateien', {
            'fields': ('video_file', 'thumbnail_url')
        }),
        ('Zeitstempel', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_thumbnail(self, obj):
        return bool(obj.thumbnail_url)
    has_thumbnail.boolean = True
    has_thumbnail.short_description = 'Thumbnail'
