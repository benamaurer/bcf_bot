#---------------------------------------------------------------------------------------------------------------
#Importing packages
import discord
import datetime
import time
from python_vlookup import python_vlookup as vlookup
from fuzzywuzzy import process
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import os


#---------------------------------------------------------------------------------------------------------------
#Loading information from reference files

#Obtaining token/guild ID
def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()


#Reading bot-specific data file and returning data=[return value]
def read_bcf(data):
    with open("bcf_data.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            if str(data) in str(line.strip()):
                return (str(line.split(" = ")[1].strip()))


# def write_bcf(data, new_value):
#     with open("bcf_data_test.txt", "w+")
#         lines = f.readlines()
#         for line in lines:
#             if str(data) in str(line.strip()):



#Prints information to the console including: sender, command run, and time
def log_sender(command, sender):
    print("---" + str(sender) + " ran (" + command + ") at " + str(time.strftime('%H:%M:%S_%m/%d/%y')) + "---")


#---------------------------------------------------------------------------------------------------------------
#Initial variable declaration


books = ["Genesis", "Exodous", "Leviticus", "Numbers", "Deutoronomy", "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job", "Psalm", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"]
line_break = "-------------------------------------------------------------------------\n "
token = read_token()
client = discord.Client()
guild_ID = int(read_bcf("guild_ID"))


#---------------------------------------------------------------------------------------------------------------
#Function list


# get_next_sunday():
# next_speaker():
# find_verse(message):
# soup_get_verse(verse_link):
# get_search_term(message):
# web_content(site_link):
# get_da_flock(message):
# book_verify(verify):
# log_sender(command, sender):


#---------------------------------------------------------------------------------------------------------------
#Functions


#Returns the date for the next sunday in mm/dd/yy format
def get_next_sunday():
    current_date = datetime.date.today()
    week_day = current_date.weekday()
    days_until_sunday = 6 - week_day
    next_sunday = current_date + datetime.timedelta(days=days_until_sunday)
    return next_sunday.strftime('%m/%d/%Y')


#Returning speaker using vlookup to grab from speaker_list_20.csv, returns special phrases for open or brothers meetings
    #Also calles get_next_sunday() to use for vlookup date
def next_speaker():
    speaker = vlookup.vlookup(str(get_next_sunday()),'speaker_list_20.csv',2)
    if speaker.find("&") != -1:
        return " there is an open meeting with brother's meeting to follow"
    elif speader.find("Topic") != -1:
        return " there is a topic meeting."
    elif speaker.find("Open") != -1:
        return " there is an open meeting."
    else:
        return (" " + str(speaker) + " is speaking.")


#Receives _verse command and calls get_search_term and soup_verse to build string containing verse(s) and website link
def find_verse(message):

    #Running get_search_term(message) with query to match to possible books
    term = get_search_term(message)

    #Printing the matched book from query to the console
    print("Book match: " + term)

    #Tries to perform vlookup on matched book to get site link term
    try:
        book_site = vlookup.vlookup(str(term), 'full_book.csv', 2)

    except:
        print("unable to complete vlookup")

    #Isolates the last space separated string in message
    verse_numbers = "".join(message.split()[-1])

    #Replaces colon with period to use in site link
    verse_site = verse_numbers.replace(":", ".")

    #Printing chapter number to console
    isolate_chapter = verse_numbers.split(":")[0]
    print("Chapter: " + isolate_chapter)

    #Printing verse number to console
    isolate_verse = verse_numbers.split(":")[1]
    print("Verse(s): " + isolate_verse)

    #Building book/chapter reference to compile in link
    reference_site = (book_site + "." + isolate_chapter)

    #Building link to use for verse range searches, contains the entire book
    book_link = ("https://www.bible.com/bible/100/" + reference_site + ".NASB1995")

    #Building link to use for individual verse lookups
    verse_link = ("https://www.bible.com/bible/100/" + book_site + "." + verse_site + ".NASB1995")

    #Getting verse(s) using bs4 and returning as formatted strings
    soup_verse = soup_get_verse(verse_link)

    #Returning exception message if no book match was found
    if term == None:
        return "No verse found, please try searching again."

    #Returning verse(s)
    if verse_numbers.find("-") != -1:
        return ("\u200B\n" + "     **" + term + " " + verse_numbers + "**  *(NASB)*\n\n" + soup_verse + "\n" + book_link)
    try:
        return ("\u200B\n" + term + " " + verse_numbers + "   **" + soup_verse + "**" + "\n\n" + book_link)
    except:
        print("Verse not found.")
        return ("Unable to retrieve individual verse.\n" + book_link)


#Returns string containing verse(s) passed in
def soup_get_verse(verse_link):

    #For verse ranges (which must contain a "-") returns all verses in range or exceptions
    if verse_link.find("-") != -1:
        try:
            #Obtaining verse range in x-y format
            removed_nasb = verse_link.replace(".NASB1995","")
            isolated_verse_group = removed_nasb.split(".")[-1]

            #Retrieving site content after formatting link above
            book_link = verse_link.replace((isolated_verse_group + "."), "")
            soup = web_content(book_link)

            #Creating list of verses from verse range
            verse_list = range(int(isolated_verse_group.split("-")[0]), (int(isolated_verse_group.split("-")[1]) + 1))

            #Creating tags from verse_list for bs4 to use
            tags = ["verse v" + str(verse) for verse in verse_list]

            #Declares all_verses to add each verse as new string in for loop
            all_verses = ""

            #Loops on tags provided corresponding to each verse
            for tag in tags:
                raw_verse = soup.find(name='span', attrs={"class":tag}).text.strip()
                if len(tag) == 7:
                    raw_verse = raw_verse[0:]
                if len(tag) == 8:
                    raw_verse = raw_verse[1:]
                if len(tag) == 9:
                    raw_verse = raw_verse[2:]
                final_individual_verse = ("**" + str(tag.replace("verse v","")) + ".** " + str(raw_verse) + "\n")
                all_verses = all_verses + final_individual_verse
            return all_verses
        except:
            print("Verse range look up failed, returned the entire book link below (check that all verses exist?)")
            return "Verse range look up failed, returned the entire book link below (check that all verses exist?)\n"

    #Returns individual verse or exception
    else:
        try:
            soup = web_content(verse_link)
            for div in soup.find_all(name='div', attrs='near-black lh-copy f3-m'):
                verse_text = div.text.strip()
                return verse_text
        except:
            print("unable to grab single verse")
            return


#Performs fuzzy search on input, returning closes book matched from list books[] above
def get_search_term(message):
    if message.find("song") != -1 or message.find("solomon") != -1:
        return "Song of Solomon"

    #removes message command substring and splits the remaining string using spaces as delimiters
    message_only = message.replace("_verse ", "")
    print("Search request: " + message_only)
    spaces = message_only.count(" ")

    # Searches for books which are not preceeded by a number (ex: Genesis)
    def search_1(message_only):
        book_searched = " ".join(message_only.split()[:1])
        match_tuple = (process.extractOne(str(book_searched), books, score_cutoff=80))
        (matched_book, match_value) = match_tuple
        verify = matched_book.lower().find(book_searched.lower())
        if verify == 0:
            return matched_book
        else:
            return


    #Searches for books which are preceeded by a number (ex: 1 Kings)
    def search_2(message_only):
        book_searched = " ".join(message_only.split()[:2])
        match_tuple = (process.extractOne(str(book_searched), books, score_cutoff=80))
        (matched_book, match_value) = match_tuple
        verify = matched_book.lower().find(book_searched.lower())
        if verify == 0:
            return matched_book
        else:
            return

    #Tries getting correct book with 2 spaces
    if spaces == 1:
        return search_1(message_only)


    #Tries getting correct book with 3 spaces
    if spaces == 2:
        return search_2(message_only)


#Returns BeautifulSoup content from link passed in
def web_content(site_link):
    content = Request(site_link, headers={"User-Agent": "Mozilla/5.0"})
    read_content = urlopen(content).read()
    soup = BeautifulSoup(read_content, "html.parser")
    return soup


#Returns text of a song from the "Little FLock" hymnal, uses web_content
def get_da_flock(message):
    message_only = message.replace("_hymn ", "")

    #Alters hymn number if in the appendix to correct for site mapping of hymns
    if message_only.find("A") != -1:
        replace_A = message_only.replace("A","")
        song_link = ("https://bibletruthpublishers.com/lkh" + str(int(replace_A) + 341) +  "LFHB")
    else:
        song_link = ("https://bibletruthpublishers.com/lkh" + str(message_only) + "LFHB")

    print(message_only)
    print(song_link)

    #Retrieving web content from song_link
    soup = web_content(song_link)

    #Declaring full_hymn to add strings to in loop below
    full_hymn = ""

    #Looping on all hymn lines found in soup
    try:
        for span in soup.find_all(name='span', attrs={"id":"ctl00_ctl00_cphLibSiteMasterPgMainContent_cphLibContentPageBody_ctl00_lblTitle"}):
            hymn_title = span.text.strip()
            title_line = ("**" + hymn_title + "**   ")
            print(hymn_title)
            break
        for span in soup.find_all(name='span', attrs={"id":"ctl00_ctl00_cphLibSiteMasterPgMainContent_cphLibContentPageBody_ctl00_lblMeter"}):
            meter = span.text.strip()
            title_line = (title_line + "*" + meter + "*\n")
            print(meter)
            break
        for div in soup.find_all(name='div', attrs='stanza-line-cont'):
            verse_text = div.text.strip()
            full_hymn = full_hymn + verse_text + "\n"
        full_hymn = os.linesep.join([s for s in full_hymn.splitlines() if s.strip()])
        return "\u200B\n" + title_line + "\n" + full_hymn + "\n\n" + song_link
    except:
        print("unable to grab hymn")


#Checks that fuzzy selected book is in the original discord message
def book_verify(verify):
    if verify == -1:
        return ("matched book incorrect, " + str(verify))
    if verify == 0:
        return ("matched book correct")


#WIP - returns link for "Sing Joyfully" hymnal, will attempt to pull text etc. in the future
def get_song(song_request):
    return "Click on this link for Sing Joyfully songs: https://hymnary.org/hymnal/SJ1989"


#Notifies console that script will respond to discord messages
print("startup successful.")


#---------------------------------------------------------------------------------------------------------------
#Discord event handler


@client.event
async def on_message(message):
    id = client.get_guild(guild_ID)
    if message.guild.id != guild_ID:
        return

    #Prevents bot from responding to its own messages by checking that it is not the message author
    if str(message.author) == "maumaubeepboop#5172":
        return

#    channels = ["<add a channel>"]
#    if message.content.find("_help") != -1
#        await message.channel.send


    if message.content.find("_help") != -1:
         try:
            log_sender(message.content, message.author)
            await message.channel.send("""
            Here is a list of the commands I can run (to run the command you must type underscore then the word):
                _help - this command, shows a list of working commands.
                _verse - looks up the requested verse and link to the book online (ex: _verse Revelation 22:21)
                _hymn - looks up the requested little flock hymn (use an "A" after a song to denote appendix) Ex: _hymn 32A
                _song - looks up the requested Sing Joyfully song (currently WIP, just links to the site for now) 
                _speaker - fetches the speaker for next sunday's meeting
                _livestream - fetches the youtube link where the livestreams are shown""")
            print(line_break)
         except:
            print("Unable to complete " + message.content + ".")


    if message.content.find("_beep") != -1:
        try:
            log_sender(message.content, message.author)
            await message.channel.send("boop")
            print(line_break)
        except:
            print("Unable to complete " + message.content + ".")


    if message.content.find("_speaker") != -1:
        try:
            log_sender(message.content, message.author)

            await message.channel.send("On Sunday, " + str(get_next_sunday() + "," + str(next_speaker())))
            await message.channel.send("Click here for the full speaker schedule for 2020: " + read_bcf("gdoc_speakers"))
            print(line_break)
        except:
            print("Unable to complete " + message.content + ".")


    if message.content.find("_verse") != -1:
        try:
            log_sender(message.content, message.author)
            message_verse = find_verse(message.content)

            message_lines = message_verse.split("\n")

            message_partial = ""

            for line in message_lines:
                if len(message_partial) + len(line) < 2000:
                    message_partial = message_partial + line + "\n"
                else:
                    await message.channel.send(message_partial)
                    message_partial = ""
            await message.channel.send(message_partial)

            print(line_break)
        except:
            print("Unable to complete " + message.content + ".")


    if message.content.find("_livestream") != -1:
        try:
            log_sender(message.content, message.author)
            await message.channel.send("Click on this link to go to the youtube livestream page: " + read_bcf("livestream_link"))
            print(line_break)
        except:
            print("Unable to complete " + message.content + ".")


    if message.content.find("_hymn") != -1:
        try:
            log_sender(message.content, message.author)
            await message.channel.send(get_da_flock(message.content))
            print(line_break)
        except:
            print("Unable to complete " + message.content + ".")


    if message.content.find("_song") != -1:
        try:
            log_sender(message.content, message.author)
            await message.channel.send(get_song(message.content))
            print(line_break)
        except:
            print("Unable to complete " + message.content + ".")


    # if message.content.find("_wed") != -1:
    #     try:
    #         log_sender(message.content, message.author)
    #         await message.channel.send(update_wed(message.content))
    #         print(line_break)
    #     except:

client.run(token)
