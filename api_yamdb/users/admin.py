from django.contrib import admin

from users.models import User
ist_filter = ('pub_date', 'review')


@admin.register(User)
class UsertAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'bio',
        'role',
        'email',
    )
    search_fields = ('username', 'email',)
    list_filter = ('role',)
    list_editable = (
        'role',
    )
