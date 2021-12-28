from django.shortcuts import render

from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response

from base.models import Product,Order,OrderItem,ShippingAddress
from base.serializer import ProductSerializer,OrderSerializer

#this import will help us identify whether the user trying to register is not registered in our database
from rest_framework import status
from datetime import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user#getting the user using json token
    data = request.data
    orderItems =data['orderItems'] #we shall get this from frontend
    #we have to first check if we have order items, then we process
    if orderItems and len(orderItems) ==0:
        return Response({'detail':'No Order Items'},status=status.HTTP_400_BAD_REQUEST)#how we access this from frontend using the import Status
    else:
        #(1) create the order
        order = Order.objects.create(
            user =user,#we got the user from the above token
            paymentMethod = data['paymentMethod'], #this is set to data
            taxPrice = data['taxPrice'],
            shippingPrice = data['shippingPrice'],
            totalPrice =data['totalPrice'],
        )
        #(2) after creating the order, we create the shipping address
        shipping = ShippingAddress.objects.create(
            order =order,
            address = data['shippingAddress']['address'],
            city = data['shippingAddress']['city'],
            postalCode= data['shippingAddress']['postalCode'],
            country = data['shippingAddress']['country'],

        )
        #(3) create order  items and set order to orderItem relationship
                # we have to go through each items inside the list
        for i in orderItems:
        #first thing we have to do is to get product by its id
            product = Product.objects.get(_id=i['product'])

            #now we can create the actual item
            item = OrderItem.objects.create(
                product = product,
                order = order,
                name = product.name,
                qty = i['qty'],#that how we gone pass it in from frontend
                price =i['price'],
                image =product.image.url,

            )
            #(4) Update  stock in the product table in the database
            product.countInStock -= item.qty
            product.save # this is going to update the countInStock
        serializer =OrderSerializer(order,many=False)
        return Response(serializer.data)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user
    orders = user.order_set.all()#will get get orders associated to that user
    #orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

#this view is to get all the orders to be seen by admin 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request,pk):
    user = request.user

    order = Order.objects.get(_id=pk)
    try:
        #if all these fail, we need to return that the order doesn't exist
        if user.is_staff or order.user == user:
            serializer =OrderSerializer(order,many=False)
            return Response(serializer.data)
        else:
            Response({'detail':'Not authorized to view this order'},
                        status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'detail':'Order does not exist'},
                        status=status.HTTP_400_BAD_REQUEST)
#this to be finished when we we get our final method of payment 
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request,pk):
    order = Order.objects.get(_id=pk)

    order.isPaid = True
    order.paidAt = datetime.now() 
    order.save()

    return Response('Order was paid')

#endpoint to update my delivered orders
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, pk):
    order = Order.objects.get(_id=pk)

    order.isDelivered = True
    order.deliveredAt = datetime.now()
    order.save()

    return Response('Order was delivered')

