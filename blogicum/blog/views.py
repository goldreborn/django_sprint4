from typing import Any

from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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


def accuire_querry(filtered=False, need_comments=False):

    req = Post.objects.select_related(
        'author', 'category', 'location'
    )

    if filtered:
        req = req.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    if need_comments:
        req = req.annotate(
            comment_count=Count('comments')
        ).order_by(
            '-pub_date'
        )
    return req


class PermissionMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class CommentMixin:
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDispatchMixin:

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(
            Comment, pk=kwargs['comment_id'], post_id=kwargs['post_id']
        )
        return super().dispatch(request, *args, **kwargs)


class PostListView(ListView):
    form_class = PostForm
    paginate_by = POSTS_PER_PAGE
    template_name = 'blog/index.html'
    queryset = accuire_querry(
        filtered=True, need_comments=True
    )


class PostCategoryListView(ListView):
    form_class = PostForm
    template_name = 'blog/category.html'
    paginate_by = POSTS_PER_PAGE

    def get_category(self):
        return get_object_or_404(
            Category, slug=self.kwargs['slug'], is_published=True
        )

    def get_queryset(self) -> QuerySet[Any]:
        return accuire_querry(filtered=True, need_comments=True).filter(
            category__slug=self.get_category().slug
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data()
        context['category'] = self.get_category()

        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.save()
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={
                'username': self.request.user.username
            }
        )


class PostUpdateView(
    LoginRequiredMixin, PermissionMixin, UpdateView
):
    model = Post
    form_class = PostForm
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
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(
    LoginRequiredMixin, PermissionMixin, DeleteView
):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(
            instance=get_object_or_404(Post, pk=kwargs['post_id']),
            files=self.request.FILES or None
        )
        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    form_class = CommentForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    queryset = accuire_querry(False, False)

    def get_object(self):

        post = get_object_or_404(Post, pk=self.kwargs['post_id'])

        access_denied = True if post.author != self.request.user else False
        post_hidden = True if not post.is_published else False
        hidden_category = True if not post.category.is_published else False
        in_future = True if post.pub_date > timezone.now() else False

        if access_denied and any([post_hidden, hidden_category, in_future]):
            raise Http404

        return post

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
                id=self.kwargs['post_id']
            )
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context


class CommentUpdateView(
    LoginRequiredMixin, PermissionMixin, CommentMixin,
    CommentDispatchMixin, UpdateView
):
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'comment_id'


class CommentDeleteView(
    LoginRequiredMixin, PermissionMixin, CommentMixin,
    CommentDispatchMixin, DeleteView
):
    template_name = 'blog/comment_confirm_delete.html'
    pk_url_kwarg = 'comment_id'


class ProfileDetailView(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PER_PAGE

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self) -> QuerySet[Any]:

        return accuire_querry(
            filtered=self.get_object() != self.request.user,
            need_comments=True
        ).filter(
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
