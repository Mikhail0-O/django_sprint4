from django.urls import path

from . import views


app_name = 'blog'

urlpatterns = [
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),
    path('posts/<int:pk>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:id>/edit_comment/<int:pk>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('posts/<int:id>/delete_comment/<int:pk>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
    path('category/<slug:slug>/',
         views.CategoryListView.as_view(),
         name='category_posts'),
    path('profile/<slug:username>/',
         views.UserDetailView.as_view(),
         name='profile'),
    path('user/',
         views.UserUpdateView.as_view(),
         name='edit_profile'),
    path('',
         views.PostListView.as_view(),
         name='index'),
]
