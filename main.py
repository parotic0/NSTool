from __future__ import print_function, unicode_literals
from PyInquirer import style_from_dict, Token, prompt, Separator
from pyfiglet import Figlet
from clint.arguments import Args
from clint.textui import puts, colored, indent
from PyInquirer import Validator, ValidationError
import twitter
import time
import webbrowser
import os
import sys
import re
import requests
import base64
import json
import sqlite3
import tweepy 
import platform  


####### todo: stop using global variables.
# logging in releated stuff
api = ""
consumer_key_array= []
consumer_secret_array = []
access_token_array = []
access_secret_array = []
authkeys = []
amtofauthkeys = 0
amtofapikeys = 0
apiconnected = False
# monitor related
acc = ""
id = ""
longurl = ""
latestid = ""
urltemp = ""
valid = False
discjoiner = False
fast = False
keyInputSuccess = ""
# misc
ostype = platform.system()
status = "🖓"


style = style_from_dict({
    Token.Separator: '#cc5454',
    Token.QuestionMark: '#673ab7 bold',
    Token.Selected: '#cc5454',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#f44336 bold',
    Token.Question: '',
})

MainOptions = [
    {
        'type': 'rawlist',
        'name': 'Options',
        'message': 'Choose Option',
        'choices': ['twitter monitor', 'settings']
    },
]

UpdateKeyOptions = [
    {
        'type': 'rawlist',
        'name': 'Options',
        'message': 'Choose Option',
        'choices': ['add new twitter API key', 'add new discord auth key', 'test twitter API keys', 'test discord auth keys', 'Back']
    },
]

TwitterOptions = [
    {
        'type': 'checkbox',
        'message': 'Enable extensions',
        'name': 'Options',
        'choices': [
            Separator('= Discord Modules ='),
            {
                'name': 'Join Discord'
            }

        ],
    }
]

MainSettings = [
    {
        'type': 'rawlist',
        'name': 'Options',
        'message': 'Choose Option',
        'choices': ['key tools', 'Back']
    },
]

UserModes = [
    {
        'type': 'rawlist',
        'name': 'User Mode Options',
        'message': 'Choose Option',
        'choices': ['User Mode', 'Application', 'help']
    },
]

ShowTwitterUsername = [
    {
        'type': 'input',
        'name': 'twitter username',
        'message': 'Enter Twitter Username @',
    },
]

userInputKeys = [
    {
        'type': 'input',
        'name': 'Consumer Key',
        'message': 'Enter consumer key: ',
    },
    {
        'type': 'input',
        'name': 'Consumer Secret Key',
        'message': 'Enter consumer secret key: ',
    },
    {
        'type': 'input',
        'name': 'Access Token Key',
        'message': 'Enter access token key: ',
    },
    {
        'type': 'input',
        'name': 'Access Token Secret Key',
        'message': 'Enter access token secret key: ',
    },

]

userInputDiscord = [
    {
        'type': 'input',
        'name': 'discord auth token',
        'message': 'Enter discord auth token: ',
    },
]

def tweettime(id,time):
    ## logins into using tweepy
    #  using tweepy because our current api doesn't let you see tweet times.
    try:
        tpa = tweepy.OAuthHandler(consumer_key_array[0],consumer_secret_array[0])
        tpa.set_access_token(access_token_array[0],access_secret_array[0])
        tpapi = tweepy.API(tpa)
        loggedin = True
    except Exception:
        loggedin = False
        print("Error API_FAILURE\nWe were unable to log into the api, this isnt a fatal error we can't see the time the tweet was tweeted.")
    if loggedin:
        tweet = tpapi.get_status(id)
        created_at = tweet.created_at
        ## still not as accurate as i want, kinda peak but its all we can do
        print("tweet time - "+str(created_at)+ "UTC")
        time = str(time)
        #if "0." in time:
        #    print("time taken - "+time.replace(time[:8], '')+"ms")
        #else:
        print("time taken - "+time+"s")

def monitor():
    ClearTERMINAL()
    puts(colored.blue('Currently Monitoring - @' + acc + ' // User ID = ' + str(id)))
    grablatestid()
    delay = 0.3
    if fast:    # fast mode = application mode, application mode = higher rate limit which means we can increase speed
        delay = 0.1
    while True:
        recent = str(api.GetUserTimeline(user_id=id, count=1, since_id=latestid, trim_user=True,
                                         exclude_replies=True, ))  # \/ this is some weird regex shit idk whats going on but it works, thanks ian lmao
        urltemp = re.findall(r"(?:(?:https?):\/\/|\b(?:[a-z\d]+\.))(?:(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))?\))+(?:\((?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))?\)|[^\s`!()\[\]{};:'\".,<>?Â«Â»â€œâ€â€˜â€™]))?",recent)
        checkurl = str(urltemp)                
        sys.stdout.write('\r O')
        
        if checkurl != "[]": # check if any urls have been picked up
            if len(urltemp) == 1:  # if theres only one url
                url = str(urltemp[0])  # wonky work around
                if "t.co" in url:       # double check that it's a url
                    start = time.process_time()   # timer  starts
                    print("Found t.co link! - " + url)
                    unshorten(url)  # gets unshortened
                    if "twitter.com" not in longurl:  # checks for twitter url, so it can ignore retweets and images
                        if "discord" not in longurl:  # checks for discord url
                            webbrowser.open(longurl)  # if it isn't a twitter/discord link, open in browser
                        else:                         # but if it is a discord link
                            if discjoiner:            # and the invite joiner is enabled
                                print("Discord Invite Detected")
                                inviteCode = longurl.replace(longurl[:27], '') # gets invite code
                                JoinInvite(inviteCode)  # runs joininvite and attempts to join discord.
                            else:
                                puts(colored.blue("Discord link was found but Discord joiner was disabled, ignoring..."))
                    else:
                        print("twitter link, ignored")
                    timea = time.process_time() - start
                    tweettime(latestid,timea)
                    print("Full URL: " + str(longurl))
                    grablatestid() # updates latest tweet, so it doesn't repeat the last found tweet.
            else:
                amtofurls = len(urltemp) # basically the same thing, but we repeat the unshorten process so we get all urls.
                counter = 0
                while counter != amtofurls: # loops until it has processed each link. 
                    url = urltemp[counter]
                    if "t.co" in url:
                        start = time.process_time()
                        print("Found t.co link! - " + url)
                        print("Unshortening...")
                        unshorten(url)
                        if "twitter.com" not in longurl:
                            if "discord" not in longurl:
                                webbrowser.open(longurl)
                            else:
                                if discjoiner:
                                    print("Discord Invite Detected")
                                    inviteCode = longurl.replace(longurl[:27], '')
                                    print(inviteCode)
                                    JoinInvite(inviteCode)
                                else:
                                    puts(colored.blue("Discord link was found but Discord joiner was disabled, ignoring..."))
                        else:
                            print("twitter link, ignored")
                        timea = time.process_time() - start
                        tweettime(recent,timea)
                        print("Full URL: " + str(longurl))
                        grablatestid()
                    counter += 1
        time.sleep(delay)
        sys.stdout.write('\r o')

def verifyUser(acc):  # verify user is real.
    global id
    check = api.GetUser(screen_name=acc) # checks if user exists
    if check != "": # if theres actually something
        puts(colored.green('Verified account'))
        id = check.id
        # follows account so if they go private it's calm
        try:
            api.CreateFriendship(user_id=id)
            puts(colored.green("Followed Account"))
        except Exception:
            print()
        print("Preparing... (this will take a couple of seconds)")
        return True

    else:
        puts(colored.red("Account doesn't exist, or API keys are incorrect\nIf you know this account is real, please check your keys"))
        return False


def ValidAccessToken(authToken):
    headers = {
        'authority': 'discordapp.com',
        'authorization': authToken,
        'accept-language': 'en-US',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.307 Chrome/78.0.3904.130 Electron/7.3.2 Safari/537.36',
        'accept': '/',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'referer': 'https://discordapp.com/store',
        'accept-encoding': 'gzip, deflate, br',
    }

    response = requests.get('https://discordapp.com/api/v6/users/@me/billing/payment-sources', headers=headers)
    return response.ok

def unshorten(url):
    global longurl
    session = requests.Session()
    response = session.head(url, allow_redirects=True) # opens link/follows it
    longurl = response.url 

def grablatestid():
    global latestid
    latest = str(api.GetUserTimeline(user_id=id, count=1, trim_user=True, exclude_replies=True))
    latestid = int(latest[11:].split(",")[0])  # thanks ian

def setdischeader(account, invitecode): # the actual invite joiner, dont know why this was split from JoinInvite
    headers = {
        'authority': 'discord.com',
        'accept-language': 'en-US',
        'authorization': account,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://discord.com/channels/@me',
    }

    params = (
        ('inputValue', '3Wh7Fa'),
        ('with_counts', 'true'),
    )

    response = requests.get(f'https://discord.com/api/v6/invites/{invitecode}', headers=headers, params=params)

    name = response.json()['guild']['name']
    id = response.json()['guild']['id']
    channel = response.json()['channel']['id']

    data = {"location": "Join a Server Modal", "location_guild_id": id, "location_channel_id": channel,
            "location_channel_type": 0}

    headers = {
        'authority': 'discord.com',
        'content-length': '0',
        'x-context-properties': base64.b64encode(json.dumps(data).encode('utf-8')),
        'authorization': account,
        'accept-language': 'en-US',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
        'accept': '*/*',
        'origin': 'https://discord.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://discord.com/channels/@me',
    }
    response = requests.post(f'https://discord.com/api/v6/invites/{invitecode}', headers=headers)
    if response.ok:
        print(f"Successfully Joined server: {name}")

def JoinInvite(inviteCode): # the invite handler
    accountsJoined = 0
    while accountsJoined != len(authkeys): # dynamic :)
        try:
            setdischeader(authkeys[accountsJoined], inviteCode)
        except KeyError:
            puts(colored.red('Failed to join server :(.'))
        accountsJoined += 1

def testapikey():
    try:
        y = api.VerifyCredentials()
    except Exception:
        puts(colored.red("Key isn't working. :("))
        return False
    if y != []:
        puts(colored.green("Key is working. :D"))
        return True

def testdiscord():
    counter = 0
    while counter != len(authkeys):
        result = ValidAccessToken(authkeys[counter])
        if result:
            puts(colored.green(str(counter+1)+" key is working :D"))
        if not result:
            puts(colored.red(str(counter+1)+" key is invalid :("))
        counter += 1
    puts(colored.cyan("Tests finished, returning to menu in 3 seconds..."))
    time.sleep(3)

def addapikeys(): # lol this is shit
    #retrieve
    puts(colored.blue("Enter consumer key"))
    consumer_key = input()

    puts(colored.blue("Enter consumer secret key"))
    consumer_secret = input()
    
    puts(colored.blue("Enter application access key"))
    access_token = input() 

    puts(colored.blue("Enter application secret key"))
    access_secret = input() 
    # add to database
    conn = sqlite3.connect('data.db')
    connection = conn.cursor()
    connection.execute("INSERT INTO data (CK, CSK, ATK, ATSK, DAK) VALUES (?, ?, ?, ?, ?)", (consumer_key, consumer_secret, access_token, access_secret, None))
    conn.commit()
    conn.close()
    print("Added to database")

def addauthkey(): 
    key = str(input()) 
    conn = sqlite3.connect('data.db')
    connection = conn.cursor()
    connection.execute("INSERT INTO data (CK, CSK, ATK, ATSK, DAK) VALUES (?, ?, ?, ?, ?)",  
                       (None, None, None, None, str(key)))
    conn.commit() 
    conn.close()

def getKEYSfromuser(): # split this into multiple functions
    global keyInputSuccess
    if keyInputSuccess == "":
        DisplayUserKeyInput = prompt(userInputKeys, style=style)
        json_str = json.dumps(DisplayUserKeyInput)
        resp = json.loads(json_str)
        consumer_key_array = resp['Consumer Key']
        consumer_secret_array = resp['Consumer Secret Key']
        access_token_array = resp['Access Token Key']
        access_secret_array = resp['Access Token Secret Key']
        tempapi = twitter.Api(consumer_key=consumer_key_array, consumer_secret=consumer_secret_array, access_token_key=access_token_array, access_token_secret=access_secret_array)
        try:
            y = tempapi.VerifyCredentials()
            if y != []:
                ClearTERMINAL()
                puts(colored.green("Successfully connected to twitter"))
                DisplayDiscordUserKeyInput = prompt(userInputDiscord, style=style)
                json_str1 = json.dumps(DisplayDiscordUserKeyInput)
                resp1 = json.loads(json_str1)
                auth = resp1['discord auth token']
                result = ValidAccessToken(auth)
                if result:
                    ClearTERMINAL()
                    puts(colored.green("Successfully connected to Discord"))
                    conn = sqlite3.connect('data.db')
                    connection = conn.cursor()
                    connection.execute("INSERT INTO data (CK, CSK, ATK, ATSK, DAK) VALUES (?, ?, ?, ?, ?)", (str(consumer_key_array), str(consumer_secret_array), str(access_token_array), str(access_secret_array), str(auth)))
                    conn.commit()
                    conn.close()
                else:
                    puts(colored.green("Failed to connect to Discord"))
                    keyInputSuccess = "1"
                    getKEYSfromuser()
        except:
            ClearTERMINAL()
            puts(colored.red("Failed to connect to twitter! "))

#def monitorpause(key): not functional, doesn't support mac/linux which is annoying. this needs to be done properly
#    if key == keyboard.Key.p:
#        input(puts(colored.blue("Monitor paused...\nPress space to continue")))

# most of this is for the cli
def TwitterUsername():
    working = False
    while not working:
        global ShowTwitterUsername
        global acc
        DisplayTwitterusername = prompt(ShowTwitterUsername, style=style)
        json_str = json.dumps(DisplayTwitterusername)  # dumps the json object into an element
        resp = json.loads(json_str)  # load the json to a string
        acc = resp['twitter username']
        working = verifyUser(acc)
        time.sleep(5)


def Settings():
    global MainSettings
    os.system('clear')
    f = Figlet(font='slant')
    puts(colored.green((f.renderText('nsTools'))))
    DisplayMainSettings = prompt(MainSettings, style=style)
    json_str = json.dumps(DisplayMainSettings)  # dumps the json object into an element
    resp = json.loads(json_str)  # load the json to a string
    if resp['Options'] == "Edit Keys":
        keysmenu()
    if resp['Options'] == "Back":
        ShowOptionScreen()
        

def Twitter():
    global TwitterOptions
    global discjoiner
    optionsselected = False
    while not optionsselected:
        os.system('clear')
        f = Figlet(font='slant')
        puts(colored.green((f.renderText('nsTool'))))
        DisplayTwitterOptions = prompt(TwitterOptions, style=style)
        json_str = json.dumps(DisplayTwitterOptions)  # dumps the json object into an element ['Open Links', 'Join Discord']
        resp = json.loads(json_str)  # load the json to a string
        ArrayOutput = resp['Options']
        if ArrayOutput == []:
            puts(colored.blue('Link Opener is on'))
            discjoiner = True
            optionsselected = True
            TwitterUsername()
            monitor()
        if ArrayOutput[0] == "Join Discord":
            print("Discord Joiner is on")
            discjoiner = True
            optionsselected = True
            TwitterUsername()
            monitor()


def ShowOptionScreen():
    global MainOptions  # make the main options variable global this contains the options that are shown to the user
    os.system('clear')
    f = Figlet(font='slant')
    puts(colored.green((f.renderText('nsTools'))))
    puts(colored.cyan(str(amtofapikeys)+" - sets of api keys loaded  |   "+str(amtofauthkeys)+" - discord auth keys loaded | "+str(status)+" - API connection"))
    DisplayMainOptions = prompt(MainOptions, style=style)  # displays the options
    json_str = json.dumps(DisplayMainOptions)  # dumps the json object into an element
    resp = json.loads(json_str)  # load the json to a string
    
    if resp['Options'] == "Settings":  # check what the user picked
        Settings()
    else:
        Twitter()


def keysmenu(): ################################################################################################### 
    global UpdateKeyOptions  # make the main options variable global this contains the options that are shown to the user
    os.system('clear')
    f = Figlet(font='slant')
    puts(colored.green((f.renderText('nsTools'))))
    DisplayKeyOptions = prompt(UpdateKeyOptions, style=style)  # displays the options
    json_str = json.dumps(DisplayKeyOptions)  # dumps the json object into an element
    resp = json.loads(json_str)  # load the json to a string
    if resp['Options'] == "add new twitter API key":  # check what the user picked
        addapikeys()
    if resp['Options'] == "Add new discord auth key":  # check what the user picked
        addauthkey()
    if resp['Options'] == "Test API keys":  # check what the user picked
        print("Which key set do you want to test?\nYou currently have "+amtofapikeys+" API Key(s)")
        key = input()
        testapikey(key)
    if resp['Options'] == "Test Discord Auth keys":  # check what the user picked
        testdiscord()
    if resp['Options'] == "Back":  # check what the user picked
        os.system('clear')
        f = Figlet(font='slant')
        puts(colored.green((f.renderText('nsTools'))))
        Settings()

def apilogin(a, b, c, d):
    global api
    global fast
    global UserModes
    global apiconnected
    global status
    DisplayUserModes = prompt(UserModes, style=style)
    json_str = json.dumps(DisplayUserModes)  # dumps the json object into an element
    resp = json.loads(json_str)  # load the json to a string
    userMode = resp['User Mode Options']
    attempts = 0
    puts(colored.blue("Press any key to manually select profile"))
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #                                                                            #
    #  on keystroke interrupt and allow user to select what set of keys to use.  #
    #                                                                            #
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    while not apiconnected:
        if attempts == 3:
            puts(colored.red("Theres an issue with your keys, Entering keys menu..."))
            time.sleep(5)
            keysmenu()

        if userMode == "help":
            print(
                "\nUser mode is generally good enough for most drops,\nit runs slightly slower than application mode but has the ability to monitor private accounts\nApplication mode is faster than user mode but cannot monitor private accounts.\nif you have no idea what this means, just go with user mode\n")
            input("press any key to contiue")
        if userMode == "User Mode":
            api = twitter.Api(consumer_key=a, consumer_secret=b, access_token_key=c, access_token_secret=d)
            apiconnected = testapikey()
            attempts+=1
        if userMode == "Application":
            api = twitter.Api(consumer_key=a, consumer_secret=b, access_token_key=c, access_token_secret=d)
            apiconnected = testapikey()
            fast = True
            attempts+=1
        if apiconnected:
            puts(colored.green("Connected to API"))
            status = "👍"
            time.sleep(2)


# this should work dynamically, in theory this can support infinite amounts of keys.
def getDatabase():
    global consumer_key_array
    global consumer_secret_array
    global access_token_array
    global access_secret_array
    global authkeys
    global amtofapikeys
    global amtofauthkeys
    result = "" #result of the function we return this at the end
    conn = sqlite3.connect('data.db')
    connection = conn.cursor()
    connection.execute('''CREATE TABLE IF NOT EXISTS "data" ("CK"   TEXT,"CSK"  TEXT,"ATK"  TEXT,"ATSK" TEXT,"DAK"  TEXT)''') # if table doesn't exist, make one
    conn.commit() # save
    apikeysindb = connection.execute('''SELECT COUNT(DISTINCT CSK) from data''') # gets the amount of api keys
    amtofapikeys = str(apikeysindb.fetchall())
    amtofapikeys = int(amtofapikeys.strip("[(,)]"))     
    authkeysindb = connection.execute('''SELECT COUNT(DISTINCT DAK) from data''')# gets the amount discord auth keys
    amtofauthkeys = str(authkeysindb.fetchall())
    amtofauthkeys = int(amtofauthkeys.strip("[(,)]"))   

    puts(colored.cyan(str(amtofapikeys)+" - sets of api keys loaded  |   "+str(amtofauthkeys)+" - discord auth keys loaded | "+str(status)+" - API connection "))
    connection.execute('''SELECT * FROM data''') # scans table to check if anything exists
    row = connection.fetchone()
    if row:    # if a row is exists
        selectedapikeys = 0
        selecteddiscordkeys = 0
        while selectedapikeys != amtofapikeys:
            connection.execute("SELECT * FROM data LIMIT 1 OFFSET ? ", (str(selectedapikeys),) )
            row = connection.fetchone()
            consumer_key_array.append(row[0])  # load keys into table
            consumer_secret_array.append(row[1])
            access_token_array.append(row[2])
            access_secret_array.append(row[3])
            selectedapikeys += 1
        while selecteddiscordkeys != amtofauthkeys:
            connection.execute("SELECT * FROM data LIMIT 1 OFFSET ? ", (str(selecteddiscordkeys),) )
            row = connection.fetchone()
            authkeys.append(row[4])
            selecteddiscordkeys += 1
        conn.close()
        result = "login"
        return result
    else:
        puts(colored.red("We cant seem to find your keys please enter them below:"))
        conn.close()
        result = "getKeys"
        return result


def checkDatabaseFile():  
    try:
        os.stat("data.db")
    except:
        file = open("data.db", "w") 


def ClearTERMINAL(): ## OS Detection included
    if ostype == "Windows":
        os.system('cls')
    if ostype == "Linux" or "Darwin":
        os.system('clear')
    f = Figlet(font='slant')  #
    puts(colored.green((f.renderText('nsTools'))))


while __name__ == '__main__':
    ClearTERMINAL()# clears the terminal and adds the logo to the top
    checkDatabaseFile()# checks if the database exists if not it creates one
    if not apiconnected:
        getdatabaseresult = getDatabase()
        if getdatabaseresult == "getKeys":
            getKEYSfromuser()
            apilogin(consumer_key_array[0], consumer_secret_array[0], access_token_array[0], access_secret_array[0])
        else:
            apilogin(consumer_key_array[0], consumer_secret_array[0], access_token_array[0], access_secret_array[0])
    ShowOptionScreen()# shows menu