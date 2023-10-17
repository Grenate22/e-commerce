from django_filters.rest_framework import FilterSet
import django_filters
from .models import Product



class ProductFilter(FilterSet):
    max = django_filters.NumberFilter(
        field_name='unit_price',lookup_expr='lt',label='max_price'
    )
    min = django_filters.NumberFilter(
        field_name='unit_price',lookup_expr='gt',label='min_price'
    )
    class Meta:
        model = Product
        fields = {
            'collection_id' : ['exact'],
        }
