from base.models import Product, Category, ProductImages, Brand



def default(request):
    categories = Category.objects.all()
    return{
        
    }