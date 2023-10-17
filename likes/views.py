from django.shortcuts import render
from django.http import HttpResponse
from storre.models import Order



def say_hello(request):
    queryset = Order.objects.filter(payment_status ='P').filter(order)
    return render(request, 'hello.html', {'name': 'Mosh'})
