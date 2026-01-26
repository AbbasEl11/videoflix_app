from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserModel


class UserModelInline(admin.StackedInline):
    model = UserModel
    can_delete = False
    verbose_name_plural = 'Benutzer Profil'
    readonly_fields = ('uidb64', 'token')


class UserAdmin(BaseUserAdmin):
    inlines = (UserModelInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    date_hierarchy = 'date_joined'


# Unregister the original User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'uidb64', 'get_email', 'get_is_active')
    list_filter = ('user__is_active',)
    search_fields = ('user__username', 'user__email', 'token', 'uidb64')
    readonly_fields = ('uidb64',)
    
    fieldsets = (
        ('Benutzer Information', {
            'fields': ('user',)
        }),
        ('Verifizierung', {
            'fields': ('uidb64', 'token')
        }),
    )
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    def get_is_active(self, obj):
        return obj.user.is_active
    get_is_active.boolean = True
    get_is_active.short_description = 'Aktiv'
    get_is_active.admin_order_field = 'user__is_active'
