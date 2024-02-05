from typing import Any

from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)

from django.urls import reverse_lazy, reverse

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone

from .models import Post, Comment, Category

from .forms import PostForm, CommentForm

User = get_user_model()

POSTS_PER_PAGE = 10


def accuire_querry(filtered: bool, need_comments: bool):

    req = Post.objects.select_related(
        'author', 'category', 'location'
    )

    if filtered is True:
        req = req.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    if need_comments is True:
        req = req.annotate(
            comment_count=Count('comments')
        )
    return req


class PermissionMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostMixin:
    model = Post
    form_class = PostForm


class CommentMixin:
    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={"post_id": self.kwargs["post_id"]}
        )


class PostListView(PostMixin, ListView):
    ordering = '-pub_date'
    paginate_by = POSTS_PER_PAGE
    template_name = 'blog/index.html'
    queryset = accuire_querry(filtered=True, need_comments=True)


class PostCategoryListView(PostMixin, ListView):
    ordering = '-pub_date'
    template_name = 'blog/category.html'
    paginate_by = POSTS_PER_PAGE

    def get_category(self):
        return get_object_or_404(Category, slug=self.kwargs['slug'])

    def dispatch(self, request, *args, **kwargs):

        if not self.get_category().is_published:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        return accuire_querry(filtered=True, need_comments=True).filter(
            category__slug=self.get_category().slug
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data()
        context['category'] = self.get_category()

        return context


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.save()
        form.instance.author = self.request.user
        form.files = self.request.FILES
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={
                'username': self.request.user.username
            }
        )


class PostUpdateView(
    LoginRequiredMixin, PermissionMixin, PostMixin, UpdateView
):
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        return redirect(
            reverse_lazy(
                'blog:post_detail',
                kwargs={
                    'post_id': self.kwargs['post_id']
                }
            )
        )

    def get_success_url(self) -> str:
        return reverse(
            'blog:post_detail', kwargs={"post_id": self.kwargs["post_id"]}
        )


class PostDeleteView(
    LoginRequiredMixin, PermissionMixin, PostMixin, DeleteView
):
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        self._post = get_object_or_404(Post, pk=kwargs['post_id'])
        self._form = PostForm(
            instance=self._post,
            files=self.request.FILES or None
        )
        context['form'] = self._form
        return context

    def get_success_url(self):
        return reverse('blog:index')


class PostDetailView(LoginRequiredMixin, DetailView):
    form_class = CommentForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    queryset = accuire_querry(False, False)

    def get_object(self):

        _post = get_object_or_404(Post, pk=self.kwargs['post_id'])

        permission_denied = True if _post.author != self.request.user else False
        post_hidden = True if not _post.is_published else False
        hidden_categor = True if not _post.category.is_published else False
        in_future = True if _post.pub_date > timezone.now() else False

        if permission_denied and any([post_hidden, hidden_categor, in_future]):
            raise Http404

        return _post

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.select_related(
            'author'
        ).filter(
            post_id=self.get_object().pk
        ).order_by(
            'created_at'
        )
        return context


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):

    def form_valid(self, form):

        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post.objects.filter(
                id=self.kwargs["post_id"]
            )
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context


class CommentUpdateView(
    LoginRequiredMixin, PermissionMixin, CommentMixin, UpdateView
):
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(
            Comment, pk=kwargs['comment_id'], post_id=kwargs['post_id']
        )
        return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(
    LoginRequiredMixin, PermissionMixin, CommentMixin, DeleteView
):
    template_name = 'blog/comment_confirm_delete.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(
            Comment, pk=kwargs['comment_id'], post_id=kwargs['post_id']
        )

        return super().dispatch(request, *args, **kwargs)


class ProfileDetailView(ListView):
    model = User
    ordering = '-pub_date'
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PER_PAGE

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self) -> QuerySet[Any]:
        return accuire_querry(filtered=False, need_comments=True).filter(
            author__username=self.get_object().username
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data()
        context['profile'] = self.get_object()

        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ('first_name', 'last_name', 'username', 'email', )

    def get_success_url(self) -> str:
        return reverse('blog:index')

    def get_object(self):
        return self.request.user
