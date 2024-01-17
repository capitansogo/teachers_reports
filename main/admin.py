from django.contrib import admin

from main.models import *

admin.site.site_header = 'Отчетность'
admin.site.site_title = 'Отчетность'
admin.site.index_title = 'Администрирование'
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Division)



