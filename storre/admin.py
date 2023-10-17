from typing import Any
from django.contrib import admin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.html import format_html, urlencode
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            ('<10','Low')
        ]
    
    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']

    def thumbnail(self,instance):
        if instance.image.name != '':
            return format_html (f'<img src="{instance.image.url}" class="thumbnail" />')
        return ''

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ['clear_inventory']
    inlines = [ProductImageInline]
    list_display = ['title', 'unit_price','inventory_status','collection_title']
    list_per_page = 10
    list_editable = ['unit_price']
    list_filter = ['collection','last_update',InventoryFilter]
    list_select_related = ['collection']


    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self,product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'
    
    @admin.action(description='clear inventory')
    def clear_inventory(self,request,queryet):
        updated_count = queryet.update(inventory=0)
        self.message_user(
            request, 
            f'{updated_count} products were successfully updated.'
            
        )

    class Media:
        css = {
            'all': ['storre/styles.css']
        }

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_select_related = ['user']
    list_display = ['first_name','last_name','membership']
    list_editable = ['membership']
    list_per_page = 10
    ordering = ['user__first_name','user__last_name']
    search_fields = ['first_name', 'last_name']

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','placed_at','customer']
    

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','product_count']

    @admin.display(ordering='products_count')
    def product_count(self,collection):
        url = reverse ('admin:storre_product_changelist') + '?' + urlencode({'collection__id':( collection.id)})
        return format_html('<a href="{}">{}</a>', url, collection.products_count )
        
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:

        return super().get_queryset(request).annotate(products_count=Count('products'))
