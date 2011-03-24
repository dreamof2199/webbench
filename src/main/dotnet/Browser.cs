/*
 * Copyright 2011 Romain Gilles
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Collections.ObjectModel;
using System.Threading;
using System.Threading.Tasks;
using System.Diagnostics;
using NLog;

using System.Security.Permissions;

namespace WebBenchBrowser
{
    /**
     * thread tuto: http://msdn.microsoft.com/en-us/library/aa645740(VS.71).aspx
     * document completed:
     *    - http://stackoverflow.com/questions/840813/how-to-use-webbrowser-control-documentcompleted-event-in-c
     *    - http://stackoverflow.com/questions/3431451/webbrowser-control-document-completed-fires-more-than-once
     *    - http://msdn.microsoft.com/en-us/library/aa752041.aspx
     *    - ...
     * ? IE http://www.codeproject.com/KB/toolbars/MicrosoftMshtml.aspx?msg=2893585
     * 
     * Nlog:
     *   - home: http://nlog-project.org/
     *   - Programmatic config: http://nlog-project.org/wiki/Configuration_API
     *   - File config: http://nlog-project.org/wiki/Configuration_file
     *   - Layout: http://nlog-project.org/wiki/Layout_renderers
     * Perf: http://msdn.microsoft.com/en-us/library/15t15zda.aspx
     * Delegate:
     *  - todo
     */
    //[assembly: PermissionSetAttribute(SecurityAction.InheritanceDemand, Name = "FullTrust")]
    //[assembly: PermissionSetAttribute(SecurityAction.LinkDemand, Name = "FullTrust")]
    public partial class Browser : Form
    {
        private static Logger logger = LogManager.GetLogger("webbench.browser");
        private static Logger actionLogger = LogManager.GetLogger("webbench.action");
        private Barrier barrier;
        private Stopwatch stopwatch = new Stopwatch();
        private HtmlDocument document;
        private volatile string documentText;
        private Barrier startupAction;
        private volatile NavigationCompleteDelegate navigationUrl_;
        private string name_;
        private volatile string action_;
        
        public string Action { get 
            {
                return action_;
            } 
            set
            {
                action_ = value;
            } 
        }

        private volatile int actionId_;

        public int ActionId
        {
            get
            {
                return actionId_;
            }
            set
            {
                actionId_ = value;
            }
        }

        public string BrowserName
        {
            get
            {
                return name_;
            }
        }

        public NavigationCompleteDelegate NavigationUrl 
        {
            get
            {
                return navigationUrl_;
            } 
            set 
            {
                navigationUrl_ = value;
            }
        }

        public Collection<WebElement> All 
        {
            get
            {
                HtmlElementCollection htmlElements = null;
                lock (this)
                {
                    htmlElements = document.All;
                }
                Collection<WebElement> result = new Collection<WebElement>();
                foreach (HtmlElement e in htmlElements)
                {
                    result.Add(WebElement.newElement(this, e));
                }
                return result;
            }
        }

        public Collection<WebElement> AllImages
        {
            get
            {
                HtmlElementCollection htmlElements = null;
                lock (this)
                {
                    htmlElements = document.Images;
                }
                Collection<WebElement> result = new Collection<WebElement>();
                foreach (HtmlElement e in htmlElements)
                {
                    result.Add(WebElement.newElement(this, e));
                }
                return result;
            }
        }

        public Collection<WebElement> AllLinks { 
            get
            {
                HtmlElementCollection htmlElements = null;
                lock (this)
                {
                    //htmlElements = document.GetElementsByTagName("a");
                    htmlElements = document.Links;
                }
                Collection<WebElement> result = new Collection<WebElement>();
                foreach (HtmlElement e in htmlElements)
                {
                    result.Add(WebElement.newElement(this, e));
                }
                return result;
            }
        } 

        static Browser()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
        }

        public static Browser NewBrowser(string name)
        {
            logger.Debug("create new browser");
            Application.DoEvents();
            return new Browser(name);
        }

        private Browser(string name)
        {
            name_ = name;
            InitializeComponent();
            webBrowser.Navigating += new WebBrowserNavigatingEventHandler(webBrowser_Navigating);
            webBrowser.AllowNavigation = true;
            //webBrowser.ScriptErrorsSuppressed = true;
            webBrowser.HandleCreated += new EventHandler(webBrowser_HandleCreated);
        }

        public string PageSource {
            get
            {
                return documentText;
            }
        }

        public string Url
        {
            get 
            {
                return toolStripUrl.Text;
            }
        }

        public string Title 
        {
            get 
            {
                return webBrowser.DocumentTitle;
            }
        }

        public void Run()
        {
            logger.Debug("run browser in new thread");
            Thread t = new Thread(start);
            t.SetApartmentState(ApartmentState.STA);
            t.Start();
            //browser.Activated += new System.EventHandler(scenario_free);
            using (startupAction = new Barrier(2))
            {
                Shown += new System.EventHandler(startup);
                startupAction.SignalAndWait();
            }
        }

        private void start() 
        {
            Application.Run(this);
        }

        private void startup(object sender, EventArgs e)
        {
            startupAction.SignalAndWait();
            //((SHDocVw.WebBrowser)webBrowser.ActiveXInstance).RegisterAsBrowser = true;
        }

        public void SetBarrier(Barrier barrier)
        {
            this.barrier = barrier;
        }

        //protected override void OnActivated(EventArgs e)
        //{
        //    base.OnActivated(e);
        //}

        private void home_Click(object sender, EventArgs e)
        {
            webBrowser.GoHome();
        }

        private void stop_Click(object sender, EventArgs e)
        {
            webBrowser.Stop();
        }

        private void refresh_Click(object sender, EventArgs e)
        {
            Refresh(null);
        }

        private void forward_Click(object sender, EventArgs e)
        {
            Forward(null);
        }

        private void back_Click(object sender, EventArgs e)
        {
            Back(null);
        }

        private void go_Click(object sender, EventArgs e)
        {
            Get(toolStripUrl.Text, null);
        }

        //Navigating actions
        public void Back()
        {
            using (Barrier action = new Barrier(2))
            {
                Back(action);
                action.SignalAndWait();
                this.barrier = null;
            }
        }

        private void Back(Barrier barrier)
        {
            logger.Debug("Back requested");

            if (barrier != null)
            {
                lock (this)
                {
                    this.barrier = barrier;
                }
            }
            webBrowser.GoBack();
        }

        public void Forward()
        {
            using (Barrier action = new Barrier(2))
            {
                Forward(action);
                action.SignalAndWait();
                this.barrier = null;
            }
        }

        private void Forward(Barrier barrier)
        {
            logger.Debug("Back requested");

            if (barrier != null)
            {
                lock (this)
                {
                    this.barrier = barrier;
                }
            }
            webBrowser.GoForward();
        }

        public void DoRefresh(String waitingUrl)
        {
            DoRefresh(UrlNavigationCompleteDelegate.NewUrlDelegate(waitingUrl));
        }

        public void DoRefresh(NavigationCompleteDelegate delegate_)
        {
            NavigationUrl = delegate_;
            DoRefresh();
        }

        public void DoRefresh()
        {
            using (Barrier action = new Barrier(2))
            {
                Refresh(action);
                action.SignalAndWait();
                this.barrier = null;
            }
        }

        private void Refresh(Barrier barrier)
        {
            logger.Debug("Refresh requested");

            if (barrier != null)
            {
                lock (this)
                {
                    this.barrier = barrier;
                }
            }
            webBrowser.Refresh();
        }

        public void Get(string url)
        {
            using (Barrier action = new Barrier(2))
            {
                Get(url, action);
                action.SignalAndWait();
                this.barrier = null;
            }
        }

        public void Quit()
        {
            Close();
        }

        private void Get(string url, Barrier barrier)
        {
            logger.Debug("Get requested to: {0}", url);

            if (barrier != null)
            {
                lock (this)
                {
                    this.barrier = barrier;
                }
            }
            webBrowser.Navigate(url);
        }

        private bool IsNavigationUrlEqualsTo(Uri url)
        {

            if (NavigationUrl != null)
                return NavigationUrl(url);
            else
            {
                logger.Error("Navigation initialisation error recive an url check without initialized target url: {0}", url);
                return true;
            }
        }

        private bool IsDocumentComplete(WebBrowser browser, WebBrowserDocumentCompletedEventArgs e)
        {
            if (IsNavigationUrlEqualsTo(e.Url))
                return true;
            return false;
        }

        //Event handling
        private void webBrowser_DocumentCompleted(object sender, WebBrowserDocumentCompletedEventArgs e)
        {
            stopwatch.Stop();
            string eurl = e.Url.ToString();         
            var browser = (WebBrowser)sender;          
            if (!(eurl.StartsWith("http://") || eurl.StartsWith("https://")))              
            {                          
                // in AJAX
                logger.Debug("Ajax code execution to: {0}, complete", toolStripUrl);
            }
            if (e.Url.AbsolutePath != this.webBrowser.Url.AbsolutePath)
            {
                // IFRAME
                logger.Debug("IFrame download complete: {0}", e.Url.AbsolutePath);
            }
            else 
            {
                logger.Debug("Root download complete: {0}", e.Url.AbsolutePath);
            }
            if (IsDocumentComplete((WebBrowser)sender, e))
            {
                // REAL DOCUMENT COMPLETE
                // Put my code here
                logger.Debug("full page download complete");
                lock (this)
                {
                    if (barrier != null)
                    {
                        NavigationUrl = null;
                        document = webBrowser.Document;
                        documentText = webBrowser.DocumentText;
                        logger.Info("document completed for action #{0} {1} in {2}, on url: {3}", ActionId, Action, stopwatch.Elapsed, e.Url.ToString());
                        LogEventInfo theEvent = new LogEventInfo(LogLevel.Info, "webbench.action", "");
                        theEvent.Properties["actionId"] = ActionId;
                        theEvent.Properties["action"] = Action;
                        theEvent.Properties["client"] = name_;
                        theEvent.Properties["elapsed"] = stopwatch.Elapsed;
                        theEvent.Properties["url"] = e.Url.ToString();
                        actionLogger.Log(theEvent);
                        //actionLogger.Info("{0}, {1}, {2}, {3}", name_, Action, stopwatch.Elapsed, e.Url.ToString());
                        stopwatch.Reset();
                        barrier.SignalAndWait();
                        barrier = null;
                    }
                }
                toolStripUrl.Text = e.Url.ToString();
            }
            else 
            {
                stopwatch.Start();
            }
        }
        
        private void webBrowser_Navigating(object sender, WebBrowserNavigatingEventArgs e)
        {
            logger.Debug("navigating to: {0}, for frame: {1}", e.Url, e.TargetFrameName);
            if (NavigationUrl == null)
            {
                logger.Debug("not navigation completion method provided setup the default one on: {1}", e.Url.ToString());
                NavigationUrl = UrlNavigationCompleteDelegate.NewUrlDelegate(e.Url);
            }
            if (!stopwatch.IsRunning)
            {
                stopwatch.Start();
            }
        }

        private void webBrowser_HandleCreated(Object sender, EventArgs e)
        {
            logger.Debug("deseable scripting errors detection");
            webBrowser.ScriptErrorsSuppressed = true;
        }

        //Search Context
        public WebElement FindElementById(string id)
        {
            logger.Debug("find by id: {0}", id);
            lock (this)
            {
                HtmlElement htmlElement = document.GetElementById(id);
                if (htmlElement != null)
                    return WebElement.newElement(this, htmlElement);
                return null;

            }
        }
        
        public Collection<WebElement> FindElementsByClassName(string name) 
        {
            HtmlElementCollection htmlElements = null;
            lock (this)
            {
                htmlElements = document.All;
            }
            Collection<WebElement> result = new Collection<WebElement>();
            foreach (HtmlElement e in htmlElements)
            {
                string class_ =  e.GetAttribute("class");
                class_ = class_ != null ? class_ : e.GetAttribute("className");
                if (class_ != null && class_.Equals(name))
                    result.Add(WebElement.newElement(this, e));
            }
            return result;
        }
        public WebElement FindElementByClassName(string name)
        {
            Collection<WebElement> result = FindElementsByClassName(name);
            return result.Count > 0 ? result[0]: null;
        }

        public Collection<WebElement> FindElementsByTagName(string tagName)
        {
            HtmlElementCollection htmlElements = null;
            lock (this)
            {
                htmlElements = document.GetElementsByTagName(tagName);
            }
            Collection<WebElement> result = new Collection<WebElement>();
            foreach (HtmlElement e in htmlElements)
            {
                result.Add(WebElement.newElement(this, e));
            }
            return result;
            
        }

        public WebElement FindElementByName(string name)
        {
            return FindElementByNameDelegate(name, null);
        }
        public WebElement FindElementByName(string name, string url)
        {
            NavigationCompleteDelegate delegate_ = url == null ? null : UrlNavigationCompleteDelegate.NewUrlDelegate(url);
            return FindElementByNameDelegate(name, delegate_);
        }
        public WebElement FindElementByNameDelegate(string name, NavigationCompleteDelegate navComplete)
        {
            logger.Debug("find by name: {0}", name);
            if (navComplete != null)
            {
                WebElement result = null;
                using (Barrier action = new Barrier(2))
                {
                    result = DoFindElementByName(name, navComplete);
                    action.SignalAndWait();
                    this.barrier = null;
                }
                return result;
            }
            else
                return DoFindElementByName(name, navComplete);
        }
        private WebElement DoFindElementByName(string name, NavigationCompleteDelegate navComplete)
        {
            HtmlElement htmlElement = null;
            lock (this)
            {
                NavigationUrl = navComplete;
                htmlElement = document.All[name];
            }
            if (htmlElement != null)
                return WebElement.newElement(this, htmlElement);
            return null;
        }
             
        public Collection<WebElement> FindElementsByLinkText(string linkText)
        {
            HtmlElementCollection htmlElements = null;
            lock (this)
            {
                htmlElements = document.Links;
            }
            Collection<WebElement> result = new Collection<WebElement>();
            foreach (HtmlElement e in htmlElements)
            {
                if (linkText.Equals(e.InnerText))
                {
                    result.Add(WebElement.newElement(this, e));
                }
            }
            return result;
        }

        public WebElement FindElementByLinkText(string linkText)
        {
            Collection<WebElement> result = FindElementsByLinkText(linkText);
            if (result.Count > 0)
                return result[0];
            else
                return null;
        }

        public Collection<WebElement> FindElementsByPartialLinkText(string linkText)
        {
            HtmlElementCollection htmlElements = null;
            lock (this)
            {
                //htmlElements = document.GetElementsByTagName("a");
                htmlElements = document.Links;
            }
            Collection<WebElement> result = new Collection<WebElement>();
            foreach (HtmlElement e in htmlElements)
            {
                string text = e.InnerText;
                /*if (text == null)
                {
                    logger.Debug("Link without text");
                }
                else */if (text.Contains(linkText))
                {
                    result.Add(WebElement.newElement(this, e));
                }
            }
            return result;
        }

        private bool HasText(HtmlElement e, string text)
        {
            if (e.InnerText == null && e.Children.Count > 0)
            {
                foreach (HtmlElement child in e.Children)
                {
                    if (HasText(child, text))
                        return true;
                }
            }
            else if (e.InnerText.Equals(text))
            {
                return true;
            }
            return false;
        }

        private bool ContainsText(HtmlElement e, string text)
        {
            if (e.InnerText == null && e.Children.Count > 0)
            {
                foreach (HtmlElement child in e.Children)
                {
                    if (ContainsText(child, text))
                        return true;
                }
            }
            else if (e.InnerText.Contains(text))
            {
                return true;
            }
            return false;
        }

        public WebElement FindElementByPartialLinkText(string linkText)
        {
            Collection<WebElement> result = FindElementsByPartialLinkText(linkText);
            if (result.Count > 0)
                return result[0];
            else
                return null;
        }

        private WebElement SwitchToFrame(int index)
        {
            //document.Window.Frames TODO
            return null;
        }

        private WebElement SwitchToFrame(string frameName)
        {
            //document.Window.Frames TODO
            return null;
        }

        private WebElement SwitchToAlert()
        {
            
            return null;
        }

        public static bool NullNavigationDelegate(Uri url)
        {
            return true;
        }
    //    private void webBrowser1_Navigating(object sender, WebBrowserNavigatingEventArgs e)
    //    {
    //        System.Windows.Forms.HtmlDocument document =
    //            this.webBrowser1.Document;

    //        if (document != null && document.All["userName"] != null &&
    //            String.IsNullOrEmpty(
    //            document.All["userName"].GetAttribute("value")))
    //        {
    //            e.Cancel = true;
    //            System.Windows.Forms.MessageBox.Show(
    //                "You must enter your name before you can navigate to " +
    //                e.Url.ToString());
    //        }
    //    }
    }

    public delegate bool NavigationCompleteDelegate(Uri url);

    

    public class UrlNavigationCompleteDelegate
    {
        private static Logger logger = LogManager.GetLogger("webbench.urlcomplete");
        private string m_url;
        public UrlNavigationCompleteDelegate(string url)
        {
            m_url = url;
        }
        public bool IsNavigationUrlEqualsTo(Uri url)
        {
            logger.Debug("validate {0} agains {1}", m_url, url); 
            if (m_url == null) return true;
            
            return m_url.StartsWith("/") ? m_url.Equals(url.AbsolutePath) : m_url.Equals(url.ToString());
        }
        public static NavigationCompleteDelegate NewUrlDelegate(Uri url) 
        {
            if (url == null) return NullNavigationDelegate;

            UrlNavigationCompleteDelegate delegate_ = new UrlNavigationCompleteDelegate(url.ToString());
            return delegate_.IsNavigationUrlEqualsTo;
        }

        public static NavigationCompleteDelegate NewUrlDelegate(string url)
        {
            if (url == null) return NullNavigationDelegate;
            
            UrlNavigationCompleteDelegate delegate_ = new UrlNavigationCompleteDelegate(url);
            return delegate_.IsNavigationUrlEqualsTo;
        }

        public static bool NullNavigationDelegate(Uri url)
        {
            return true;
        }
    }
}
