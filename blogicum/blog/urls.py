from django.urls import path

from . import views
from blogicum.settings import TEMPLATES_PATH

app_name = 'blog'

handler404 = f'{TEMPLATES_PATH}/404.html'
handler500 = f'{TEMPLATES_PATH}/500.html'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('profile/<slug:profile_slug>/', views.Post.author.),
    path('posts/<int:post_id>/',
         views.PostDetailView.as_view(),
         name='post_detail'),
    path('category/<slug:category_slug>/',
         views.PostCategoryListView.as_view(),
         name='category_posts'),
    path('posts/<int:post_id>/edit/',
         views.PostUpdateView.as_view(),
         name='post_edit'),
    path('posts/<int:post_id>/delete/',
         views.PostDeleteView.as_view(),
         name='post_delete'),
    path('posts/create/',
         views.PostCreateView.as_view(),
         name='post_create'),
    path('logged_in_only/', views.only_for_logged_in),
]
