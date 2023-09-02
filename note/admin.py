from django.contrib import admin

from .models import Place

# Register your models here.
class NoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'completed_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(Place, NoteAdmin)
