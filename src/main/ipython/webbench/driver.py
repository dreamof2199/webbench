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

#import sys
#sys.path.append('c:\\programs\\selenium\\selenium-dotnet-2.0b2')
import clr
#clr.AddReference('WebDriver.Common')
#clr.AddReference('WebDriver.IE')
#clr.AddReference('WebDriver.Firefox')
#from OpenQA.Selenium import By as _By
#from OpenQA.Selenium.IE import InternetExplorerDriver
#from OpenQA.Selenium.Firefox import FirefoxDriver

clr.AddReference('WebBenchBrowser')
clr.AddReference('NLog')

from WebBenchBrowser import Browser as _Browser
#from WebBenchBrowser import _WebElement

from NLog import LogManager

import time
import inspect
from contextlib import contextmanager
import random
import threading

# create logger
logger = LogManager.GetLogger("webbench.driver")

_action_counter = 0
NO_ACTION_ID = -1

@contextmanager
def action(obj, name):
    global _action_counter
    _action_counter = _action_counter + 1
    logger.Debug('execute action: #{0}, {1}', _action_counter, name)
    #if hasattr(obj,'action'):
    obj.setaction(name)
    obj.setactionid(_action_counter)
    if obj.getrandom() > 0:
        sleep_time = random.random() * obj.getrandom()
        logger.Debug('random: sleep {0}s before executing action {1}', sleep_time, name)
        time.sleep(sleep_time)
    try:
        yield
    finally:
        obj.setaction(None)
        obj.setactionid(NO_ACTION_ID)

def random_action():
    def _action(f):
        def __action(*args, **kargs):
            if inspect.ismethod(f) and f.im_self.getrandom() > 0:
                localdata = threading.local()
                if not localdata.random : 
                    localdata.random = random.Random()
                    localdata.random.seed()
                wait_time = f.im_self.getrandom() * localdata.random.random()
                logger.Debug('sleep {0}s before action execution', wait_time)
                time.sleep(wait_time)
            return f(*args, **kargs)
        __action.func_name = f.func_name
        return __action
    return _action

class Wrapper(object):
    def __init__(self, delegate):
        """Creates a webbench wrapper instance.
        A Wrapper delegate the action to the wrapped object.

        Args:
          delegate: a IWebElement object on which the action will 
                    be delegate and the execution time will be computed
          //timeout:  the amount of time to wait for extension socket
        """
        self.delegate = delegate
    
    def getaction(self):
        return self.delegate.Action
    
    def setaction(self, name):
        self.delegate.Action = name
    action = property(getaction, setaction, None, "I'm the 'action' property.")
    
    def getactionid(self):
        return self.delegate.ActionId
    
    def setactionid(self, id):
        self.delegate.ActionId = id
    action_id = property(getactionid, setactionid, None, "I'm the 'action_id' property.")
    
    def getrandom(self):
        return 0

class SearchContext(Wrapper):
    #Find element
    def find_element(self, by):
        return None #FIXME

    def find_elements(self, by):
        return None #FIXME
    
    def find_element_by_id(self, id):
        """Finds element by id."""
        return _wrap_to_webelement(self, self.delegate.FindElementById(id))
        
    #def find_elements_by_id(self, id):
    #    """Finds element by id."""
    #    return _wrap_to_webelements(self, self.delegate.FindElementsBy(_By.Id(id)))

    #def find_element_by_xpath(self, xpath):
    #    """Finds an element by xpath."""
    #    return _wrap_to_webelement(self.delegate.FindElement(_By.XPath(xpath)))
    #
    #def find_elements_by_xpath(self, xpath):
    #    """Finds multiple elements by xpath."""
    #    return _wrap_to_webelements(self.delegate.FindElements(_By.XPath(xpath)))

    def find_element_by_link_text(self, link_text):
        """Finds an element by its link text."""
        return _wrap_to_webelement(self, self.delegate.FindElementByLinkText(link_text))

    def find_elements_by_link_text(self, link_text):
        """Finds elements by their link text."""
        return _wrap_to_webelements(self, self.delegate.FindElementsByLinkText(link_text))

    def find_element_by_partial_link_text(self, link_text):
        """Finds an element by a partial match of its link text."""
        return _wrap_to_webelement(self, self.delegate.FindElementByPartialLinkText(link_text))

    def find_elements_by_partial_link_text(self, link_text):
        """Finds elements by a partial match of their link text."""
        return _wrap_to_webelements(self, self.delegate.FindElementsByPartialLinkText(link_text))

    def find_element_by_name(self, name, url = None):
        """Finds an element by its name."""
        return _wrap_to_webelement(self, self.delegate.FindElementByName(name, url))

    def _find_elements_by_name(self, name):
        """Finds elements by their name."""
        return _wrap_to_webelements(self, self.delegate.FindElementsByName(name))

    def find_element_by_tag_name(self, name):
        """Finds an element by its tag name."""
        return _wrap_to_webelement(self, self.delegate.FindElementByTagName(name))

    def find_elements_by_tag_name(self, name):
        """Finds elements by their tag name."""
        return _wrap_to_webelements(self, self.delegate.FindElementsByTagName(name))

    def find_element_by_class_name(self, name):
        """Finds an element by their class name."""
        return _wrap_to_webelement(self, self.delegate.FindElementByClassName(name))
    #
    def find_elements_by_class_name(self, name):
        """Finds elements by their class name."""
        return _wrap_to_webelements(self, self.delegate.FindElementsByClassName(name))
    #
    #def find_element_by_css_selector(self, css_selector):
    #    """Find and return an element by CSS selector."""
    #    return _wrap_to_webelement(self.delegate.FindElement(_By.CssSelector(css_selector)))
    #
    #def find_elements_by_css_selector(self, css_selector):
    #    """Find and return list of multiple elements by CSS selector."""
    #    return _wrap_to_webelements(self.delegate.FindElements(_By.CssSelector(css_selector)))
    #

def _wrap_to_webelements(parent, list_):
    result = []
    for element in list_:
        result.append(_wrap_to_webelement(parent,element))
    return tuple(result)

def _wrap_to_webelement(parent, delegate):
    return WebElement(parent, delegate) if delegate else None

    
    
#class WebElement(SearchContext):
class WebElement(Wrapper):
    def __init__(self, parent, delegate):
        Wrapper.__init__(self, delegate)
        self._parent_browser = parent
        
    def getrandom(self):
        return self._parent_browser.getrandom()
    @property
    def tag_name(self):
        """Gets this element's tagName property."""
        return self.delegate.TagName

    @property
    def text(self):
        """Gets the text of the element."""
        return self.delegate.Text

    @property
    def parent(self):
        """Gets the text of the element."""
        return _wrap_to_webelement(self._parent_browser, self.delegate.Parent)

    @property
    def outer_html(self):
        """Gets the outer html of the element."""
        return self.delegate.OuterHtml
    
    @property
    def inner_html(self):
        """Gets the inner html of the element."""
        return self.delegate.InnerHtml
    
    def click(self, url = None):
        """Clicks the element."""
        self.delegate.Click(url)
    
    def click_delegate(self, delegate = None):
        """Clicks the element."""
        self.delegate.ClickDelegate(delegate)

    def submit(self):
        """Submits a form."""
        self.delegate.Submit()

    @property
    def parent_browser(self):
        return self._parent_browser

    @property
    def id(self):
        return self.delegate.GetAttribute('id')

    @property
    def value(self):
        """Gets the value of the element's value attribute."""
        return self.delegate.Value

    def clear(self):
        """Clears the text if it's a text entry element."""
        self.delegate.Clear()

    def get_attribute(self, name):
        """Gets the attribute value."""
        return self.delegate.GetAttribute(name)
        
    @property
    def children(self):
        return _wrap_to_webelements(self._parent_browser, self.delegate.Children)

    #def toggle(self):
    #    """Toggles the element state."""
    #    return self.delegate.Toggle()

    #def is_selected(self):
    #    """Whether the element is selected."""
    #    return self.Selected
    #
    #def select(self):
    #    """Selects an element."""
    #    self.delegate.Select()
    #
    def is_enabled(self):
        """Whether the element is enabled."""
        return self.delegate.Enabled

    def send_keys(self, value):
        """Simulates typing into the element."""
        self.delegate.SendKeys(value)

    def is_link(self):
        """Whether the element is an anchor."""
        return self.delegate.IsLink()

    def is_input(self):
        """Whether the element is an input."""
        return self.delegate.IsInput()
    
    def is_text_area(self):
        """Whether the element is a text area."""
        return self.delegate.IsTextArea()
    
    def support_value(self):
        """Whether the element supports value more formally is a text area or an input."""
        return self.delegate.SupportValue()
    
    
    # RenderedWebElement Items
    #def is_displayed(self):
    #    """Whether the element would be visible to a user"""
    #    return self.delegate.Displayed

    #@property
    #def size(self):
    #    """ Returns the size of the element """
    #    return self.delegate.Size
    #
    #@property
    #def location(self):
    #    """ Returns the coordinates of the upper-left corner of this element relative to the upper-left corner of the page. """
    #    return self.delegate.Location
    #
    #def value_of_css_property(self, property_name):
    #    """ Returns the value of a CSS property """
    #    return self.delegate.GetValueOfCssProperty(property_name)
    #
    #def hover(self):
    #    """ Simulates the user hovering the mouse over this element. """
    #    self.delegate.Hover()
    #
    #def drag_and_drop_by(self, move_right, move_down):
    #    self.delegate.DragAndDropBy(move_right, move_down)
    #
    #def drag_and_drop_on(self, element):
    #    self.delegate.DragAndDropOn(element.delegate)
    #

#class By(Wrapper):
#    @staticmethod
#    def id(id):
#        By.Id(id)
#    
#    @staticmethod
#    def name(name):
#        _By.Name(name)
#    
#    @staticmethod
#    def tag_name(name):
#        _By.TagName(name)
#    
#    @staticmethod
#    def link_text(text):
#        _By.LinkText(text)
#    
#    @staticmethod
#    def partial_link_text(text):
#        _By.PartialLinkText(text)
#    
#    @staticmethod
#    def class_name(name):
#        _By.ClassName(name)
#    @staticmethod
#    def css_selector(selector):
#        _By.CssSelector(selector)
#    
#    @staticmethod
#    def xpath(xpath):
#        _By.XPath(xpath)
#
#class Alert(Wrapper):
#    pass

#class WebDriver(SearchContext):
class WebDriver(SearchContext):
    def __init__(self, delegate, random_time = 0):
        SearchContext.__init__(self, delegate)
        self.random_time = random_time
    def getrandom(self):
        return self.random_time
    @property
    def name(self):
        """Returns the name of the underlying browser for this instance."""
        return self.delegate.BrowserName
    
    @property
    def action(self, action):
        self.delegate.Action = action
    
    @property
    def all_links(self):
        """Returns all the links available in the docuement."""
        return _wrap_to_webelements(self, self.delegate.AllLinks)
    
    @property
    def all_images(self):
        """Returns all the images available in the docuement."""
        return _wrap_to_webelements(self, self.delegate.AllImages)
    
    @property
    def title(self):
        """Gets the title of the current page."""
        return self.delegate.Title
    
    @property
    def current_url(self):
        """Gets the current url."""
        return self.delegate.Url
    
    def get_page_source(self):
        """Gets the page source."""
        return self.delegate.PageSource

    def close(self):
        """Closes the current window."""
        self.delegate.Close()
        self.delegate.Dispose(True)
    
    def quit(self):
        """Quits the driver and close every associated window."""
        self.delegate.Quit()
        self.delegate.Dispose()
    
    #def get_current_window_handle(self):
    #    return self.delegate.GetWindowHandle()
    #
    #def get_window_handles(self):
    #    return self.delegate.GetWindowHandles()
    #
    #
    #Target Locators
    #def switch_to_active_element(self):
    #    """Returns the element with focus, or BODY if nothing has focus."""
    #    return WebElement(self.delegate.SwitchTo().ActiveElement())
    #
    #def switch_to_window(self, window_name):
    #    """Switches focus to a window."""
    #    self.delegate.SwitchTo().Window(window_name)
    #
    #def switch_to_frame(self, index_or_name_or_element):
    #    """Switches focus to a frame by index or name or web element."""
    #    if isinstance(index_or_name_or_element,WebElement):
    #        self.delegate.SwitchTo().Frame(index_or_name_or_element.delegate)
    #    else:
    #        #if isinstance(index_or_name_or_element,int):
    #        self.delegate.SwitchTo().Frame(index_or_name_or_element)
    #
    #def switch_to_default_content(self):
    #    """Switch to the default frame"""
    #    self.delegate.SwitchTo().DefaultContent()
    #    
    #
    #def switch_to_alert(self):
    #    """ Switch to the alert on the page """
    #    return self.delegate.SwitchTo().Alert() #TODO FIXME wrap it !!!
    
    
    #Navigation 
    def get(self, url):
        """Loads a web page in the current browser."""
        self.delegate.Get(url)
    
    def back(self):
        """Goes back in browser history."""
        self.delegate.Back()

    def forward(self):
        """Goes forward in browser history."""
        self.delegate.Forward()

    def refresh(self, delegate = None):
        """Refreshes the current page."""
        self.delegate.DoRefresh(delegate)
        
    def hide(self):
        if self.delegate.Visible:
            self.delegate.Visible = False

class Ie (WebDriver):
    def __init__(self, name = "default", random_time = 0):
        WebDriver.__init__(self, _Browser.NewBrowser(name), random_time)
    def run(self):
        self.delegate.Run()
        

#class FireFox (WebDriver):
#    def __init__(self):
#        WebDriver.__init__(self, FireFoxDriver())
#