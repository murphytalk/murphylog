from django.contrib import admin
from models import Entry

class EntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject','text','text_type','private','post_date','last_edit']
#    prepopulated_fields = {
#        'slug': ('first_name', 'last_name')
#    }

admin.site.register(Entry, EntryAdmin)
