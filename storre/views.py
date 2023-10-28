from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view,action
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Collection,OrderItem, Review, Cart, CartItem,Customer,Order,ProductImage
from .serializers import ProductSerializers, CollectionSerializers, ReviewSerializers, CartSerializers,CartItemSerializers,AddCartItemSerializers,UpdateCartItemSerializers,CustomerSerializers,OrderSerializers,CreateOrderSerializers,UpdateOrderSerializers,ProductImageSerializers
from .filters import ProductFilter
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly
from .task import notify_me


class ProductViewset(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializers
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title','description']
    ordering_fields = ['unit_price','last_update']


   #what happen underground of the filtering backend
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     collection_id = self.request.query_params.get('collection_id')
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)
    #     return queryset
    def perform_create(self,request, *args, **kwargs):
        instance = self.get_object()
        notify_me.delay(instance.unit_price)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error':'product cannot be deleted'})
        return super().destroy(request, *args, **kwargs)

   
# views for product using fbv here.
# @api_view(['GET','POST'])
# def product_list(request):
#     if request.method == "GET":
#         queryset = Product.objects.all()
#         serializer = ProductSerializers(queryset, many=True, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'POST':
#         serializer = ProductSerializers(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# @api_view(['GET','PUT','DELETE'])
# def product_details(request,id):
#     product = get_object_or_404(Product,pk=id)
#     if request.method == 'GET':
#         serializer = ProductSerializers(product,context={'request': request})
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = ProductSerializers(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionViewset(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializers
    permission_classes = [IsAdminOrReadOnly]
    
    def delete(self, request,pk):
        collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')).all(),pk=pk)
        if collection.products.count() > 0:
            return Response({'error':'collection cannot be deleted'})
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



#cbv for collection 
# class CollectionList(ListCreateAPIView):
#     queryset = Collection.objects.annotate(products_count=Count('products')).all()
#     serializer_class = CollectionSerializers

# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Collection.objects.annotate(products_count=Count('products')).all()
#     serializer_class = CollectionSerializers

#     def delete(self, request,pk):
#         collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')).all(),pk=pk)
#         if collection.products.count() > 0:
#             return Response({'error':'collection cannot be deleted'})
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


#my code for fbv for get of object ,put and delete
# @api_view(['GET','PUT','DELETE'])
# def collection_details(request,pk):

#     collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')).all(),pk=pk)
#     if request.method == 'GET':
#         serializer = CollectionSerializers(collection)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = CollectionSerializers(data=request.data)
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         if collection.products.count() > 0:
#             return Response({'error':'collection cannot be deleted'})
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewset(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializers

#why we use this mixin and not the normal genericviewset we have anonymous user be able to create cart but we dont have listmixin cuz we dont want to list all cart in the database to anyuser
#we then have retrievemixin because each id will be unique so there wont be mixup of cart item for each user
class CartViewSet(CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializers

class CartItemViewSet(ModelViewSet):
    # when specifying the http_method_names it should be in a lower case
    http_method_names = ['get','post','patch','delete']
   
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializers
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializers
        return CartItemSerializers
    
    def get_serializer_context(self):
        cart_id = self.kwargs['cart_pk']
        if not Cart.objects.filter(pk=cart_id).exists():
            return Response('No cart_id found' )
        return {'cart_id': self.kwargs['cart_pk']}
    

    def get_queryset(self):
        return CartItem.objects.select_related('cart','product').filter(cart_id=self.kwargs['cart_pk'])
    
class CustomerViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,GenericViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializers
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['GET','PUT'])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializers(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializers(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        
class OrderViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','delete','head','otpions']

    def get_permissions(self):
        if self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
            serializer = CreateOrderSerializers(data=request.data, context= {'user_id': self.request.user.id})
            serializer.is_valid(raise_exception=True)
            order = serializer.save()
            serializer = OrderSerializers(order)
            return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializers
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializers
        return OrderSerializers


    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.prefetch_related('items__product').all()
        customer_id =Customer.objects.only('id').get(user_id=user.id)
        return Order.objects.prefetch_related('items__product').filter(customer_id=customer_id)
    
class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializers
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])
    
    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}
    