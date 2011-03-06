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
     *    - ...
     * ? IE http://www.codeproject.com/KB/toolbars/MicrosoftMshtml.aspx?msg=2893585
     * 
     * Nlog:
     *   - home: http://nlog-project.org/
     *   - Programmatic config: http://nlog-project.org/wiki/Configuration_API
     *   - File config: http://nlog-project.org/wiki/Configuration_file
     *   - Layout: http://nlog-project.org/wiki/Layout_renderers
     * Perf: http://msdn.microsoft.com/en-us/library/15t15zda.aspx
     */
    //[assembly: PermissionSetAttribute(SecurityAction.InheritanceDemand, Name = "FullTrust")]
    //[assembly: PermissionSetAttribute(SecurityAction.LinkDemand, Name = "FullTrust")]
    public partial class Browser : Form
    {
        private static Logger logger = LogManager.GetLogger("borwser");
        private Barrier barrier;
        private Stopwatch stopwatch = new Stopwatch();
        private HtmlDocument document;
        private Barrier startupAction;

        static Browser()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
        }

        public static Browser newBrowser()
        {
            logger.Debug("create new browser");
            Application.DoEvents();
            return new Browser();
        }

        private Browser()
        {
            InitializeComponent();
            webBrowser.Navigating += new WebBrowserNavigatingEventHandler(webBrowser_Navigating);
            
        }

        public void run()
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
            Get(url.Text, null);
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
            logger.Debug("Back requested");

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

        //Event handling
        private void webBrowser_DocumentCompleted(object sender, WebBrowserDocumentCompletedEventArgs e)
        {
            string eurl = e.Url.ToString();         
            var browser = (WebBrowser)sender;          
            if (!(eurl.StartsWith("http://") || eurl.StartsWith("https://")))              
            {                          
                // in AJAX
                logger.Debug("Ajax code execution to: {0}, complete", url);
            }         
            if (e.Url.AbsolutePath != this.webBrowser.Url.AbsolutePath)              
            {             
                // IFRAME
                logger.Debug("IFrame download complete: {0}", e.Url.AbsolutePath);
            }              
            else              
            {                          
                // REAL DOCUMENT COMPLETE             
                // Put my code here         
                logger.Debug("full page download complete");
                lock (this)
                {
                    if (barrier != null)
                    {
                        stopwatch.Stop();
                        logger.Info("document completed in {0}ms, for url: {1}", stopwatch.Elapsed, e.Url.ToString());
                        stopwatch.Reset();
                        document = webBrowser.Document;
                        barrier.SignalAndWait();
                        barrier = null;
                    }
                }
                url.Text = e.Url.ToString();
            }
        }

        
        private void webBrowser_Navigating(object sender, WebBrowserNavigatingEventArgs e)
        {
            logger.Debug("navigating to: {0}", e.Url);
            if (!e.TargetFrameName.Equals(""))
                logger.Debug("navigating for a iframe: {0}",e.TargetFrameName);
            if (!stopwatch.IsRunning)
                stopwatch.Start();
        }

        //Search Context
        public WebElement FindElementById(string id)
        {
            return WebElement.newElement(this, webBrowser.Document.GetElementById(id));
        }
        public Collection<WebElement> FindElementsByTagName(string tagName)
        {
            HtmlElementCollection htmlElements = null;
            lock (this)
            {
                htmlElements = webBrowser.Document.GetElementsByTagName(tagName);
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
            logger.Debug("find by name: {0}", name);
            lock (this)
            {
                HtmlElement htmlElement = document.All[name];
                if (htmlElement != null)
                    return WebElement.newElement(this, htmlElement);
                return null;
                
            }
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
                if (text == null)
                {
                    logger.Debug("Link without text");
                }
                else if (text.Contains(linkText))
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
            //webBrowser.Document.Window.Frames TODO
            return null;
        }

        private WebElement SwitchToFrame(string frameName)
        {
            //webBrowser.Document.Window.Frames TODO
            return null;
        }

        private WebElement SwitchToAlert()
        {
            
            return null;
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
}
