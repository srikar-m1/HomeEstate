from django.shortcuts import render


def index(request):
    return render(request, 'index.html')  # Render a basic home template
