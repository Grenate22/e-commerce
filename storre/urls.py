from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('collections',views.CollectionViewset)
router.register('products',views.ProductViewset, basename='products')
router.register('carts',views.CartViewSet)
router.register('orders',views.OrderViewSet, basename='orders')

product_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
product_router.register('reviews', views.ReviewViewset, basename='product-review')
cart_router = routers.NestedDefaultRouter(router,'carts',lookup='cart')
cart_router.register('items',views.CartItemViewSet, basename='cart-items')



urlpatterns = router.urls + product_router.urls + cart_router.urls

