#!/usr/bin/env python3
from os import access
import re
import requests
import json


def get_account_info(domain, access_token):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    res = requests.get('https://' + domain + '/api/v1/session/current_session_account', headers=headers).json()
    return res


def post_text(domain, access_token, params):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    url = "https://{}/api/v1/posts".format(domain)
    response = requests.post(url, headers=headers, json=params)
    if response.status_code != 200:
        raise Exception('リクエストに失敗しました。')
    return response


def filterPosts(twts):
    replyMatch = re.compile(r"@\w+")
    urlMatch = re.compile(r"https?://")
    data = []
    for text in twts:
        if replyMatch.search(text) or urlMatch.search(text):
            continue
        data.append(text)
    return data


def fetchPosts(domain, access_token, account_id, params):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    url = "https://{}/api/v1/accounts/{}/posts".format(domain, account_id)
    response = requests.get(url, headers=headers, json=params)
    if response.status_code != 200:
        raise Exception('リクエストに失敗しました。')
    return response


def fetchPostsLoop(domain, access_token, account_id, params, loop):
    posts = []
    for i in range(loop):
        try:
            req = fetchPosts(domain, access_token, account_id, params)
            # print(req.status_code)
            req = req.json()
            for x in req:
                last_id = x['id']
                print(x['text'])
                if x['visibility'] == 1 or x['visibility'] == 2:
                    print("鍵投稿のためスキップしました。 {}".format(x['text']))
                    continue
                seikei = re.compile(r"<[^>]*?>").sub("", x['text'])
                posts.append(seikei)
                params["max_id"] = last_id
        except Exception as e:
            print("読み込みエラー: {}".format(e))
            break
    # 重複投稿を削除
    posts = list(set(posts))
    return posts


def loadMastodonAPI(domain, access_token, account_id, params):
    posts = fetchPostsLoop(domain, access_token, account_id, params, 200)
    return "\n".join(filterPosts(posts))
