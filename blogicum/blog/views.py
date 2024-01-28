from typing import Any
from django.db.models.base import Model as Model

from django.shortcuts import (
    HttpResponse as HttpResponse, get_object_or_404, redirect, render
)

from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)

from django.views.generic.edit import FormMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from functools import wraps

from .models import Post, Comment, Category
from .forms import PostForm, CommentForm
from .handler import Handler

User = get_user_model()

POSTS_PER_PAGE = 10

POST_CHANGEBLES = [
    'title',
    'text'
]

COMMENT_CHANGEBLES = [
    'text'
]

PROFILE_CHANGEBLES = [
    'first_name',
    'last_name',
    'birthday'
]

def accuire_querry(obj):

    return obj.objects.select_related(
        'location', 'author', 'category'
    )


class PostListView(ListView):
    model = Post
    ordering = '-created_at'
    paginate_by = POSTS_PER_PAGE

    template_name = 'blog/index.html'
    
    def get_queryset(self):
    
        query = Post.objects.select_related(
                'author', 'location', 'category'
            ).filter(
                is_published=True,
                category__is_published=True
            )

        return query


class PostCategoryListView(ListView):
    model = Post
    form_class = PostForm
    ordering = '-created_at'
    paginate_by = POSTS_PER_PAGE

    template_name = 'blog/category.html'

    def dispatch(self, request, *args, **kwargs):
        self._category = get_object_or_404(Category, slug=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:

        return {
            'category': {
                'title': self._category.title,
                'description': self._category.description
            },
            'page_obj': accuire_querry(Post).filter(
                category__slug=self._category.slug,
                category__is_published=True,
                is_published=True
            )
        }


class PostCreateView(CreateView, LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            raise PermissionDenied
        self._form = PostForm(request.POST or None)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        form.save()
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(UpdateView, LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class PostDeleteView(DeleteView, LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/index.html'
    

    def dispatch(self, request, *args, **kwargs):
        self._post = get_object_or_404(Post, pk=kwargs['pk'])
        self._form = PostForm(request.POST or None, instance=self._post, files=request.FILES)
        self._post.delete
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self._post.pk})


class PostDetailView(DetailView, FormMixin):
    model = Post
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        self._post = get_object_or_404(Post, pk=kwargs['pk'])

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        return super().get_queryset().filter(
            pk=self._post.pk
        )


class ProfileDetailView(DetailView):
    model = User
    ordering = '-created_at'
    paginate_by = POSTS_PER_PAGE
    template_name = 'blog/profile.html'

    def get_object(self):
        return User.objects.get(username=self.kwargs.get("username"))

    def dispatch(self, request, *args, **kwargs):

        self._user = User(username=kwargs['username'])

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:

        return {
            'profile': self._user,
            'page_obj': accuire_querry(Post).filter(
                author__username=self._user.get_username()
            ),
            'comment_form': CommentForm()
        }


class ProfileUpdateView(UpdateView, LoginRequiredMixin):
    model = User
    from_class = PostForm
    template_name = 'blog/profile.html'
    success_url = reverse_lazy('blog:profile')
    fields = '__all__'

    def get_object(self):
        return User.objects.get(username=self.kwargs.get("username"))


class CommentCreateView(CreateView, LoginRequiredMixin):
    model = Comment
    form_class = CommentForm

    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self._post = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        form = form.save(commit=False)

        form.author = self.request.user
        form.post = self._post

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self._post.pk})


def identity_required(instance):
    def decorate(func):
        @wraps(func)
        def wrapper(request, pk):
            probe = get_object_or_404(instance, pk=pk, author=request.user)
            if probe.author != request.user:
                raise PermissionDenied(
                    'Нет доступа к данной странице'
                )
            return func(request, pk)
        return wrapper
    return decorate


def only_for_logged_in():
    return HttpResponse(
        'Только для залогиненых пользователей'
    )


@identity_required(Comment)
@login_required
def add_comment(request, pk):

    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        Comment = form.save(commit=False)
        Comment.author = request.user
        Comment.created_at = now()
        Comment.post = post
        Comment.save()
    return redirect('post:detail', pk=pk)


def csrf_failure_error(request, reason=''):
    return Handler._error_(request, 403)


def page_not_found_error(request, reason=''):
    return Handler._error_(request, 404)


def template_error(request, reason=''):
    return Handler._error_(request, 500)
