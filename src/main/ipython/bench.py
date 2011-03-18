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
import clr
import ConfigParser
clr.AddReference('NLog')
import webbench
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

RUN_METHOD = 'run'
SETUP_METHOD = 'setup' 
logger = None
counter = None

def debug(message):
    logger.Debug(message)

def info(message):
    logger.Info(message)

def initlogger(log_level, cvspath, logpath):
    #logger configuration
    #doc at: http://nlog-project.org/wiki/Configuration_API
    #http://nlog-project.org/wiki/Event-context_layout_renderer
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
    consoleTarget.Layout = "[${level}] | ${threadid} | ${message}"
    fileTarget.FileName = logpath
    fileTarget.Layout = "${date:format=HH\\:MM\\:ss} | ${level} | [${threadid}] - ${message}"
    csvTarget.FileName = cvspath
    csvLayout = CsvLayout()
    csvLayout.WithHeader = True
    csvLayout.Columns.Add(CsvColumn("date", "${date:format=HH\\:MM\\:ss}"));
    csvLayout.Columns.Add(CsvColumn("thread", "${threadid}"));
    csvLayout.Columns.Add(CsvColumn("action", "${event-context:item=action}"));
    csvLayout.Columns.Add(CsvColumn("elapsed", "${event-context:item=elapsed}"));
    csvTarget.Layout = csvLayout;
            
    # Step 4. Define rules
    rule1 = LoggingRule("*", log_level, consoleTarget)
    config.LoggingRules.Add(rule1)
    
    rule2 = LoggingRule("*", log_level, fileTarget)
    config.LoggingRules.Add(rule2)
    
    #rule3 = LoggingRule("webbench.action", LogLevel.Info, csvTarget)
    rule3 = LoggingRule("webbench.action", log_level, consoleTarget)
    config.LoggingRules.Add(rule3);
    
    # Step 5. Activate the configuration
    LogManager.Configuration = config
    return LogManager.GetLogger("webbench")
    #pass

def main():
    optparser = optparse.OptionParser( usage = USAGE)
    optparser.add_option( '-D', '--debug', help = DEBUG_OPT,
        dest = 'debug', action='store_true', default=False )
    optparser.add_option( '--dry-run', help = DRY_RUN_OPT,
                          dest = 'dry_run', action='store_true', default=False )

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
    if options.debug:
        log_level = LogLevel.Debug
    else :
        log_level = LogLevel.Info
        
    logger = initlogger(log_level, csvpath, logpath)

    if options.dry_run:
        logger.Info('dry-run mode activated') 
    
    if not os.path.isfile(scenario) :
        optparser.error("scenario path must point a file: {0}".format(str(scenario))) 
    
    global_ = {'debug': logger.Debug, 'info': logger.Info, 'warn': logger.Warn, 'error': logger.Error}
    local = global_ #dict()
    execfile(scenario, global_, local)
    setup_method = local.get(SETUP_METHOD, None)
    run_method = local.get(RUN_METHOD, None)
    if not run_method:
        optparser.error("experiment script must contains a 'run(browser)' method without parameters that provide the future experiment scenario execution")    
    logger.Info('****************************************')
    logger.Info('process scenario: {0}', scenario)
    logger.Info('****************************************')
    start_time = time.time()
    try:
        logger.Debug('create browser instance')
        browser = webbench.Ie('client-1')
        config = ConfigParser.SafeConfigParser()        
        if os.path.isfile(configpath) :
            with open(configpath) as configfile:
                config.readfp(configfile)
        setup_method(config)
        browser.run()
        run_method(browser)
    finally:
        elapsed_time = time.time() - start_time
        logger.Info('****************************************')
        logger.Info("scenarion [{0}] processed in {1}s", scenario, elapsed_time)
        logger.Info('****************************************')

if __name__=='__main__':
    main()
