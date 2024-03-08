from django.shortcuts import render,get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from drf_spectacular.utils import extend_schema,OpenApiResponse,OpenApiExample
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view,action
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.parsers import MultiPartParser,FileUploadParser
from .models import Product, Collection,OrderItem, Review, Cart, CartItem,Customer,Order,ProductImage
from .serializers import ProductSerializers, CollectionSerializers, ReviewSerializers, CartSerializers,CartItemSerializers,AddCartItemSerializers,UpdateCartItemSerializers,CustomerSerializers,OrderSerializers,CreateOrderSerializers,UpdateOrderSerializers,ProductImageSerializers
from .filters import ProductFilter
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly
from .customresponse import JsonResponse
from .task import notify_me


class CollectionViewset(ModelViewSet):
    http_method_names = ['get','post','patch','delete','head','otpions']
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializers
    permission_classes = [IsAdminOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return JsonResponse(data=serializer.data,status="Success",statuscode=status.HTTP_201_CREATED,msg="Collection created",
                            headers=headers)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(data=serializer.data,status="Success",statuscode=status.HTTP_200_OK,msg="Collection list")
    
    @extend_schema(
        summary="Retrieve an instance of collection", 
        responses={
            200: OpenApiResponse(response=CollectionSerializers,
                                 description='Retrieved. Retrieve an instance of collection'),
            404: OpenApiResponse(response=CollectionSerializers, description='Not Found (Collection not found)'),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return JsonResponse(data=serializer.data,status="Success", statuscode=status.HTTP_200_OK,msg="Collection Retrieved")
        except Http404:
            return JsonResponse(msg="Collection not found",status="Fail",statuscode=status.HTTP_404_NOT_FOUND)


    def delete(self, request,pk):
        collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')).all(),pk=pk)
        if collection.products.count() > 0:
            return Response({'error':'collection cannot be deleted'})
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductViewset(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializers
    parser_classes = [MultiPartParser,FileUploadParser]
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    lookup_field = "slug"
    # permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title','description']
    ordering_fields = ['unit_price','last_update']

    @extend_schema(
        summary="Retrieve an instance of Product", 
        responses={
            200: OpenApiResponse(response=ProductSerializers,
                                 description='Retrieved. Retrieve an instance of Product'),
            404: OpenApiResponse(response=ProductSerializers, description='Not Found (Product not found)'),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return JsonResponse(data=serializer.data,status="Success", statuscode=status.HTTP_200_OK,msg="Product Retrieved")
        except Http404:
            return JsonResponse(msg="Product not found",status="Fail",statuscode=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error':'product cannot be deleted'})
        return super().destroy(request, *args, **kwargs)


class ReviewViewset(ModelViewSet):
    http_method_names = ['get','post','patch','delete','head','otpions']
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
    
# class CustomerViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,GenericViewSet):
#     queryset = Customer.objects.all()
#     serializer_class = CustomerSerializers
#     permission_classes = [IsAuthenticated]
    
#     @action(detail=False, methods=['GET','PUT'])
#     def me(self, request):
#         customer = Customer.objects.get(user_id=request.user.id)
#         if request.method == 'GET':
#             serializer = CustomerSerializers(customer)
#             return Response(serializer.data)
#         elif request.method == 'PUT':
#             serializer = CustomerSerializers(customer, data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data)
        
class OrderViewSet(ModelViewSet):
    http_method_names = ['get','post','patch','head','otpions']

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
    
