from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views import generic

from YAASApp.forms import ProfileForm, UserForm, UpdateUserForm
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


@login_required
@transaction.atomic
def userdetail(request):
    update_user_form = UpdateUserForm(request.POST, instance=request.user)
    if request.method == 'POST':
        if update_user_form.is_valid():
            update_user_form.save()
            return redirect('YAASApp:userdetail')

    return render(request, 'YAASApp/profile.html', {'update_user_form': update_user_form})


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
