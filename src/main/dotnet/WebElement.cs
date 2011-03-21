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
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using NLog;
using System.Threading;
using System.Security.Permissions;

namespace WebBenchBrowser
{
    //[assembly: PermissionSetAttribute(SecurityAction.LinkDemand, Name = "FullTrust")]
    public class WebElement
    {
        private Browser parentBrowser;
        private static Logger logger = LogManager.GetLogger("webelement");
        private volatile HtmlElement underlying;
        public static WebElement newElement(Browser parent, HtmlElement element)
        {
            return new WebElement(parent, element);
        }
        public string Name
        {
            get
            {
                return underlying.Name;
            }
            set
            {
                underlying.Name = value;
            }
        }
        public Collection<WebElement> Children
        {
            get
            {
                Collection<WebElement> result = new Collection<WebElement>();
                foreach (HtmlElement e in underlying.Children)
                {
                    result.Add(newElement(parentBrowser, e));
                }
                return result;
            }
        }

        public string Action 
        {
            get 
            {
                return parentBrowser.Action;
            }
            set
            {
                parentBrowser.Action = value;
            }
        }

        public string Id
        {
            get
            {
                return underlying.Id;
            }
            set
            {
                underlying.Id = value;
            }
        }

        public string Text
        {
            get 
            {
                return underlying.InnerText;
            }
        }

        public string InnerHtml
        {
            get
            {
                return underlying.InnerHtml;
            }
        }

        public WebElement Parent
        {
            get
            {
                return newElement(parentBrowser, underlying.Parent);
            }
        }

        public string OuterHtml
        {
            get
            {
                return underlying.OuterHtml;
            }
        }

        public string TagName
        {
            get
            {
                return underlying.TagName;
            }
        }

        public bool Enabled
        {
            get
            {
                return underlying.Enabled;
            }
        }

        //public bool Selected
        //{
        //    get 
        //    {
        //        underlying
        //    }
        //}

        public string Value
        {
            get
            {
                if (IsInput())
                {
                    underlying.Focus();
                    return ((mshtml.IHTMLInputElement)underlying.DomElement).value;
                }
                if (IsTextArea())
                {
                    underlying.Focus();
                    return ((mshtml.IHTMLTextAreaElement)underlying.DomElement).value;
                }
                return null;
            }
            set
            {
                if (IsInput())
                {
                    underlying.Focus();
                    ((mshtml.IHTMLInputElement)underlying.DomElement).value = value;
                    //underlying.RaiseEvent("onchange");
                }
                if (IsTextArea())
                {
                    underlying.Focus();
                    ((mshtml.IHTMLTextAreaElement)underlying.DomElement).value = value;
                    //underlying.RaiseEvent("onchange");
                }
            }
        }


        private WebElement(Browser parent, HtmlElement underlying)
        {
            this.parentBrowser = parent;
            this.underlying = underlying;
        }

        public string GetAttribute(string attributeName) 
        {
            //return underlying.GetAttribute(attributeName);
            mshtml.IHTMLElement element = (mshtml.IHTMLElement)underlying.DomElement;
            object result = element.getAttribute(attributeName);
            return result != null ? result.ToString(): null;
        }

        public void Click(string url)
        {
            ClickDelegate(UrlNavigationCompleteDelegate.NewUrlDelegate(url));
        }

        public void ClickDelegate(NavigationCompleteDelegate delegate_)
        {
            this.parentBrowser.NavigationUrl = delegate_;
            logger.Debug("click with delegate");
            Click();
        }

        public void Click()
        {
            using (Barrier action = new Barrier(2))
            {
                logger.Debug("click on: {0}", OuterHtml);
                lock (parentBrowser) parentBrowser.SetBarrier(action);
                DoClick();
                action.SignalAndWait();
                lock (parentBrowser) parentBrowser.SetBarrier(null);
            }
        }
        private void DoClick()
        {
            if (IsFocusable())
                underlying.Focus();
            mshtml.IHTMLElement element = (mshtml.IHTMLElement)underlying.DomElement;
            element.click();
        }

        public bool IsFocusable() 
        {
            return !IsLink();
        }

        public bool IsLink()
        {
            return underlying.DomElement is mshtml.IHTMLAnchorElement;
            //return (underlying.TagName.ToLower().Equals("a"));
        }

        public bool IsInput()
        {
            return (underlying.TagName.ToLower().Equals("input"));
        }
        public bool IsTextArea()
        {
            return (underlying.TagName.ToLower().Equals("textarea"));
        }
        public bool SupportValue()
        {
            return IsInput() || IsTextArea();
        }

        public void Submit()
        {
            using (Barrier action = new Barrier(2))
            {
                lock (parentBrowser) parentBrowser.SetBarrier(action);
                DoSubmit();
                action.SignalAndWait();
                lock (parentBrowser) parentBrowser.SetBarrier(null);
            }
        }

        private void DoSubmit()
        {
            logger.Debug("submit element: {0}", OuterHtml);
            if (underlying.TagName.ToLower().Equals("input"))
            {
                mshtml.IHTMLInputElement input = (mshtml.IHTMLInputElement)underlying.DomElement;
                mshtml.IHTMLFormElement form = input.form;
                if (form != null)
                {
                    form.submit();
                }
                else
                {
                    string type = underlying.GetAttribute("type").ToLower();
                    if (type != null && ("submit".Equals(type) || "image".Equals(type)))
                    {
                        ((mshtml.IHTMLElement)input).click();
                    }
                }
            }
            DoSubmit(underlying);
            
        }
        
        private void DoSubmit(HtmlElement element)
        {
            if (element == null)
            {
                return;
            }
            if (element.TagName.ToLower().Equals("form"))
            {
                mshtml.IHTMLFormElement ielement = (mshtml.IHTMLFormElement)element.DomElement;
                ielement.submit();
            }
            if (element.TagName.ToLower().Equals("input"))
            {
                mshtml.IHTMLInputElement input = (mshtml.IHTMLInputElement)element.DomElement;
                mshtml.IHTMLFormElement form = input.form;
                if (form != null)
                {
                    form.submit();
                }
            }
            DoSubmit(element.Parent);
        }

        public void Clear()
        {
            if (IsInput())
            {
                underlying.Focus();
                ((mshtml.IHTMLInputElement)underlying.DomElement).value = "";
                //underlying.RaiseEvent("onchange");
            }
            if (IsTextArea())
            {
                underlying.Focus();
                ((mshtml.IHTMLTextAreaElement)underlying.DomElement).value = "";
                //underlying.RaiseEvent("onchange");
            }
        }

        public void SendKeys(string keys)
        {
            logger.Debug("send keys: {0}", keys);
            Value = keys;
        }

        public void SendKeys(string keys, string url)
        {
            if (url == null)
            {
                SendKeys(keys);
            }
            else
            {
                logger.Debug("send keys: {0} and waiting for {1}", keys, url);
                using (Barrier action = new Barrier(2))
                {
                    lock (parentBrowser)
                    {
                        parentBrowser.NavigationUrl = UrlNavigationCompleteDelegate.NewUrlDelegate(url);
                        parentBrowser.SetBarrier(action);
                    }
                    Value = keys;
                    action.SignalAndWait();
                    lock (parentBrowser) parentBrowser.SetBarrier(null);
                }
            }
        }

        
    }
}
