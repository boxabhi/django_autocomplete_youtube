from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache import cache

from ipware import get_client_ip
from faker import Faker
fake = Faker()
from .models import *


def generate_data(request):
    for i in range(0 , 100):
        FakeAddress.objects.create(address=fake.address())
    return JsonResponse({'status' : 200})




def home(request):
    return render(request, 'index.html')



def search_address(request):
    address = request.GET.get('address')
    payload = []
    if address:
        fake_address_objs = FakeAddress.objects.filter(address__icontains=address)
        
        for fake_address_obj in fake_address_objs:
            payload.append(fake_address_obj.address)


    return JsonResponse({'status' : 200 , 'data' : payload})

















CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip





def rate_limiting(request):
    current_ip = get_client_ip(request)
    
    if cache.get(current_ip):
        total_calls = cache.get(current_ip)
        if total_calls >= 5:
            return JsonResponse({'status' : 501 , 'message' : 'You have exahusted the limit' , 'time' : f'You can try after {cache.ttl(current_ip)} seconds'})
        else:
            cache.set(current_ip, total_calls+1)
            return JsonResponse({'status' : 200 , 'message' : 'You called this api' , 'total_calls' : total_calls})
            
                
    
    cache.set(current_ip , 1 , timeout=60)
    return JsonResponse({'status' : 200 , 'ip' : get_client_ip(request)})
