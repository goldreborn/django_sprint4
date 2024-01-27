from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import (
    get_object_or_404, redirect, render, HttpResponse
)

from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)

from django.urls import reverse_lazy, reverse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from functools import wraps

from users.models import Profile
from .models import Post, Comment
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


class PostListView(ListView):
    model = Post
    ordering = '-date_published'
    paginate_by = POSTS_PER_PAGE


class PostCategoryListView(PostListView):
    queryset = Post.objects.prefetch_related(
        'category'
    )


class PostCreateView(CreateView, LoginRequiredMixin):
    model = Post
    form_class = PostForm

    fields = '__all__'
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(UpdateView, LoginRequiredMixin):
    model = Post
    form_class = PostForm

    fields = '__all__'


class PostDeleteView(DeleteView, LoginRequiredMixin):
    model = Post
    success_url = reverse_lazy('blog:index')


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.Comment.select_related('author')
        )
        return context


class ProfileDetailView(DetailView):
    model = User
    ordering = '-created_at'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self) -> QuerySet[Any]:

        query_set = super().get_queryset()

        query_set.prefetch_related(
            'posts'
        ).filter(
            author=self.request.user
        )

        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            context = {filter(
                lambda x: x if 'password' not in x else None,
                context
            )}

        profile = {'profile': context}

        return profile


class CommentCreateView(CreateView, LoginRequiredMixin):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self._post = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self._post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post:detail', kwargs={'pk': self._post.pk})


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


def edit_instance(obj, request, pk, changebles):

    instance = get_object_or_404(obj, pk=pk)
    instance_name = obj.__name__.lower()

    form = globals()[f'{obj}Form']()(request.POST or None, instance=instance)

    context = {'form': form}

    if form.is_valid():
        form.save()
        new_changes = {i: form.cleaned_data[i] for i in changebles}

        context.update(new_changes)
    return render(request, f'{instance_name}:detail', context)


def delete_instance(obj, request, pk):

    instance = get_object_or_404(obj, pk=pk)
    instance_name = obj.__name__.lower()

    form = obj(instance=instance)

    context = {'form': form}

    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request, f'{instance_name}/{instance_name}.html', context)


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


@login_required
@identity_required(Comment)
def edit_comment(request, pk):
    edit_instance(Comment, request, pk, COMMENT_CHANGEBLES)


@login_required
@identity_required(Profile)
def edit_profile(request, pk):
    edit_instance(Profile, request, pk, PROFILE_CHANGEBLES)


@login_required
@identity_required(Post)
def edit_post(request, pk):
    edit_instance(Post, request, pk, POST_CHANGEBLES)


@login_required
@identity_required(Comment)
def delete_comment(request, pk):
    delete_instance(Comment, request, pk)


@login_required
@identity_required(Post)
def delete_post(request, pk):
    delete_instance(Post, request, pk)


@login_required
@identity_required(Profile)
def password_change(request, pk):
    pass


def csrf_failure_error(request, reason=''):
    return Handler._error_(request, 403)


def page_not_found_error(request, reason=''):
    return Handler._error_(request, 403)


def template_error(request, reason=''):
    return Handler._error_(request, 500)
