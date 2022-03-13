import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from dotenv import dotenv_values
import datetime
from bs4 import BeautifulSoup
import time
from googletrans import Translator
from pytz import country_timezones


# Set your driverpath from .env file like this:
# DRIVERPATH = C:/Users/.../../.../chromedriver.exe

#Then load the .env file
config = dotenv_values(".env")
driverpath = config['CHROMEDRIVER']



def scrapee_brighttalk(url,driverpath):
    email_regex= "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    info_of_zoom = {
            'Date': None,
            'Emails': None,
            'Time': None,
            'Time/Date Object': None,
            'Timezone': '',
            'Topic':None,
            'Websites':None,
            'zoom_url':None
        }



    
    #Selenium
    s = Service(driverpath)
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    driver = webdriver.Chrome(service=s,options=opts)
    driver.get(url)
    driver.implicitly_wait(20)

    htmltext = driver.page_source

    driver.quit()

    if 'This talk is no longer available' in htmltext:
        try:
            info_of_zoom['Topic'] = re.findall(string = htmltext,pattern='"title":"([^"]+)')[0]
        except:
            info_of_zoom['Topic'] = re.findall(string=htmltext,pattern='"name":"([^"]+)')[0]
        info_of_zoom['Date'] = 'Thu, Jan 01, 1970'
        info_of_zoom['Time'] = '12:00 AM'
        info_of_zoom['Time/Date Object'] = 0
        info_of_zoom['Timezone'] = ''
        return info_of_zoom

    date_time = re.findall(string=htmltext,pattern='datetime="([^ ]+)"')[0]
    #   2022-01-26T18:00:00Z For example #

    soup = BeautifulSoup(htmltext, 'html.parser').find_all('a')
    templinks = [str(link.get('href')) for link in soup if  not ('brighttalk' in str(link.get('href') or 'BrightTALK' in str(link.get('href'))))]
    links = []
    for link in templinks:
        if link not in links and (link.startswith('http') or link.startswith('www')):
            links.append(link)

    emails = re.findall(string=htmltext,pattern=email_regex)
    emails_f = []



    for piece in emails:
        if not piece == '' or not len(piece) < 2 and piece.strip() not in emails_f:
            emails_f.append(piece.strip())
    
    if emails_f == []: emails_f = None    



    info_of_zoom['Topic'] = re.findall(pattern='webcast-title">([^<]+)',string=htmltext)[0]
    info_of_zoom['Date'] = re.findall(pattern='text___2-_xE">([^<]+)',string=htmltext)[0]
       

    info_of_zoom['Time'] = date_time.split('T')[1].strip('Z')
    info_of_zoom['Time/Date Object'] = int(datetime.datetime.strptime(date_time,'%Y-%m-%dT%H:%M:%SZ').timestamp())
    info_of_zoom['Websites'] = links
    info_of_zoom['Emails'] = emails_f
    info_of_zoom['zoom_url'] = url

    return info_of_zoom

def scrapee_on24(url,driverpath):

    regex_url = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    email_regex= "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    if 'gateway.on24' in url:
        print('Can not scrape gateway websites')
        return ''
    DEBUG_MODE = False

    info_of_zoom = {
            'Date': None,
            'Emails': None,
            'Time': None,
            'Time/Date Object': None,
            'Timezone': '',
            'Topic':None,
            'Websites':None,
            'zoom_url':None
        }

    info_of_zoom['zoom_url'] = url

    #Selenium
    s = Service(driverpath)
    opts = webdriver.ChromeOptions()
    opts.add_argument("start-maximized") #// https://stackoverflow.com/a/26283818/1689770
    opts.add_argument("enable-automation")# // https://stackoverflow.com/a/43840128/1689770
    opts.add_argument("--headless") #// only if you are ACTUALLY running headless
    opts.add_argument("--no-sandbox")# //https://stackoverflow.com/a/50725918/1689770
    opts.add_argument("--disable-infobars")# //https://stackoverflow.com/a/43840128/1689770
    opts.add_argument("--disable-dev-shm-usage")# //https://stackoverflow.com/a/50725918/1689770
    opts.add_argument("--disable-browser-side-navigation")# //https://stackoverflow.com/a/49123152/1689770
    opts.add_argument("--disable-gpu")# //https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc
    opts.add_argument('--log-level=3')
    opts.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=s,options=opts)
    driver.set_page_load_timeout(25)
    driver.get(url)
    time.sleep(6)
    htmltext = driver.page_source



    if DEBUG_MODE:
        with open('log.txt','w') as fh:
            fh.write(htmltext)


    found_time = False
    found_date = False
    found_topic = False

    # START THE TRANSLATOR
    translator = Translator()
    event_time = ""

    soup = BeautifulSoup(htmltext, 'html.parser')

    emails = re.findall(string=htmltext,pattern=email_regex)
    urls = re.findall(string=htmltext,pattern=regex_url)

    urls_f =[]
    emails_f = []

    # FOCUS ON URL HERE !!
    for url in urls:
        for piece in url:
            if not piece == '' or not len(piece) < 2 and piece not in urls_f:
                if 'https' in piece and 'on24' not in piece and 'recaptcha' not in piece:
                    urls_f.append(piece)
                else:
                    if 'http' in piece and 'on24' not in piece and 'recaptcha' not in piece:
                        urls_f.append(piece)
    if urls_f == []: urls_f = None
    info_of_zoom['Websites'] = urls_f

    # FOCUS ON EMAIL HERE !!!
    for piece in emails:
        if not piece == '' or not len(piece) < 2 and piece.strip() not in urls_f:
            emails_f.append(piece.strip())
    if emails_f == []: emails_f = None    
    info_of_zoom['Emails'] = emails_f


    # FOCUS ON TOPIC HERE !!
    if not found_topic:
        if len(soup.find_all("span", {"name":"title"})) > 0:
            for span in soup.find_all("span", {"name":"title"}):
                if span.text != '':
                    event_topic = span.text
                    found_topic = True
                    info_of_zoom['Topic'] = event_topic.strip()
                    break

    if len(soup.find_all("h1", {"id":"eventTitle"})) > 0:
        for span in soup.find_all("h1", {"id":"eventTitle"}):
            if span.text != '':
                event_topic = span.text
                found_topic = True
                info_of_zoom['Topic'] = event_topic.strip()
                break   

    if ' On Demand' in htmltext or " on demand" in htmltext:
        info_of_zoom['Date'] = 'Thu, Jan 01, 1970'
        info_of_zoom['Time'] = '12:00 AM'
        info_of_zoom['Time/Date Object'] = 1
        info_of_zoom['Timezone'] = ''
        if " US " in htmltext: info_of_zoom['Timezone'] = "US"
        elif " EU " in htmltext: info_of_zoom['Timezone'] = "EU"
        elif " AS " in htmltext: info_of_zoom['Timezone'] = "AS"
        return info_of_zoom
    
    if 'This event is no longer available' in htmltext:
        info_of_zoom['Topic'] = soup.find("td",{'class':'headline'}).text
        info_of_zoom['Date'] = 'Thu, Jan 01, 1970'
        info_of_zoom['Time'] = '12:00 AM'
        info_of_zoom['Time/Date Object'] = 0
        info_of_zoom['Timezone'] = ''
        if " US " in htmltext: info_of_zoom['Timezone'] = "US"
        elif " EU " in htmltext: info_of_zoom['Timezone'] = "EU"
        elif " AS " in htmltext: info_of_zoom['Timezone'] = "AS"

        return info_of_zoom


    # EXCEPITON ONE FOR DATE/TIME
    if not found_time and not found_date:
        if len(soup.find_all("span", {"class":"eventTimeText"})) > 0:
            indx = 0
            for span in soup.find_all("span", {"class":"eventTimeText"}):
                indx += 1
                if indx == 1:
                    event_date = span.text
                    found_date = True
                    info_of_zoom['Date'] = event_date
                elif indx == 2:
                    event_time = span.text
                    found_time = True
                    if event_time == '': event_time = event_date

                    try:
                        info_of_zoom['Time'] = re.findall('\d+:\d+ [Aa|Pp]\.[Mm]',string=event_time)[0]
                    except:
                        info_of_zoom['Time'] = re.findall('\d+:\d+ [Aa|Pp][Mm]',string=event_time)[0]                        

    # FOCUS ON DATE HERE !!

    if not found_date:
        if 'Date:' not in htmltext and 'Time:' not in htmltext:
            if len(soup.find_all("span", {"name":"date"})) > 0:
                for span in soup.find_all("span", {"name":"date"}):
                    if span.text != '':
                        event_date = span.text
                        found_date = True
                        info_of_zoom['Date'] = event_date.strip()
                        break     
    if not found_date:

            event_date = re.findall(pattern='Date:(.+)',string=htmltext)[0]

            year_of_on24 = re.findall(pattern="2\d\d\d",string=event_date)[0]
            month_of_on24 = re.findall(pattern="Jan|January|Feb|February|March|Mar|April|Apr|May|June|July|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec|jan|january|feb|february|march|mar|april|apr|may|june|july|august|aug|september|sep|october|oct|november|nov|december|dec",string=event_date)[0].capitalize()
            num_day_of_on24 = re.findall(pattern="(\d+),",string=event_date)[0]
            week_day_of_on24 = re.findall(pattern='Monday|monday|Mon|mon|Tuesday|tuesday|Tues|tues|Tue|tue|Wednesday|wednesday|Wed|wed|Thursday|thursday|Thurs|thurs|Thur|thur|Thu|thu|Friday|friday|Fri|fri|Saturday|saturday|Sat|sat|Sunday|sunday|Sun|sun',string=event_date)[0]
            info_of_zoom['Date'] = f'{week_day_of_on24} {month_of_on24} {num_day_of_on24}, {year_of_on24}'
            found_date = True   



    # FOCUS ON TIME HERE !!
    if not found_time:
        if len(soup.find_all("span", {"name":"time"})) > 0:
            for span in soup.find_all("span", {"name":"time"}):
                if span.text != '':
                    event_time = span.text
                    found_time = True
                    info_of_zoom['Time'] = event_time
                    break

    if not found_time:
        try:
            event_time = re.findall(pattern='Time:(.+)',string=htmltext)[0]
            event_time = re.findall('\d+:\d+ [Aa|Pp]\.[Mm]',string=event_time)[0]
            info_of_zoom['Time'] = event_time
            found_time = True
        except:
            pass
                



    if event_date == 'Available On Demand' or event_time == 'Available On Demand':
        
        info_of_zoom['Date'] = 'Thu, Jan 01, 1970'
        info_of_zoom['Time'] = '12:00 AM'
        info_of_zoom['Time/Date Object'] = 1
        info_of_zoom['Timezone'] = ''

    elif found_time and found_date:
        timetext = re.findall(pattern='(\d\d:\d\d [AaPp][Mm])',string=info_of_zoom['Time'])[0]
        info_of_zoom['Timezone'] = info_of_zoom['Time'].replace(timetext,'').strip()

        month = re.findall(pattern='January|Jan|February|Feb|March|Mar|April|Apr|May|June|July|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec|january|jan|february|feb|march|mar|april|apr|may|june|july|august|aug|september|sep|october|oct|november|nov|december|dec',string=info_of_zoom['Date'])[0]


        info_of_zoom['Date'] = info_of_zoom['Date'].replace(month,month[0:3].capitalize())  

        weekday = re.findall(pattern='Monday|monday|Mon|mon|Tuesday|tuesday|Tues|tues|Tue|tue|Wednesday|wednesday|Wed|wed|Thursday|thursday|Thurs|thurs|Thur|thur|Thu|thu|Friday|friday|Fri|fri|Saturday|saturday|Sat|sat|Sunday|sunday|Sun|sun',string=info_of_zoom['Date'])[0]

        day_of_month = re.findall(pattern='\d+',string=info_of_zoom['Date'])[0]
        year = re.findall(pattern='\d\d\d\d',string=info_of_zoom['Date'])[0]

        info_of_zoom['Date'] = info_of_zoom['Date'].replace(weekday,weekday[0:3].capitalize())  

        info_of_zoom['Time/Date Object'] = int(datetime.datetime.strptime(month[0:3].capitalize()+' '+day_of_month + ", "+year+ ' ' + timetext, '%b %d, %Y %H:%M %p').timestamp())

        if len(info_of_zoom['Time'].split()) > 2:
            timezone_wlist = info_of_zoom['Time'].split()[2:]
            info_of_zoom['Timezone'] = ''
            for w in timezone_wlist:
                info_of_zoom['Timezone'] += w[0]

    if info_of_zoom['Timezone'] != '':
        timezones = {
            'GMT':'EU',
            'UTC':'EU',
            'ECT':'EU',
            'EET':'EU',
            'ART':'EU',
            'EAT':'EU',
            'MET':'AS',
            'NET':'AS',
            'CST':'US',
            'EST':'US',
            'AST':'US'
        }

        if 'European' in info_of_zoom['Time']:
            info_of_zoom['Timezone'] = 'EU'
            return info_of_zoom

        if info_of_zoom['Timezone'] in timezones:
            info_of_zoom['Timezone'] = timezones[info_of_zoom['Timezone']]
        else:
            print('Please send me this error: ',info_of_zoom['Time'],info_of_zoom['Timezone'])
    else:

        info_of_zoom['Timezone'] = ''
        if " US " in htmltext: info_of_zoom['Timezone'] = ""
        elif " EU " in htmltext: info_of_zoom['Timezone'] = ""
        elif " AS " in htmltext: info_of_zoom['Timezone'] = ""

        
    return info_of_zoom

def scrapee_gtw(url,driverpath):
    countries = [
{'timezones': ['Europe/Andorra'], 'code': 'AD', 'continent': 'Europe', 'name': 'Andorra', 'capital': 'Andorra la Vella'},
{'timezones': ['Asia/Kabul'], 'code': 'AF', 'continent': 'Asia', 'name': 'Afghanistan', 'capital': 'Kabul'},
{'timezones': ['America/Antigua'], 'code': 'AG', 'continent': 'North America', 'name': 'Antigua and Barbuda', 'capital': "St. John's"},
{'timezones': ['Europe/Tirane'], 'code': 'AL', 'continent': 'Europe', 'name': 'Albania', 'capital': 'Tirana'},
{'timezones': ['Asia/Yerevan'], 'code': 'AM', 'continent': 'Asia', 'name': 'Armenia', 'capital': 'Yerevan'},
{'timezones': ['Africa/Luanda'], 'code': 'AO', 'continent': 'Africa', 'name': 'Angola', 'capital': 'Luanda'},
{'timezones': ['America/Argentina/Buenos_Aires', 'America/Argentina/Cordoba', 'America/Argentina/Jujuy', 'America/Argentina/Tucuman', 'America/Argentina/Catamarca', 'America/Argentina/La_Rioja', 'America/Argentina/San_Juan', 'America/Argentina/Mendoza', 'America/Argentina/Rio_Gallegos', 'America/Argentina/Ushuaia'], 'code': 'AR', 'continent': 'South America', 'name': 'Argentina', 'capital': 'Buenos Aires'},
{'timezones': ['Europe/Vienna'], 'code': 'AT', 'continent': 'Europe', 'name': 'Austria', 'capital': 'Vienna'},
{'timezones': ['Australia/Lord_Howe', 'Australia/Hobart', 'Australia/Currie', 'Australia/Melbourne', 'Australia/Sydney', 'Australia/Broken_Hill', 'Australia/Brisbane', 'Australia/Lindeman', 'Australia/Adelaide', 'Australia/Darwin', 'Australia/Perth'], 'code': 'AU', 'continent': 'Oceania', 'name': 'Australia', 'capital': 'Canberra'},
{'timezones': ['Asia/Baku'], 'code': 'AZ', 'continent': 'Asia', 'name': 'Azerbaijan', 'capital': 'Baku'},
{'timezones': ['America/Barbados'], 'code': 'BB', 'continent': 'North America', 'name': 'Barbados', 'capital': 'Bridgetown'},
{'timezones': ['Asia/Dhaka'], 'code': 'BD', 'continent': 'Asia', 'name': 'Bangladesh', 'capital': 'Dhaka'},
{'timezones': ['Europe/Brussels'], 'code': 'BE', 'continent': 'Europe', 'name': 'Belgium', 'capital': 'Brussels'},
{'timezones': ['Africa/Ouagadougou'], 'code': 'BF', 'continent': 'Africa', 'name': 'Burkina Faso', 'capital': 'Ouagadougou'},
{'timezones': ['Europe/Sofia'], 'code': 'BG', 'continent': 'Europe', 'name': 'Bulgaria', 'capital': 'Sofia'},
{'timezones': ['Asia/Bahrain'], 'code': 'BH', 'continent': 'Asia', 'name': 'Bahrain', 'capital': 'Manama'},
{'timezones': ['Africa/Bujumbura'], 'code': 'BI', 'continent': 'Africa', 'name': 'Burundi', 'capital': 'Bujumbura'},
{'timezones': ['Africa/Porto-Novo'], 'code': 'BJ', 'continent': 'Africa', 'name': 'Benin', 'capital': 'Porto-Novo'},
{'timezones': ['Asia/Brunei'], 'code': 'BN', 'continent': 'Asia', 'name': 'Brunei Darussalam', 'capital': 'Bandar Seri Begawan'},
{'timezones': ['America/La_Paz'], 'code': 'BO', 'continent': 'South America', 'name': 'Bolivia', 'capital': 'Sucre'},
{'timezones': ['America/Noronha', 'America/Belem', 'America/Fortaleza', 'America/Recife', 'America/Araguaina', 'America/Maceio', 'America/Bahia', 'America/Sao_Paulo', 'America/Campo_Grande', 'America/Cuiaba', 'America/Porto_Velho', 'America/Boa_Vista', 'America/Manaus', 'America/Eirunepe', 'America/Rio_Branco'], 'code': 'BR', 'continent': 'South America', 'name': 'Brazil', 'capital': 'Bras\xc3\xadlia'},
{'timezones': ['America/Nassau'], 'code': 'BS', 'continent': 'North America', 'name': 'Bahamas', 'capital': 'Nassau'},
{'timezones': ['Asia/Thimphu'], 'code': 'BT', 'continent': 'Asia', 'name': 'Bhutan', 'capital': 'Thimphu'},
{'timezones': ['Africa/Gaborone'], 'code': 'BW', 'continent': 'Africa', 'name': 'Botswana', 'capital': 'Gaborone'},
{'timezones': ['Europe/Minsk'], 'code': 'BY', 'continent': 'Europe', 'name': 'Belarus', 'capital': 'Minsk'},
{'timezones': ['America/Belize'], 'code': 'BZ', 'continent': 'North America', 'name': 'Belize', 'capital': 'Belmopan'},
{'timezones': ['America/St_Johns', 'America/Halifax', 'America/Glace_Bay', 'America/Moncton', 'America/Goose_Bay', 'America/Blanc-Sablon', 'America/Montreal', 'America/Toronto', 'America/Nipigon', 'America/Thunder_Bay', 'America/Pangnirtung', 'America/Iqaluit', 'America/Atikokan', 'America/Rankin_Inlet', 'America/Winnipeg', 'America/Rainy_River', 'America/Cambridge_Bay', 'America/Regina', 'America/Swift_Current', 'America/Edmonton', 'America/Yellowknife', 'America/Inuvik', 'America/Dawson_Creek', 'America/Vancouver', 'America/Whitehorse', 'America/Dawson'], 'code': 'CA', 'continent': 'North America', 'name': 'Canada', 'capital': 'Ottawa'},
{'timezones': ['Africa/Kinshasa', 'Africa/Lubumbashi'], 'code': 'CD', 'continent': 'Africa', 'name': 'Democratic Republic of the Congo', 'capital': 'Kinshasa'},
{'timezones': ['Africa/Brazzaville'], 'code': 'CG', 'continent': 'Africa', 'name': 'Republic of the Congo', 'capital': 'Brazzaville'},
{'timezones': ['Africa/Abidjan'], 'code': 'CI', 'continent': 'Africa', 'name': "C\xc3\xb4te d'Ivoire", 'capital': 'Yamoussoukro'},
{'timezones': ['America/Santiago', 'Pacific/Easter'], 'code': 'CL', 'continent': 'South America', 'name': 'Chile', 'capital': 'Santiago'},
{'timezones': ['Africa/Douala'], 'code': 'CM', 'continent': 'Africa', 'name': 'Cameroon', 'capital': 'Yaound\xc3\xa9'},
{'timezones': ['Asia/Shanghai', 'Asia/Harbin', 'Asia/Chongqing', 'Asia/Urumqi', 'Asia/Kashgar'], 'code': 'CN', 'continent': 'Asia', 'name': "People's Republic of China", 'capital': 'Beijing'},
{'timezones': ['America/Bogota'], 'code': 'CO', 'continent': 'South America', 'name': 'Colombia', 'capital': 'Bogot\xc3\xa1'},
{'timezones': ['America/Costa_Rica'], 'code': 'CR', 'continent': 'North America', 'name': 'Costa Rica', 'capital': 'San Jos\xc3\xa9'},
{'timezones': ['America/Havana'], 'code': 'CU', 'continent': 'North America', 'name': 'Cuba', 'capital': 'Havana'},
{'timezones': ['Atlantic/Cape_Verde'], 'code': 'CV', 'continent': 'Africa', 'name': 'Cape Verde', 'capital': 'Praia'},
{'timezones': ['Asia/Nicosia'], 'code': 'CY', 'continent': 'Asia', 'name': 'Cyprus', 'capital': 'Nicosia'},
{'timezones': ['Europe/Prague'], 'code': 'CZ', 'continent': 'Europe', 'name': 'Czech Republic', 'capital': 'Prague'},
{'timezones': ['Europe/Berlin'], 'code': 'DE', 'continent': 'Europe', 'name': 'Germany', 'capital': 'Berlin'},
{'timezones': ['Africa/Djibouti'], 'code': 'DJ', 'continent': 'Africa', 'name': 'Djibouti', 'capital': 'Djibouti City'},
{'timezones': ['Europe/Copenhagen'], 'code': 'DK', 'continent': 'Europe', 'name': 'Denmark', 'capital': 'Copenhagen'},
{'timezones': ['America/Dominica'], 'code': 'DM', 'continent': 'North America', 'name': 'Dominica', 'capital': 'Roseau'},
{'timezones': ['America/Santo_Domingo'], 'code': 'DO', 'continent': 'North America', 'name': 'Dominican Republic', 'capital': 'Santo Domingo'},
{'timezones': ['America/Guayaquil', 'Pacific/Galapagos'], 'code': 'EC', 'continent': 'South America', 'name': 'Ecuador', 'capital': 'Quito'},
{'timezones': ['Europe/Tallinn'], 'code': 'EE', 'continent': 'Europe', 'name': 'Estonia', 'capital': 'Tallinn'},
{'timezones': ['Africa/Cairo'], 'code': 'EG', 'continent': 'Africa', 'name': 'Egypt', 'capital': 'Cairo'},
{'timezones': ['Africa/Asmera'], 'code': 'ER', 'continent': 'Africa', 'name': 'Eritrea', 'capital': 'Asmara'},
{'timezones': ['Africa/Addis_Ababa'], 'code': 'ET', 'continent': 'Africa', 'name': 'Ethiopia', 'capital': 'Addis Ababa'},
{'timezones': ['Europe/Helsinki'], 'code': 'FI', 'continent': 'Europe', 'name': 'Finland', 'capital': 'Helsinki'},
{'timezones': ['Pacific/Fiji'], 'code': 'FJ', 'continent': 'Oceania', 'name': 'Fiji', 'capital': 'Suva'},
{'timezones': ['Europe/Paris'], 'code': 'FR', 'continent': 'Europe', 'name': 'France', 'capital': 'Paris'},
{'timezones': ['Africa/Libreville'], 'code': 'GA', 'continent': 'Africa', 'name': 'Gabon', 'capital': 'Libreville'},
{'timezones': ['Asia/Tbilisi'], 'code': 'GE', 'continent': 'Asia', 'name': 'Georgia', 'capital': 'Tbilisi'},
{'timezones': ['Africa/Accra'], 'code': 'GH', 'continent': 'Africa', 'name': 'Ghana', 'capital': 'Accra'},
{'timezones': ['Africa/Banjul'], 'code': 'GM', 'continent': 'Africa', 'name': 'The Gambia', 'capital': 'Banjul'},
{'timezones': ['Africa/Conakry'], 'code': 'GN', 'continent': 'Africa', 'name': 'Guinea', 'capital': 'Conakry'},
{'timezones': ['Europe/Athens'], 'code': 'GR', 'continent': 'Europe', 'name': 'Greece', 'capital': 'Athens'},
{'timezones': ['America/Guatemala'], 'code': 'GT', 'continent': 'North America', 'name': 'Guatemala', 'capital': 'Guatemala City'},
{'timezones': ['America/Guatemala'], 'code': 'GT', 'continent': 'North America', 'name': 'Haiti', 'capital': 'Port-au-Prince'},
{'timezones': ['Africa/Bissau'], 'code': 'GW', 'continent': 'Africa', 'name': 'Guinea-Bissau', 'capital': 'Bissau'},
{'timezones': ['America/Guyana'], 'code': 'GY', 'continent': 'South America', 'name': 'Guyana', 'capital': 'Georgetown'},
{'timezones': ['America/Tegucigalpa'], 'code': 'HN', 'continent': 'North America', 'name': 'Honduras', 'capital': 'Tegucigalpa'},
{'timezones': ['Europe/Budapest'], 'code': 'HU', 'continent': 'Europe', 'name': 'Hungary', 'capital': 'Budapest'},
{'timezones': ['Asia/Jakarta', 'Asia/Pontianak', 'Asia/Makassar', 'Asia/Jayapura'], 'code': 'ID', 'continent': 'Asia', 'name': 'Indonesia', 'capital': 'Jakarta'},
{'timezones': ['Europe/Dublin'], 'code': 'IE', 'continent': 'Europe', 'name': 'Republic of Ireland', 'capital': 'Dublin'},
{'timezones': ['Asia/Jerusalem'], 'code': 'IL', 'continent': 'Asia', 'name': 'Israel', 'capital': 'Jerusalem'},
{'timezones': ['Asia/Calcutta'], 'code': 'IN', 'continent': 'Asia', 'name': 'India', 'capital': 'New Delhi'},
{'timezones': ['Asia/Baghdad'], 'code': 'IQ', 'continent': 'Asia', 'name': 'Iraq', 'capital': 'Baghdad'},
{'timezones': ['Asia/Tehran'], 'code': 'IR', 'continent': 'Asia', 'name': 'Iran', 'capital': 'Tehran'},
{'timezones': ['Atlantic/Reykjavik'], 'code': 'IS', 'continent': 'Europe', 'name': 'Iceland', 'capital': 'Reykjav\xc3\xadk'},
{'timezones': ['Europe/Rome'], 'code': 'IT', 'continent': 'Europe', 'name': 'Italy', 'capital': 'Rome'},
{'timezones': ['America/Jamaica'], 'code': 'JM', 'continent': 'North America', 'name': 'Jamaica', 'capital': 'Kingston'},
{'timezones': ['Asia/Amman'], 'code': 'JO', 'continent': 'Asia', 'name': 'Jordan', 'capital': 'Amman'},
{'timezones': ['Asia/Tokyo'], 'code': 'JP', 'continent': 'Asia', 'name': 'Japan', 'capital': 'Tokyo'},
{'timezones': ['Africa/Nairobi'], 'code': 'KE', 'continent': 'Africa', 'name': 'Kenya', 'capital': 'Nairobi'},
{'timezones': ['Asia/Bishkek'], 'code': 'KG', 'continent': 'Asia', 'name': 'Kyrgyzstan', 'capital': 'Bishkek'},
{'timezones': ['Pacific/Tarawa', 'Pacific/Enderbury', 'Pacific/Kiritimati'], 'code': 'KI', 'continent': 'Oceania', 'name': 'Kiribati', 'capital': 'Tarawa'},
{'timezones': ['Asia/Pyongyang'], 'code': 'KP', 'continent': 'Asia', 'name': 'North Korea', 'capital': 'Pyongyang'},
{'timezones': ['Asia/Seoul'], 'code': 'KR', 'continent': 'Asia', 'name': 'South Korea', 'capital': 'Seoul'},
{'timezones': ['Asia/Kuwait'], 'code': 'KW', 'continent': 'Asia', 'name': 'Kuwait', 'capital': 'Kuwait City'},
{'timezones': ['Asia/Beirut'], 'code': 'LB', 'continent': 'Asia', 'name': 'Lebanon', 'capital': 'Beirut'},
{'timezones': ['Europe/Vaduz'], 'code': 'LI', 'continent': 'Europe', 'name': 'Liechtenstein', 'capital': 'Vaduz'},
{'timezones': ['Africa/Monrovia'], 'code': 'LR', 'continent': 'Africa', 'name': 'Liberia', 'capital': 'Monrovia'},
{'timezones': ['Africa/Maseru'], 'code': 'LS', 'continent': 'Africa', 'name': 'Lesotho', 'capital': 'Maseru'},
{'timezones': ['Europe/Vilnius'], 'code': 'LT', 'continent': 'Europe', 'name': 'Lithuania', 'capital': 'Vilnius'},
{'timezones': ['Europe/Luxembourg'], 'code': 'LU', 'continent': 'Europe', 'name': 'Luxembourg', 'capital': 'Luxembourg City'},
{'timezones': ['Europe/Riga'], 'code': 'LV', 'continent': 'Europe', 'name': 'Latvia', 'capital': 'Riga'},
{'timezones': ['Africa/Tripoli'], 'code': 'LY', 'continent': 'Africa', 'name': 'Libya', 'capital': 'Tripoli'},
{'timezones': ['Indian/Antananarivo'], 'code': 'MG', 'continent': 'Africa', 'name': 'Madagascar', 'capital': 'Antananarivo'},
{'timezones': ['Pacific/Majuro', 'Pacific/Kwajalein'], 'code': 'MH', 'continent': 'Oceania', 'name': 'Marshall Islands', 'capital': 'Majuro'},
{'timezones': ['Europe/Skopje'], 'code': 'MK', 'continent': 'Europe', 'name': 'Macedonia', 'capital': 'Skopje'},
{'timezones': ['Africa/Bamako'], 'code': 'ML', 'continent': 'Africa', 'name': 'Mali', 'capital': 'Bamako'},
{'timezones': ['Asia/Rangoon'], 'code': 'MM', 'continent': 'Asia', 'name': 'Myanmar', 'capital': 'Naypyidaw'},
{'timezones': ['Asia/Ulaanbaatar', 'Asia/Hovd', 'Asia/Choibalsan'], 'code': 'MN', 'continent': 'Asia', 'name': 'Mongolia', 'capital': 'Ulaanbaatar'},
{'timezones': ['Africa/Nouakchott'], 'code': 'MR', 'continent': 'Africa', 'name': 'Mauritania', 'capital': 'Nouakchott'},
{'timezones': ['Europe/Malta'], 'code': 'MT', 'continent': 'Europe', 'name': 'Malta', 'capital': 'Valletta'},
{'timezones': ['Indian/Mauritius'], 'code': 'MU', 'continent': 'Africa', 'name': 'Mauritius', 'capital': 'Port Louis'},
{'timezones': ['Indian/Maldives'], 'code': 'MV', 'continent': 'Asia', 'name': 'Maldives', 'capital': 'Mal\xc3\xa9'},
{'timezones': ['Africa/Blantyre'], 'code': 'MW', 'continent': 'Africa', 'name': 'Malawi', 'capital': 'Lilongwe'},
{'timezones': ['America/Mexico_City', 'America/Cancun', 'America/Merida', 'America/Monterrey', 'America/Mazatlan', 'America/Chihuahua', 'America/Hermosillo', 'America/Tijuana'], 'code': 'MX', 'continent': 'North America', 'name': 'Mexico', 'capital': 'Mexico City'},
{'timezones': ['Asia/Kuala_Lumpur', 'Asia/Kuching'], 'code': 'MY', 'continent': 'Asia', 'name': 'Malaysia', 'capital': 'Kuala Lumpur'},
{'timezones': ['Africa/Maputo'], 'code': 'MZ', 'continent': 'Africa', 'name': 'Mozambique', 'capital': 'Maputo'},
{'timezones': ['Africa/Windhoek'], 'code': 'NA', 'continent': 'Africa', 'name': 'Namibia', 'capital': 'Windhoek'},
{'timezones': ['Africa/Niamey'], 'code': 'NE', 'continent': 'Africa', 'name': 'Niger', 'capital': 'Niamey'},
{'timezones': ['Africa/Lagos'], 'code': 'NG', 'continent': 'Africa', 'name': 'Nigeria', 'capital': 'Abuja'},
{'timezones': ['America/Managua'], 'code': 'NI', 'continent': 'North America', 'name': 'Nicaragua', 'capital': 'Managua'},
{'timezones': ['Europe/Amsterdam'], 'code': 'NL', 'continent': 'Europe', 'name': 'Kingdom of the Netherlands', 'capital': 'Amsterdam'},
{'timezones': ['Europe/Oslo'], 'code': 'NO', 'continent': 'Europe', 'name': 'Norway', 'capital': 'Oslo'},
{'timezones': ['Asia/Katmandu'], 'code': 'NP', 'continent': 'Asia', 'name': 'Nepal', 'capital': 'Kathmandu'},
{'timezones': ['Pacific/Nauru'], 'code': 'NR', 'continent': 'Oceania', 'name': 'Nauru', 'capital': 'Yaren'},
{'timezones': ['Pacific/Auckland', 'Pacific/Chatham'], 'code': 'NZ', 'continent': 'Oceania', 'name': 'New Zealand', 'capital': 'Wellington'},
{'timezones': ['Asia/Muscat'], 'code': 'OM', 'continent': 'Asia', 'name': 'Oman', 'capital': 'Muscat'},
{'timezones': ['America/Panama'], 'code': 'PA', 'continent': 'North America', 'name': 'Panama', 'capital': 'Panama City'},
{'timezones': ['America/Lima'], 'code': 'PE', 'continent': 'South America', 'name': 'Peru', 'capital': 'Lima'},
{'timezones': ['Pacific/Port_Moresby'], 'code': 'PG', 'continent': 'Oceania', 'name': 'Papua New Guinea', 'capital': 'Port Moresby'},
{'timezones': ['Asia/Manila'], 'code': 'PH', 'continent': 'Asia', 'name': 'Philippines', 'capital': 'Manila'},
{'timezones': ['Asia/Karachi'], 'code': 'PK', 'continent': 'Asia', 'name': 'Pakistan', 'capital': 'Islamabad'},
{'timezones': ['Europe/Warsaw'], 'code': 'PL', 'continent': 'Europe', 'name': 'Poland', 'capital': 'Warsaw'},
{'timezones': ['Europe/Lisbon', 'Atlantic/Madeira', 'Atlantic/Azores'], 'code': 'PT', 'continent': 'Europe', 'name': 'Portugal', 'capital': 'Lisbon'},
{'timezones': ['Pacific/Palau'], 'code': 'PW', 'continent': 'Oceania', 'name': 'Palau', 'capital': 'Ngerulmud'},
{'timezones': ['America/Asuncion'], 'code': 'PY', 'continent': 'South America', 'name': 'Paraguay', 'capital': 'Asunci\xc3\xb3n'},
{'timezones': ['Asia/Qatar'], 'code': 'QA', 'continent': 'Asia', 'name': 'Qatar', 'capital': 'Doha'},
{'timezones': ['Europe/Bucharest'], 'code': 'RO', 'continent': 'Europe', 'name': 'Romania', 'capital': 'Bucharest'},
{'timezones': ['Europe/Kaliningrad', 'Europe/Moscow', 'Europe/Volgograd', 'Europe/Samara', 'Asia/Yekaterinburg', 'Asia/Omsk', 'Asia/Novosibirsk', 'Asia/Krasnoyarsk', 'Asia/Irkutsk', 'Asia/Yakutsk', 'Asia/Vladivostok', 'Asia/Sakhalin', 'Asia/Magadan', 'Asia/Kamchatka', 'Asia/Anadyr'], 'code': 'RU', 'continent': 'Europe', 'name': 'Russia', 'capital': 'Moscow'},
{'timezones': ['Africa/Kigali'], 'code': 'RW', 'continent': 'Africa', 'name': 'Rwanda', 'capital': 'Kigali'},
{'timezones': ['Asia/Riyadh'], 'code': 'SA', 'continent': 'Asia', 'name': 'Saudi Arabia', 'capital': 'Riyadh'},
{'timezones': ['Pacific/Guadalcanal'], 'code': 'SB', 'continent': 'Oceania', 'name': 'Solomon Islands', 'capital': 'Honiara'},
{'timezones': ['Indian/Mahe'], 'code': 'SC', 'continent': 'Africa', 'name': 'Seychelles', 'capital': 'Victoria'},
{'timezones': ['Africa/Khartoum'], 'code': 'SD', 'continent': 'Africa', 'name': 'Sudan', 'capital': 'Khartoum'},
{'timezones': ['Europe/Stockholm'], 'code': 'SE', 'continent': 'Europe', 'name': 'Sweden', 'capital': 'Stockholm'},
{'timezones': ['Asia/Singapore'], 'code': 'SG', 'continent': 'Asia', 'name': 'Singapore', 'capital': 'Singapore'},
{'timezones': ['Europe/Ljubljana'], 'code': 'SI', 'continent': 'Europe', 'name': 'Slovenia', 'capital': 'Ljubljana'},
{'timezones': ['Europe/Bratislava'], 'code': 'SK', 'continent': 'Europe', 'name': 'Slovakia', 'capital': 'Bratislava'},
{'timezones': ['Africa/Freetown'], 'code': 'SL', 'continent': 'Africa', 'name': 'Sierra Leone', 'capital': 'Freetown'},
{'timezones': ['Europe/San_Marino'], 'code': 'SM', 'continent': 'Europe', 'name': 'San Marino', 'capital': 'San Marino'},
{'timezones': ['Africa/Dakar'], 'code': 'SN', 'continent': 'Africa', 'name': 'Senegal', 'capital': 'Dakar'},
{'timezones': ['Africa/Mogadishu'], 'code': 'SO', 'continent': 'Africa', 'name': 'Somalia', 'capital': 'Mogadishu'},
{'timezones': ['America/Paramaribo'], 'code': 'SR', 'continent': 'South America', 'name': 'Suriname', 'capital': 'Paramaribo'},
{'timezones': ['Africa/Sao_Tome'], 'code': 'ST', 'continent': 'Africa', 'name': 'S\xc3\xa3o Tom\xc3\xa9 and Pr\xc3\xadncipe', 'capital': 'S\xc3\xa3o Tom\xc3\xa9'},
{'timezones': ['Asia/Damascus'], 'code': 'SY', 'continent': 'Asia', 'name': 'Syria', 'capital': 'Damascus'},
{'timezones': ['Africa/Lome'], 'code': 'TG', 'continent': 'Africa', 'name': 'Togo', 'capital': 'Lom\xc3\xa9'},
{'timezones': ['Asia/Bangkok'], 'code': 'TH', 'continent': 'Asia', 'name': 'Thailand', 'capital': 'Bangkok'},
{'timezones': ['Asia/Dushanbe'], 'code': 'TJ', 'continent': 'Asia', 'name': 'Tajikistan', 'capital': 'Dushanbe'},
{'timezones': ['Asia/Ashgabat'], 'code': 'TM', 'continent': 'Asia', 'name': 'Turkmenistan', 'capital': 'Ashgabat'},
{'timezones': ['Africa/Tunis'], 'code': 'TN', 'continent': 'Africa', 'name': 'Tunisia', 'capital': 'Tunis'},
{'timezones': ['Pacific/Tongatapu'], 'code': 'TO', 'continent': 'Oceania', 'name': 'Tonga', 'capital': 'Nuku\xca\xbbalofa'},
{'timezones': ['Europe/Istanbul'], 'code': 'TR', 'continent': 'Asia', 'name': 'Turkey', 'capital': 'Ankara'},
{'timezones': ['America/Port_of_Spain'], 'code': 'TT', 'continent': 'North America', 'name': 'Trinidad and Tobago', 'capital': 'Port of Spain'},
{'timezones': ['Pacific/Funafuti'], 'code': 'TV', 'continent': 'Oceania', 'name': 'Tuvalu', 'capital': 'Funafuti'},
{'timezones': ['Africa/Dar_es_Salaam'], 'code': 'TZ', 'continent': 'Africa', 'name': 'Tanzania', 'capital': 'Dodoma'},
{'timezones': ['Europe/Kiev', 'Europe/Uzhgorod', 'Europe/Zaporozhye', 'Europe/Simferopol'], 'code': 'UA', 'continent': 'Europe', 'name': 'Ukraine', 'capital': 'Kyiv'},
{'timezones': ['Africa/Kampala'], 'code': 'UG', 'continent': 'Africa', 'name': 'Uganda', 'capital': 'Kampala'},
{'timezones': ['America/New_York', 'America/Detroit', 'America/Kentucky/Louisville', 'America/Kentucky/Monticello', 'America/Indiana/Indianapolis', 'America/Indiana/Marengo', 'America/Indiana/Knox', 'America/Indiana/Vevay', 'America/Chicago', 'America/Indiana/Vincennes', 'America/Indiana/Petersburg', 'America/Menominee', 'America/North_Dakota/Center', 'America/North_Dakota/New_Salem', 'America/Denver', 'America/Boise', 'America/Shiprock', 'America/Phoenix', 'America/Los_Angeles', 'America/Anchorage', 'America/Juneau', 'America/Yakutat', 'America/Nome', 'America/Adak', 'Pacific/Honolulu'], 'code': 'US', 'continent': 'North America', 'name': 'United States', 'capital': 'Washington, D.C.'},
{'timezones': ['America/Montevideo'], 'code': 'UY', 'continent': 'South America', 'name': 'Uruguay', 'capital': 'Montevideo'},
{'timezones': ['Asia/Samarkand', 'Asia/Tashkent'], 'code': 'UZ', 'continent': 'Asia', 'name': 'Uzbekistan', 'capital': 'Tashkent'},
{'timezones': ['Europe/Vatican'], 'code': 'VA', 'continent': 'Europe', 'name': 'Vatican City', 'capital': 'Vatican City'},
{'timezones': ['America/Caracas'], 'code': 'VE', 'continent': 'South America', 'name': 'Venezuela', 'capital': 'Caracas'},
{'timezones': ['Asia/Saigon'], 'code': 'VN', 'continent': 'Asia', 'name': 'Vietnam', 'capital': 'Hanoi'},
{'timezones': ['Pacific/Efate'], 'code': 'VU', 'continent': 'Oceania', 'name': 'Vanuatu', 'capital': 'Port Vila'},
{'timezones': ['Asia/Aden'], 'code': 'YE', 'continent': 'Asia', 'name': 'Yemen', 'capital': "Sana'a"},
{'timezones': ['Africa/Lusaka'], 'code': 'ZM', 'continent': 'Africa', 'name': 'Zambia', 'capital': 'Lusaka'},
{'timezones': ['Africa/Harare'], 'code': 'ZW', 'continent': 'Africa', 'name': 'Zimbabwe', 'capital': 'Harare'},
{'timezones': ['Africa/Algiers'], 'code': 'DZ', 'continent': 'Africa', 'name': 'Algeria', 'capital': 'Algiers'},
{'timezones': ['Europe/Sarajevo'], 'code': 'BA', 'continent': 'Europe', 'name': 'Bosnia and Herzegovina', 'capital': 'Sarajevo'},
{'timezones': ['Asia/Phnom_Penh'], 'code': 'KH', 'continent': 'Asia', 'name': 'Cambodia', 'capital': 'Phnom Penh'},
{'timezones': ['Africa/Bangui'], 'code': 'CF', 'continent': 'Africa', 'name': 'Central African Republic', 'capital': 'Bangui'},
{'timezones': ['Africa/Ndjamena'], 'code': 'TD', 'continent': 'Africa', 'name': 'Chad', 'capital': "N'Djamena"},
{'timezones': ['Indian/Comoro'], 'code': 'KM', 'continent': 'Africa', 'name': 'Comoros', 'capital': 'Moroni'},
{'timezones': ['Europe/Zagreb'], 'code': 'HR', 'continent': 'Europe', 'name': 'Croatia', 'capital': 'Zagreb'},
{'timezones': ['Asia/Dili'], 'code': 'TL', 'continent': 'Asia', 'name': 'East Timor', 'capital': 'Dili'},
{'timezones': ['America/El_Salvador'], 'code': 'SV', 'continent': 'North America', 'name': 'El Salvador', 'capital': 'San Salvador'},
{'timezones': ['Africa/Malabo'], 'code': 'GQ', 'continent': 'Africa', 'name': 'Equatorial Guinea', 'capital': 'Malabo'},
{'timezones': ['America/Grenada'], 'code': 'GD', 'continent': 'North America', 'name': 'Grenada', 'capital': "St. George's"},
{'timezones': ['Asia/Almaty', 'Asia/Qyzylorda', 'Asia/Aqtobe', 'Asia/Aqtau', 'Asia/Oral'], 'code': 'KZ', 'continent': 'Asia', 'name': 'Kazakhstan', 'capital': 'Astana'},
{'timezones': ['Asia/Vientiane'], 'code': 'LA', 'continent': 'Asia', 'name': 'Laos', 'capital': 'Vientiane'},
{'timezones': ['Pacific/Truk', 'Pacific/Ponape', 'Pacific/Kosrae'], 'code': 'FM', 'continent': 'Oceania', 'name': 'Federated States of Micronesia', 'capital': 'Palikir'},
{'timezones': ['Europe/Chisinau'], 'code': 'MD', 'continent': 'Europe', 'name': 'Moldova', 'capital': 'Chi\xc5\x9fin\xc4\x83u'},
{'timezones': ['Europe/Monaco'], 'code': 'MC', 'continent': 'Europe', 'name': 'Monaco', 'capital': 'Monaco'},
{'timezones': ['Europe/Podgorica'], 'code': 'ME', 'continent': 'Europe', 'name': 'Montenegro', 'capital': 'Podgorica'},
{'timezones': ['Africa/Casablanca'], 'code': 'MA', 'continent': 'Africa', 'name': 'Morocco', 'capital': 'Rabat'},
{'timezones': ['America/St_Kitts'], 'code': 'KN', 'continent': 'North America', 'name': 'Saint Kitts and Nevis', 'capital': 'Basseterre'},
{'timezones': ['America/St_Lucia'], 'code': 'LC', 'continent': 'North America', 'name': 'Saint Lucia', 'capital': 'Castries'},
{'timezones': ['America/St_Vincent'], 'code': 'VC', 'continent': 'North America', 'name': 'Saint Vincent and the Grenadines', 'capital': 'Kingstown'},
{'timezones': ['Pacific/Apia'], 'code': 'WS', 'continent': 'Oceania', 'name': 'Samoa', 'capital': 'Apia'},
{'timezones': ['Europe/Belgrade'], 'code': 'RS', 'continent': 'Europe', 'name': 'Serbia', 'capital': 'Belgrade'},
{'timezones': ['Africa/Johannesburg'], 'code': 'ZA', 'continent': 'Africa', 'name': 'South Africa', 'capital': 'Pretoria'},
{'timezones': ['Europe/Madrid', 'Africa/Ceuta', 'Atlantic/Canary'], 'code': 'ES', 'continent': 'Europe', 'name': 'Spain', 'capital': 'Madrid'},
{'timezones': ['Asia/Colombo'], 'code': 'LK', 'continent': 'Asia', 'name': 'Sri Lanka', 'capital': 'Sri Jayewardenepura Kotte'},
{'timezones': ['Africa/Mbabane'], 'code': 'SZ', 'continent': 'Africa', 'name': 'Swaziland', 'capital': 'Mbabane'},
{'timezones': ['Europe/Zurich'], 'code': 'CH', 'continent': 'Europe', 'name': 'Switzerland', 'capital': 'Bern'},
{'timezones': ['Asia/Dubai'], 'code': 'AE', 'continent': 'Asia', 'name': 'United Arab Emirates', 'capital': 'Abu Dhabi'},
{'timezones': ['Europe/London'], 'code': 'GB', 'continent': 'Europe', 'name': 'United Kingdom', 'capital': 'London'},
]

    timezone_list = [
'[GMT-12:00] Colombo',

'[GMT-11:00] Apia',

'[GMT-10:00] Santiago',

'[GMT-09:00] Santiago',

'[GMT-08:00] Tijuana',

'[GMT-07:00] Chihuahua, La Paz, Mazatlan',

'[GMT-06:00] Santiago',

'[GMT-05:00] Indiana',

'[GMT-04:30] Caracas, La Paz',

'[GMT-04:00] Santiago',

'[GMT-03:30] Grenada',

'[GMT-03:00] Buenos_Aires, Georgetown',

'[GMT-02:00] Azores',

'[GMT-01:00] Azores',

'[GMT+01:00] Sarajevo, Skopje, Warsaw, Zagreb',

'[GMT+02:00] Helsinki, Kyiv, Riga, Sofia, Tallinn, Vilnius',

'[GMT+03:00] Moscow, St. Petersburg, Volgograd',

'[GMT+03:30] Tehran',

'[GMT+04:00] Baku, Tbilisi, Yerevan',

'[GMT+04:30] Kabul',

'[GMT+05:00] Karachi',

'[GMT+05:30] Comoro',

'[GMT+05:45] Katmandu',

'[GMT+06:00] Almaty, Novosibirsk',

'[GMT+06:30] Rangoon',

'[GMT+07:00] Bangkok, Hanoi, Jakarta',

'[GMT+08:00] Irkutsk, Ulaan Bataar',

'[GMT+09:00] Yakutsk',

'[GMT+09:30] Darwin',

'[GMT+10:00] Hobart',

'[GMT+11:00] Magadan, Solomon Is., New Caledonia',

'[GMT+12:00] Fiji, Kamchatka, Marshall Is.',

"[GMT+13:00] Nuku'alofa",

    ]


    regex_url = '(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])'
    email_regex= "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"

    info_of_zoom = {
        'Date': None,
        'Emails': None,
        'Time': None,
        'Time/Date Object': None,
        'Timezone': None,
        'Topic':None,
        'Websites':None,
        'zoom_url':None
    }
    s = Service(driverpath)
    opts = webdriver.ChromeOptions()
    opts.add_argument("start-maximized") #// https://stackoverflow.com/a/26283818/1689770
    opts.add_argument("enable-automation")# // https://stackoverflow.com/a/43840128/1689770
    opts.add_argument("--headless") #// only if you are ACTUALLY running headless
    opts.add_argument("--no-sandbox")# //https://stackoverflow.com/a/50725918/1689770
    opts.add_argument("--disable-infobars")# //https://stackoverflow.com/a/43840128/1689770
    opts.add_argument("--disable-dev-shm-usage")# //https://stackoverflow.com/a/50725918/1689770
    opts.add_argument("--disable-browser-side-navigation")# //https://stackoverflow.com/a/49123152/1689770
    opts.add_argument("--disable-gpu")# //https://stackoverflow.com/questions/51959986/how-to-solve-selenium-chromedriver-timed-out-receiving-message-from-renderer-exc
    opts.add_argument('--log-level=3')
    opts.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=s,options=opts)
    driver.set_page_load_timeout(25)


    
    driver.get(url)
    time.sleep(5)
        

    htmltext = driver.page_source


    soup = BeautifulSoup(htmltext, 'html.parser')
    found_time_text = False


    if 'This Webinar has Ended' in htmltext or 'Webinar is expired' in htmltext:
        print("Webinar has ended.")
        expired = True
        info_of_zoom['zoom_url'] = url
        info_of_zoom['Date'] = 'Jan 01, 1970'
        info_of_zoom['Time'] = '12:00 AM'
        info_of_zoom['Time/Date Object'] = 0
        info_of_zoom['Timezone'] = ''
        for h4 in soup.find_all("h4", {"data-bind":"text:webinarSubject, style:{color:brandingInfo.selectedHeaderColor}"}):
            if len(h4.text) > 0:
                info_of_zoom['Topic'] = h4.text.strip()
                break

    else:
        info_of_zoom['zoom_url'] = url
        expired = False

    # START THE TRANSLATOR
    translator = Translator()

    if found_time_text==False:
    # Tue, Feb 1, 2022 5:30 PM - 6:30 PM AST

        if len(soup.find_all("div", {"id":"training-times"})) > 0:
            for div in soup.find_all("div", {"id":"training-times"}):



                try:
                    translated_text = translator.translate(div.text.strip()).text
                except:
                    translated_text = div.text.strip()
                


                if len(translated_text.strip().split()) > 10:
                    timezone_text = translated_text.strip().split()[-1]
                    translated_text = translated_text.strip().split()[0:9]
                    translated_text = ' '.join(translated_text)
                else:
                    timezone_text = translated_text.strip().split("-")[-1].strip()

                try:

                    time_text = translated_text.strip().split("-")[0].strip()

                    


                    if '+' in timezone_text or '-' in timezone_text:
                        
                        try:
                            timezone = "+" + timezone_text.split("+")[1]
                            
                        except:
                            timezone = "-" + timezone_text.split("-")[1]

                    else:
                        timezone = timezone_text.strip().split().pop()

            
                    


                    
                    year_of_gtw = re.findall(pattern="2\d\d\d",string=time_text)[0]

                    month_of_gtw = re.findall(pattern="Jan|January|Feb|February|March|Mar|April|Apr|May|June|July|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec|jan|january|feb|february|march|mar|april|apr|may|june|july|august|aug|september|sep|october|oct|november|nov|december|dec",string=time_text)[0].capitalize()

                    week_day_of_gtw = re.findall(pattern="Monday|monday|Mon|mon|Tuesday|tuesday|Tues|tues|Tue|tue|Wednesday|wednesday|Wed|wed|Thursday|thursday|Thurs|thurs|Thur|thur|Thu|thu|Friday|friday|Fri|fri|Saturday|saturday|Sat|sat|Sunday|sunday|Sun|sun",string=time_text)[0].capitalize()

                    num_day_of_gtw = re.findall(pattern="(\d+),",string=time_text)[0]

                    time_of_gtw = re.findall('\d+:\d+ [Aa|Pp][Mm]',string=time_text)[0]


                    month_of_gtw = month_of_gtw[0:3]
                    week_day_of_gtw = week_day_of_gtw[0:3]



                    info_of_zoom['Date'] = f"{week_day_of_gtw}, {month_of_gtw} {num_day_of_gtw}, {year_of_gtw}"
                    info_of_zoom['Time'] = re.findall('\d+:\d+ [A|P]M',string=time_text)[0]
                    info_of_zoom['Time/Date Object'] = int(datetime.datetime.strptime((info_of_zoom["Date"] + " " + info_of_zoom["Time"]), '%a, %b %d, %Y %H:%M %p').timestamp())



                    
                    info_of_zoom["Timezone"] = timezone
                    found_time_text = True
                    break
                except:
                    found_time_text = False
        else:
            for select in soup.find_all("select", {"id":"training-series-times"}):
                try:
                    after_text = translator.translate(select.text).text
                except:
                    after_text = select.text
                try:

                    time_text = after_text.strip().split("\n")[0].strip().split("-")[0].strip()


                    timezone_text = after_text.strip().split("\n")[0].strip().split("-")[1].strip()


                    if '+' in timezone_text or '-' in timezone_text:
                        
                        try:
                            timezone = "+" + timezone_text.split("+")[1]
                            
                        except:
                            timezone = "-" + timezone_text.split("-")[1]

                    else:
                        timezone = timezone_text.strip().split().pop()

                    
                    obj_text = time_text.split(",")[1].strip() + ", " + time_text.split(",")[2].strip()

                    
                    year_of_gtw = re.findall(pattern="2\d\d\d",string=time_text)[0]
                    month_of_gtw = re.findall(pattern="Jan|January|Feb|February|March|Mar|April|Apr|May|June|July|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec|jan|january|feb|february|march|mar|april|apr|may|june|july|august|aug|september|sep|october|oct|november|nov|december|dec",string=time_text)[0].capitalize()
                    week_day_of_gtw = re.findall(pattern="Monday|monday|Mon|mon|Tuesday|tuesday|Tues|tues|Tue|tue|Wednesday|wednesday|Wed|wed|Thursday|thursday|Thurs|thurs|Thur|thur|Thu|thu|Friday|friday|Fri|fri|Saturday|saturday|Sat|sat|Sunday|sunday|Sun|sun",string=time_text)[0].capitalize()
                    num_day_of_gtw = re.findall(pattern="(\d+),",string=time_text)[0]
                    time_of_gtw = re.findall('\d+:\d+ [Aa|Pp][M|m]',string=time_text)[0]

                    month_of_gtw = month_of_gtw[0:3]
                    week_day_of_gtw = week_day_of_gtw[0:3]

                    info_of_zoom['Date'] = f"{week_day_of_gtw}, {month_of_gtw} {num_day_of_gtw}, {year_of_gtw}"
                    info_of_zoom['Time'] = time_of_gtw
                    info_of_zoom['Time/Date Object'] = int(datetime.datetime.strptime((info_of_zoom["Date"] + " " + info_of_zoom["Time"]), '%a, %b %d, %Y %H:%M %p').timestamp())
                    info_of_zoom["Timezone"] = timezone

                    found_time_text = True

                except:
                    found_time_text = False

    if found_time_text == False:
        if not expired: 
            print('No time data found in this webinar : ', url)
        timezone = ''
        info_of_zoom['Date'] = 'Thu, Jan 01, 1970'
        info_of_zoom['Time'] = '12:00 AM'
        info_of_zoom['Time/Date Object'] = 0
        info_of_zoom['Timezone'] = ''
    

    if not expired:
        for timezone_str in timezone_list:
            
            if 'Canada' in timezone:
                timezone = "America/"

            elif timezone in timezone_str:
                timezone = timezone_str.split(']')[1].strip()
                if ',' in timezone: timezone = timezone.split(',')[0]
                info_of_zoom['Timezone'] = timezone

        for country in countries:
            for tz in country['timezones']:
                if timezone in tz:
                    timezone = tz.split('/')[0]
                    break

    if timezone == 'Pacific' or timezone == 'Canada' or timezone == 'America' or timezone == 'Indian': info_of_zoom['Timezone'] = 'US'
    elif timezone == 'Europe': info_of_zoom['Timezone'] = 'EU'
    elif timezone in ['Asia','Atlantic','Africa','Australia','Pacific','SST']: info_of_zoom['Timezone'] = 'AS'





    for h1 in soup.find_all('h1', {'class':'word-wrap-break'}):
        info_of_zoom['Topic'] = h1.text.strip()

    #Website finder !
    info_of_zoom['Websites'] = []
    try:
        urls = re.findall(string=htmltext,pattern=regex_url)

        found_urls = True
    except:
        found_urls = False

    if found_urls:
        for url in urls:
            if 'zoom' not in url:
                info_of_zoom['Websites'].append(url)
    
    if info_of_zoom['Websites'] == []: info_of_zoom['Websites'] = None
    # End of website finder?

    # Email gatherer
    emails = re.findall(email_regex, str(htmltext))
    emails_f = []
    if 'name@domain.com' in emails:
        emails.remove('name@domain.com')

    try:
        for email in emails:
            if 'zoom' not in email and email not in emails_f: 
                emails_f.append(email)


        info_of_zoom['Emails'] = list(dict.fromkeys(emails_f))
    except:
        info_of_zoom['Emails'] = None\

    if info_of_zoom['Emails'] == []: info_of_zoom['Emails'] = None
    # End of email gatherer



    driver.quit()
    return info_of_zoom


def scrapee_zoom(url,driverpath):
    timezone_country = {}

    for countrycode in country_timezones:
        timezones = country_timezones[countrycode]
        for timezone in timezones:
            timezone_country[timezone] = countrycode


    regex_url = '(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])'
    countries = [
    {'timezones': ['Europe/Andorra'], 'code': 'AD', 'continent': 'Europe', 'name': 'Andorra', 'capital': 'Andorra la Vella'},
    {'timezones': ['Asia/Kabul'], 'code': 'AF', 'continent': 'Asia', 'name': 'Afghanistan', 'capital': 'Kabul'},
    {'timezones': ['America/Antigua'], 'code': 'AG', 'continent': 'North America', 'name': 'Antigua and Barbuda', 'capital': "St. John's"},
    {'timezones': ['Europe/Tirane'], 'code': 'AL', 'continent': 'Europe', 'name': 'Albania', 'capital': 'Tirana'},
    {'timezones': ['Asia/Yerevan'], 'code': 'AM', 'continent': 'Asia', 'name': 'Armenia', 'capital': 'Yerevan'},
    {'timezones': ['Africa/Luanda'], 'code': 'AO', 'continent': 'Africa', 'name': 'Angola', 'capital': 'Luanda'},
    {'timezones': ['America/Argentina/Buenos_Aires', 'America/Argentina/Cordoba', 'America/Argentina/Jujuy', 'America/Argentina/Tucuman', 'America/Argentina/Catamarca', 'America/Argentina/La_Rioja', 'America/Argentina/San_Juan', 'America/Argentina/Mendoza', 'America/Argentina/Rio_Gallegos', 'America/Argentina/Ushuaia'], 'code': 'AR', 'continent': 'South America', 'name': 'Argentina', 'capital': 'Buenos Aires'},
    {'timezones': ['Europe/Vienna'], 'code': 'AT', 'continent': 'Europe', 'name': 'Austria', 'capital': 'Vienna'},
    {'timezones': ['Australia/Lord_Howe', 'Australia/Hobart', 'Australia/Currie', 'Australia/Melbourne', 'Australia/Sydney', 'Australia/Broken_Hill', 'Australia/Brisbane', 'Australia/Lindeman', 'Australia/Adelaide', 'Australia/Darwin', 'Australia/Perth'], 'code': 'AU', 'continent': 'Oceania', 'name': 'Australia', 'capital': 'Canberra'},
    {'timezones': ['Asia/Baku'], 'code': 'AZ', 'continent': 'Asia', 'name': 'Azerbaijan', 'capital': 'Baku'},
    {'timezones': ['America/Barbados'], 'code': 'BB', 'continent': 'North America', 'name': 'Barbados', 'capital': 'Bridgetown'},
    {'timezones': ['Asia/Dhaka'], 'code': 'BD', 'continent': 'Asia', 'name': 'Bangladesh', 'capital': 'Dhaka'},
    {'timezones': ['Europe/Brussels'], 'code': 'BE', 'continent': 'Europe', 'name': 'Belgium', 'capital': 'Brussels'},
    {'timezones': ['Africa/Ouagadougou'], 'code': 'BF', 'continent': 'Africa', 'name': 'Burkina Faso', 'capital': 'Ouagadougou'},
    {'timezones': ['Europe/Sofia'], 'code': 'BG', 'continent': 'Europe', 'name': 'Bulgaria', 'capital': 'Sofia'},
    {'timezones': ['Asia/Bahrain'], 'code': 'BH', 'continent': 'Asia', 'name': 'Bahrain', 'capital': 'Manama'},
    {'timezones': ['Africa/Bujumbura'], 'code': 'BI', 'continent': 'Africa', 'name': 'Burundi', 'capital': 'Bujumbura'},
    {'timezones': ['Africa/Porto-Novo'], 'code': 'BJ', 'continent': 'Africa', 'name': 'Benin', 'capital': 'Porto-Novo'},
    {'timezones': ['Asia/Brunei'], 'code': 'BN', 'continent': 'Asia', 'name': 'Brunei Darussalam', 'capital': 'Bandar Seri Begawan'},
    {'timezones': ['America/La_Paz'], 'code': 'BO', 'continent': 'South America', 'name': 'Bolivia', 'capital': 'Sucre'},
    {'timezones': ['America/Noronha', 'America/Belem', 'America/Fortaleza', 'America/Recife', 'America/Araguaina', 'America/Maceio', 'America/Bahia', 'America/Sao_Paulo', 'America/Campo_Grande', 'America/Cuiaba', 'America/Porto_Velho', 'America/Boa_Vista', 'America/Manaus', 'America/Eirunepe', 'America/Rio_Branco'], 'code': 'BR', 'continent': 'South America', 'name': 'Brazil', 'capital': 'Bras\xc3\xadlia'},
    {'timezones': ['America/Nassau'], 'code': 'BS', 'continent': 'North America', 'name': 'Bahamas', 'capital': 'Nassau'},
    {'timezones': ['Asia/Thimphu'], 'code': 'BT', 'continent': 'Asia', 'name': 'Bhutan', 'capital': 'Thimphu'},
    {'timezones': ['Africa/Gaborone'], 'code': 'BW', 'continent': 'Africa', 'name': 'Botswana', 'capital': 'Gaborone'},
    {'timezones': ['Europe/Minsk'], 'code': 'BY', 'continent': 'Europe', 'name': 'Belarus', 'capital': 'Minsk'},
    {'timezones': ['America/Belize'], 'code': 'BZ', 'continent': 'North America', 'name': 'Belize', 'capital': 'Belmopan'},
    {'timezones': ['America/St_Johns', 'America/Halifax', 'America/Glace_Bay', 'America/Moncton', 'America/Goose_Bay', 'America/Blanc-Sablon', 'America/Montreal', 'America/Toronto', 'America/Nipigon', 'America/Thunder_Bay', 'America/Pangnirtung', 'America/Iqaluit', 'America/Atikokan', 'America/Rankin_Inlet', 'America/Winnipeg', 'America/Rainy_River', 'America/Cambridge_Bay', 'America/Regina', 'America/Swift_Current', 'America/Edmonton', 'America/Yellowknife', 'America/Inuvik', 'America/Dawson_Creek', 'America/Vancouver', 'America/Whitehorse', 'America/Dawson'], 'code': 'CA', 'continent': 'North America', 'name': 'Canada', 'capital': 'Ottawa'},
    {'timezones': ['Africa/Kinshasa', 'Africa/Lubumbashi'], 'code': 'CD', 'continent': 'Africa', 'name': 'Democratic Republic of the Congo', 'capital': 'Kinshasa'},
    {'timezones': ['Africa/Brazzaville'], 'code': 'CG', 'continent': 'Africa', 'name': 'Republic of the Congo', 'capital': 'Brazzaville'},
    {'timezones': ['Africa/Abidjan'], 'code': 'CI', 'continent': 'Africa', 'name': "C\xc3\xb4te d'Ivoire", 'capital': 'Yamoussoukro'},
    {'timezones': ['America/Santiago', 'Pacific/Easter'], 'code': 'CL', 'continent': 'South America', 'name': 'Chile', 'capital': 'Santiago'},
    {'timezones': ['Africa/Douala'], 'code': 'CM', 'continent': 'Africa', 'name': 'Cameroon', 'capital': 'Yaound\xc3\xa9'},
    {'timezones': ['Asia/Shanghai', 'Asia/Harbin', 'Asia/Chongqing', 'Asia/Urumqi', 'Asia/Kashgar'], 'code': 'CN', 'continent': 'Asia', 'name': "People's Republic of China", 'capital': 'Beijing'},
    {'timezones': ['America/Bogota'], 'code': 'CO', 'continent': 'South America', 'name': 'Colombia', 'capital': 'Bogot\xc3\xa1'},
    {'timezones': ['America/Costa_Rica'], 'code': 'CR', 'continent': 'North America', 'name': 'Costa Rica', 'capital': 'San Jos\xc3\xa9'},
    {'timezones': ['America/Havana'], 'code': 'CU', 'continent': 'North America', 'name': 'Cuba', 'capital': 'Havana'},
    {'timezones': ['Atlantic/Cape_Verde'], 'code': 'CV', 'continent': 'Africa', 'name': 'Cape Verde', 'capital': 'Praia'},
    {'timezones': ['Asia/Nicosia'], 'code': 'CY', 'continent': 'Asia', 'name': 'Cyprus', 'capital': 'Nicosia'},
    {'timezones': ['Europe/Prague'], 'code': 'CZ', 'continent': 'Europe', 'name': 'Czech Republic', 'capital': 'Prague'},
    {'timezones': ['Europe/Berlin'], 'code': 'DE', 'continent': 'Europe', 'name': 'Germany', 'capital': 'Berlin'},
    {'timezones': ['Africa/Djibouti'], 'code': 'DJ', 'continent': 'Africa', 'name': 'Djibouti', 'capital': 'Djibouti City'},
    {'timezones': ['Europe/Copenhagen'], 'code': 'DK', 'continent': 'Europe', 'name': 'Denmark', 'capital': 'Copenhagen'},
    {'timezones': ['America/Dominica'], 'code': 'DM', 'continent': 'North America', 'name': 'Dominica', 'capital': 'Roseau'},
    {'timezones': ['America/Santo_Domingo'], 'code': 'DO', 'continent': 'North America', 'name': 'Dominican Republic', 'capital': 'Santo Domingo'},
    {'timezones': ['America/Guayaquil', 'Pacific/Galapagos'], 'code': 'EC', 'continent': 'South America', 'name': 'Ecuador', 'capital': 'Quito'},
    {'timezones': ['Europe/Tallinn'], 'code': 'EE', 'continent': 'Europe', 'name': 'Estonia', 'capital': 'Tallinn'},
    {'timezones': ['Africa/Cairo'], 'code': 'EG', 'continent': 'Africa', 'name': 'Egypt', 'capital': 'Cairo'},
    {'timezones': ['Africa/Asmera'], 'code': 'ER', 'continent': 'Africa', 'name': 'Eritrea', 'capital': 'Asmara'},
    {'timezones': ['Africa/Addis_Ababa'], 'code': 'ET', 'continent': 'Africa', 'name': 'Ethiopia', 'capital': 'Addis Ababa'},
    {'timezones': ['Europe/Helsinki'], 'code': 'FI', 'continent': 'Europe', 'name': 'Finland', 'capital': 'Helsinki'},
    {'timezones': ['Pacific/Fiji'], 'code': 'FJ', 'continent': 'Oceania', 'name': 'Fiji', 'capital': 'Suva'},
    {'timezones': ['Europe/Paris'], 'code': 'FR', 'continent': 'Europe', 'name': 'France', 'capital': 'Paris'},
    {'timezones': ['Africa/Libreville'], 'code': 'GA', 'continent': 'Africa', 'name': 'Gabon', 'capital': 'Libreville'},
    {'timezones': ['Asia/Tbilisi'], 'code': 'GE', 'continent': 'Asia', 'name': 'Georgia', 'capital': 'Tbilisi'},
    {'timezones': ['Africa/Accra'], 'code': 'GH', 'continent': 'Africa', 'name': 'Ghana', 'capital': 'Accra'},
    {'timezones': ['Africa/Banjul'], 'code': 'GM', 'continent': 'Africa', 'name': 'The Gambia', 'capital': 'Banjul'},
    {'timezones': ['Africa/Conakry'], 'code': 'GN', 'continent': 'Africa', 'name': 'Guinea', 'capital': 'Conakry'},
    {'timezones': ['Europe/Athens'], 'code': 'GR', 'continent': 'Europe', 'name': 'Greece', 'capital': 'Athens'},
    {'timezones': ['America/Guatemala'], 'code': 'GT', 'continent': 'North America', 'name': 'Guatemala', 'capital': 'Guatemala City'},
    {'timezones': ['America/Guatemala'], 'code': 'GT', 'continent': 'North America', 'name': 'Haiti', 'capital': 'Port-au-Prince'},
    {'timezones': ['Africa/Bissau'], 'code': 'GW', 'continent': 'Africa', 'name': 'Guinea-Bissau', 'capital': 'Bissau'},
    {'timezones': ['America/Guyana'], 'code': 'GY', 'continent': 'South America', 'name': 'Guyana', 'capital': 'Georgetown'},
    {'timezones': ['America/Tegucigalpa'], 'code': 'HN', 'continent': 'North America', 'name': 'Honduras', 'capital': 'Tegucigalpa'},
    {'timezones': ['Europe/Budapest'], 'code': 'HU', 'continent': 'Europe', 'name': 'Hungary', 'capital': 'Budapest'},
    {'timezones': ['Asia/Jakarta', 'Asia/Pontianak', 'Asia/Makassar', 'Asia/Jayapura'], 'code': 'ID', 'continent': 'Asia', 'name': 'Indonesia', 'capital': 'Jakarta'},
    {'timezones': ['Europe/Dublin'], 'code': 'IE', 'continent': 'Europe', 'name': 'Republic of Ireland', 'capital': 'Dublin'},
    {'timezones': ['Asia/Jerusalem'], 'code': 'IL', 'continent': 'Asia', 'name': 'Israel', 'capital': 'Jerusalem'},
    {'timezones': ['Asia/Calcutta'], 'code': 'IN', 'continent': 'Asia', 'name': 'India', 'capital': 'New Delhi'},
    {'timezones': ['Asia/Baghdad'], 'code': 'IQ', 'continent': 'Asia', 'name': 'Iraq', 'capital': 'Baghdad'},
    {'timezones': ['Asia/Tehran'], 'code': 'IR', 'continent': 'Asia', 'name': 'Iran', 'capital': 'Tehran'},
    {'timezones': ['Atlantic/Reykjavik'], 'code': 'IS', 'continent': 'Europe', 'name': 'Iceland', 'capital': 'Reykjav\xc3\xadk'},
    {'timezones': ['Europe/Rome'], 'code': 'IT', 'continent': 'Europe', 'name': 'Italy', 'capital': 'Rome'},
    {'timezones': ['America/Jamaica'], 'code': 'JM', 'continent': 'North America', 'name': 'Jamaica', 'capital': 'Kingston'},
    {'timezones': ['Asia/Amman'], 'code': 'JO', 'continent': 'Asia', 'name': 'Jordan', 'capital': 'Amman'},
    {'timezones': ['Asia/Tokyo'], 'code': 'JP', 'continent': 'Asia', 'name': 'Japan', 'capital': 'Tokyo'},
    {'timezones': ['Africa/Nairobi'], 'code': 'KE', 'continent': 'Africa', 'name': 'Kenya', 'capital': 'Nairobi'},
    {'timezones': ['Asia/Bishkek'], 'code': 'KG', 'continent': 'Asia', 'name': 'Kyrgyzstan', 'capital': 'Bishkek'},
    {'timezones': ['Pacific/Tarawa', 'Pacific/Enderbury', 'Pacific/Kiritimati'], 'code': 'KI', 'continent': 'Oceania', 'name': 'Kiribati', 'capital': 'Tarawa'},
    {'timezones': ['Asia/Pyongyang'], 'code': 'KP', 'continent': 'Asia', 'name': 'North Korea', 'capital': 'Pyongyang'},
    {'timezones': ['Asia/Seoul'], 'code': 'KR', 'continent': 'Asia', 'name': 'South Korea', 'capital': 'Seoul'},
    {'timezones': ['Asia/Kuwait'], 'code': 'KW', 'continent': 'Asia', 'name': 'Kuwait', 'capital': 'Kuwait City'},
    {'timezones': ['Asia/Beirut'], 'code': 'LB', 'continent': 'Asia', 'name': 'Lebanon', 'capital': 'Beirut'},
    {'timezones': ['Europe/Vaduz'], 'code': 'LI', 'continent': 'Europe', 'name': 'Liechtenstein', 'capital': 'Vaduz'},
    {'timezones': ['Africa/Monrovia'], 'code': 'LR', 'continent': 'Africa', 'name': 'Liberia', 'capital': 'Monrovia'},
    {'timezones': ['Africa/Maseru'], 'code': 'LS', 'continent': 'Africa', 'name': 'Lesotho', 'capital': 'Maseru'},
    {'timezones': ['Europe/Vilnius'], 'code': 'LT', 'continent': 'Europe', 'name': 'Lithuania', 'capital': 'Vilnius'},
    {'timezones': ['Europe/Luxembourg'], 'code': 'LU', 'continent': 'Europe', 'name': 'Luxembourg', 'capital': 'Luxembourg City'},
    {'timezones': ['Europe/Riga'], 'code': 'LV', 'continent': 'Europe', 'name': 'Latvia', 'capital': 'Riga'},
    {'timezones': ['Africa/Tripoli'], 'code': 'LY', 'continent': 'Africa', 'name': 'Libya', 'capital': 'Tripoli'},
    {'timezones': ['Indian/Antananarivo'], 'code': 'MG', 'continent': 'Africa', 'name': 'Madagascar', 'capital': 'Antananarivo'},
    {'timezones': ['Pacific/Majuro', 'Pacific/Kwajalein'], 'code': 'MH', 'continent': 'Oceania', 'name': 'Marshall Islands', 'capital': 'Majuro'},
    {'timezones': ['Europe/Skopje'], 'code': 'MK', 'continent': 'Europe', 'name': 'Macedonia', 'capital': 'Skopje'},
    {'timezones': ['Africa/Bamako'], 'code': 'ML', 'continent': 'Africa', 'name': 'Mali', 'capital': 'Bamako'},
    {'timezones': ['Asia/Rangoon'], 'code': 'MM', 'continent': 'Asia', 'name': 'Myanmar', 'capital': 'Naypyidaw'},
    {'timezones': ['Asia/Ulaanbaatar', 'Asia/Hovd', 'Asia/Choibalsan'], 'code': 'MN', 'continent': 'Asia', 'name': 'Mongolia', 'capital': 'Ulaanbaatar'},
    {'timezones': ['Africa/Nouakchott'], 'code': 'MR', 'continent': 'Africa', 'name': 'Mauritania', 'capital': 'Nouakchott'},
    {'timezones': ['Europe/Malta'], 'code': 'MT', 'continent': 'Europe', 'name': 'Malta', 'capital': 'Valletta'},
    {'timezones': ['Indian/Mauritius'], 'code': 'MU', 'continent': 'Africa', 'name': 'Mauritius', 'capital': 'Port Louis'},
    {'timezones': ['Indian/Maldives'], 'code': 'MV', 'continent': 'Asia', 'name': 'Maldives', 'capital': 'Mal\xc3\xa9'},
    {'timezones': ['Africa/Blantyre'], 'code': 'MW', 'continent': 'Africa', 'name': 'Malawi', 'capital': 'Lilongwe'},
    {'timezones': ['America/Mexico_City', 'America/Cancun', 'America/Merida', 'America/Monterrey', 'America/Mazatlan', 'America/Chihuahua', 'America/Hermosillo', 'America/Tijuana'], 'code': 'MX', 'continent': 'North America', 'name': 'Mexico', 'capital': 'Mexico City'},
    {'timezones': ['Asia/Kuala_Lumpur', 'Asia/Kuching'], 'code': 'MY', 'continent': 'Asia', 'name': 'Malaysia', 'capital': 'Kuala Lumpur'},
    {'timezones': ['Africa/Maputo'], 'code': 'MZ', 'continent': 'Africa', 'name': 'Mozambique', 'capital': 'Maputo'},
    {'timezones': ['Africa/Windhoek'], 'code': 'NA', 'continent': 'Africa', 'name': 'Namibia', 'capital': 'Windhoek'},
    {'timezones': ['Africa/Niamey'], 'code': 'NE', 'continent': 'Africa', 'name': 'Niger', 'capital': 'Niamey'},
    {'timezones': ['Africa/Lagos'], 'code': 'NG', 'continent': 'Africa', 'name': 'Nigeria', 'capital': 'Abuja'},
    {'timezones': ['America/Managua'], 'code': 'NI', 'continent': 'North America', 'name': 'Nicaragua', 'capital': 'Managua'},
    {'timezones': ['Europe/Amsterdam'], 'code': 'NL', 'continent': 'Europe', 'name': 'Kingdom of the Netherlands', 'capital': 'Amsterdam'},
    {'timezones': ['Europe/Oslo'], 'code': 'NO', 'continent': 'Europe', 'name': 'Norway', 'capital': 'Oslo'},
    {'timezones': ['Asia/Katmandu'], 'code': 'NP', 'continent': 'Asia', 'name': 'Nepal', 'capital': 'Kathmandu'},
    {'timezones': ['Pacific/Nauru'], 'code': 'NR', 'continent': 'Oceania', 'name': 'Nauru', 'capital': 'Yaren'},
    {'timezones': ['Pacific/Auckland', 'Pacific/Chatham'], 'code': 'NZ', 'continent': 'Oceania', 'name': 'New Zealand', 'capital': 'Wellington'},
    {'timezones': ['Asia/Muscat'], 'code': 'OM', 'continent': 'Asia', 'name': 'Oman', 'capital': 'Muscat'},
    {'timezones': ['America/Panama'], 'code': 'PA', 'continent': 'North America', 'name': 'Panama', 'capital': 'Panama City'},
    {'timezones': ['America/Lima'], 'code': 'PE', 'continent': 'South America', 'name': 'Peru', 'capital': 'Lima'},
    {'timezones': ['Pacific/Port_Moresby'], 'code': 'PG', 'continent': 'Oceania', 'name': 'Papua New Guinea', 'capital': 'Port Moresby'},
    {'timezones': ['Asia/Manila'], 'code': 'PH', 'continent': 'Asia', 'name': 'Philippines', 'capital': 'Manila'},
    {'timezones': ['Asia/Karachi'], 'code': 'PK', 'continent': 'Asia', 'name': 'Pakistan', 'capital': 'Islamabad'},
    {'timezones': ['Europe/Warsaw'], 'code': 'PL', 'continent': 'Europe', 'name': 'Poland', 'capital': 'Warsaw'},
    {'timezones': ['Europe/Lisbon', 'Atlantic/Madeira', 'Atlantic/Azores'], 'code': 'PT', 'continent': 'Europe', 'name': 'Portugal', 'capital': 'Lisbon'},
    {'timezones': ['Pacific/Palau'], 'code': 'PW', 'continent': 'Oceania', 'name': 'Palau', 'capital': 'Ngerulmud'},
    {'timezones': ['America/Asuncion'], 'code': 'PY', 'continent': 'South America', 'name': 'Paraguay', 'capital': 'Asunci\xc3\xb3n'},
    {'timezones': ['Asia/Qatar'], 'code': 'QA', 'continent': 'Asia', 'name': 'Qatar', 'capital': 'Doha'},
    {'timezones': ['Europe/Bucharest'], 'code': 'RO', 'continent': 'Europe', 'name': 'Romania', 'capital': 'Bucharest'},
    {'timezones': ['Europe/Kaliningrad', 'Europe/Moscow', 'Europe/Volgograd', 'Europe/Samara', 'Asia/Yekaterinburg', 'Asia/Omsk', 'Asia/Novosibirsk', 'Asia/Krasnoyarsk', 'Asia/Irkutsk', 'Asia/Yakutsk', 'Asia/Vladivostok', 'Asia/Sakhalin', 'Asia/Magadan', 'Asia/Kamchatka', 'Asia/Anadyr'], 'code': 'RU', 'continent': 'Europe', 'name': 'Russia', 'capital': 'Moscow'},
    {'timezones': ['Africa/Kigali'], 'code': 'RW', 'continent': 'Africa', 'name': 'Rwanda', 'capital': 'Kigali'},
    {'timezones': ['Asia/Riyadh'], 'code': 'SA', 'continent': 'Asia', 'name': 'Saudi Arabia', 'capital': 'Riyadh'},
    {'timezones': ['Pacific/Guadalcanal'], 'code': 'SB', 'continent': 'Oceania', 'name': 'Solomon Islands', 'capital': 'Honiara'},
    {'timezones': ['Indian/Mahe'], 'code': 'SC', 'continent': 'Africa', 'name': 'Seychelles', 'capital': 'Victoria'},
    {'timezones': ['Africa/Khartoum'], 'code': 'SD', 'continent': 'Africa', 'name': 'Sudan', 'capital': 'Khartoum'},
    {'timezones': ['Europe/Stockholm'], 'code': 'SE', 'continent': 'Europe', 'name': 'Sweden', 'capital': 'Stockholm'},
    {'timezones': ['Asia/Singapore'], 'code': 'SG', 'continent': 'Asia', 'name': 'Singapore', 'capital': 'Singapore'},
    {'timezones': ['Europe/Ljubljana'], 'code': 'SI', 'continent': 'Europe', 'name': 'Slovenia', 'capital': 'Ljubljana'},
    {'timezones': ['Europe/Bratislava'], 'code': 'SK', 'continent': 'Europe', 'name': 'Slovakia', 'capital': 'Bratislava'},
    {'timezones': ['Africa/Freetown'], 'code': 'SL', 'continent': 'Africa', 'name': 'Sierra Leone', 'capital': 'Freetown'},
    {'timezones': ['Europe/San_Marino'], 'code': 'SM', 'continent': 'Europe', 'name': 'San Marino', 'capital': 'San Marino'},
    {'timezones': ['Africa/Dakar'], 'code': 'SN', 'continent': 'Africa', 'name': 'Senegal', 'capital': 'Dakar'},
    {'timezones': ['Africa/Mogadishu'], 'code': 'SO', 'continent': 'Africa', 'name': 'Somalia', 'capital': 'Mogadishu'},
    {'timezones': ['America/Paramaribo'], 'code': 'SR', 'continent': 'South America', 'name': 'Suriname', 'capital': 'Paramaribo'},
    {'timezones': ['Africa/Sao_Tome'], 'code': 'ST', 'continent': 'Africa', 'name': 'S\xc3\xa3o Tom\xc3\xa9 and Pr\xc3\xadncipe', 'capital': 'S\xc3\xa3o Tom\xc3\xa9'},
    {'timezones': ['Asia/Damascus'], 'code': 'SY', 'continent': 'Asia', 'name': 'Syria', 'capital': 'Damascus'},
    {'timezones': ['Africa/Lome'], 'code': 'TG', 'continent': 'Africa', 'name': 'Togo', 'capital': 'Lom\xc3\xa9'},
    {'timezones': ['Asia/Bangkok'], 'code': 'TH', 'continent': 'Asia', 'name': 'Thailand', 'capital': 'Bangkok'},
    {'timezones': ['Asia/Dushanbe'], 'code': 'TJ', 'continent': 'Asia', 'name': 'Tajikistan', 'capital': 'Dushanbe'},
    {'timezones': ['Asia/Ashgabat'], 'code': 'TM', 'continent': 'Asia', 'name': 'Turkmenistan', 'capital': 'Ashgabat'},
    {'timezones': ['Africa/Tunis'], 'code': 'TN', 'continent': 'Africa', 'name': 'Tunisia', 'capital': 'Tunis'},
    {'timezones': ['Pacific/Tongatapu'], 'code': 'TO', 'continent': 'Oceania', 'name': 'Tonga', 'capital': 'Nuku\xca\xbbalofa'},
    {'timezones': ['Europe/Istanbul'], 'code': 'TR', 'continent': 'Asia', 'name': 'Turkey', 'capital': 'Ankara'},
    {'timezones': ['America/Port_of_Spain'], 'code': 'TT', 'continent': 'North America', 'name': 'Trinidad and Tobago', 'capital': 'Port of Spain'},
    {'timezones': ['Pacific/Funafuti'], 'code': 'TV', 'continent': 'Oceania', 'name': 'Tuvalu', 'capital': 'Funafuti'},
    {'timezones': ['Africa/Dar_es_Salaam'], 'code': 'TZ', 'continent': 'Africa', 'name': 'Tanzania', 'capital': 'Dodoma'},
    {'timezones': ['Europe/Kiev', 'Europe/Uzhgorod', 'Europe/Zaporozhye', 'Europe/Simferopol'], 'code': 'UA', 'continent': 'Europe', 'name': 'Ukraine', 'capital': 'Kyiv'},
    {'timezones': ['Africa/Kampala'], 'code': 'UG', 'continent': 'Africa', 'name': 'Uganda', 'capital': 'Kampala'},
    {'timezones': ['America/New_York', 'America/Detroit', 'America/Kentucky/Louisville', 'America/Kentucky/Monticello', 'America/Indiana/Indianapolis', 'America/Indiana/Marengo', 'America/Indiana/Knox', 'America/Indiana/Vevay', 'America/Chicago', 'America/Indiana/Vincennes', 'America/Indiana/Petersburg', 'America/Menominee', 'America/North_Dakota/Center', 'America/North_Dakota/New_Salem', 'America/Denver', 'America/Boise', 'America/Shiprock', 'America/Phoenix', 'America/Los_Angeles', 'America/Anchorage', 'America/Juneau', 'America/Yakutat', 'America/Nome', 'America/Adak', 'Pacific/Honolulu'], 'code': 'US', 'continent': 'North America', 'name': 'United States', 'capital': 'Washington, D.C.'},
    {'timezones': ['America/Montevideo'], 'code': 'UY', 'continent': 'South America', 'name': 'Uruguay', 'capital': 'Montevideo'},
    {'timezones': ['Asia/Samarkand', 'Asia/Tashkent'], 'code': 'UZ', 'continent': 'Asia', 'name': 'Uzbekistan', 'capital': 'Tashkent'},
    {'timezones': ['Europe/Vatican'], 'code': 'VA', 'continent': 'Europe', 'name': 'Vatican City', 'capital': 'Vatican City'},
    {'timezones': ['America/Caracas'], 'code': 'VE', 'continent': 'South America', 'name': 'Venezuela', 'capital': 'Caracas'},
    {'timezones': ['Asia/Saigon'], 'code': 'VN', 'continent': 'Asia', 'name': 'Vietnam', 'capital': 'Hanoi'},
    {'timezones': ['Pacific/Efate'], 'code': 'VU', 'continent': 'Oceania', 'name': 'Vanuatu', 'capital': 'Port Vila'},
    {'timezones': ['Asia/Aden'], 'code': 'YE', 'continent': 'Asia', 'name': 'Yemen', 'capital': "Sana'a"},
    {'timezones': ['Africa/Lusaka'], 'code': 'ZM', 'continent': 'Africa', 'name': 'Zambia', 'capital': 'Lusaka'},
    {'timezones': ['Africa/Harare'], 'code': 'ZW', 'continent': 'Africa', 'name': 'Zimbabwe', 'capital': 'Harare'},
    {'timezones': ['Africa/Algiers'], 'code': 'DZ', 'continent': 'Africa', 'name': 'Algeria', 'capital': 'Algiers'},
    {'timezones': ['Europe/Sarajevo'], 'code': 'BA', 'continent': 'Europe', 'name': 'Bosnia and Herzegovina', 'capital': 'Sarajevo'},
    {'timezones': ['Asia/Phnom_Penh'], 'code': 'KH', 'continent': 'Asia', 'name': 'Cambodia', 'capital': 'Phnom Penh'},
    {'timezones': ['Africa/Bangui'], 'code': 'CF', 'continent': 'Africa', 'name': 'Central African Republic', 'capital': 'Bangui'},
    {'timezones': ['Africa/Ndjamena'], 'code': 'TD', 'continent': 'Africa', 'name': 'Chad', 'capital': "N'Djamena"},
    {'timezones': ['Indian/Comoro'], 'code': 'KM', 'continent': 'Africa', 'name': 'Comoros', 'capital': 'Moroni'},
    {'timezones': ['Europe/Zagreb'], 'code': 'HR', 'continent': 'Europe', 'name': 'Croatia', 'capital': 'Zagreb'},
    {'timezones': ['Asia/Dili'], 'code': 'TL', 'continent': 'Asia', 'name': 'East Timor', 'capital': 'Dili'},
    {'timezones': ['America/El_Salvador'], 'code': 'SV', 'continent': 'North America', 'name': 'El Salvador', 'capital': 'San Salvador'},
    {'timezones': ['Africa/Malabo'], 'code': 'GQ', 'continent': 'Africa', 'name': 'Equatorial Guinea', 'capital': 'Malabo'},
    {'timezones': ['America/Grenada'], 'code': 'GD', 'continent': 'North America', 'name': 'Grenada', 'capital': "St. George's"},
    {'timezones': ['Asia/Almaty', 'Asia/Qyzylorda', 'Asia/Aqtobe', 'Asia/Aqtau', 'Asia/Oral'], 'code': 'KZ', 'continent': 'Asia', 'name': 'Kazakhstan', 'capital': 'Astana'},
    {'timezones': ['Asia/Vientiane'], 'code': 'LA', 'continent': 'Asia', 'name': 'Laos', 'capital': 'Vientiane'},
    {'timezones': ['Pacific/Truk', 'Pacific/Ponape', 'Pacific/Kosrae'], 'code': 'FM', 'continent': 'Oceania', 'name': 'Federated States of Micronesia', 'capital': 'Palikir'},
    {'timezones': ['Europe/Chisinau'], 'code': 'MD', 'continent': 'Europe', 'name': 'Moldova', 'capital': 'Chi\xc5\x9fin\xc4\x83u'},
    {'timezones': ['Europe/Monaco'], 'code': 'MC', 'continent': 'Europe', 'name': 'Monaco', 'capital': 'Monaco'},
    {'timezones': ['Europe/Podgorica'], 'code': 'ME', 'continent': 'Europe', 'name': 'Montenegro', 'capital': 'Podgorica'},
    {'timezones': ['Africa/Casablanca'], 'code': 'MA', 'continent': 'Africa', 'name': 'Morocco', 'capital': 'Rabat'},
    {'timezones': ['America/St_Kitts'], 'code': 'KN', 'continent': 'North America', 'name': 'Saint Kitts and Nevis', 'capital': 'Basseterre'},
    {'timezones': ['America/St_Lucia'], 'code': 'LC', 'continent': 'North America', 'name': 'Saint Lucia', 'capital': 'Castries'},
    {'timezones': ['America/St_Vincent'], 'code': 'VC', 'continent': 'North America', 'name': 'Saint Vincent and the Grenadines', 'capital': 'Kingstown'},
    {'timezones': ['Pacific/Apia'], 'code': 'WS', 'continent': 'Oceania', 'name': 'Samoa', 'capital': 'Apia'},
    {'timezones': ['Europe/Belgrade'], 'code': 'RS', 'continent': 'Europe', 'name': 'Serbia', 'capital': 'Belgrade'},
    {'timezones': ['Africa/Johannesburg'], 'code': 'ZA', 'continent': 'Africa', 'name': 'South Africa', 'capital': 'Pretoria'},
    {'timezones': ['Europe/Madrid', 'Africa/Ceuta', 'Atlantic/Canary'], 'code': 'ES', 'continent': 'Europe', 'name': 'Spain', 'capital': 'Madrid'},
    {'timezones': ['Asia/Colombo'], 'code': 'LK', 'continent': 'Asia', 'name': 'Sri Lanka', 'capital': 'Sri Jayewardenepura Kotte'},
    {'timezones': ['Africa/Mbabane'], 'code': 'SZ', 'continent': 'Africa', 'name': 'Swaziland', 'capital': 'Mbabane'},
    {'timezones': ['Europe/Zurich'], 'code': 'CH', 'continent': 'Europe', 'name': 'Switzerland', 'capital': 'Bern'},
    {'timezones': ['Asia/Dubai'], 'code': 'AE', 'continent': 'Asia', 'name': 'United Arab Emirates', 'capital': 'Abu Dhabi'},
    {'timezones': ['Europe/London'], 'code': 'GB', 'continent': 'Europe', 'name': 'United Kingdom', 'capital': 'London'},
    ]


    info_of_zoom = {
            'Date': None,
            'Emails': None,
            'Time': None,
            'Time/Date Object': None,
            'Timezone': '',
            'Topic':None,
            'Websites':None,
            'zoom_url':None
        }

    s = Service(driverpath)
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--lang=en")  

    driver = webdriver.Chrome(service=s,options=opts)

    driver.set_page_load_timeout(25)

    driver.get(url)
    htmltext = driver.page_source




    soup = BeautifulSoup(htmltext, 'html.parser')
    found_timezone = False
    email_regex= "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"

    if 'Webinar has expired' in htmltext or 'Webinar is expired' in htmltext:
            return None
    else:
            info_of_zoom['zoom_url'] = url
        # Timezone finder

    if found_timezone == False:
            for a in soup.find_all('a', {'id':'switch_timezone'}):

                timezone_str = a.text
                found_timezone = True

    if found_timezone == False:
            for b in soup.find_all('button', {'id':'switch_timezone'}):
                timezone_str = b.text
                found_timezone = True

        # End of timezone finder
        
        


        # Date finder
    found_date = False

    if found_date == False:
            for div in soup.find_all('div', {'class':'form-group horizontal'}):
                if 'Time' in div.text:
                    raw_text = div.text.strip()

                    try:
                        info_of_zoom['Date'] = re.findall(string=raw_text, pattern='([A-Z][a-z][a-z] \d+, [2][0]\d\d)')[0]                
                        found_date = True
                    except:
                        pass

        # End of date finder

        #Website finder !
    info_of_zoom['Websites'] = []
    try:
            urls = re.findall(string=htmltext,pattern=regex_url)

            found_urls = True
    except:
            found_urls = False

    if found_urls:
            for url in urls:
                if 'zoom' not in url and url not in info_of_zoom['Websites']:
                    info_of_zoom['Websites'].append(url)
        
    if info_of_zoom['Websites'] == []: info_of_zoom['Websites'] = None
    else:
            for webs in info_of_zoom['Websites']:
                if 'https://' in webs:
                    if not len(webs.replace('https://','')) > 1:
                        info_of_zoom['Websites'].remove(webs)
        # End of website finder?


        # Topic finder !!
    found_topic = False

    if found_topic == False:
            for div in soup.find_all('div', {'class':'form-group horizontal'}):

                if 'Topic' in div.text:
                    info_of_zoom['Topic'] = div.text.replace('Topic','').strip()
                    found_topic = True
                    break



        # End of Topic finder


    #  Time finder !!! 
    found_time = False
    if found_time == False:
            for d in soup.find_all('div', {'class':'controls'}):

                try:
                    info_of_zoom['Time'] = re.findall(string=d.text,pattern='(\d\d:\d\d [A-Z][A-Z])')[0]
                    found_time = True
                except:
                    pass

    if found_time == False:
            for ddd in soup.find_all('span', {'class':'real-label-span'}):
                if 'AM' in ddd.text or 'PM' in ddd.text:

                    time_str = ddd.text.strip()

                    info_of_zoom['Time'] = re.findall(string=ddd.text,pattern='(\d\d:\d\d [A-Z][A-Z])')[0]
                    found_time = True

    if found_time == False:
            for d in soup.find_all('div', {'class':'controls'}):
                if ('AM' in d.text or 'PM' in d.text) and 'Please' not in d.text:
                    time_str = d.text.split('in')[0].strip()
                    try:
                        info_of_zoom['Time'] = re.findall(string=time_str,pattern='(\d\d:\d\d [A-Z][A-Z])')[0]
                        found_time = True
                    except:
                        continue

        # End Time finder



        # Email gatherer
    emails = re.findall(email_regex, str(htmltext))
    emails_f = []
    if 'name@domain.com' in emails:
            emails.remove('name@domain.com')
    for em in emails:
            if em not in emails_f:
                emails_f.append(em)

    info_of_zoom['Emails'] = emails_f
        # End of email gatherer


        # timezone formatter
    if found_timezone:
            if ' ' in timezone_str.strip():
                timezone_str = timezone_str.strip().replace(' ','_')
            else:
                timezone_str = timezone_str.strip()        
            
            if 'Canada' in timezone_str:
                timezone_founded = "America/"

            for country in countries:
                for timezone in country['timezones']:
                    if timezone_str in timezone:
                        timezone_founded = timezone
                        break
            try:
                timezone = timezone_founded.split('/')[0]
                if timezone == 'Pacific' or timezone == 'Canada' or timezone == 'America' or timezone == 'Indian': info_of_zoom['Timezone'] = 'US'
                elif timezone == 'Europe': info_of_zoom['Timezone'] = 'EU'
                elif timezone in ['Asia','Atlantic','Africa','Australia','Pacific','SST']: info_of_zoom['Timezone'] = 'AS'
            except:
                info_of_zoom['Timezone'] = ''


        # End of timezone formatter
            
        # Time\date object creator
    if found_date and found_time:
        
            obj = info_of_zoom['Date'] + ' ' +info_of_zoom['Time']
            if len(obj.split()) == 5:
                if obj.split()[4].strip() not in ['AM','PM','am','pm','Am','Pm']:
                    print(f'\n\n Unknown word in time "AM OR PM ?" please send to Emir for inspection: {obj} \n Using "AM" as default.\n')
                    obj = obj.replace(obj.split()[4],'AM')
                    info_of_zoom['Time/Date Object'] = int(datetime.datetime.strptime(obj, '%b %d, %Y %H:%M %p').timestamp())
                else:
                    info_of_zoom['Time/Date Object'] = int(datetime.datetime.strptime(obj, '%b %d, %Y %H:%M %p').timestamp())
    else:
            info_of_zoom['Time/Date Object'] = 0
            info_of_zoom['Date'] = 'Jan 01, 1970'
            info_of_zoom['Time'] = '12:00 AM'
            info_of_zoom['Timezone'] = ''

        # end of time\date creator    


    return info_of_zoom