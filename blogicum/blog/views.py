from typing import Any

from django.shortcuts import (get_object_or_404, redirect)

from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)

from django.urls import reverse_lazy, reverse

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.views.generic.list import MultipleObjectMixin
from django.http import Http404

from .models import Post, Comment, Category
from .forms import PostForm, CommentForm
from .handler import Handler
from datetime import date

User = get_user_model()

POSTS_PER_PAGE = 10


def accuire_querry(obj):

    return obj.objects.select_related(
        'location', 'author', 'category'
    )


def comments_count(query):

    for mod in query:
        mod.comment_count = Comment.objects.filter(
            post__pk=mod.pk
        ).count()


class PermissionMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostListView(ListView):
    model = Post
    ordering = '-pub_date'
    paginate_by = POSTS_PER_PAGE

    template_name = 'blog/index.html'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):

        query = accuire_querry(Post).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=date.today()
        )

        comments_count(query)

        return query


class PostCategoryListView(ListView):
    model = Post
    form_class = PostForm
    ordering = '-pub_date'
    template_name = 'blog/category.html'

    def dispatch(self, request, *args, **kwargs):
        self._category = get_object_or_404(Category, slug=kwargs['slug'])

        if not self._category.is_published:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:

        context = {
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

        comments_count(context['page_obj'])

        return context


class PostCreateView(LoginRequiredMixin, CreateView):
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


class PostUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):

        self._post = get_object_or_404(Post, pk=kwargs['post_id'])

        if not request.user.is_authenticated:
            return redirect(reverse('blog:post_detail',
                                    kwargs={'post_id': self._post.pk}))

        self._form = PostForm(
            request.POST or None, instance=self._post
        )

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context['form'] = self._form
        return context


class PostDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        self._post = get_object_or_404(Post, pk=kwargs['post_id'])
        self._form = PostForm(instance=self._post)

        if request.method is request.POST:
            self._post.delete()

        if not request.user.is_authenticated:
            return redirect('login')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = self._form
        return context


class PostDetailView(DetailView):
    model = Post
    form_class = CommentForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self._post = get_object_or_404(Post, pk=kwargs['post_id'])
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
        ).order_by(
            'created_at'
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            raise PermissionDenied
        self._post = get_object_or_404(Post, pk=kwargs['post_id'])
        self._user = request.user

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        form.instance.author = self._user
        form.instance.post = self._post

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self._post.pk})


class CommentUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'comk'

    def dispatch(self, request, *args, **kwargs):
        self._comment = Comment.objects.get(
            pk=kwargs['comk']
        )
        self._post = Post.objects.get(
            pk=kwargs['post_id']
        )
        self._form = CommentForm(
            request.POST or None
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = self._form
        return context


class CommentDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_confirm_delete.html'
    pk_url_kwarg = 'comk'

    def dispatch(self, request, *args, **kwargs):
        self._post = Post.objects.get(pk=kwargs['post_id'])
        self._comment = Comment.objects.get(
            pk=kwargs['comk']
        )
        self._form = CommentForm(request.POST or None, instance=self._comment)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        self._comment.delete()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self._post.pk})


class ProfileDetailView(DetailView, MultipleObjectMixin):
    model = User
    ordering = '-created_at'
    paginate_by = POSTS_PER_PAGE
    template_name = 'blog/profile.html'
    raise_exception = True

    def get_object(self):
        return User(username=self.kwargs.get('username'))

    def dispatch(self, request, *args, **kwargs):

        self._user = self.get_object()

        if User.objects.get(username=request.user.get_username()).DoesNotExist:
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:

        context = {
            'profile': self._user,
            'page_obj': Paginator(accuire_querry(Post).filter(
                author__username=self._user.get_username()
            ), POSTS_PER_PAGE).get_page(self.request.GET.get('page'))
        }

        comments_count(context['page_obj'])

        return context


class ProfileEditView(PermissionMixin, LoginRequiredMixin, UpdateView):

    template_name = 'blog/user.html'
    fields = '__all__'
    slug_url_kwarg = 'username'

    def get_object(self):
        return User(username=self.kwargs.get('username'))

    def dispatch(self, request, *args, **kwargs):

        self._user = self.get_object()

        if self.request.user is not self._user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class PasswordUpdateView(UpdateView, LoginRequiredMixin, UserPassesTestMixin):

    template_name = 'registration/password_change_form.html'

    def dispatch(self, request, *args, **kwargs):
        self._user = User(username=request.user.get_username())
        return super().dispatch(request, *args, **kwargs)


def csrf_failure(request, reason=''):
    return Handler._error_(request, 403)


def page_not_found(request, exception):
    return Handler._error_(request, 404)


def server_error(request):
    return Handler._error_(request, 500)
