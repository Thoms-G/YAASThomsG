from django.urls import path

from YAASApp.api_rest import api_auction_list, api_auction_by_id, api_auction_by_title, api_bid_auction
from . import views

app_name = 'YAASApp'
urlpatterns = (
    path('language/<slug:lang_code>', views.change_language, name='language'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.EditUserView.as_view(), name='userdetail'),
    path('createauction/', views.create_auction, name='createauction'),
    path('saveauction/', views.save_auction, name='saveauction'),
    path('', views.AuctionIndex.as_view(), name='auctionindex'),
    path('auctionbyname/', views.AuctionSearch.as_view(), name='auction_by_name'),
    path('detail/<int:pk>/', views.AuctionDetail.as_view(), name='auctiondetail'),
    path('auctionuser/', views.AuctionUser.as_view(), name='auctionuser'),
    path('editauction/<int:id>', views.EditUserAuction.as_view(), name='edit_user_auction'),
    path('bidauction/<int:auction_id>', views.bid_auction, name='bid_auction'),

    path('banauctions/', views.BanAuctions.as_view(), name='list_ban_auction'),
    path('banauctions/<int:auction_id>', views.ban_auction, name='ban_auction'),
    path('emails/', views.email_history, name='emails'),

    path('api/auctions/', api_auction_list),
    path('api/auctions/<int:auction_id>', api_auction_by_id),
    path('api/auctionsbytitle/', api_auction_by_title),
    path('api/bid/', api_bid_auction),

    path('generatedata/', views.data_generation, name="data_generation"),
)
