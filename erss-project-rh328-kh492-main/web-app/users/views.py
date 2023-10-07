from django.shortcuts import render,redirect, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django import forms
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from django.contrib.auth import login, authenticate, logout
from .funcs import *

import socket
import time

import sys
sys.path.append('..')
import front_end_pb2 as front
from helper import *
from handler import *
# server_module = importlib.import_module('.server', package='..')
import pytz
curr_time = datetime.now()
curr_time = pytz.utc.localize(curr_time)

print("---Try to connect to backend---")
FRONT_SOCKET = None

while True:
    try:
        print("try1")
        FRONT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("try2")
        FRONT_SOCKET.connect(("KaijianuangsMBP.lan", 45678))
        print("connect to backend successfully")
        break
    except:
        time.sleep(0.5)
        continue
        
#user side view
def intro(request):
    return render(request, 'users/intro.html')

# def login(request):
#     if request.method == 'POST':
#         form = 


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            useraccount = UserAccount(user = user)
            useraccount.save()
            messages.success(request, f'Your account has been created! You are now able to login!')
            return redirect('login')
        else:
            form = UserRegistrationForm()
            return render(request, 'users/user_register.html',{'form':form})
    else:
        form = UserRegistrationForm()
        return render(request, 'users/user_register.html',{'form':form})

@login_required
def profile(request):
    user = request.user
    content = {}
    content["username"] = user.username
    content["email"] = user.email
    userAccount = user.useraccount
    content["useraccount"] = userAccount
    ups_id = userAccount.ups_userid
    flag = (userAccount.phone == 0 and userAccount.cardInfo == 0 and userAccount.ups_userid == -1) or ups_id == -1
    content["ups_id"] = userAccount.ups_userid
    if ups_id == -2:
        content["ups_id"] == "Pending verification"
    content["useraccount_initialized"] = None if flag else True
    content["addresses"] = userAccount.addresses.all()
    return render(request,'users/profile.html',content)

@login_required
def EditAsUser(request):
    if request.method == 'GET':
        form = UserEditForm()
        return render(request, 'users/EditAsUser.html', {'form':form})
    else:
        form = UserEditForm(request.POST)
        if form.is_valid():
            request.user.email = form.cleaned_data['email']
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()
            messages.success(request, f'Successfully updated!')
            return redirect('profile')
        else:
            form = UserEditForm()
            return render(request, 'users/EditAsUser.html',{'form':form})

@login_required
def EditOptional(request):
    curr_user = request.user
    if request.method =='POST':
        form = EditOptionalForm(request.POST)
        if form.is_valid():
            curr_user.useraccount.phone = form.cleaned_data['phone']
            curr_user.useraccount.cardInfo = form.cleaned_data['cardInfo']
            curr_user.useraccount.ups_userid = form.cleaned_data['ups_account_id']
            curr_user.useraccount.save()
            messages.success(request, f'Your optional Info has been updated!\nYour ups username is sent to ups for verification!')
            return redirect('profile')
        else:
            form = EditOptionalForm()
            return render(request, 'users/EditOptional.html',{'form':form})
    else:
        form = EditOptionalForm()
        return render(request, 'users/EditOptional.html',{'form':form})
    
@login_required
def EditAddress(request):
    return render(request, 'users/EditAddress.html')

def home(request):
    return render(request, 'users/home.html')

@login_required
def AddAddress(request):
    curr_user_account = request.user.useraccount
    if request.method =='POST':
        form = AddAddressForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['addressName']
            tag = form.cleaned_data['tag']
            if(tag=='my own tag'):
                tag = form.cleaned_data['myTag']
            address_x = form.cleaned_data['address_x']
            address_y = form.cleaned_data['address_y']
            address = Address(owner=curr_user_account,addressName=name,tag=tag,address_x=address_x,address_y=address_y)
            address.save()
            messages.success(request, f'Your optional Info has been updated!')
            return redirect('profile')
        else:
            form = AddAddressForm()
            return render(request, 'users/AddAddress.html',{'form':form})
    else:
        form = AddAddressForm()
        return render(request, 'users/AddAddress.html',{'form':form})

#amazon side view
class htmlProduct:
    def __init__(self, ID, description, category, price):
        self.id = ID
        self.description = description
        self.category = category
        self.price = price

def products(request):
    context = {}
    context['category'] = 'all'
    all_products = Product.objects.all()
    htmlProducts = []
    for product in all_products:
        cat = Category.objects.filter(id = product.category_id).first().category
        htmlProducts.append(htmlProduct(product.id, product.description, cat,product.price))
    context['products'] = htmlProducts
    context['categories'] = Category.objects.all()
    return render(request, 'users/products.html',context)

def productsByCategory(request, category_id):
    context = {}
    if category_id == -1:
        context["category"] = "all"
        all_products = Product.objects.all()
    else:
        cat = Category.objects.filter(id = category_id).first()
        context["category"] = cat.category
        #get products that has a foreign key of cat
        all_products = cat.products.all()
    htmlProducts = []
    for product in all_products:
        cat = Category.objects.filter(id = product.category_id).first().category
        htmlProducts.append(htmlProduct(product.id,product.description,cat,product.price))
    context["products"]=htmlProducts
    context["categories"] = Category.objects.all()
    return render(request,'users/products.html',context)

#Order and Package Part:
#TODO: show all orders, the address should be changed too
#if backend change the database

class OrderAndPack:
    def __init__(self, order, pack, product, track_num):
        self.order = order
        self.package = pack
        self.product = product
        self.track_num = track_num    

@login_required
def allOrdersAndPackages(request):
    context = {}
    user = request.user
    orders = Order.objects.filter(customer=user).order_by('-generate_time')
    combines = []
    for order in orders:
        pack = order.package
        product = order.product
        if pack.track_num==-1:
            track_num = "not generated yet"
        else:
            track_num = pack.track_num
        combines.append(OrderAndPack(order,pack,product,track_num))
    context["OrdersAndPacks"] = combines
    return render(request,'users/AllOrders.html',context)

@login_required
def before_checkout(request, product_id):
    user = request.user
    # if user.useraccount.ups_userid==-2:
    #     messages.warning(request, f"The ups is verifying your information!")
    #     return redirect('profile')
    # if user.useraccount.ups_userid==-1:
    #     messages.warning(request, f"You have to fill in the optional info to purchase!")
    #     return redirect('profile')
    context = {}
    userAccount = user.useraccount
    addresses = userAccount.addresses.all()
    # user=User.objects.get(user = user)

    if request.method =='POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            address_x = form.cleaned_data["address_x"]
            address_y = form.cleaned_data["address_y"]
            product_num = form.cleaned_data["productNum"]
            ups_id = form.cleaned_data["ups_id"]
            whID = get_closest_wh(address_x, address_y)
            wh = Warehouse.objects.filter(id=whID).first()
            product = Product.objects.filter(id = product_id).first()
            if not ups_id:
                package = Package(customer = user,warehouse = wh, address_x = address_x, 
                    address_y = address_y)
                package.save()
                order = Order(customer = user,product = product,package = package, product_num=product_num)
                order.save()
            else:
                package = Package(customer = user,warehouse = wh, address_x = address_x, 
                    address_y = address_y, ups_id = ups_id)
                package.save()
                order = Order(customer = user,product = product,package = package, product_num=product_num)
                order.save()
            #TODO: backend should process every package with status: processing
            # result = notify_backend(package.id)
            # if result:

            packageid = package.id
            command = front.FCommands()
            command.buy.packageid = packageid
            
            sendMsg(command, FRONT_SOCKET)

            # recvMsg(front.BResponses, FRONT_SOCKET)
            # if not response.isValid:
            #     package.delete()
            #     order.delete()
            #     messages.error(request, f'You fail to place the order due to invalid UPS_id!')
            # else:
            subject = "Your order has been placed!"
            content = f'You have ordered {product_num} {product.description}\n'
            content += f'Delivering to {wh}\n'
            content += "Best,\nMini Amazon Team\n"
            from_email = settings.EMAIL_HOST_USER
            email_list = [user.email]
            send_mail(subject,content,from_email,email_list,fail_silently=True)
            messages.success(request,f'You have successfully put the order!')
            return redirect('products')
            # else:
            #     package.delete()
            #     order.delete()
            #     messages.warning(request,f'Something failed! Please try again!')
            #     return redirect('products')
        else:
            form = PurchaseForm()
            return render(request,'users/BeforeCheckOut.html',{'form':form,'product_id':product_id, 'addresses': addresses})
    else:
        form = PurchaseForm()
        return render(request,'users/BeforeCheckOut.html',{'form':form,'product_id':product_id, 'addresses':addresses})
class Carts:
    def __init__(self, id, product, product_num, x, y):
        self.cart_id = id
        self.product = product
        self.product_num = product_num
        self.address_x = x
        self.address_y = y

@login_required
def allCarts(request):
    context = {}
    user = request.user
    carts = ShoppingCart.objects.filter(customer=user)
    combines = []
    for item in carts:
        cart_id = item.id
        prod = item.product
        address_x = item.address_x
        address_y = item.address_y
        num = item.product_num
        combines.append(Carts(cart_id, prod,num,address_x,address_y))
    context["Carts"] = combines
    return render(request,'users/AllShoppingCart.html',context)

@login_required
def addShoppingCart(request, product_id):
    user = request.user
    # if user.useraccount.ups_userid==-2:
    #     messages.warning(request, f"The ups is verifying your information!")
    #     return redirect('profile')
    # if user.useraccount.ups_userid==-1:
    #     messages.warning(request, f"You have to fill in the optional info to purchase!")
    #     return redirect('profile')
    if request.method =='POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            address_x = form.cleaned_data["address_x"]
            address_y = form.cleaned_data["address_y"]
            product_num = form.cleaned_data["productNum"]
            ups_id = form.cleaned_data['ups_id']
            whID = get_closest_wh(address_x, address_y)
            wh = Warehouse.objects.filter(id=whID).first()

            product = Product.objects.filter(id = product_id).first()
            if not ups_id:
                shoppingcart = ShoppingCart(customer = user, product = product, warehouse = wh, address_x = address_x,
                    address_y = address_y, product_num = product_num)
                shoppingcart.save()
            else:
                shoppingcart = ShoppingCart(customer = user, product = product, warehouse = wh, address_x = address_x,
                    address_y = address_y, product_num = product_num, ups_id = ups_id)
                shoppingcart.save()
            #TODO: backend should process every package with status: processing
            # result = notify_backend(package.id)
            # if result:
            messages.success(request,f'You have successfully added the item to your cart!')
            return redirect('allCarts')
            # else:
            #     package.delete()
            #     order.delete()
            #     messages.warning(request,f'Something failed! Please try again!')
            #     return redirect('products')
        else:
            form = PurchaseForm()
            messages.error(request,f'Fail to add the item to your cart!')
            return render(request,'users/BeforAddingToCart.html',{'form':form,'product_id':product_id})
    else:
        form = PurchaseForm()
        return render(request,'users/BeforAddingToCart.html',{'form':form,'product_id':product_id})
    


@login_required
def buyShoppingCart(request):
    user = request.user
    if request.method =='POST':
        allShoppingCart = ShoppingCart.objects.filter(customer = user)
        subject = "Your order has been placed!"
        content = ""
        for item in allShoppingCart:
            wh = item.warehouse
            product = item.product
            product_num = item.product_num
            address_x = item.address_x
            address_y = item.address_y
            ups_id = item.ups_id
            package = Package(customer = user,warehouse = wh, address_x = address_x, 
            address_y = address_y, ups_id = ups_id)
            package.save()
            order = Order(customer = user,product = product,package = package, product_num=product_num)
            order.save()
            item.delete()
            packageid = package.id

            command = front.FCommands()
            command.buy.packageid = packageid
            
            sendMsg(command, FRONT_SOCKET)

            # response = recvMsg(front.BResponses, FRONT_SOCKET)
            # if not response.isValid:
            #     package.delete()
            #     order.delete()
            #     messages.error(request,f'You fail to place order {product_num} {product.description} due to invalid UPS_id!')
            # else:
            content += f'You have ordered {product_num} {product.description}\n'
            content += f'Delivering to {wh}\n'

        content += "Best,\nMini Amazon Team\n"
        from_email = settings.EMAIL_HOST_USER
        email_list = [user.email]
        send_mail(subject,content,from_email,email_list,fail_silently=True)
        messages.success(request,f'You have successfully put the order!')
        return redirect('products')

    else:
        form = PurchaseForm()
        return render(request,'users/BeforeCheckOut.html')

@login_required
def cancelCart(request, product_id):
    user = request.user
    curitem = ShoppingCart.objects.filter(id = product_id).first()
    curitem.delete()
    messages.success(request,f'You have successfully delete the item!')
    return redirect('allCarts')

def report_issue_request(request, package_id):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['email']:
                email = form.cleaned_data['email']
            if form.cleaned_data['content']:
                content=(form.cleaned_data['content'])
            
            subject = "[Mini-Amazon] Your problem has been reported!"
            body= "Dear Customer,\n\nYour problem related to package which package_id is "  + str(package_id)+" has been successfully reported. Thank you for reaching out to us. We will get back to you as soon as possible.\n\nBest regards,\nThe Mini-Amazon Team"
            sender = "hkj277501781@outlook.com"
            receiver = []
            receiver.append(email)
            new, created=Report.objects.get_or_create(id=package_id,content=content,email=email)
            send_mail(
                    subject,
                    body,
                    sender,
                    receiver,
                    fail_silently=False
                    )   
            messages.success(request, 'Your message have been uploaded.')
        else:
            messages.error(request, 'Please check your format.')
    form = ReportForm()
    return render(request, 'users/report_issue.html', locals())

def associateUps(request, package_id):
    if request.method == 'POST':
        form = AccociateForm(request.POST)
        if form.is_valid():
            ups_id = -1
            if form.cleaned_data['ups_id']:
                ups_id = form.cleaned_data['ups_id']
                command = front.FCommands()
                command.associate.userid = ups_id
                command.associate.packageid = package_id
                
                sendMsg(command, FRONT_SOCKET)
                
                # if response.isValid:
                curPackage = Package.objects.get(id = package_id)
                curPackage.ups_id = ups_id
                curPackage.save()
                messages.success(request, 'Your message have been uploaded.')
                # else:
                #     messages.error(request, 'Your ups_id does not exist')
            else:
                messages.error(request, 'Your do not enter your ups_id')
        else:
            messages.error(request, 'Please check your format.')
    form = AccociateForm()
    return render(request, 'users/AssociateUps.html', {'form':form,'package_id':package_id})
