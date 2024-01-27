from django.urls import path
from blogicum.settings import TEMPLATES_PATH

from . import views


app_name = 'blog'

handler403 = 'blog.views.csrf_failure_error'
handler404 = 'blog.views.page_not_found_error'
handler500 = 'blog.views.template_error'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('profile/<slug:profile_slug>/',
         views.ProfileDetailView.as_view()),
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
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('<int:pk>/comment/edit/', views.edit_comment, name='edit_comment'),
    path('<int:pk>/comment/delete/', views.delete_comment, name='delete_comment'),
]
