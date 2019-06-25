#from django.http import JsonResponse
#from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render_to_response
from wxpy import *

def test_api(request):
    # bot = Bot(cache_path=True,console_qr=True, qr_callback=get_qr)
    return render_to_response('hello.html')

def search(request):
     bot = Bot(cache_path=True, qr_callback=get_qr)
     embed()


def get_qr(uuid,status,qrcode):
    address = "./abc.png"
    with open(address, "wb") as f:
        f.write(qrcode)

    # context = {}
    # context['hello'] = "hello world!"
    # return render(request, 'hello.html', context)
