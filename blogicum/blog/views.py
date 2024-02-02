from typing import Any
from django.http.response import HttpResponseRedirect

from django.shortcuts import (get_object_or_404, redirect)

from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)

from django.urls import reverse_lazy, reverse

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
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


class PostMixin:
    model = Post
    form_class = PostForm

    def get_success_url(self):

        if self.__class__.__name__.__contains__('Delete'):
            return reverse('blog:index')
        elif self.__class__.__name__.__contains__('Create'):
            return reverse(
                'blog:profile', kwargs={
                    'username': self.request.user.get_username()
                }
            )
        else:
            return reverse(
                'blog:post_detail', kwargs={"post_id": self.kwargs["post_id"]}
            )


class CommentMixin():
    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={"post_id": self.kwargs["post_id"]}
        )


class PostListView(PostMixin, ListView):
    ordering = 'pub_date'
    paginate_by = POSTS_PER_PAGE

    template_name = 'blog/index.html'

    def get_queryset(self):

        query = accuire_querry(Post).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=date.today()
        )

        comments_count(query)

        return query


class PostCategoryListView(PostMixin, ListView):
    ordering = 'pub_date'
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


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'

    def form_valid(self, form):

        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(
    PermissionMixin, LoginRequiredMixin, PostMixin, UpdateView
):
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):

        self._post = get_object_or_404(Post, pk=kwargs['post_id'])

        self._form = PostForm(
            request.POST or None, instance=self._post
        )

        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseRedirect(
            reverse('blog:post_detail', kwargs={'post_id': self._post.pk})
        )

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = self._form
        return context

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self._post.pk})


class PostDeleteView(
    PermissionMixin, LoginRequiredMixin, PostMixin, DeleteView
):
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

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
            pk=self._post.pk,
            is_published=True
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.prefetch_related(
            'author'
        ).filter(
            is_published=True,
            post_id=self._post.pk
        ).order_by(
            'created_at'
        )
        return context


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):

    def form_valid(self, form):

        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=date.today()),
            id=self.kwargs["post_id"])

        return super().form_valid(form)


class CommentUpdateView(
    PermissionMixin, LoginRequiredMixin, CommentMixin, UpdateView
):
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'comk'

    def dispatch(self, request, *args, **kwargs):
        self._comment = get_object_or_404(
            Comment, pk=kwargs['comk']
        )
        self._post = Post.objects.get(
            pk=kwargs['post_id']
        )
        self._form = CommentForm(
            request.POST or None, instance=self._comment
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


class CommentDeleteView(
    PermissionMixin, LoginRequiredMixin, CommentMixin, DeleteView
):
    template_name = 'blog/comment_confirm_delete.html'
    pk_url_kwarg = 'comk'

    def dispatch(self, request, *args, **kwargs):
        self._post = Post.objects.get(pk=kwargs['post_id'])
        self._comment = get_object_or_404(
            Comment, pk=kwargs['comk']
        )
        self._form = CommentForm(request.POST or None, instance=self._comment)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        self._comment.delete()

        return super().form_valid(form)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    ordering = 'pub_date'
    template_name = 'blog/profile.html'
    raise_exception = True

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def dispatch(self, request, *args, **kwargs):

        self._user = self.get_object()

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


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User

    template_name = 'blog/user.html'
    fields = '__all__'
    slug_field = 'username'

    def get_object(self):
        return User.objects.get(username=self.kwargs.get('username'))

    def dispatch(self, request, *args, **kwargs):

        self._user = self.get_object()

        return super().dispatch(request, *args, **kwargs)


def csrf_failure(request, exception):
    return Handler._error_(request, 403)


def page_not_found(request, exception):
    return Handler._error_(request, 404)


def server_error(request):
    return Handler._error_(request, 500)
