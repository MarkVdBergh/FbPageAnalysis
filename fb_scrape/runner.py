from pprint import pprint
from time import mktime

import facebook
from datetime import datetime, timedelta

import requests
import sys
#
# from profilehooks import timecall
# from pymongo import InsertOne
from pymongo import MongoClient
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError, DuplicateKeyError
from pytz import UTC

from helpers import logit
from settings import FB_APP_ID, FB_APP_SECRET, FB_API_VERSION, MONGO_HOST, MONGO_PORT

fb_access_token = FB_APP_ID + "|" + FB_APP_SECRET
client = MongoClient(host=MONGO_HOST, port=MONGO_PORT, )


'''
users
    id
    name
    pic

    pages_active
    posts
    comments
    reactions

    total_posts
    total_comments
    total_reactions

posts
    id





comments
    id






'''

















def scrape_post_ids(page_id, since=None, until=None):
    graph = facebook.GraphAPI(access_token=fb_access_token, timeout=60, version=FB_API_VERSION)
    # For fields see: https://developers.facebook.com/docs/graph-api/reference/v2.8/post/
    field_list = ['id']
    fields = ','.join(field_list)
    chunk = graph.get_connections(page_id, connection_name='posts', fields=fields, date_format='U', since=since, until=until)
    # Add data to each post
    post_ids = []
    print(chunk)
    while True:  # get all chuncks of 25 posts for a page
        # post_ids += [post for post in chunk['data']]
        # Attempt to make a request to the next page of data, if it exists.
        # When there are no more pages (['paging']['next']), break from the loop and end the script.
        try:
            print("save ...")
            chunk = requests.get(chunk['paging']['next']).json()
            print(chunk)
            # print(1/0)
            logit(scrape_post_ids.__name__, 'info', '{}: {} post_ids downloaded for {}'.format(datetime.now(), len(post_ids), page_id))
        except KeyError:
            break
    # posts.reverse()  # posts are retrieved in reverse order (oldest last)
    return post_ids





if __name__ == '__main__':
    pass
