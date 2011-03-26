import time

WAIT_TIME = None

def setup(config):
    global WAIT_TIME
    debug('nothing to setup')
    WAIT_TIME = config.getint('DEFAULT','wait_time')

def run2(browser):
    debug('setup run scenario')
    browser.get('http://code.google.com/intl/fr-FR/')
    element = browser.find_element_by_link_text('Google Web Toolkit')
    element.click()
    browser.back()
    element = browser.find_element_by_link_text('APIs & Tools')
    element.click()
    
def run(browser):
    info('start run')
    debug('sleep {0}s', WAIT_TIME)
    time.sleep(WAIT_TIME)
    with action(browser, 'get main page'):
        browser.get('http://localhost:8080/examples/')
    debug('sleep {0}s', WAIT_TIME)
    time.sleep(WAIT_TIME)
    element = browser.find_element_by_link_text('Servlets examples')
    with action(element, 'click on servlet examples link'):
        element.click('/examples/servlets/')
    debug('sleep {0}s', WAIT_TIME)
    time.sleep(WAIT_TIME)
    browser.back()
    time.sleep(WAIT_TIME)