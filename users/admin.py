from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import User, Order
from .forms import UserModelCreateForm, UserModelUpdateForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


@admin.register(User)
class UserModelAdmin(ModelAdmin):
    add_form = UserCreationForm
    form_class = UserChangeForm
    add_fieldsets = (
        ("Yangi foydalanuvchi qo'shish", {
            "fields": ("username", "first_name", "last_name", "middle_name", "password",)
        }), 
    )
    fieldsets = (
        ("Foydalanuvchini tahrirlash", {
            "fields": ("username", "first_name", "last_name", "middle_name", "bio", "image", )
        }), 
    )
    list_display = ["username", "first_name", "last_name", "activity"]
    search_fields = ["username", "first_name", "last_name", "middle_name"]
    list_filter = ["activity"]


@admin.register(Order)
class OrderModelAdmin(ModelAdmin):
    list_display = ["pk", "amount", ]
