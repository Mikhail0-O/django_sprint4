from http import HTTPStatus

from django.shortcuts import render
from django.views.generic import TemplateView


class About(TemplateView):
    template_name = 'pages/about.html'


class Rules(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=HTTPStatus.NOT_FOUND)


def permission_denied(request, exception=None):
    return render(request, 'pages/403csrf.html', status=HTTPStatus.FORBIDDEN)


def server_error(request, exception=None):
    return render(request, 'pages/500.html', status=HTTPStatus.LOOP_DETECTED)
