import datetime

from django.utils import timezone
from django.utils.timezone import utc
from django_cron import CronJobBase, Schedule

from YAASApp.models import Auction, Bid
from YAASApp.utils import util_send_mail
from YAASThomasGAY.settings import TIME_ZONE


class ResolveAuctions(CronJobBase):
    RUN_EVERY_MINS = 1  # every 1 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'YAASApp.resolve_auctions'  # a unique code

    def do(self):
        auctions = Auction.objects.filter(status='AC').order_by('deadline')
        print("Begin cron")
        for auction in auctions:
            if auction.deadline <= timezone.now():
                auction.status = 'DU'
                auction.save()

                if auction.last_bidder is not None:
                    auction.status = 'AD'
                    auction.save()
                    util_send_mail("Auction adjudicated", "Your auction: " + auction.title + " is adjudicated",
                                   auction.seller.email)
                    util_send_mail("Auction adjudicated", "You won this auction: " + auction.title,
                                   auction.last_bidder.email)

                    bids = Bid.objects.filter(auction=auction)
                    for bid in bids:
                        util_send_mail("Auction adjudicated", "Auction: " + auction.title + " is adjudicated",
                                       bid.bidder.email)
                    print("All emails send")
                else:
                    util_send_mail("Auction adjudicated", "Your auction: " + auction.title +
                                   " is due but there is no bid", auction.seller.email)
                    print("no bidder")

            else:
                break
