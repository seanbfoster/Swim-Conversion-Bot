import praw
import re
import time
import mysql.connector
from timeconvert import timeconvert

# Initialize Reddit instance
reddit = praw.Reddit(client_id='redacted',
                     client_secret='redacted',
                     user_agent='my user agent',
                     username='SwimConverter',
                     password='redacted')

# Specificy the subreddit for the Reddit instance
subreddit = reddit.subreddit('swimming')

# Phrase to trigger the bot
keyphrase = '!timeconvert'

# Finds the time in the comment
def findtime(comment):
    # Will find MM:SS.HH, SS.HH, or MM:SS
    time = re.findall("(\d{1,2}\:\d{2}\.\d{1,2}|\d{1,2}\.\d{1,2}|\d{1,2}:\d{1,2})", comment)

    # Check to see if more than one time is found
    if len(time) != 1:
        return None

    # Return the time found
    else:
        return time[0]

# Finds the event in the comment
def findevent(comment):
    # Will find every valid event
    event = re.search("(([1,2,4,5,8]|15|16)(0{1,3})|1650) (fly|butterfly|back|backstroke|breast|breastroke|breaststroke|free|freestyle|im|individual medley)", comment)
    # If no event is found, return none
    if event == None:
        return None
    # Return event
    else:
        return event

# Takes the event and uses regex to find any valid distance
def finddistance(event):
    distance = re.search("(([1,2,4,5,8]|15|16)(0{1,3})|1650)", event.group())
    return distance.group()

# Takes the event and uses regex to find any valid stroke
def findstroke(event):
    stroke = re.search("(fly|butterfly|back|backstroke|breast|breastroke|breaststroke|free|freestyle|im|individual medley)", event.group())
    return simplifystroke(stroke.group())

# Format the stroke so timeconvert can read it
def simplifystroke(stroke):
    if stroke == "butterfly":
        return "fly"
    if stroke == "backstroke":
        return "back"
    if stroke == "breastroke" or stroke == "breaststroke":
        return "breast"
    if stroke == "freestyle":
        return "free"
    if stroke == "individual medley":
        return "im"
    else:
        return stroke

# Finds any valid courses in the comments
def findcourse(comment):
    return re.findall("(scy|short course yards|scm|short course meters|lcm|long course meters)", comment)

# Takes a list of courses and returns the first one
def findfromcourse(courses):
    course = courses[0]
    fromcourse = simplifycourse(course)
    return fromcourse

# Takes a list of courses and returns the second one
def findtocourse(courses):
    course = courses[1]
    tocourse = simplifycourse(course)
    return tocourse

# Format the course so timeconvert can read it
def simplifycourse(course):
    if course == "short course yards":
        return "scy"
    if course == "short course meters":
        return "scm"
    if course == "long course meters":
        return "lcm"
    else:
        return course

# Takes a comment and tries to find all relavent data.
# If found, it converts the time and generates a comment
def generatecomment(comment):
    # Not case sensitive
    comment = comment.lower()

    time = findtime(comment)
    event = findevent(comment)

    #If no event is found, Initialize distance and stroke to None
    if event != None:
        distance = finddistance(event)
        stroke = findstroke(event)
    else:
        distance = None
        stroke = None


    courses = findcourse(comment)

    # if 2 courses are found, Initialize fromcourse and tocourse
    if len(courses) == 2:
        fromcourse = findfromcourse(courses)
        tocourse = findtocourse(courses)
        # Check to see if the courses are the same, as this is not valid
        if fromcourse == tocourse:
            fromcourse = None
            tocourse = None

    # Initialize fromcourse and tocourse to none if 2 courses weren't found in comment
    else:
        fromcourse = None
        tocourse = None
    print("time: " + str(time) + "\ndistance: " + str(distance) + "\nstroke: " + str(stroke) + "\nfromcourse: " + str(fromcourse) + "\ntocourse: " + str(tocourse))
    dataisgood = gooddata(time, distance, stroke, fromcourse, tocourse)

    # If valid data, generate a comment with information
    if dataisgood == True:
        comment = (time + " in " + tocourse + " is " + timeconvert(str(stroke), int(distance), str(fromcourse), str(tocourse), str(time)) + "\n\n[More Information](https://www.reddit.com/user/SwimConverter/comments/ef4ai2/rswimming_time_converter_bot_timeconvert/)")
    # Invalid data, generate an error message
    else:
        comment = "Error: Invalid data provided, check [this](https://www.reddit.com/user/SwimConverter/comments/ef4ai2/rswimming_time_converter_bot_timeconvert/) out for help"

    return comment

# Check to see if all data in initialized
def gooddata(time, distance, stroke, course, tocourse):
    if time == None:
        return False
    if distance == None:
        return False
    if stroke == None:
        return False
    if course == None:
        return False
    if tocourse == None:
        return False
    else:
        return True

# MySql configuration/connection
def sqlconnection():
    return mysql.connector.connect(user='root', passwd='',
                              host='localhost',
                              database='swimconvert')

# Check if id is already used (sql database)
def uniqueid(id):
    print("in uniqueid")
    sql = sqlconnection()
    mycursor = sql.cursor()
    grab = "SELECT * FROM comments WHERE comment_id=\"" + id + "\""
    mycursor.execute(grab)
    result = mycursor.fetchall()
    mycursor.close()
    sql.close()
    if not result:
        return True
    else:
        return False

# Main loop. If keyphrase is found in a comment, check if comment id
# is already been responded to (stored in sql database). If id is unique
# try to respond to the comment. If succesful, log the comment id to the
# sql database and log it to the console. Except an API exception and try
# to figure out how long the bot should wait before it tries to respond again.
def main():
    while True:
        for comment in subreddit.stream.comments():
            if keyphrase in comment.body:
                checkid = uniqueid(comment.id)
                if checkid == True:
                    while True:
                        try:
                            botresponse = generatecomment(comment.body)
                            comment.reply(botresponse)
                            sql = sqlconnection()
                            mycursor = sql.cursor()
                            mycursor.execute("INSERT INTO comments (comment_id) VALUES (\"" + comment.id + "\")")
                            sql.commit()
                            mycursor.close()
                            sql.close()
                            print("Responded to comment (id: " + comment.id + ")")
                        except praw.exceptions.APIException as e:
                            print("Error: " + str(e))
                            print("Waiting 10 minutes and will retry again")
                            time.sleep(600)
                        except prawcore.exceptions.ServerError as e:
                            print("Error: " + str(e) + "\nWaiting 10 minutes")
                            time.sleep(600)
                        break
                else:
                    print("Already responded to this comment (id: " + comment.id + ")")

if __name__== "__main__":
    main()
