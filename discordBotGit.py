import discord
from discord.ext import commands
import pandas as pd
import praw

# discord vars
token = 'NjA4NTI3MDMxNjMzNzA3MDA5.XUpdJw.s53o8ZwGpmLAgKYVYfyejQnZ93I'
# add link: https://discordapp.com/api/oauth2/authorize?client_id=608527031633707009&permissions=0&scope=bot

# reddit vars
clid = 'xn0ad2KiBrq6xg'
clsecret = 'XXXX'
app_name = 'redditScrape'
acc_user = 'XXXX'
acc_pass = 'XXXX'


# scrapes reddit for posts
class ScrapeKey():
    def __init__(self, searchKey, subName, imageHost = 'i.redd.it'):
        self.redditScrape = praw.Reddit(client_id=clid,
                     client_secret=clsecret,
                     user_agent=app_name,
                     username=acc_user,
                     password=acc_pass)

        self.redditSub = self.redditScrape.subreddit(subName)
        self.search = searchKey
        self.imageHost = imageHost

        self.postsDict = {'title': [],
                          'url': []
                          }

    # creates dict of titles and urls with image host specified
    def scrape(self):
        self.redditResults = self.redditSub.search(self.search, sort= 'top', time_filter= 'day', limit = 500)
        for post in self.redditResults:
            if self.imageHost in post.url:
                self.postsDict['title'].append(post.title)
                self.postsDict['url'].append(post.url)

    # returns dictionary of posts
    def getPosts(self):
        return self.postsDict

# creates iterator of post URLs
class postIter():
    def __init__(self, searchKey, subname, imageHost):
        self.redditScrape = ScrapeKey(searchKey, subname, imageHost)
        self.postsFormatted = []

    # formats scraped posts
    def formatPosts(self):
        self.redditScrape.scrape()
        self.postsRaw = self.redditScrape.getPosts()
        self.postsData = pd.DataFrame(self.postsRaw)

    # makes post data iterator
    def makePostIter(self):
        self.titleList = self.postsData['title'].tolist()
        self.urlList = self.postsData['url'].tolist()
        for postIndex in range(0,len(self.urlList)):
            self.postsFormatted.append(self.titleList[postIndex] + '\n' + self.urlList[postIndex])

    # returns number of posts scraped
    def getPostLen(self):
        return len(self.postsFormatted)

    # returns iterator of posts
    def getPostIter(self):
        return iter(self.postsFormatted)

# creates bot and sets default sub to search from
client = commands.Bot(command_prefix='!')
client.remove_command('help')
sub = 'all'
img = 'i.redd.it'

helpMsg = "rsearch: Searches for top posts/images in current subreddit - default is r/all\nrsub: Switches search subreddit to inputted name - no argument switches to r/all\nrimg:switches image provider to search by - no argument switches to i.redd.it\nrget: Gets next post found by rsearch - rsearch must be called before"

@client.event
async def on_ready():
    print("The bot is ready!")
    await client.change_presence(game=discord.Game(name="Going Brazy"))

# help message
@client.command()
async def help():
    await client.say(helpMsg)

# searches for top posts in current subreddit with keyword
@client.command()
async def rsearch(*, arg):
    global postStack
    postIterTest = postIter(arg, sub, img)
    postIterTest.formatPosts()
    postIterTest.makePostIter()
    if postIterTest.getPostLen() <= 0 :
        await client.say("No posts found")
    else:
        postStack = postIterTest.getPostIter()
        await client.say("Posts found")

# switches subreddit to scrape from
@client.command()
async def rsub(arg = 'all'):
    global sub
    sub = arg
    await client.say("Now searching from: r/" + sub)

# switches image provider to scrape from
@client.command()
async def rimg(arg = 'i.redd.it'):
    global img
    img = arg
    await client.say("Now searching for posts with images from: " + img)

# gets next title/url pair in stack of posts scraped
@client.command()
async def rget():
    try:
        await client.say(next(postStack))
    except StopIteration:
        await client.say("Reached end of posts")
    except NameError:
        await client.say("No posts scraped yet")


client.run(token)