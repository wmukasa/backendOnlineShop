from rest_framework import serializers
from  django.contrib.auth.models import User
from  rest_framework_simplejwt.tokens import RefreshToken 
from .models import Product,Order,OrderItem,ShippingAddress,Review

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model =User
        fields = ['id','_id','username','email','name','isAdmin'] 

    def get__id(self,obj):
        return obj.id

    def get_isAdmin(self,obj):
        return obj.is_staff

    def get_name(self,obj):
        name = obj.first_name
        if name =='':
            name = obj.email
        return name
class UserSerializerWithToken(UserSerializer):#we exact our UserSerializer
    # initializing serializer with token
    token = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model =User
        fields = ['id','_id','username','email','name','isAdmin','token'] 

    def get_token(self,obj):
        token = RefreshToken.for_user(obj)#it is the object of the actual user
        return str(token.access_token)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model =Review
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model =Product
        fields = '__all__'
    def get_reviews(self,obj):
        reviews = obj.review_set.all()
        serializer = ReviewSerializer(reviews,many=True)
        return serializer.data

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model =ShippingAddress
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model =OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    orderItems= serializers.SerializerMethodField(read_only=True)
    shippingAddress= serializers.SerializerMethodField(read_only=True)
    user= serializers.SerializerMethodField(read_only=True)
    class Meta:
        model =Order
        fields = '__all__'

    def get_orderItems(self, obj):
        items = obj.orderitem_set.all()#this is simple query set
        #now we want to serialize this data into json
        serializer = OrderItemSerializer(items,many=True)#we want multiple items many is set true
        return serializer.data

    def get_shippingAddress(self,obj):
        try:
            address = ShippingAddressSerializer(
                    obj.shippingaddress,many=False).data#this is a one to one relationship thats why we can doctype
            #many is set to false because we going to have one shipping address
        except:
            address = False
        return address
    
    def get_user(self,obj):
        user= obj.user
        serializer = UserSerializer(user,many=False)
        return serializer.data