import datetime
import logging


class TimeFormat():
    '''Helper class used for different kind of time format conversions e.g.
    dateTime to String or DateTime to date'''

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("TimeFormat instantiation started")

        # Get current date and time
        self.currentTime = datetime.datetime.now()

        self.logger.info("TimeFormat instantiated")

    def getDateTime(self):
        '''Get current date and time as DateTime.DateTime object'''
        return self.currentTime

    def getDateTimeAsString(self):
        '''Get current date and time in format of YYYY-MM-DD HH-MM-SS'''
        return self.currentTime.strftime("%Y-%m-%d %H:%M:%S")

    def getNumberOfTheDay(self):
        '''Get number of the week day 1 monday - 7 sunday'''
        # Get number of the day from DateTime obejct.
        # In Python, first day of the week is 0
        numberOfTheDay = datetime.date.weekday(self.currentTime)
        # Add 1 to day so it is easier to compare. Now instead of Monday
        # being 0, Monday is 1 and therefore Sunday is 7
        return numberOfTheDay + 1

    def getTodayAsString(self):
        '''Get current date as string e.g. 2018-01-01'''
        return datetime.date.today().strftime("%Y-%m-%d")

    def getDateTimeStringFromDateTimeObject(self, dateTimeObject, form):
        '''Get date time string from dateTime object in form of passed in
        format e.g. 2018-01-01'''
        return dateTimeObject.strftime(form)
