from django.shortcuts import render


# Create your views here.

def temp_view(request):
    return render(request, 'raports/home.html')
