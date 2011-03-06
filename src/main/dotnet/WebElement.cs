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
using NLog;
using System.Threading;
using System.Security.Permissions;

namespace WebBenchBrowser
{
    //[assembly: PermissionSetAttribute(SecurityAction.LinkDemand, Name = "FullTrust")]
    public class WebElement
    {
        private Browser parent;
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

        public string TagName
        {
            get
            {
                return underlying.TagName;
            }
        }

        private WebElement(Browser parent, HtmlElement underlying)
        {
            this.parent = parent;
            this.underlying = underlying;
        }

        public string GetAttribute(string attributeName) 
        {
            return underlying.GetAttribute(attributeName);
        }

        public void Click()
        {
            using (Barrier action = new Barrier(2))
            {
                lock (parent) parent.SetBarrier(action);
                DoClick();
                action.SignalAndWait();
                lock (parent) parent.SetBarrier(null);
            }
        }
        private void DoClick()
        {
            underlying.Focus();
            mshtml.IHTMLElement element = (mshtml.IHTMLElement)underlying.DomElement;
            element.click();
        }


        public bool IsInput()
        {
            return (underlying.TagName.ToLower().Equals("input"));
        }
        public bool IsTextArea()
        {
            return (underlying.TagName.ToLower().Equals("textarea"));
        }
        public bool hasValue()
        {
            return IsInput() || IsTextArea();
        }

        public void Submit()
        {
            using (Barrier action = new Barrier(2))
            {
                lock (parent) parent.SetBarrier(action);
                DoSubmit();
                action.SignalAndWait();
                lock (parent) parent.SetBarrier(null);
            }
        }

        private void DoSubmit()
        {
            logger.Debug("submit element: <{0} ... name='{1}' ...", underlying.TagName, underlying.Name);
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
            if (IsInput())
            {
                underlying.Focus();
                ((mshtml.IHTMLInputElement)underlying.DomElement).value = keys;
                //underlying.RaiseEvent("onchange");
            }
            if (IsTextArea())
            {
                underlying.Focus();
                ((mshtml.IHTMLTextAreaElement)underlying.DomElement).value = keys;
                //underlying.RaiseEvent("onchange");
            }
        }
    }
}
