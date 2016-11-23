from django.shortcuts import render
import os


def get_files(path='./'):
    for top, dirs, files in os.walk(path):
        for nm in files:
            yield os.path.join(top, nm)


# Create your views here.
def home(request):
    context = {'title': 'Sample Web App',
               'subtitle': 'Version 9.9.9',
               'body': list(get_files())}
    return render(request, 'main/home.html', context)
