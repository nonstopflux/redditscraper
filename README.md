# reddit

## RedditScraper.py

Pulls a listing of posts from https://pushshift.io/reddit/ and then checks each of those posts on reddit and pulls the current stats.

Variables to be set are as follows:
- **sub** is the name of the subreddit you would like to scrape
- **after** is the earliest date you would like to pull
- **before** is the latest date you would like to pull
- **fast** will scrape not quite twice as fast, but it will not include the value for upvote ratio

Returned values are as follows:
- postid
- title
- readable date/time
- permalink
- domain
- url
- author
- score
- upvote ratio (returns 0 when fast is set to false)
- number of comments
