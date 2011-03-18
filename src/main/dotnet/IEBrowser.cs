using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using NLog;
//using SHDocVw;

namespace WebBenchBrowser
{
    class IEBrowser : IBrowser
    {
        private static Logger logger = LogManager.GetLogger("webbench.iebrowser");

        //SHDocVw.InternetExplorer ie;

        private IEBrowser()
        {
            //ie = new SHDocVw.InternetExplorer();
        }

        public static IEBrowser NewBrowser()
        {
            return new IEBrowser();
        }

        public void Get(string url) { 
            //ie.Navigate2(ref url, 
        }
    }
}
