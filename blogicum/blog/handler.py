from django.shortcuts import render

ERROR_TEMPLATES = [
    '403csrf.html',
    '404.html',
    '500.html'
]


class Handler(Exception):

    @staticmethod
    def _error_(request, error_type: int):
        for x in ERROR_TEMPLATES:
            if str(error_type) in x:
                return render(
                    request=request,
                    template_name=f'pages/errors/{x}',
                    status=error_type
                )
