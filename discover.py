'''Find valid tags and usernames.


The file will contain things like:

tag:12345:romance
'''
import gzip
import re
import requests
import string
import sys
import time
import random

DEFAULT_HEADERS = {'User-Agent': 'ArchiveTeam'}


class FetchError(Exception):
    '''Custom error class when fetching does not meet our expectation.'''


def main():
    # Take the program arguments given to this script
    # Normal programs use 'argparse' but this keeps things simple
    start_num = int(sys.argv[1])
    end_num = int(sys.argv[2])
    output_filename = sys.argv[3]  # this should be something like myfile.txt.gz

    assert start_num <= end_num

    print('Starting', start_num, end_num)

    gzip_file = gzip.GzipFile(output_filename, 'wb')

    for shortcode in check_range(start_num, end_num):
        # Write the valid result one per line to the file
        line = '{0}\n'.format(shortcode)
        gzip_file.write(line.encode('ascii'))

    gzip_file.close()

    print('Done')


def check_range(start_num, end_num):
    '''Check if page exists.

    Each line is like tag:12345:romance
    '''

    for num in range(start_num, end_num + 1):
        shortcode = num
        url = 'http://www.panoramio.com/user/{0}'.format(shortcode)
        counter = 0

        while True:
            # Try 20 times before giving up
            if counter > 20:
                # This will stop the script with an error
                raise Exception('Giving up!')

            try:
                text = fetch(url)
            except FetchError:
                # The server may be overloaded so wait a bit
                print('Sleeping... If you see this')
                time.sleep(10)
            else:
                if text:
                    for user in extract_user(text) for tag in extract_tags(text):
                        yield 'tag:{0}:{1}'.format(user, tag)
                break  # stop the while loop

            counter += 1


def fetch(url):
    '''Fetch the URL and check if it returns OK.

    Returns True, returns the response text. Otherwise, returns None
    '''
    print('Fetch', url)
    response = requests.get(url, headers=DEFAULT_HEADERS)

    # response doesn't have a reason attribute all the time??
    print('Got', response.status_code, getattr(response, 'reason'))

    if response.status_code == 200:
        # The item exists
        if not response.text:
            # If HTML is empty maybe server broke
            raise FetchError()

        return response.text
    elif response.status_code == 404:
        # Does not exist
        return
    else:
        # Problem
        raise FetchError()


def extract_user(text):
    '''Return a list of tags from the text.'''
    # Search for <a href="/user/1707816/tags/Bell%27Italia">Bell'Italia</a>
    return re.findall(r'"/user/([^/]+)/tags/', text)


def extract_tags(text):
    '''Return a list of tags from the text.'''
    # Search for <a href="/user/1707816/tags/Bell%27Italia">Bell'Italia</a>
    return re.findall(r'"/user/[0-9]+/tags/([^"]+)"', text)

if __name__ == '__main__':
    main()
