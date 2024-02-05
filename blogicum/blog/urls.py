from django.urls import path, include

from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),

    path('profile/<str:username>/',
         views.ProfileDetailView.as_view(),
         name='profile'),

    path('edit/',
         views.ProfileEditView.as_view(),
         name='edit_profile'),

    path('posts/', include('blog.paths_url')),

    path('category/<slug:slug>/',
         views.PostCategoryListView.as_view(),
         name='category_posts'),
]
