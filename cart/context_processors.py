from .cart import Cart

#create context processor

def cart(request):
    return  {'cart' : Cart(request)}