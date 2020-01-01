import re

def timeconvert(stroke, distance, course, tocourse, time):
    # Setting the conversion factors
    hsecs = gethseconds(time)
    ffactor = getffactor(stroke, distance, course, tocourse)
    fincre = getincre(stroke, distance, course, tocourse)

    # Standard conversions, divided by 100 to get seconds
    if course == "scy" and (tocourse == "lcm" or tocourse == "scm"):
        seconds = (hsecs * ffactor + fincre) / 100
    if course == "lcm" and (tocourse == "scy" or tocourse == "scm"):
        seconds = ((hsecs - fincre) / ffactor) / 100
    if course == "scm" and tocourse == "scy":
        seconds = (hsecs / ffactor) / 100
    if course == "scm" and tocourse == "lcm":
        seconds = (hsecs + fincre) / 100

    # format the time to MM:SS.HH
    convertedtime = formattime(seconds)

    return convertedtime

# converts a time from seconds to MM:SS.HH
def formattime(seconds):
    mm = int(seconds / 60)
    ss = int(seconds % 60)
    hh = str(seconds % 1)

    hh = re.search("\.\d{1,3}", hh).group()[1:3]

    # if format is 1.1, change to 1.10
    if len(hh) < 2:
        hh += "0"

    #if seconds in a single digit and it doesn't have minutes, add a 0. (Will not print 04.23, instead 4.23)
    if mm is not 0 and len(str(ss)) < 2:
        ss = "0" + str(ss)

    # if there are no minutes, return seconds followed by hundredths
    if mm == 0:
        return str(ss) + "." + hh

    # Returns in MM:SS.HH format
    else:
        return str(mm) + ":" + str(ss) + "." + str(hh)

# converts a time from MM:SS.HH format to hundredths of a second
def gethseconds(time):
    #If minutes are provided, set minutes and seconds
    if re.search("\d{1,2}:", time) is not None:
        minutes = re.search("\d{1,2}:", time).group()[:-1]
        seconds = re.search(":\d{1,2}", time).group()[1:]
    #If minutes are not provided, set minutes to 0 and set seconds
    else:
        minutes = 0
        seconds = re.search("\d{1,2}\.", time).group()[:-1]

    # If hundredths is not set (ex: 1:48)
    if re.search("\.\d{1,2}", time) is None:
        return (float(minutes) * 60 * 100) + (float(seconds) * 100)

    #If hundreths is .1, it is changed to .10
    if (len(re.search("\.\d{1,2}", time).group()[1:])) < 2:
        hundredths = int((re.search("\.\d", time).group()[1:])) * 10

    #Set hundredths to the 2 digits following a period
    else:
        hundredths = re.search("\.\d\d", time).group()[1:]

    #Convert minutes and seconds to hundredths
    return (float(minutes) * 60 * 100) + (float(seconds) * 100) + float(hundredths)

# fFactor Conversion Cases
# LCM to SCM -> 1.0
# LCM to/from SCY distance 400/800 to/from 500/1000 -> 0.8925
# LCM to/from SCY distance 1500 to/from 1650 -> 1.02
# All Other Cases -> 1.11
def getffactor(stroke, distance, course, tocourse):
    if course == "lcm" and tocourse == "scm":
        return 1.0
    if ((course == "lcm" and tocourse == "scy") or (course == "scy" and tocourse == "lcm")) and (
            400 <= distance <= 1000) and stroke != "im":
        return .8925
    if ((course == "scy" and tocourse == "lcm") or (course == "lcm" and tocourse == "scy")) and distance >= 1500:
        return 1.02

    else:
        return 1.11

# default values for each stroke
def increhelper(stroke):
    if stroke == "fly":
        return 70
    if stroke == "back":
        return 60
    if stroke == "breast":
        return 100
    if stroke == "free":
        return 80
    if stroke == "im":
        return 80

# Calculates the fIncre value
def getincre(stroke, distance, course, tocourse):
    # Stroke is Medley and LCM to/from SCY distance 400 to/from 500
    if stroke == "im" and ((course == "lcm" and tocourse == "scy") or (course == "scy" and tocourse == "lcm")) and (
            distance == 400 or distance == 500):
        return 640
    # Stroke is not Medley and LCM to/from SCY distance > 200
    if stroke != "im" and (
            (course == "lcm" and tocourse == "scy") or (course == "scy" and tocourse == "lcm")) and distance > 200:
        return 0
    # SCY to/from SCM
    if (course == "scy" and tocourse == "scm") or (course == "scm" and tocourse == "scy"):
        return 0

    # LCM to/from SCM Distance
    # Distance  fincre
    # 500/400	640
    # 800/1000	1280
    # 1500/1650	2400
    if (course == "lcm" and tocourse == "scm") or (course == "scm" and tocourse == "lcm") and distance >= 400:
        if distance == 400 or distance == 500:
            return 640
        if distance == 800 or distance == 1000:
            return 1280
        if distance == 1500 or distance == 1650:
            return 2400

    # All other cases
    # Distance fincre
    # 50	   incre
    # 100	   2*incre
    # 200	   4*incre
    # 400	   8*incre
    # Others   0
    if distance == 50:
        return increhelper(stroke)
    if distance == 100:
        return 2 * increhelper(stroke)
    if distance == 200:
        return 4 * increhelper(stroke)
    if distance == 400:
        return 8 * increhelper(stroke)
    else:
        return 0
