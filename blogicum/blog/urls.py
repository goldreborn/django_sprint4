from django.urls import path


from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),

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

    path('posts/<int:pk>/comment/',
         views.CommentCreateView.as_view(), name='add_comment'),

    path('posts/<int:pk>/edit_comment/<int:comk>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),

    path('posts/<int:pk>/delete_comment/<int:comk>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),
]
