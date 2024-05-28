from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class UserModelCreateForm(UserCreationForm):
    class Meta:
        fields = ( "username", "first_name", "last_name", "middle_name", "bio", "password1", "password2", )

class UserModelUpdateForm(UserChangeForm):
    class Meta:
        fields = ( "username", "first_name", "last_name", "middle_name", "bio", "image", )
