from .exceptions import InvalidUsernameException, UnknownException, RateLimitException
from bs4 import BeautifulSoup
import requests
import urllib.request
import sys
import time
import json
import os


def clean_username(username):
    if not username:
        raise InvalidUsernameException("Username can not be null")
    try:
        username = username.strip().lower()
        if username:
            return username
        else:
            raise InvalidUsernameException()
    except Exception as e:
        raise InvalidUsernameException(repr(e))


def create_user_dir(username):
    foldername = "instagram_downloads/instagram_" + username
    if not os.path.exists(foldername):
        os.makedirs(foldername)
    return foldername


def get_response(username):
    response = requests.get("https://www.instagram.com/" + username + "/")
    if response.status_code == 404:
        raise InvalidUsernameException()
    return response


def get_user_data_json(script_tags):
    try:
        json_text = None
        for tag in script_tags:
            if "sharedData" in tag.text:
                json_text = tag.text
                break

        json_text = json_text[len("window._sharedData = "):]
        json_text = json_text[:-1]
        json_obj = json.loads(json_text)
        return json_obj
    except Exception as e:
        raise UnknownException()


def printt(verbose, msg, end=False):
    if verbose:
        if end:
            print(msg, end="")
        else:
            print(msg)
        sys.stdout.flush()


def get_images(images, count, w, verbose, foldername):
    printt(verbose, "\nDownloading image from first page")
    for image in images:
        if "GraphImage" == image["__typename"]:
            urllib.request.urlretrieve(image["display_src"], foldername + "/" + str(count) + ".jpg")
            count += 1
            printt(verbose, ".", end=True)
            time.sleep(w)
    return count


def get_next_pages_images(images, count, w, verbose, foldername):
    printt(verbose,"\nDownloading images from next page")
    for image in images:
        if "GraphImage" == image["node"]["__typename"]:
            urllib.request.urlretrieve(image["node"]["display_url"], foldername + "/" + str(count) + ".jpg")
            count += 1
            printt(verbose, ".", end=True)
            time.sleep(w)
    return count


def validate_params(verbose, wait_between_request):
    if not isinstance(verbose, bool):
        raise ValueError("Invalid value for verbose. Accepted values are True or False.")
    if not isinstance(wait_between_request, int) or wait_between_request < 0:
        raise ValueError("Invalid value for wait_between_requests. Pass a positive integer.")


def download(username, verbose=True, wait_between_requests=0):
    validate_params(verbose, wait_between_requests)
    username = clean_username(username)
    response = get_response(username)
    soup = BeautifulSoup(response.text, 'lxml')
    script_tags = (soup.find_all('script'))
    json_obj = get_user_data_json(script_tags)

    user_id = json_obj["entry_data"]["ProfilePage"][0]["user"]["id"]
    images = json_obj["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]

    foldername = create_user_dir(username)
    printt(verbose, "\n\nDownloading data for " + username + " in directory "+foldername, end="")
    count = 0
    count = get_images(images, count, wait_between_requests, verbose, foldername)

    # check if more images are present
    is_next = json_obj["entry_data"]["ProfilePage"][0]["user"]["media"]["page_info"]["has_next_page"]
    end_cursor = json_obj["entry_data"]["ProfilePage"][0]["user"]["media"]["page_info"]["end_cursor"]

    # until next pages are available
    while is_next:
        next_url = 'https://www.instagram.com/graphql/query/?query_id=17888483320059182&variables=' \
                   '{"id":"' + user_id + '","first":12,"after":"' + end_cursor + '"}'
        response = None
        try:
            response = requests.get(next_url)
        except Exception as e:
            raise UnknownException(repr(e))

        json_obj = json.loads(response.text)

        # if there are too many requests in a minute
        if "fail" == json_obj["status"]:
            raise RateLimitException()

        images = json_obj["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
        count = get_next_pages_images(images, count, wait_between_requests, verbose, foldername)

        page_info = json_obj["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]
        is_next = page_info["has_next_page"]
        if is_next:
            end_cursor = page_info["end_cursor"]

    printt(verbose, "\nDownloaded "+str(count)+" images")
