
from blogicum.settings import TEMPLATES_PATH
from os import listdir
from django.shortcuts import render
from inspect import getmembers


ERROR_TEMPLATES = listdir(f'{TEMPLATES_PATH}/pages/errors/')


class Handler(Exception):

    @staticmethod
    def _error_(request, error_type: int):
        for x in ERROR_TEMPLATES:
            if str(error_type) in x:
                return render(
                    request=request,
                    template_name=f'{TEMPLATES_PATH}{x}',
                    status=error_type
                )
