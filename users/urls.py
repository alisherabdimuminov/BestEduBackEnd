from django.urls import path

from .views import (
    get_all_users,
    get_one_user,
    update_user,
    login,
    signup,
    logout,
    get_users_count,
    change_password,
)


urlpatterns = [
    path('', get_all_users, name="users"),
    path('user/<int:id>/', get_one_user, name="user"),
    path('user/<int:id>/edit/', update_user, name="update_user"),

    # authorization
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout, name='logout'),

    path('count/', get_users_count, name="get_users_count"),
    path('change_password/', change_password, name="change_password"),
]
