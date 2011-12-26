from django.shortcuts import render


def index(request):
    return render(request, 'site_index/index.html')

