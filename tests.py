from datetime import datetime, timedelta
from pprint import pprint

from pytz import UTC

from fb_scrape.runner import scrape_post_ids
from fb_scrape.scrapers import  scrape_reactions, scrape_comments, scrape_posts

# Tests fb_scrape
# pprint(scrape_post_ids(page_id='53668151866', since=datetime.now(tz=UTC) - timedelta(days=365,hours=20)))
pprint(scrape_posts(page_id='53668151866', since=datetime.now(tz=UTC) - timedelta(days=0, hours=20)))
# pprint(scrape_reactions('298515443880063'))
# pprint(scrape_comments('53668151866_10154855940796867'))


# Todo: post save post or post post save?
