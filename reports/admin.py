from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reason', 'reporter', 'is_resolved', 'created_at')
    list_filter = ('reason', 'is_resolved', 'created_at')
    search_fields = ('reporter__cpf', 'description')
    
    actions = ['resolve_reports']

    def resolve_reports(self, request, queryset):
        queryset.update(is_resolved=True)
    resolve_reports.short_description = "Marcar como resolvidos"
