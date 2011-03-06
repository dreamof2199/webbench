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
using System.Collections.ObjectModel;
using System.Collections.Generic;
using System.ComponentModel;
using System;
using System.Threading;
using WebBenchBrowser;
using NLog;
using NLog.Targets;
using NLog.Config;

namespace TestStarter
{
    class Program
    {
        static Browser browser;
        static Barrier startupAction = new Barrier(2);
        //private static Mutex mut = new Mutex(false);
        private static Logger logger = LogManager.GetLogger("test");
        [STAThread]
        static void Main(string[] args)
        {
            //doc at: http://nlog-project.org/wiki/Configuration_API
            //http://nlog-project.org/wiki/Event-context_layout_renderer
            // Step 1. Create configuration object 
            LoggingConfiguration config = new LoggingConfiguration();

            // Step 2. Create targets and add them to the configuration 
            //console
            ColoredConsoleTarget consoleTarget = new ColoredConsoleTarget();
            config.AddTarget("console", consoleTarget);
            //file
            //FileTarget fileTarget = new FileTarget();
            //config.AddTarget("file", fileTarget);

            // Step 3. Set target properties 
            consoleTarget.Layout = "${date:format=HH\\:MM\\:ss} ${logger} [${threadid}] - ${message}";
            //fileTarget.FileName = "${basedir}/file.txt";
            //fileTarget.Layout = "${message}";

            // Step 4. Define rules
            LoggingRule rule1 = new LoggingRule("*", LogLevel.Debug, consoleTarget);
            config.LoggingRules.Add(rule1);

            //LoggingRule rule2 = new LoggingRule("*", LogLevel.Debug, fileTarget);
            //config.LoggingRules.Add(rule2);

            // Step 5. Activate the configuration
            LogManager.Configuration = config;

            browser = Browser.newBrowser();
            parallel();   
        }


        static void parallel() 
        {
            logger.Debug("start browser thread");
            browser.run();
            scenario_examples(null, null);
        }



        static void run() 
        {
            browser.run();
        }

        static void scenario_examples(object sender, EventArgs e)
        {
            browser.Get("http://localhost:8080/examples/");
            Thread.Sleep(5000);
            WebElement element = browser.FindElementByLinkText("Servlets examples");
            Thread.Sleep(1000);
            element.Click();
            Thread.Sleep(1000);
            browser.Back();
            Thread.Sleep(1000);

            Collection<WebElement> examples = browser.FindElementsByPartialLinkText("xamples");
            logger.Info("found {0} link", examples.Count);
            examples[0].Click();

            examples = browser.FindElementsByPartialLinkText("Execute");
            logger.Info("found {0} link", examples.Count);
            examples[4].Click();
            element = browser.FindElementByName("cookiename");
            element.SendKeys("TestKey");
            element = browser.FindElementByName("cookievalue");
            element.SendKeys("TestValue");
            element.Submit();
        }
    }
}
