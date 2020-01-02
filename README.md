# Reddit Swim Conversion Bot
###### Program in action can be found [here](https://www.reddit.com/user/SwimConverter/)
## [Timeconverter.py](python/timeconverter.py) explained
In swimming, times only make sense when given in context with the course. This means that a time in one course means nothing in another course, that is why time converters are useful. **[Timeconverter.py](python/timeconverter.py) uses [USA Swimming's](https://support.teamunify.com/en/articles/260-course-conversion-of-timesfactoring-of-times) time conversion standards**. There are three recognized courses: **short course yards, short course meters, and long course meters**. Courses are commonly abbreviated as: **scy**, **scm**, and **lcm**. Timeconverter.py is a fully functioning time converter, meaning it can perform all valid conversions from and course to any course. To use timeconvert, import timeconvert from timeconvert.py and pass it the following parameters: **stroke**, **distance**, **course**, **tocourse**, **time**. Stroke must be any valid stroke in it's abbreviated form: **fly**, **back**, **breast**, **free**, and **im**. Distance must be a valid distance: **50**, **100**, **200**, **400**, **500**, **800**, **1000**, **1500**, and **1650**. Courses must be abbreviated. The following are valid time formats: **MM:SS.HH**, **MM:SS**, and **SS.HH**. Timeconvert will return a time in either MM:SS.HH or SS.HH format.
## [Swimconverterbot.py](python/swimconverterbot.py) explained
After creating a Reddit instance and establishing a MySql connection, this program will look through all comments posted in r/swimming for the keyword "***!timeconvert***". *Nothing in swimconverter.py is case sensitive*. Once a comment is found with the designated keyword, the program will look through the mySql database to ensure the comment hasn't already been responded to. If it has, the program will log to the console that it has already responded and then continue to look for more comments. If the comment is unique, the program looks through the comment for all the necessary parameters. If a parameter cannot be found, it is assigned None type so the program knows not to convert the comment. Once all of the parameters are found, the program will call timeconvert which returns the conversion. If the comment fails to post due to a praw api exception, the program will wait the designated time and try again. Once the comment is posted, the comment id is logged to the MySQL database to ensure it isn't responded to again.
## Further plans for this project
1. Proper error handling in timeconvert.py
2. Auto-detect comments that need to be converted
   - Look for times in all posts/comments
   - Find region where comment was posted (meters or yards)
   - Figure out whether a time was swam in short course or long course
 3. Statistics on times
    - Log all times converted for each event
    - Every month/year, report the average time in each event (compare to previous month/year)
