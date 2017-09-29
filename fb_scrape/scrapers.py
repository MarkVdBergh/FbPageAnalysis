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


def scrape_posts(page_id, since=None, until=None):
    '''
    Scrapes all posts from the page starting at 'since' till 'until'
    :param page_id: string. The facebook id of the page. Ex: '53668151866'
    :param since: datetime. Timezone=utc
    :param until: datetime. Timezone=utc
    :return: list of dicts. [{'id','created_time','from','to','type','status_type','message','message_tags','link',
                              'name','description','picture','story','shares'}, ..., {}]
                            Ex: [{u'created_time': 1504188000,
                                  u'from': {u'id': u'53668151866', u'name': u'Open Vld'},
                                  u'id': u'53668151866_10154856021046867',
                                  u'link': u'https://www.facebook.com/openvld/photos/a.61804781866.84643.53668151866/10154856021046867/?type=3',
                                  u'message': u'Morgen zit de eerste schooldag er weeral op. DEEL als jij ook iedereen een fijne eerste schooldag of werkdag toewenst.',
                                  u'name': u'Timeline Photos',
                                  u'picture': u'https://scontent.xx.fbcdn.net/v/t1.0-0/s130x130/21231844_10154856021046867_7242492475452613449_n.jpg?oh=5829aa743386134a892968a1a5ee732c&oe=5A584AC5',
                                  u'shares': {u'count': 23},
                                  u'status_type': u'added_photos',
                                  u'type': u'photo'}, ..., {}]
    '''
    graph = facebook.GraphAPI(access_token=fb_access_token, timeout=60, version=FB_API_VERSION)
    # For fields see: https://developers.facebook.com/docs/graph-api/reference/v2.8/post/
    field_list = ['id', 'created_time', 'from', 'to',
                  'type', 'status_type',
                  'message', 'message_tags',
                  'link', 'name', 'description', 'picture',
                  'story',
                  'shares']
    fields = ','.join(field_list)
    chunk = graph.get_connections(page_id, connection_name='posts', fields=fields, date_format='U', since=since, until=until)
    # Add data to each post
    posts = []
    while True:  # get all chuncks of 25 posts for a page
        posts += [post for post in chunk['data']]
        # Attempt to make a request to the next page of data, if it exists.
        # When there are no more pages (['paging']['next']), break from the loop and end the script.
        try:
            chunk = requests.get(chunk['paging']['next']).json()
            logit(scrape_posts.__name__, 'info', '{}: {} posts downloaded for {}'.format(datetime.now(), len(posts), page_id))
        except KeyError:
            break
    # posts.reverse()  # posts are retrieved in reverse order (oldest last)
    return posts


def scrape_reactions(id):
    '''
    Scrapes all reactions from a post or comment
    :param id: string. Ex: '53668151866_10154856021046867'
    :return: list of dicts. [{'type', 'id', 'name', 'pic'}, ..., {}]
                            Ex: [{'id': '10212285251675821', 'name': 'Kristof Sofie Demey-Van Haverbeke',
                                'pic': 'https://scontent.xx.fbcdn.net/v/t1.0-1/p100x100/12718374_10209591178725681_2154386594049448412_n.jpg?oh=15a2fdad3c2e2cd8bd73e4e58b3315a9&oe=5A1CC502',
                                'type': 'LIKE'}]
    '''
    graph = facebook.GraphAPI(access_token=fb_access_token, timeout=60, version=FB_API_VERSION)
    field_list = ['id', 'type', 'name', 'pic']
    fields = ','.join(field_list)
    chunk = graph.get_connections(id, connection_name='reactions', fields=fields, date_format='U')
    reactions = []
    while True:
        reactions += [reaction for reaction in chunk['data']]  # [{u'type': u'LOVE', u'id': u'1366741256698203', u'name': u'Daisy Van Lens', u'pic':'http://...'}, ...]
        # Attempt to make a request to the next page of data, if it exists.
        # When there are no more reactions (['paging']['next']), break from the loop and end the script.
        try:
            chunk = requests.get(chunk['paging']['next']).json()
            logit(scrape_reactions.__name__, 'info', '{}: {} reactions downloaded for {}'.format(datetime.now(), len(reactions), id))
        except KeyError:
            break
    return reactions


# todo: get shares


def scrape_comments(id):
    '''
    Scrapes all comments on a post or comment
    :param id: string.
    :return: list of dicts. Ex. [{'comment':{'id':'10154855940796867_10154856179011867'
                                             'comment_count':1,
                                             'created_time':1504180035,
                                             'from':{'id':'10209219750785129','name':'Rutten Jan'},
                                             'message':'Goed, maar 1 keer vind ik wat weinig; iedereen die ...'
                                             'reactions':[],
                                             'replies':[{'comment': {'id': '10154855940796867_10154855946361867',
                                                                     'comment_count': 0,'created_time': 1504173973,
                                                                    'from': {'id': '10211998015572200', 'name': 'Helena Luyten'},
                                                                    'message': 'Een goed voorstel. Terecht .'},
                                                                    'reactions': [{'id': '53668151866','name': 'Open Vld',
                                                                                   'pic': 'https://scontent.xx.fbcdn.net/v/t1.0-1/p100x100/539883_10151360444726867_1044997288_n.jpg?oh=9e828324b3139aaeba50879bad086572&oe=5A531255',
                                                                                   'type': 'LIKE'}],
                                                                    'replies': []}, ...
    '''
    graph = facebook.GraphAPI(access_token=fb_access_token, timeout=60, version=FB_API_VERSION)
    field_list = ['id', 'created_time', 'from', 'message', 'comment_count', ]
    fields = ','.join(field_list)
    chunk = graph.get_connections(id, connection_name='comments', fields=fields, date_format='U')
    comments = []
    # print(chunk)

    while True:
        for comment in chunk['data']:
            # pprint(comment)
            reactions = scrape_reactions(comment['id'])
            replies = scrape_comments(comment['id'])  # get all reply's
            # print(1 / 0)
            comments.append({'comment': comment, 'reactions': reactions, 'replies': replies})

        # Attempt to make a request to the next page of data, if it exists.
        # When there are no more reactions (['paging']['next']), break from the loop and end the script.
        try:
            chunk = requests.get(chunk['paging']['next']).json()
            logit(scrape_comments.__name__, 'info', '{}: {} comments downloaded for {}'.format(datetime.now(), len(comments), id))
        except KeyError:
            break
    return comments


if __name__ == '__main__':
    pass
