from order.forms import OrderForm, ShopCartForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.utils.crypto import get_random_string

from order.models import ShopCart, Order, OrderProduct
from product.models import Category, Images, Product, Variants
from user.models import UserProfile


def index(request):
    return HttpResponse("Order Page")


@login_required(login_url='/login')  # Check login
def addtoshopcart(request, id):
    url = request.META.get('HTTP_REFERER')  # get last url
    current_user = request.user  # Access User Session information
    if current_user.is_staff is True:
        return HttpResponse('You can not do this action.')
    product = Product.objects.get(pk=id)
    if product.amount == 0:
        messages.success(request, "Product Out of Stock! Sorry!")
        return HttpResponseRedirect(url)
    variantid = None
    if product.variant != "None":
        variantid = request.POST.get('variantid')  # from variant add to cart
        checkinvariant = ShopCart.objects.filter(
            variant_id=variantid, user_id=current_user.id)  # Check product in shopcart
        if checkinvariant:
            control = 1  # The product is in the cart
        else:
            control = 0  # The product is not in the cart"""
    else:
        checkinproduct = ShopCart.objects.filter(
            product_id=id, user_id=current_user.id)  # Check product in shopcart
        if checkinproduct:
            control = 1  # The product is in the cart
        else:
            control = 0  # The product is not in the cart"""

    if request.method == 'POST':  # if there is a post
        form = ShopCartForm(request.POST)
        if form.is_valid():
            if control == 1:  # Update  shopcart
                if product.variant == 'None':
                    data = ShopCart.objects.get(
                        product_id=id, user_id=current_user.id)
                else:
                    data = ShopCart.objects.get(
                        product_id=id, variant_id=variantid, user_id=current_user.id)
                data.quantity += form.cleaned_data['quantity']
                data.save()  # save data
            else:  # Inser to Shopcart
                data = ShopCart()
                data.user_id = current_user.id
                data.product_id = id
                if variantid is not None:
                    data.variant_id = variantid
                data.quantity = form.cleaned_data['quantity']
                data.save()
        messages.success(request, "Product added to Shopcart ")
        return HttpResponseRedirect(url)

    else:  # if there is no post
        if control == 1:  # Update  shopcart
            data = ShopCart.objects.get(
                product__id=id, user_id=current_user.id)
            data.quantity += 1
            data.save()
        else:  # Inser to Shopcart
            data = ShopCart()  # model ile bağlantı kur
            data.user_id = current_user.id
            data.product_id = id
            data.quantity = 1
            data.variant_id = None
            data.save()  #
        messages.success(request, "Product added to Shopcart")
        return HttpResponseRedirect(url)


def shopcart(request):
    categories = Category.objects.all()
    current_user = request.user  # Access User Session information
    if current_user.is_staff is True:
        return HttpResponse('You are not authorized to view this page.')
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    for rs in shopcart:
        if rs.variant is None:
            product = Product.objects.get(pk=rs.product.id)
            if rs.quantity > product.amount:
                rs.quantity = product.amount
            try:
                if rs.product.promotion:
                    rs.product.price = round(rs.product.pricepromotion(),2)
                    rs.amount = rs.product.price * rs.quantity
                    total += rs.amount
            except:
                total += rs.product.price * rs.quantity
        else:
            variant = Variants.objects.get(pk=rs.variant.id)
            if rs.quantity > variant.quantity:
                rs.quantity = variant.quantity
            try:
                if rs.product.promotion:
                    rs.variant.price = round(rs.variant.price * (100 - rs.product.promotion.percent) / 100, 2)
                    rs.varamount = rs.variant.price * rs.quantity
                    total += rs.varamount
            except:
                total += rs.variant.price * rs.quantity
        rs.save()

    context = {'shopcart': shopcart,
               'categories': categories,
               'total': total,
               }
    return render(request, 'order/shopcart_products.html', context)


@login_required(login_url='/login')  # Check login
def deletefromcart(request, id):
    ShopCart.objects.filter(id=id).delete()
    messages.success(request, "Your item deleted form Shopcart.")
    return HttpResponseRedirect("/shopcart")


@login_required(login_url='/login')
def orderproduct(request):
    category = Category.objects.all()
    current_user = request.user
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    for rs in shopcart:
        if rs.variant is None:
            product = Product.objects.get(pk=rs.product.id)
            if rs.quantity > product.amount:
                rs.quantity = product.amount
            try:
                if rs.product.promotion:
                    rs.product.price = round(rs.product.pricepromotion(), 2)
                    rs.amount = rs.product.price * rs.quantity
                    total += rs.amount
            except:
                total += rs.product.price * rs.quantity
        else:
            variant = Variants.objects.get(pk=rs.variant.id)
            if rs.quantity > variant.quantity:
                rs.quantity = variant.quantity
            try:
                if rs.product.promotion:
                    rs.variant.price = round(rs.variant.price * (100 - rs.product.promotion.percent) / 100, 2)
                    rs.varamount = rs.variant.price * rs.quantity
                    total += rs.varamount
            except:
                total += rs.variant.price * rs.quantity
        rs.save()

    if request.method == 'POST':  # if there is a post
        form = OrderForm(request.POST)
        # return HttpResponse(request.POST.items())
        if form.is_valid():
            # Send Credit card to bank,  If the bank responds ok, continue, if not, show the error
            # ..............

            data = Order()
            # get product quantity from form
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.address = form.cleaned_data['address']
            data.city = form.cleaned_data['city']
            data.phone = form.cleaned_data['phone']
            data.user_id = current_user.id
            data.total = total
            data.ip = request.META.get('REMOTE_ADDR')
            ordercode = get_random_string(5).upper()  # random cod
            data.code = ordercode
            data.save()

            for rs in shopcart:
                detail = OrderProduct()
                detail.order_id = data.id  # Order Id
                detail.product_id = rs.product_id
                detail.user_id = current_user.id
                detail.quantity = rs.quantity

                if rs.product.variant == 'None':
                    detail.price = rs.product.price
                else:
                    detail.price = rs.variant.price


                detail.variant_id = rs.variant_id
                detail.amount = rs.amount
                detail.save()
                # ***Reduce quantity of sold product from Amount of Product
                if rs.product.variant == 'None':
                    product = Product.objects.get(id=rs.product_id)
                    product.amount -= rs.quantity
                    product.save()
                else:
                    variant = Variants.objects.get(id=rs.product_id)
                    variant.quantity -= rs.quantity
                    variant.save()
                # ************ <> *****************

            # Clear & Delete shopcart
            ShopCart.objects.filter(user_id=current_user.id).delete()
            request.session['cart_items'] = 0
            messages.success(
                request, "Your Order has been completed. Thank you ")
            return render(request, 'order/order_completed.html', {'ordercode': ordercode, 'category': category})
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect("/order/orderproduct")

    form = OrderForm()
    profile = UserProfile.objects.get(user_id=current_user.id)
    context = {'shopcart': shopcart,
               'category': category,
               'total': total,
               'form': form,
               'profile': profile,
               }
    return render(request, 'order/order_form.html', context)
