from typing import Any

from django.shortcuts import (
    HttpResponse as HttpResponse, get_object_or_404, render
)

from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)

from django.urls import reverse_lazy, reverse

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.http import Http404
from django.core.paginator import Paginator
from django.views.generic.list import MultipleObjectMixin

from .models import Post, Comment, Category
from .forms import PostForm, CommentForm
from .handler import Handler
from datetime import date

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


class PermissionMixin(UserPassesTestMixin):

    def dispatch(self, request, *args, **kwargs):
        self._user = User(username=request.user.get_username())
        self._post = Post(author=self._user.get_username())
        self._comment = Comment(author=self._user.get_username())

        return super().dispatch(request, *args, **kwargs)


class PostListView(ListView):
    model = Post
    ordering = '-created_at'
    paginate_by = POSTS_PER_PAGE

    template_name = 'blog/index.html'

    def get_queryset(self):

        query = accuire_querry(Post).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=date.today()
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

        if self._category.is_published is False:
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:

        return {
            'category': {
                'title': self._category.title,
                'description': self._category.description
            },
            'page_obj': Paginator(accuire_querry(Post).filter(
                category__slug=self._category.slug,
                category__is_published=True,
                is_published=True,
                pub_date__lte=date.today()
            ), POSTS_PER_PAGE).get_page(self.request.GET.get('page'))
        }


class PostCreateView(CreateView, LoginRequiredMixin, PermissionMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):

        self._user = request.user

        if not request.user.is_authenticated:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        form.save()
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self._user.get_username()})


class PostUpdateView(UpdateView, LoginRequiredMixin, PermissionMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        self._post = get_object_or_404(Post, pk=kwargs['pk'])
        self._form = PostForm(
            request.POST or None, instance=self._post, files=request.FILES
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = self._form
        context.update({'comment_count': Comment.objects.count()})
        return context


class PostDeleteView(DeleteView, LoginRequiredMixin, PermissionMixin):
    model = Post
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        self._post = get_object_or_404(Post, pk=kwargs['pk'])
        self._form = PostForm(instance=self._post)

        if request.method is request.POST:
            self._post.delete()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = self._form
        return context


class PostDetailView(DetailView):
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

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.prefetch_related(
            'author'
        ).filter(
            post_id=self._post.pk
        )
        return context


class ProfileDetailView(DetailView, MultipleObjectMixin):
    model = User
    ordering = '-created_at'
    paginate_by = POSTS_PER_PAGE
    template_name = 'blog/profile.html'

    def get_object(self):
        return User.objects.get(username=self.kwargs.get('username'))

    def dispatch(self, request, *args, **kwargs):

        self._user = User(username=kwargs['username'])

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:

        return {
            'profile': self._user,
            'page_obj': Paginator(accuire_querry(Post).filter(
                author__username=self._user.get_username()
            ), POSTS_PER_PAGE).get_page(self.request.GET.get('page')),
        }


class CommentCreateView(CreateView, LoginRequiredMixin):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            raise PermissionDenied
        self._post = get_object_or_404(Post, pk=kwargs['pk'])
        self._user = request.user

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        form.instance.author = self._user
        form.instance.post = self._post

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self._post.pk})


class CommentUpdateView(UpdateView, LoginRequiredMixin, PermissionMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return Comment.objects.get(pk=self.kwargs.get('comk'))

    def dispatch(self, request, *args, **kwargs):
        self._post = get_object_or_404(Post, pk=kwargs['pk'])
        self._comment = Comment(pk=kwargs['comk'])
        self._form = CommentForm(
            request.POST or None, instance=self._comment, files=request.FILES
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = self._form
        context.update({'comment_count': Comment.objects.count})
        return context


class CommentDeleteView(DeleteView, LoginRequiredMixin, PermissionMixin):
    model = Comment
    form_class = CommentForm

    def get_object(self):
        return Comment.objects.get(pk=self.kwargs.get('comk'))

    def dispatch(self, request, *args, **kwargs):
        self._comment = Comment(pk=kwargs['comk'])
        self._post = get_object_or_404(Post, pk=kwargs['pk'])
        self._form = CommentForm(request.POST or None, instance=self._comment)
        self._comment.delete()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self._post.pk})


class ProfileEditUpdateView(UpdateView, LoginRequiredMixin, PermissionMixin):

    template_name = 'blog/user.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PasswordUpdateView(UpdateView, LoginRequiredMixin, PermissionMixin):

    template_name = 'registration/password_change_form.html'

    def dispatch(self, request, *args, **kwargs):
        self._user = User(username=request.user.get_username())
        return super().dispatch(request, *args, **kwargs)


def edit_profile(request):

    template_name = 'blog/user.html'

    return render(request, template_name)


def only_for_logged_in():
    return HttpResponse(
        'Только для залогиненых пользователей'
    )


def permission_denied(request, reason=None, template_name='403csrf.html'):
    return Handler._error_(request, 403)


def page_not_found(request, exception=None, template_name='404.html'):
    return Handler._error_(request, 404)


def server_error(request, exception=None, template_name='500.html'):
    return Handler._error_(request, 500)
