from django.contrib import admin
from .models import Picture, Complaint, Geolocation, Verify, Comment, Like

class ComplaintInline(admin.TabularInline):
    model = Complaint
    extra = 0

class GeolocationInline(admin.TabularInline):
    model = Geolocation
    max_num = 1
    extra = 0

class VerifyInline(admin.StackedInline):
    model = Verify
    max_num = 1
    extra = 0

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content', 'user__cpf', 'user__email')
    inlines = [GeolocationInline, VerifyInline, ComplaintInline, CommentInline]
    
    actions = ['deactivate_pictures', 'activate_pictures']

    def deactivate_pictures(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_pictures.short_description = "Desativar fotos selecionadas"

    def activate_pictures(self, request, queryset):
        queryset.update(is_active=True)
    activate_pictures.short_description = "Ativar fotos selecionadas"

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('picture', 'title', 'created_at')
    list_filter = ('title', 'created_at')
    search_fields = ('title', 'content', 'picture__id')

@admin.register(Verify)
class VerifyAdmin(admin.ModelAdmin):
    list_display = ('picture', 'is_fake', 'created_at')
    list_filter = ('is_fake',)
    search_fields = ('picture__id', 'verify_message')

admin.site.register(Geolocation)
admin.site.register(Comment)
admin.site.register(Like)
