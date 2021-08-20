from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('404/', views.page_not_found, name='page_not_found'),
    path('500/', views.server_error, name='server_error'),
    path('new/', views.new_post, name="new_post"),
    path('follow/', views.follow_index, name="follow_index"),
    path('group/<slug:slug>/', views.group_posts, name="post_in_group"),
    path('<str:username>/', views.profile, name="profile"),
    path('<str:username>/follow/', views.profile_follow,
         name="profile_follow"),
    path('<str:username>/unfollow/', views.profile_unfollow,
         name="profile_unfollow"),
    path('<str:username>/<int:post_id>/', views.post_view, name="post"),
    path('<str:username>/<int:post_id>/edit/',
         views.post_edit, name="post_edit"),
    path('<str:username>/<int:post_id>/comment/',
         views.add_comment, name="add_comment"),
]
