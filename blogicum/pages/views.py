from django.shortcuts import render


def about(request):
    template_name = 'pages/about.html'
    return render(request, template_name)


def rules(request):
    template_name = 'pages/rules.html'
    return render(request, template_name)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def permission_denied(request, exception=None):
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request, exception=None):
    return render(request, 'pages/500.html', status=500)
