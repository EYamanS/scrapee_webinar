# scrapee_webinar
Online webinar page info scraper supporting (event.on24.com,register.gotowebinar.com,XXXXX.zoom.us,brigttalk) urls

**Example Output: ** 

    info_of_zoom = {
            'Date': 16/10/2020,
            'Emails': ['eyamansivrikaya@outlook.com','example@domain.com'],
            'Time': None,
            'Time/Date Object': 1647174775,
            'Timezone': 'EU',
            'Topic': 'How does scrapee_webinar work?',
            'Websites': ['https://github.com/EYamanS/','https://www.linkedin.com/in/emir-yaman-sivrikaya/'],
            'zoom_url': 'https://www.the-url-you-specified'
        }
        
        
        

scrapee_webinar uses chrome driver so, **You have to specify a chrome-driverpath for every function.**
Download ChromeDriver from : https://chromedriver.chromium.org/downloads
**Important:** You also have to have chrome installed and your chrome version should match chromedriver version.


**How to Use ?**

**event.on24.com/..**
scrapee_on24(url,driverpath)

**register.gotowebinar.com/..**
scrapee_gtw(url,driverpath)

**brighttalk.com/..**
scrapee_brighttalk(url,driverpath)

**XXX.zoom.XX/...**
scrapee_zoom(url,driverpath)

