from django.shortcuts import get_object_or_404
from .models import Post
from .error_handler import ErrorHandler
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied

POSTS_ON_MAIN = 10




@login_required
def only_for_logged_in(request):
    return HttpResponseForbidden(
        'Только для зарегистрированных пользователей'
    )


def csrf_failure_error(request):
    return ErrorHandler._error_(request, 403)


def page_not_found_error(request):
    return ErrorHandler._error_(request, 404)


def template_error(request):
    return ErrorHandler._error_(request, 500)
