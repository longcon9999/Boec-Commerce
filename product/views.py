from product.forms import CommentForm
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from product.models import Comment


def index(request):
    return HttpResponse("My Product Page")


def addcomment(request, id):
    url = request.META.get('HTTP_REFERER')  # get last url
    if request.method == 'POST':  # check post
        form = CommentForm(request.POST)
        if form.is_valid():
            data = Comment()  # create relation with model
            data.subject = form.cleaned_data['subject']
            data.comment = form.cleaned_data['comment']
            data.rate = form.cleaned_data['rate']
            data.ip = request.META.get('REMOTE_ADDR')
            data.product_id = id
            current_user = request.user
            if current_user.is_staff is True:
                messages.error(
                    request, "You can not review the product.")
            else:
                data.user_id = current_user.id
                data.save()  # save data to table
                messages.success(
                    request, "Your review has ben sent. Thank you for your interest.")
            return HttpResponseRedirect(url)

    return HttpResponseRedirect(url)


def colors(request):
    return render(request, 'product/product_color.html')
