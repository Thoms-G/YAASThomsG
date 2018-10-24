import datetime
import os
from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.urls import reverse
from django.utils import translation
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import generic, View
from django.utils.translation import ugettext as _
from YAASApp.forms import ProfileForm, UserForm, AuctionForm, ConfAuctionForm
from YAASApp.models import Auction, Bid, Profile

# Register a new user
from YAASApp.utils import util_send_mail
from YAASThomasGAY.settings import EMAIL_FILE_PATH


def change_language(request, lang_code):
    translation.activate(lang_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
    messages.add_message(request, messages.INFO, "language change to" + lang_code)

    if request.user.is_authenticated:
        user = request.user
        user.profile.preferred_language = lang_code
        user.profile.save()
    return HttpResponseRedirect(reverse("YAASApp:auctionindex"))


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

    if user is not None and user.is_superuser is False:
        login(request, user)
        return HttpResponseRedirect(reverse('YAASApp:language', args=(user.profile.preferred_language,)))
    if user is not None and user.is_superuser:
        login(request, user)
        return HttpResponseRedirect(reverse('YAASApp:auctionindex'))

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


@login_required
def create_auction(request):
    if request.method == 'POST':
        auction_form = AuctionForm(data=request.POST)

        if auction_form.is_valid():
            auction = auction_form.save(commit=False)

            if auction.deadline < datetime.datetime.now(auction.deadline.tzinfo) + datetime.timedelta(days=3):
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

        if auction.seller != request.user and auction.current_price < bid_price and auction.last_bidder != request.user \
                and auction.status == 'AC':
            if auction.last_bidder is not None:
                util_send_mail('New bid on your auction', 'A new bid has been done on the auction you were wining ' +
                               auction.title, auction.last_bidder.email)
            auction.last_bidder = request.user
            auction.current_price = bid_price
            auction.save()
            bid = Bid(bidder=request.user, auction=auction, bid_price=bid_price)
            bid.save()
            util_send_mail('New bid on your auction', 'A new bid has been done on ' + auction.title,
                           auction.seller.email)
            messages.add_message(request, messages.INFO, _("Bid saved"))
        else:
            messages.add_message(request, messages.ERROR, _("Bid is not conform (check the price)"))

    else:
        messages.add_message(request, messages.ERROR, _("Bid is not conform (check the price)"))

    return HttpResponseRedirect(reverse("YAASApp:auctiondetail", args=(auction_id,)))


class BanAuctions(generic.ListView):
    template_name = 'YAASApp/banauctions.html'
    context_object_name = 'ban_auctions'

    @method_decorator(login_required)
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BanAuctions, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Auction.objects.filter(status='BA')


@login_required
@staff_member_required
def ban_auction(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    if auction.status == 'AC':
        auction.status = 'BA'
        auction.save()
        util_send_mail("Auction banned", "Your auction: " + auction.title + " has been banned", auction.seller.email)
        bids = Bid.objects.filter(auction=auction)
        for bid in bids:
            util_send_mail("Auction banned", "Auction: " + auction.title + " has been banned", bid.bidder.email)
        return HttpResponseRedirect(reverse('YAASApp:list_ban_auction'))


@login_required
@staff_member_required
def email_history(request):
    if request.user.is_superuser:
        directory = EMAIL_FILE_PATH
        emails = []
        for file in os.listdir(directory):
            with open(os.path.join(directory, file), 'r') as email_file:
                data = email_file.read()
            emails.append(data)
        return render(request, 'YAASApp/emails.html', {"emails": emails})
    else:
        messages.warning(request, _("You must be admin."))
        return redirect('YAASApp:auctiondetail')


def data_generation(request):
    Bid.objects.all().delete()
    Auction.objects.all().delete()
    User.objects.all().delete()

    names = ["Emma", "Louise", "Jade", "Alice", "Chloé", "Lina", "Mila", "Léa", "Manon", "Rose", "Anna", "Inès", "Camille", "Lola", "Ambre", "Léna", "Zoé", "Juliette", "Julia", "Lou", "Sarah", "Lucie", "Mia", "Jeanne", "Romane", "Agathe", "Éva", "Nina", "Charlotte", "Inaya", "Gabriel", "Louis", "Raphaël", "Jules", "Adam", "Lucas", "Léo", "Hugo", "Arthur", "Nathan", "Liam", "Éthan", "Maël", "Paul", "Tom", "Sacha", "Noah", "Gabin", "Nolan", "Enzo", "Mohamed", "Aaron", "Timéo", "Théo", "Mathis", "Axel", "Victor", "Antoine", "Valentin", "Martin"]
    surnames = ["Léon", "Yanis", "Augustin", "Éliott", "Maxence", "Évan", "Matheo", "Alexandre", "Thomas", "Simon", "Gaspard", "Naël", "Tiago", "Amir", "Isaac", "Nino", "Ibrahim", "Lyam", "Lenny", "Malo", "Imran", "Marceau", "Alexis", "Kaïs", "Camille", "Noa", "Oscar", "Noam", "Mathys", "Esteban", "Ayden", "Ilyes", "Lorenzo", "Kylian", "Adrien", "Côme", "Wassim", "Ismaël", "Soan", "Amine", "Youssef", "Naïm", "Milo", "Benjamin", "Ayoub", "Joseph", "Owen", "Ali", "William", "Jean", "Louka", "Adem", "Bastien", "Léandre", "Antonin", "Noham", "Logan", "Kenzo", "Younes", "Sandro", "David"]
    objects = ["mirror", "air freshener", "water bottle", "candle", "sidewalk", "playing card", "perfume", "chalk", "sticky note", "street lights", "cup", "tomato", "desk", "watch", "toothpaste", "scotch tape", "ring", "model car", "television", "shoes", "fridge", "beef", "lace", "food", "face wash", "blanket", "radio", "wagon", "drawer", "tooth picks", "mp3 player", "puddle", "spring", "controller", "bowl", "couch", "glow stick", "boom box", "paper", "bookmark", "rubber band", "needle", "toilet", "wallet", "headphones", "helmet", "newspaper", "washing machine", "keyboard", "milk", "house", "fake flowers", "chair", "blouse", "lip gloss", "thread", "cookie jar", "clock", "clamp", "glasses", "shovel", "tissue box", "rubber duck", "tv", "teddies", "eraser", "towel", "clothes", "chapter book", "packing peanuts", "sailboat", "white out", "knife", "toothbrush", "chocolate", "lotion", "nail file", "flowers", "thermostat", "money", "sun glasses", "coasters", "speakers", "bag", "ipod", "vase", "doll", "eye liner", "sharpie", "bracelet", "cat", "stop sign", "greeting card", "window", "soap", "picture frame", "hair tie", "candy wrapper", "hair brush", "soy sauce packet", "photo album", "bottle", "leg warmers", "conditioner", "balloon", "grid paper", "phone", "seat belt", "shampoo", "shawl", "plastic fork", "rug", "remote", "credit card", "floor", "car", "soda can", "canvas", "spoon", "pants"]

    User.objects.create_superuser(username="admin", password="admin2018", email="admin@mail.com").save()

    for i in range(len(names)):
        user = User.objects.create(first_name=names[i], last_name=surnames[i], username=names[i],
                                   password="mdp__"+names[i],
                                   email=names[i]+"@mail.com")

        user.save()

        Profile.objects.create(user=user, preferred_language="en").save()
        price = (12*i+7) % 100
        auction = Auction.objects.create(title=objects[i],
                                         description="See my "+objects[i],
                                         seller=user,
                                         deadline=datetime.datetime.now()+datetime.timedelta(days=price+4),
                                         minimum_price=price,
                                         current_price=price,
                                         last_bidder=None).save()

    return redirect("YAASApp:auctionindex")