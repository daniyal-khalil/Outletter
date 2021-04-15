from django.contrib import admin
from django.core.paginator import Paginator

from Outletter.user.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ordering = ('-date_joined', )
    list_filter = ('is_staff', 'is_active')
    list_display = ('email', 'user_name', 'first_name', 'last_name', 'profile_image')
    search_fields = ('email', 'user_name', 'first_name', 'last_name')
    paginator = Paginator
    list_per_page = 5