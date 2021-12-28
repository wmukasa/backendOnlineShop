from django.shortcuts import render

from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from base.models import Product,Review
from base.serializer import ProductSerializer

#thsi import will help us identify whether the user trying to register is not register in our database
from rest_framework import status

# @api_view(['GET'])
# def getRouters(request):
#     routes=[
#         '/api/products/',
#         '/api/products/create',
#     ]
#     return Response(routes)

@api_view(['GET'])
def getProducts(request):
    query = request.query_params.get('keyword')
    if query == None:
        query = ''

    products = Product.objects.filter(
        name__icontains=query).order_by('-createdAt')

    page = request.query_params.get('page')
    paginator = Paginator(products, 4)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    if page == None:
        page = 1

    page = int(page)
    print('Page:', page)
    serializer = ProductSerializer(products, many=True)
    return Response({'products': serializer.data, 'page': page, 'pages': paginator.num_pages})

@api_view(['GET'])
def getTopProducts(requests):
    #- means the highest rated and [0:5],0 to 5 items, we only get few
    products = Product.objects.filter(rating__gte=4).order_by('-rating')[0:5]
    serializer = ProductSerializer(products, many=True)
    return  Response(serializer.data)


@api_view(['GET'])
def getProduct(request,pk):
    # for i in products:
    #     if i['_id'] == pk:
    #         product = i
    #         break
    product = Product.objects.get(_id=pk)
    serializer = ProductSerializer(product,many=False)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def createProduct(request):
    user = request.user
    product = Product.objects.create(
         user = user,
         name ='Sample Name',
         price = 0,
         brand = 'Sample brand',
         countInStock =0,
         category='Sample category',
         description =''
    )
    serializer = ProductSerializer(product,many=False)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateProduct(request,pk):
    #we have to get form data
    data = request.data
    product = Product.objects.get(_id=pk)
    product.name = data['name']
    product.price = data['price']
    product.brand = data['brand']
    product.countInStock = data['countInStock']
    product.category = data['category']
    product.description = data['description']
    product.save()
    serializer = ProductSerializer(product,many=False)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteProduct(request,pk):
    product = Product.objects.get(_id=pk)
    product.delete()
    return Response('Product deleted')

@api_view(['POST'])
def uploadImage(request):
    data = request.data
    product_id = data['product_id']
    product = Product.objects.get(_id=product_id)
    product.image = request.FILES.get('image')
    product.save()

    return Response('Image was uploaded')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def creareProductReview(request,pk):#pk the product id to be reviewed
    user = request.user
    product=Product.objects.get(_id=pk)
    data = request.data

    #1 -Review already  exists
    alreadyExists = product.review_set.filter(user =user).exists()
    if alreadyExists:
        content  ={'detail':'Product already reviewed'}
        return Response(content,status=status.HTTP_400_BAD_REQUEST)
    #2 -No Rating  or 0
    elif data['rating'] ==0:
        content  ={'detail':'Please select a rating'}
        return Response(content,status=status.HTTP_400_BAD_REQUEST)
    #2 -Create review 
    else:
        review = Review.objects.create(
            user = user,
            product = product,
            name = user.first_name,
            rating =data['rating'],
            comment = data['comment'],

        )
        reviews = product.review_set.all()
        product.numReviews = len(reviews)
        #rating is calculated by get all the reviews and then diving it by the number of the reviews
        total = 0 # we start with zero then calculate all the reviews calculated
        for i in reviews:
            total +=i.rating
        product.rating = total/len(reviews)
        product.save()

        return Response('Review Added')
