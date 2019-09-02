import discord
from discord.ext import commands
import pandas as pd
import praw

# discord vars
token = 'XXX'
# add link: https://discordapp.com/api/oauth2/authorize?client_id=608527031633707009&permissions=0&scope=bot

# reddit vars
clid = 'XXXX'
clsecret = 'XXXX'
app_name = 'XXXX'
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

    # formats scraped posts
    def formatPosts(self):
        self.redditScrape.scrape()
        self.postsRaw = self.redditScrape.getPosts()
        self.postsData = pd.DataFrame(self.postsRaw)

    # makes lists of post titles and image urls
    def makePostIter(self):
        self.titleList = self.postsData['title'].tolist()
        self.urlList = self.postsData['url'].tolist()

    # returns number of posts scraped
    def getPostLen(self):
        return len(self.urlList)

    # returns iterator of titles
    def getTitle(self):
        return iter(self.titleList)

    # returns iterator of urls
    def getUrl(self):
        return iter(self.urlList)

# creates bot and sets default subreddit to search from
client = commands.Bot(command_prefix='!')
client.remove_command('help')
sub = 'all'
img = 'i.redd.it'


@client.event
async def on_ready():
    print("The bot is ready!")
    await client.change_presence(game=discord.Game(name="No Current Search"))

# help message with embed
@client.command(pass_context=True)
async def help():

    helpEmbed = discord.Embed(

        colour = discord.Colour.green()

    )
    helpEmbed.set_author(name = "Help")
    helpEmbed.add_field(name = "!rsearch", value="Searches for top posts/images in current subreddit - default is r/all", inline=False)
    helpEmbed.add_field(name = "!rget", value="Gets next post found by rsearch - rsearch must be called before", inline=False)
    helpEmbed.add_field(name = "!rsub", value="Switches search subreddit to inputted name - no argument switches to r/all", inline=False)
    helpEmbed.add_field(name = "!rimg", value="Switches image provider to search by - no argument switches to i.redd.it", inline=False)

    await client.say(embed=helpEmbed)

# searches for top posts in current subreddit with keyword
@client.command()
async def rsearch(*, arg):
    global postStack
    global titleStack
    global urlStack
    searchStatus = "Current Search: {}".format(arg)
    await client.change_presence(game = discord.Game(name = searchStatus))
    postIterTest = postIter(arg, sub, img)
    postIterTest.formatPosts()
    postIterTest.makePostIter()
    if postIterTest.getPostLen() <= 0 :
        await client.say("No posts found")
    else:
        titleStack = postIterTest.getTitle()
        urlStack = postIterTest.getUrl()
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

# gets next title/url pair in stack of posts scraped using discord embed
@client.command()
async def rget():
    try:
        postEmbed = discord.Embed(
            color=discord.Colour.orange()
        )
        postEmbed.set_author(name=next(titleStack))
        postEmbed.set_image(url=next(urlStack))
        await client.say(embed=postEmbed)
    except StopIteration:
        await client.say("Reached end of posts")
    except NameError:
        await client.say("No posts scraped yet")


client.run(token)