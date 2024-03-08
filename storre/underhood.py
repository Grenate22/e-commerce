   #what happen underground of the filtering backend
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     collection_id = self.request.query_params.get('collection_id')
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)
    #     return queryset
    # def perform_create(self,request, *args, **kwargs):
    #     instance = self.get_object()
    #     notify_me.delay(instance.unit_price)
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)


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