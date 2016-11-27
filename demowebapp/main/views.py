from django.shortcuts import render
import os
from version import VERSION


def get_files(path='./'):
    for top, dirs, files in os.walk(path):
        for nm in files:
            if not './.' in top and not nm.startswith('.'):
                yield os.path.join(top, nm)


# Create your views here.
def home(request):
    context = {'title': 'Sample Web App',
               'subtitle': 'Version {0}'.format(VERSION),
               'body': list(get_files('./cloudshell-artifactory-demo'))}
    return render(request, 'main/home.html', context)
