from django.urls import path

from .views import (
    get_all_users,
    get_one_user,
    update_user,
    login,
    signup,
    get_users_count,
)


urlpatterns = [
    path('', get_all_users, name="users"),
    path('user/<int:id>/', get_one_user, name="user"),
    path('user/<int:id>/edit/', update_user, name="update_user"),

    # authorization
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),

    path('count/', get_users_count, name="get_users_count"),
]
