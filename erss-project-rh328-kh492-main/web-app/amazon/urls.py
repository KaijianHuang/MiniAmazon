"""rideweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from users import views as users_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # users side view
    path('login', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('intro/', users_views.intro, name = 'intro'),
    path('register/',users_views.register, name='register'),
    path('logout/',auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', users_views.profile, name='profile'),
    path('editasuser/', users_views.EditAsUser, name='editasuser'),
    path('editaddress/', users_views.EditAddress, name='editaddress'),
    path('editoptional/', users_views.EditOptional, name='editoptional'),
    path('addaddress/', users_views.AddAddress, name='addaddress'),
    path('products/', users_views.products, name='products'),
    path('', users_views.home, name = 'home'),
    path('before_checkout/<int:product_id>/',users_views.before_checkout, name = 'beforecheckout'),
    path('category/<int:category_id>/',users_views.productsByCategory, name='categoryView'),
    path('orders/',users_views.allOrdersAndPackages, name = 'orders'),
    path('beforeaddingtocart/<int:product_id>/', users_views.addShoppingCart, name='addShoppingCart'),
    path('allCart/', users_views.allCarts, name = 'allCarts'),
    path('buyShoppingCart/', users_views.buyShoppingCart, name = 'buyShoppingCart'),
    path('cancelCart/<int:product_id>', users_views.cancelCart, name = 'cancelCart'),
    path('report_issue_request/<int:package_id>', users_views.report_issue_request, name = 'report_issue_request'),
    path('associateUps/<int:package_id>', users_views.associateUps, name = 'associateUps'),
]
