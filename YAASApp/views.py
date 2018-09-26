from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views import generic, View

from YAASApp.forms import ProfileForm, UserForm
from YAASApp.models import Auction


# Register a new user
def register(request):
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('YAASApp:auctionindex')
    else:
        user_form = UserForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST)
    return render(request, 'YAASApp/register.html', {'user_form': user_form, 'profile_form': profile_form})


@csrf_exempt
def userlogin(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return redirect('YAASApp:auctionindex')

    return render_to_response('YAASApp/login.html', )


class EditUserView(View):
    def get(self, request):
        u = request.user
        return render(request, 'YAASApp/profile.html')

    def post(self, request):
        u = request.user
        if request.POST["new_email"] != u.email:
            u.email = request.POST["new_email"]
            u.save()

        if request.POST["new_password"] is not None:
            u.set_password(request.POST["new_password"])
            u.save()
        # Always redirect after a successful POST request
        return HttpResponseRedirect(reverse('YAASApp:userdetail'))
# TODO : faire deux classes, une pour le password et une pour le mail


class AuctionIndex(generic.ListView):
    template_name = 'YAASApp/home.html'
    context_object_name = 'auction_list'

    def get_queryset(self):
        return Auction.objects.all()


@login_required
class AuctionDetail(generic.DetailView):
    model = Auction
    template_name = 'YAASApp/detailauction.html'
    # TODO : AuctionDetail
