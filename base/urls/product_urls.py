from django.urls import path
# from  .import views
from  base.views import product_views as views 
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView, 
# )

urlpatterns =[
    # path('',views.getRouters,name="routes"),

    path('',views.getProducts,name="products"),
    path('categoryBlouse/',views.getBlouseProducts,name="blouse-categorylist"),
    path('categoryThrowOn/',views.getThrowONProducts,name="throwons-categorylist"),
    
    path('listProducts/',views.getProductswithoutPage,name="product-withoutPageLimit"),
    path('categoryProducts/<category>/',views.getSelectedCategory,name="product-categorylist"),
  
    path('create/',views.createProduct,name="product-create"),
    path('upload/',views.uploadImage,name="image-upload"),

    path('<str:pk>/reviews/',views.creareProductReview,name="create-review"),
    path('top/',views.getTopProducts,name="top-products"),
    path('<str:pk>',views.getProduct,name="product"),

    path('update/<str:pk>/',views.updateProduct,name="product-update"),
    path('delete/<str:pk>/',views.deleteProduct,name="product-delete"),
]