
# Import Splinter and BeautifulSoup
from os import error
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
# Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now(),
      'scrape_data':hemispheres_images(browser)

    }
# Stop webdriver and return data
    browser.quit()
    return data



#assign the url and visit the mars nasa news site 
def mars_news(browser):
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)
   
# Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

#Set up HTML parser 
    html = browser.html 
    news_soup = soup(html, "html.parser")
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except:
        return None, None

    return news_title, news_p


# # use markdown to separate the article scraping from the image scraping.
# 
def featured_image(browser): 
# Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)
# Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

# Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

# Find the relative image url--full image url 
#get('src') pull the link to the image 
    try: 
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError: 
        return None     

#add the base URL to create an absolute URL
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
    return img_url



#panda built-in .read_html() to scrape entire mars profile table 

def mars_facts():
    try:
      # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]
    except BaseException:
        return None
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

#Mars Hemispheres 
def hemispheres_images(browser):
    url = 'https://marshemispheres.com'
    browser.visit(url)
    html = browser.html
    all_urls_to_scrape = soup(html, 'html.parser')
    items = []
    try:
        for a in all_urls_to_scrape.find_all('a',class_='itemLink'):
            items.append(a.attrs.get('href'))
    except AttributeError:
        print('none')
    # pull urls  from item list based on index position
    urls_to_open = [items[i] for i in (0,2,4,6,8)]
    # remove the blank url 
    urls_to_open.pop()
    urls_to_open
    #initialize empty list for image_url and title
    hemisphere_image_urls = []
    try:
        for url_i in urls_to_open:
            browser.visit(url+'/'+url_i)
            visted_url_html = browser.html
            visited_url_soup = soup(visted_url_html,'html.parser')
            img_url = visited_url_soup.select('.downloads ul li a')[0].get('href')
            img_title = visited_url_soup.select('.cover h2')[0].text
            hemisphere_image_urls.append({'image_url':url+'/'+img_url, 'image_title':img_title})
    except BaseException:
        print('none')
    
    return hemisphere_image_urls



if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())


