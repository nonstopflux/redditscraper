import json
import requests
import string
import time
import datetime
import sqlite3


# Variables
sub    = 'redditdev'     # name of the subreddit you would like to scrape
after  = '2018-05-01'    # earliest date that will be scraped
before = '2018-05-31'    # latest date that will be scraped
fast   = False           # True will be faster, won't pull upvote ratio


# Initiate things
sql = sqlite3.connect('redditScraper.db')
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS posts (name TEXT, title TEXT, readable_utc TEXT, permalink TEXT, domain TEXT, url TEXT, author TEXT, score TEXT, upvote_ratio TEXT, num_comments TEXT)')
sql.commit()
print('Loaded SQL Database and Tables')

after = time.mktime(datetime.datetime.strptime(after, '%Y-%m-%d').timetuple())
after = int(after)
readable_after = time.strftime('%d %b %Y %I:%M %p', time.localtime(after))
before = time.mktime(datetime.datetime.strptime(before, '%Y-%m-%d').timetuple())
before = int(before) + 86399
readable_before = time.strftime('%d %b %Y %I:%M %p', time.localtime(before))
print('Searching for posts between ' + readable_after + ' and ' + readable_before + '.')
currentDate = before


# Perform a new full pull from Pushshift
def newpull(thisBefore):
    global currentDate
    readable_thisBefore = time.strftime('%d %b %Y %I:%M %p', time.localtime(thisBefore))
    print('Searching posts before ' + str(readable_thisBefore))
    url = 'http://api.pushshift.io/reddit/search/submission/?subreddit=' + sub + '&size=500&before=' + str(thisBefore)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print('    Discussion: HTML Error - ', response.status_code)
        time.sleep(60)
        return
    curJSON = response.json()

    # Update each Pushshift result with Reddit data
    for child in curJSON['data']:

        # Check to see if already added
        name = str(child['id'])
        cur.execute('SELECT * FROM posts WHERE name == ?', [name])
        if cur.fetchone():
            print(str(child['id']) + ' skipped (already in database)')
            continue

        # If not, get more data
        if fast is True:
            searchURL = 'http://reddit.com/by_id/t3_'
        else:
            searchURL = 'http://reddit.com/'
        url = searchURL + str(name) + '.json'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print('    Discussion: HTML Error - ', response.status_code)
            time.sleep(60)
            break
        postJSON = response.json()
        if fast is True:
            jsonStart = postJSON
        else:
            jsonStart = postJSON[0]

        # Check to see if Date has passed
        global currentDate
        created_utc = jsonStart['data']['children'][0]['data']['created_utc']
        currentDate = int(created_utc)
        if currentDate <= after:
            break

        # If not, process remaining data
        try:
            title = str(jsonStart['data']['children'][0]['data']['title'])  # Checks for emojis and other non-printable characters
        except UnicodeEncodeError:
            title = ''.join(c for c in str(jsonStart['data']['children'][0]['data']['title']) if c in string.printable)
        readable_utc = time.strftime('%d %b %Y %I:%M %p', time.localtime(created_utc))
        permalink    = (str(jsonStart['data']['children'][0]['data']['permalink']))
        domain       = (str(jsonStart['data']['children'][0]['data']['domain']))
        url          = (str(jsonStart['data']['children'][0]['data']['url']))
        author       = (str(jsonStart['data']['children'][0]['data']['author']))
        score        = (str(jsonStart['data']['children'][0]['data']['score']))
        num_comments = (str(jsonStart['data']['children'][0]['data']['num_comments']))
        if fast is True:
            upvote_ratio = 0
        else:
            upvote_ratio = (str(jsonStart['data']['children'][0]['data']['upvote_ratio']))

        # Write it to SQL Database
        cur.execute('INSERT INTO posts VALUES(?,?,?,?,?,?,?,?,?,?)', [name, title, readable_utc, permalink, domain, url, author, score, upvote_ratio, num_comments])
        sql.commit()

# Run the newpull
while currentDate >= after:
    newpull(currentDate)
