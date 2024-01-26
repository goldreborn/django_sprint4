
from blogicum.settings import TEMPLATES_PATH
from os import listdir
from django.shortcuts import render

ERROR_TEMPLATES = listdir(f'{TEMPLATES_PATH}/pages/errors')


class ErrorHandler(Exception):

    def _error_(request, error_type: int):
        for enum, x in enumerate(ERROR_TEMPLATES):
            if str(error_type) in x:
                return render(
                    request=request,
                    template_name=f'{TEMPLATES_PATH}{x}',
                    status=map(
                        lambda x: x if x.isdigit() else None,
                        ERROR_TEMPLATES[enum]
                    )
                )