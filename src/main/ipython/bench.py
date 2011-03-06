#
# Copyright 2011 Romain Gilles
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
''''
aims to provide a simple integration of selenium WebDriver
but in peformance oriented.
'''
import webbench

USAGE='''
'''

def setup():
    return webbench.Ie()

def run(browser):
    #browser.get('http://ptxs11290-a:8092/kplustp/')
    browser.get('http://www.google.com')
    #print browser.current_url
    #user_name = browser.find_element_by_name('j_username')
    #user_name.send_keys('kplustp')
    #password = browser.find_element_by_name('j_password')
    #password.send_keys('kplustp20')
    
    #password.submit()
    
    print browser.current_url
    #browser.quit()
    
    #imapuser
    #passwd
    #button

if __name__=='__main__':
    browser = setup()
    run(browser)
    
    browser2 = setup()
    