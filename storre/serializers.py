from decimal import Decimal
from django.db import transaction
from rest_framework import serializers 
from .models import Product,Collection,Review, Cart, CartItem, Customer, Order,OrderItem,ProductImage
from .signals import order_created

class CollectionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id','title','products_count']

    products_count = serializers.IntegerField(read_only=True)

        
class ProductImageSerializers(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = ProductImage
        fields = ['id','image']

class ProductSerializers(serializers.ModelSerializer):
    images = ProductImageSerializers(many=True, read_only=True)
    image_url = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),write_only=True)
    class Meta:
        model = Product
        fields = ['id','title','slug','description','price','price_with_tax','inventory','collection','images',"image_url"]

   # if i want the collection to have an hyperlink 
    # collection = serializers.HyperlinkedRelatedField(
    #     queryset = Collection.objects.all(),
    #     view_name= 'collection-detail'
    # )
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')

    def calculate_tax(self,product:Product):
        return product.unit_price * Decimal(1.1)
    
    def create(self, validated_data):
        print(validated_data)
        image = validated_data.pop("image_url",[])
        product = Product(**validated_data)
        product.slug = product.title
        product.save()
        for image in image:
            ProductImage.objects.create(product=product, image=image)
        return product
    
class ReviewSerializers(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id','name','description','date','product']


class SimpleProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','unit_price']

#by default methodfield is readonly
class CartItemSerializers(serializers.ModelSerializer):
    product = SimpleProductSerializers()
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_price']

#once you use the methodfield you have to add the get_ follow by the name of the field 
    def get_total_price(self,obj):
        return obj.quantity * obj.product.unit_price
    
class AddCartItemSerializers(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
   
    def validate_product_id(self,value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given id found')
        return value
    
    def validate(self, data):
        cart_id = self.context['cart_id']
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart with the given cart_id found')
        return data

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id,product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        
        return self.instance

    class Meta:
        model = CartItem
        fields = ['id','product_id','quantity']

class UpdateCartItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
    

class CartSerializers(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializers(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id','items','total_price']
    
    def get_total_price(self, cart):
        return sum([item.quantity *item.product.unit_price for item in cart.items.all()])
        

class CustomerSerializers(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id','user_id','phone','birth_date','membership']



class OrderItemSerializers(serializers.ModelSerializer):
    product = SimpleProductSerializers()
    class Meta:
        model = OrderItem
        fields = ['id','product','quantity','unit_price']


class OrderSerializers(serializers.ModelSerializer):
    items = OrderItemSerializers(many=True)
    class Meta:
        model = Order
        fields = ['id','items','placed_at','payment_status','customer']

class UpdateOrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

class CreateOrderSerializers(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self,value):
        if not Cart.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No cart with the given id found')
        if CartItem.objects.filter(cart_id=value).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return value

 

    def save(self, **kwargs):
        #with transaction library any block of code inside the transaction will have to execute all changes before it save it
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']

            user_id =self.context['user_id']
            customer_id= Customer.objects.get(user_id=user_id)
            order = Order.objects.create(customer=customer_id)

            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                order = order, product = item.product, 
                unit_price = item.product.unit_price ,
                quantity = item.quantity, 
            ) for item in cart_items
            ]

            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(self.__class__, order=order)

            return order




   
