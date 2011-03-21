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
#TODO
# - handle configuration
# - handle rando
# - introduce parallel
# - introduce
# - todo use logger

import optparse
import os.path  
import time
import threading
from threading import Thread
import clr
import ConfigParser
clr.AddReference('NLog')
import webbench
from webbench.driver import action
#from NLog import Logger
from NLog import LogManager
from NLog import LogLevel
from NLog.Config import LoggingConfiguration
from NLog.Targets import ColoredConsoleTarget
from NLog.Targets import FileTarget
from NLog.Config import LoggingRule
from NLog.Layouts import CsvLayout
from NLog.Layouts import CsvColumn
#
USAGE = '''usage: %prog [options] senario_path'''
DEBUG_OPT='''Specify the application has to run in debug mode.
Default value is: [False]
In this mode there is no multi-processing.'''
DRY_RUN_OPT='''Activate the dry run execution mode no actions will be executed.
Default value is: [False]'''

DRY_RUN_OPT='''Activate the dry run execution mode no actions will be executed.
Default value is: [False]'''

NB_BROWSER_DEFAULT = 1
NB_BROWSER_OPT='''Specify the number of concurrent browser. Default value is [{0}]'''.format(NB_BROWSER_DEFAULT)

RANDOM_TIME_DEFAULT = 0
RANDOM_TIME_OPT='''Specify the limit of random value in secondes. Default value is [{0}]'''.format(RANDOM_TIME_DEFAULT)

LAUNCH_DELAY_DEFAULT = 0
LAUNCH_DELAY_OPT='''Specify the time delay between each scenario execution. Default value is [{0}]'''.format(LAUNCH_DELAY_DEFAULT)

KEEP_ALIVE_DEFAULT = False
KEEP_ALIVE_OPT='''Specify if the browser must be kept alive after scenario execution. 
This feature is available only when only 1 browser is used. Default value is [{0}]'''.format(KEEP_ALIVE_DEFAULT)

RUN_METHOD = 'run'
SETUP_METHOD = 'setup'
logger = LogManager.GetLogger("webbench")
counter = None

def debug(message):
    logger.Debug(message)

def info(message):
    logger.Info(message)

def initlogger(log_level, csvpath, logpath):
    print 'log level: %r' % log_level
    print 'csv path: %r' % csvpath
    print 'log path: %r' % logpath

    #logger configuration
    #doc at: 
    #  - http://nlog-project.org/wiki/Configuration_API
    #  - http://nlog-project.org/wiki/Event-context_layout_renderer
    # Step 1. Create configuration object 
    config = LoggingConfiguration()
    
    # Step 2. Create targets and add them to the configuration 
    #console
    consoleTarget = ColoredConsoleTarget()
    config.AddTarget("console", consoleTarget)
    #file
    fileTarget = FileTarget()
    config.AddTarget("file", fileTarget)
    #csv
    csvTarget = FileTarget();
    config.AddTarget("csv", csvTarget);
    
    # Step 3. Set target properties 
    consoleTarget.Layout = "[${level}] | ${threadid} (${logger}) | ${message}"
    fileTarget.FileName = logpath
    fileTarget.Layout = "${date:format=HH\\:MM\\:ss} | ${level} | [${threadid}] - ${message}"
    
    csvTarget.FileName = csvpath
    #csvTarget.Layout = "${date:format=HH\\:MM\\:ss}, ${threadid}, ${message}"
    csvLayout = CsvLayout()
    csvLayout.WithHeader = True
    csvLayout.Columns.Add(CsvColumn("date", "${date:format=HH\\:MM\\:ss.fffffff}"));
    csvLayout.Columns.Add(CsvColumn("thread", "${threadid}"))
    csvLayout.Columns.Add(CsvColumn("client", "${event-context:item=client}"))
    csvLayout.Columns.Add(CsvColumn("action", "${event-context:item=action}"))
    csvLayout.Columns.Add(CsvColumn("elapsed", "${event-context:item=elapsed}"))
    csvLayout.Columns.Add(CsvColumn("url", "${event-context:item=url}"))
    csvTarget.Layout = csvLayout;
    
    # Step 4. Define rules
    rule1 = LoggingRule("*", log_level, consoleTarget)
    config.LoggingRules.Add(rule1)
    
    rule2 = LoggingRule("*", log_level, fileTarget)
    config.LoggingRules.Add(rule2)
    
    #rule3 = LoggingRule("webbench.action", LogLevel.Info, csvTarget)
    rule3 = LoggingRule("webbench.action", log_level, csvTarget)
    config.LoggingRules.Add(rule3);
    
    # Step 5. Activate the configuration
    LogManager.Configuration = config
    #pass


def getscenariomethodes(scenariopath):
    global_ = {'debug': logger.Debug, 'info': logger.Info, 'warn': logger.Warn, 'error': logger.Error, 'action': action}
    local = global_ #dict()
    execfile(scenariopath, global_, local)
    setup_method = local.get(SETUP_METHOD, None)
    run_method = local.get(RUN_METHOD, None)
    return (run_method, setup_method)

def main():
    optparser = optparse.OptionParser( usage = USAGE)
    optparser.add_option( '-D', '--debug', help = DEBUG_OPT,
        dest = 'debug', action='store_true', default=False )
    optparser.add_option( '--dry-run', help = DRY_RUN_OPT,
                          dest = 'dry_run', action='store_true', default=False )
    optparser.add_option( '-n', '--nb-browser', help = NB_BROWSER_OPT,
                          dest = 'nb_browser', type='int', default=NB_BROWSER_DEFAULT )
    optparser.add_option( '-r', '--random-time', help = RANDOM_TIME_OPT,
                          dest = 'random_time', type='float', default=RANDOM_TIME_DEFAULT )
    optparser.add_option( '-d', '--launch-delay', help = LAUNCH_DELAY_OPT,
                          dest = 'launch_delay', type='int', default=LAUNCH_DELAY_DEFAULT )
    optparser.add_option( '--keep-alive', help = KEEP_ALIVE_OPT,
                          dest = 'keep_alive', action='store_true', default=KEEP_ALIVE_DEFAULT )
    
    options, args = optparser.parse_args()

    if len(args) == 1:
        scenario = args[0]
    else:
        optparser.error("you must specify a scenario path")
        
    filename = os.path.basename(scenario)
    if filename.find('.') > -1:
        filename = filename[:filename.find('.')]
    basedir = os.path.dirname(scenario)
    basedir = '.' if len(basedir) == 1 else basedir
    filename = os.path.join(basedir,filename)
    csvpath = filename + '.csv'
    configpath = filename + '.cfg'
    logpath = filename + '.log'
    
    if os.path.exists(logpath):
        os.remove(logpath)
    if os.path.exists(csvpath):
        os.remove(csvpath)
        
    if options.debug:
        log_level = LogLevel.Debug
        print 'debug mode activated'
    else :
        log_level = LogLevel.Info
        
    initlogger(log_level, csvpath, logpath)

    if options.dry_run:
        logger.Info('dry-run mode activated') 
    
    if not os.path.isfile(scenario) :
        optparser.error("scenario path must point a file: {0}".format(str(scenario))) 
    
    (run_method, setup_method) = getscenariomethodes(scenario);
    if not run_method:
        optparser.error("experiment script must contains a 'run(browser)' method without parameters that provide the future experiment scenario execution")
    logger.Info('****************************************')
    logger.Info('process scenario: {0}', scenario)
    logger.Info('****************************************')
    start_time = time.time()
    try:
        config = ConfigParser.SafeConfigParser()        
        if os.path.isfile(configpath) :
            logger.Debug('load configuration at: {0}', configpath)
            with open(configpath) as configfile:
                config.readfp(configfile)
        browsers = []
        scenarios = []
        logger.Debug('create {0} browser instance(s)', options.nb_browser)
        for i in xrange(0,options.nb_browser):
            browser = webbench.Ie('client-{0}'.format(i))
            browsers.append(browser)
            (run_method, setup_method) = getscenariomethodes(scenario)
            scenarios.append((run_method,browser))
            if setup_method:
                setup_method(config)
            browser.run()
        threads = []
        logger.Debug('run {0} scenario(s) with delay of {1}', options.nb_browser, options.launch_delay)
        for (run_method, browser) in scenarios:
            time.sleep(options.launch_delay)
            thread = Thread(target=run_method, name=browser.name, args=(browser,))
            threads.append(thread)
            #run_method(browser)#launch in a thread
            thread.start()
        logger.Debug('wait for end of {0} scenario(s)', options.nb_browser)
        for thread in threads:
            thread.join()
        
        if not(options.nb_browser == 1 and options.keep_alive):
            logger.Debug('close {0} browser(s)', options.nb_browser)
            for (run_method, browser) in scenarios:
                browser.quit()
    finally:
        elapsed_time = time.time() - start_time
        logger.Info('****************************************')
        logger.Info("scenarion [{0}] processed in {1}s", scenario, elapsed_time)
        logger.Info('****************************************')
        

if __name__=='__main__':
    main()
