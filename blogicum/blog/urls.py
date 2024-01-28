from django.urls import path
from django.contrib.auth.views import PasswordResetConfirmView

from . import views


app_name = 'blog'

handler403 = 'blog.views.csrf_failure_error'
handler404 = 'blog.views.page_not_found_error'
handler500 = 'blog.views.template_error'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),


    path('profile/<slug:username>/edit/',
         views.ProfileUpdateView.as_view(),
         name='edit_profile'),

    path('profile/<slug:username>/',
         views.ProfileDetailView.as_view(),
         name='profile'),
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'),

    path('category/<slug:slug>/',
         views.PostCategoryListView.as_view(),
         name='category_posts'),

    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),

    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),

    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'),

    path('logged_in_only/', views.only_for_logged_in),
    path('<int:pk>/comment/', views.CommentCreateView.as_view(), name='add_comment')
]
