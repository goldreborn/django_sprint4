
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Profile
from django.urls import reverse_lazy, reverse


class ProfileListView(ListView):
    model = Profile
    ordering = 'id'
    paginate_by = 10


class ProfileCategoryListView(ProfileListView):
    model = Profile
    pass


class ProfileCreateView(CreateView, LoginRequiredMixin):
    model = Profile

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ProfileUpdateView(UpdateView, LoginRequiredMixin):
    model = Profile

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class ProfileDeleteView(DeleteView, LoginRequiredMixin):
    model = Profile
    success_url = reverse_lazy('birthday:list')


class ProfileDetailView(DetailView):
    model = Profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
