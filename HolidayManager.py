import datetime
import json
from tokenize import Name
from unicodedata import name
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from config import menuTextLoc, jsonFileLoc

@dataclass
class Holiday:
    name: str
    date: datetime

    def __init__(self, name, date):
        self.__name = name
        self.__date = date 

    def __str__(self):
        return f'{self.__name} ({self.__date})'

    def __repr__(self):
        return f'{self.__name} ({self.__date})'

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, newName):
        self.__name = newName

    @name.deleter
    def name(self):
        del self.__name

    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, newDate):
        self.__date = newDate

    @date.deleter
    def date(self):
        del self.__date

class HolidayList:
    def __init__(self):
       self.innerHolidays = []

    def addHoliday(self, holidayObj, name, date, autoLoad):
        holidayType = type(holidayObj)
        if holidayType == Holiday:
            self.innerHolidays.append(holidayObj)
            if autoLoad == False:
                print('\nSuccess:')
                print(f'{name} ({date}) has been added to the holiday list.')
        else:
            print('Error: Not a holiday object')

    def findHoliday(self, HolidayName):
        for a in self.innerHolidays:
            if a.name == HolidayName:
                print(a)

    def removeHoliday(self, HolidayName, Date):
        found = False
        for a in self.innerHolidays:
            if a.name == HolidayName and a.date == Date:
                found = True
                self.innerHolidays.remove(a)
                print(f'\nSuccess:\n{HolidayName} has been removed from the list.')
        if found == False:
            print(f'\nError:\n{HolidayName} not found.')

    def read_json(self, filelocation):
        with open(filelocation) as jsonFile:
            jsonHolidays = json.load(jsonFile)
        holidaysDictList = jsonHolidays['holidays']
        for a in holidaysDictList:
            holiday = Holiday(a['name'],a['date'])
            holidayList.addHoliday(holiday,a['name'],a['date'],True)

    def save_to_json(self):
        holidayDictList = []
        for a in self.innerHolidays:
            b = {}
            b['name'] = a.name
            b['date'] = a.date
            holidayDictList.append(b)

        with open('Holiday_List.json','w') as file:
            json.dump(holidayDictList, file, indent = 2)

    def scrapeHolidays(self,url,year):
        html = getHTML(url)
        soup = BeautifulSoup(html,'html.parser')
        table = soup.find('table',attrs = {'class':'table--holidaycountry'})
        holidayNames = []
        holidayDates = []
        holidays = []

        for row in table.find_all_next('td',attrs = {'class':''}):
            a = str(row)
            if '</a>' in a:
                b = a.split('</a>')[0]
                c = b.split('\">')[1]
                holidayNames.append(c)

        for row in table.find_all_next('th',attrs = {'class':'nw'}):
            a = str(row)
            b = a.split('>')[1]
            c = b.split('<')[0]
            month = c.split(' ')[0]
            day = c.split(' ')[1]
            monthNum = datetime.datetime.strptime(month, '%b').month

            if len(str(monthNum)) == 1:
                monthNum = '0' + str(monthNum)
            else:
                monthNum = str(monthNum)

            if len(day) == 1:
                day = '0' + day

            d = f'{year}-{monthNum}-{day}'
            holidayDates.append(d)

        num = 0
        for a in range(len(holidayDates)):
            holiday = {}
            holiday['name'] = holidayNames[num]
            holiday['date'] = holidayDates[num]
            holidays.append(holiday)
            num += 1

        for a in holidays:
            b = self.duplicateHoliday(a['name'], a['date'])
            if b == False:
                newHoliday = Holiday(a['name'], a['date'])
                self.addHoliday(newHoliday, a['name'], a['date'], True)    

    def duplicateHoliday(self, holidayName, holidayDate):
        duplicate = False
        for a in self.innerHolidays:
            if a.name == holidayName and a.date == holidayDate:
                duplicate = True
        return duplicate

    def numHolidays(self):
        return len(self.innerHolidays)

    def filter_holidays_by_week(self, year, week_number):
        templist = []
        for a in self.innerHolidays:
            b = str(a.date)
            c = b.split('-')
            d = {}
            d['name'] = a.name
            Hyear = int(c[0])
            Hmonth = int(c[1])
            Hday = int(c[2])
            d['date'] = datetime.datetime(Hyear,Hmonth,Hday)
            templist.append(d)

        holidays = filter(lambda x: x['date'].isocalendar().year == int(year) and x['date'].isocalendar().week == int(week_number), templist)
        
        self.displayHolidaysInWeek(holidays)

    def displayHolidaysInWeek(self, holidayList):
        for a in holidayList:
            b = a['date']
            if len(str(b.month)) == 1:
                month = f'0{b.month}'
            else:
                month = b.month
            if len(str(b.day)) == 1:
                day = f'0{b.day}'
            else:
                day = b.day
            c = f'{b.year}-{month}-{day}'
            a = Holiday(a['name'],c)
            print(a)

    def viewCurrentWeek(self):
        today = datetime.date.today()
        currentYear, currentWeek, currentDay = today.isocalendar()
        holidayList.filter_holidays_by_week(currentYear,currentWeek)

changes = True
validDate = False
urlList = [
{'url':'https://www.timeanddate.com/holidays/us/2020', 'year':'2020'},
{'url':'https://www.timeanddate.com/holidays/us/2021', 'year':'2021'},
{'url':'https://www.timeanddate.com/holidays/us/2022', 'year':'2022'},
{'url':'https://www.timeanddate.com/holidays/us/2023', 'year':'2023'},
{'url':'https://www.timeanddate.com/holidays/us/2024', 'year':'2024'},
]

def getHTML(url):
            response = requests.get(url)
            return response.text

def validate(date):
    global validDate

    try:
        validDate = bool(datetime.datetime.strptime(date, '%Y-%m-%d'))
    except ValueError:
        validDate = False
        print('Incorrect data format, should be YYYY-MM-DD')


def menuAdd():
    global validDate
    global changes

    print('\nAdd a Holiday')
    print('==================')

    holidayName = input('Holiday: ')
    
    while validDate == False:
        holidayDate = input('Date: ')
        validate(holidayDate)

    validDate = False

    newHoliday = Holiday(holidayName,holidayDate)
    holidayList.addHoliday(newHoliday,holidayName,holidayDate,False)
    changes = True

    print('\nWould you like to continue?')
    selection = input('[y/n]: ')

    valid = False
    while valid == False:
        if selection == 'n':
            menu()
            valid = True
        elif selection == 'y':
            menuAdd()
            valid = True
        else:
            print('Invalid entry')
            valid = False
            selection = input('[y/n]: ')

def menuRemove():
    global validDate
    global changes

    print('\nRemove a Holiday')
    print('==================')

    holidayName = input('Holiday: ')
    
    while validDate == False:
        holidayDate = input('Date: ')
        validate(holidayDate)

    validDate = False

    holidayList.removeHoliday(holidayName,holidayDate)
    changes = True

    print('\nWould you like to continue?')
    selection = input('[y/n]: ')

    valid = False
    while valid == False:
        if selection == 'n':
            menu()
            valid = True
        elif selection == 'y':
            menuRemove()
            valid = True
        else:
            print('Invalid entry')
            valid = False
            selection = input('[y/n]: ')

def menuSave():
    global changes

    print('\nSave Holiday List')
    print('==================')

    print('Are you sure you want to save your changes?')
    selection = input('[y/n]: ')

    valid = False
    while valid == False:
        if selection == 'n':
            print('\nCanceled:\nHoliday list file save canceled.')
            menu()
            valid = True
        elif selection == 'y':
            holidayList.save_to_json()
            changes = False
            print('\nSuccess:\nYour changes have been saved.')
            menu()
            valid = True
        else:
            print('Invalid entry')
            valid = False
            selection = input('[y/n]: ')

def menuView():
    print('\nView Holidays')
    print('==================')

    holidayYear = input('Year: ')
    holidayWeek = input('Week #[1-52], Leave blank for current week: ')
    if holidayWeek == '':
        print(f'\nThese are holidays for this week:')
        holidayList.viewCurrentWeek()
    else:
        print(f'\nThese are holidays for {holidayYear} week #{holidayWeek}:')
        holidayList.filter_holidays_by_week(holidayYear,holidayWeek)

    print('\nWould you like to continue?')
    selection = input('[y/n]: ')

    valid = False
    while valid == False:
        if selection == 'n':
            menu()
            valid = True
        elif selection == 'y':
            menuView()
            valid = True
        else:
            print('Invalid entry')
            valid = False
            selection = input('[y/n]: ')

def menuExit():
    global changes

    print('\nExit')
    print('==================')
    print('\nAre you sure you want to exit?')

    if changes == True:
        print('Your changes will be lost.')

    selection = input('[y/n]: ')

    valid = False
    while valid == False:
        if selection == 'y':
            print('\nGoodbye!')
            valid = True
        elif selection == 'n':
            menu()
            valid = True
        else:
            print('Invalid entry')
            valid = False
            selection = input('[y/n]: ')

def menuSelect():
    selection = input('\nSelect Menu Item: ')
    if selection == '1':
        menuAdd()
    elif selection == '2':
        menuRemove()
    elif selection == '3':
        menuSave()
    elif selection == '4':
        menuView()
    elif selection == '5':
        menuExit()
    else:
        print('Invalid entry')
        menuSelect()

def menu():
    menuTextFile = open(menuTextLoc,'r')
    menuText = menuTextFile.read()
    menuTextFile.close()
    print(str(menuText))
    menuSelect()

def startup():
    print('\nHoliday Management')
    print('==================')
    print(f'There are {holidayList.numHolidays()} holidays in the system.')

def main():
    global holidayList
    holidayList = HolidayList()
    print('\nLoading...\n')
    holidayList.read_json(jsonFileLoc)
    for url in urlList:
        holidayList.scrapeHolidays(url['url'],url['year'])
    startup()
    menu()

if __name__ == "__main__":
    main();