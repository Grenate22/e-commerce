from django.shortcuts import render
from django.http import HttpResponse
from .tasks import notify_customers

# Create your views here.
def hello(request):
    notify_customers.delay('hello')
    return HttpResponse('who dey zuzu')