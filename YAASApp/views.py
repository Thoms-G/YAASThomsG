import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import generic, View

from YAASApp.forms import ProfileForm, UserForm, AuctionForm, ConfAuctionForm
from YAASApp.models import Auction, Bid

# Register a new user
from YAASApp.utils import util_send_mail


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
def user_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return redirect('YAASApp:auctionindex')

    return render_to_response('YAASApp/login.html', )


@login_required
def user_logout(request):
    logout(request)
    return redirect('YAASApp:auctionindex')


class EditUserView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'YAASApp/profile.html')

    @method_decorator(login_required)
    def post(self, request):
        u = request.user

        if request.POST["new_email"] != u.email:
            u.email = request.POST["new_email"]
            u.save()

        if request.POST["new_password"] != '':
            u.set_password(request.POST["new_password"])
            u.save()
            update_session_auth_hash(request, u)

        # Always redirect after a successful POST request
        return HttpResponseRedirect(reverse('YAASApp:userdetail'))


# TODO : Send a confirmation email
@login_required
def create_auction(request):
    if request.method == 'POST':
        auction_form = AuctionForm(data=request.POST)

        if auction_form.is_valid():
            auction = auction_form.save(commit=False)

            if auction.deadline < datetime.datetime.now(auction.deadline.tzinfo)+datetime.timedelta(days=3):
                messages.warning(request, "Deadline is not valid")
                return render(request, 'YAASApp/createauction.html', {'auction_form': auction_form})

            cd = auction_form.cleaned_data
            b_title = cd['title']
            b_description = cd['description']
            b_minimum_price = cd['minimum_price']
            b_deadline = cd['deadline']
            conf_form = ConfAuctionForm({'b_title': b_title,
                                         'b_description': b_description,
                                         'b_minimum_price': b_minimum_price,
                                         'b_deadline': b_deadline})
            return render(request, 'YAASApp/auctionconf.html', {'conf_form': conf_form})

    auction_form = AuctionForm(data=request.POST)
    return render(request, 'YAASApp/createauction.html', {'auction_form': auction_form})

@login_required
def save_auction(request):
    option = request.POST['option']
    if option == 'Yes':
        title = request.POST['b_title']
        description = request.POST['b_description']
        m_p = request.POST['b_minimum_price']
        deadline = request.POST['b_deadline']
        auction = Auction(title=title, description=description,
                          minimum_price=m_p, deadline=deadline,
                          current_price=m_p, seller=request.user,
                          last_bidder=None)
        auction.save()
        util_send_mail('Auction creation', 'Your auction has successfully been created!', request.user.email)
        return HttpResponseRedirect(reverse('YAASApp:auctionuser'))
    else:
        return redirect('YAASApp:auctionindex')


class AuctionIndex(generic.ListView):
    template_name = 'YAASApp/home.html'
    context_object_name = 'auction_list'

    def get_queryset(self):
        return Auction.objects.filter(status='AC')


class AuctionSearch(generic.ListView):
    template_name = 'YAASApp/auctionbyname.html'
    context_object_name = 'auctions'

    @method_decorator(csrf_exempt)
    def get_queryset(self):
        intitle = self.request.GET['searchbox']
        return Auction.objects.filter(status='AC', title__icontains=intitle)


class AuctionDetail(generic.DetailView):
    model = Auction
    template_name = 'YAASApp/detailauction.html'


class AuctionUser(generic.ListView):
    template_name = 'YAASApp/userauctions.html'
    context_object_name = 'user_auctions'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AuctionUser, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Auction.objects.filter(seller=self.request.user, status='AC')


class EditUserAuction(View):
    @method_decorator(login_required)
    def get(self, request, id):
        auction = get_object_or_404(Auction, id=id)
        return render(request, 'YAASApp/editauction.html', {'auction': auction})

    @method_decorator(login_required)
    def post(self, request, id):
        auction = get_object_or_404(Auction, id=id)

        if request.POST['description'] != auction.description:
            auction.description = request.POST['description']
            auction.save()

        return HttpResponseRedirect(reverse('YAASApp:edit_user_auction', args=(auction.id,)))


@login_required
def bid_auction(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    if request.POST['bid_price'] != '':
        bid_price = Decimal(request.POST['bid_price'])

        if auction.seller != request.user and auction.current_price < bid_price and auction.last_bidder != request.user:
            auction.last_bidder = request.user
            auction.current_price = bid_price
            auction.save()
            bid = Bid(bidder=request.user, auction=auction, bid_price=bid_price)
            bid.save()
            messages.add_message(request, messages.INFO, "Bid saved")
        else:
            messages.add_message(request, messages.ERROR, "Bid is not conform (check the price)")

    else:
        messages.add_message(request, messages.ERROR, "Bid is not conform (check the price)")

    return HttpResponseRedirect(reverse("YAASApp:auctiondetail", args=(auction_id,)))


