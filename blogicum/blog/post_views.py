
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from inspect import currentframe
from .models import Post
from django.urls import reverse_lazy, reverse

class PostListView(ListView):
    model = Post
    ordering = 'id'
    paginate_by = 10

class PostCategoryListView(PostListView):
    model = Post
    pass


class PostCreateView(CreateView, LoginRequiredMixin):
    model = Post

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(UpdateView, LoginRequiredMixin):
    model = Post

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostDeleteView(DeleteView, LoginRequiredMixin):
    model = Post
    success_url = reverse_lazy('birthday:list')


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context