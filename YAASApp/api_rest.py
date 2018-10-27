from decimal import Decimal

from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from django.shortcuts import get_object_or_404

from YAASApp.models import Auction, Bid
from YAASApp.serializers import AuctionSerializer, BidSerializer
from YAASApp.utils import util_send_mail
from YAASApp.views import soft_deadline


@api_view(['GET'])
@renderer_classes([JSONRenderer,])
def api_auction_list(request):
    auctions = Auction.objects.all()
    serializer = AuctionSerializer(auctions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@renderer_classes([JSONRenderer,])
def api_auction_by_id(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    serializer = AuctionSerializer(auction)
    return Response(serializer.data)


@api_view(['GET'])
@renderer_classes([JSONRenderer,])
def api_auction_by_title(request):
    in_title = request.query_params['intitle']
    auctions = Auction.objects.filter(title__icontains=in_title)
    serializer = AuctionSerializer(auctions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer,])
def api_bid_auction(request):
    auction = get_object_or_404(Auction, id=request.query_params['auction_id'])
    if request.query_params['bid_price'] != '' and request.query_params['bid_price'] is not None:
        bid_price = Decimal(request.query_params['bid_price'])

        if auction.seller != request.user and auction.current_price < bid_price and auction.last_bidder != request.user\
                and auction.status == 'AC':
            if auction.last_bidder is not None:
                util_send_mail('New bid on your auction', 'A new bid has been done on the auction you were wining',
                               auction.last_bidder.email)
            auction.last_bidder = request.user
            auction.current_price = bid_price
            auction.save()
            bid = Bid(bidder=request.user, auction=auction, bid_price=bid_price)
            bid.save()
            util_send_mail('New bid on your auction', 'A new bid has been done on your auction', auction.seller.email)
            soft_deadline(auction=auction)
            serializer = BidSerializer(bid)
            return Response(serializer.data)
        else:
            return Response({'error': 'Bid is not conform (check the price, the deadline or the seller)'})

    else:
        return Response({'error': 'Bid price is empty'})
