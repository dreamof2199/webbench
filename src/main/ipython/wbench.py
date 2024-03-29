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
#import threading
#import subprocess
#from threading import Thread
import clr
#import ConfigParser
clr.AddReference('NLog')
import webbench
from webbench.driver import action
from webbench.runner import *
#from NLog import Logger
from NLog import LogManager
#from NLog import LogLevel
#from NLog.Config import LoggingConfiguration
#from NLog.Targets import ColoredConsoleTarget
#from NLog.Targets import FileTarget
#from NLog.Config import LoggingRule
#from NLog.Layouts import CsvLayout
#from NLog.Layouts import CsvColumn
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

HEADLESS_DEFAULT = False
HEADLESS_OPT='''Specify if the scenario must be executed in headless mode. Default value is [{0}]'''.format(HEADLESS_DEFAULT)

logger = LogManager.GetLogger("webbench.bench")

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
    optparser.add_option( '--headless', help = HEADLESS_OPT,
                          dest = 'headless', action='store_true', default=HEADLESS_DEFAULT )
    
    options, args = optparser.parse_args()

    if len(args) == 1:
        scenario = args[0]
    else:
        optparser.error("you must specify a scenario path")
    if options.nb_browser < 1:
        optparser.error("you must specify number of browser(s) gretter than 0 and not {0}".format(options.nb_browser))
    if options.launch_delay < 0 :
        optparser.error("you must specify number of browser(s) gretter or equals to 0 and not {0}".format(options.launch_delay))
    if options.random_time < 0 :
        optparser.error("you must specify number of browser(s) gretter or equals to 0 and not {0}".format(options.random_time))
    
    initconsollogger(options.debug)
    

    if options.dry_run:
        logger.Info('dry-run mode activated') 
    
    if not os.path.isfile(scenario) :
        optparser.error("scenario path must point a file: {0}".format(str(scenario))) 
    
    (run_method, setup_method) = getscenariomethodes(scenario, 'webbench')
    if not run_method:
        optparser.error("experiment script must contains a 'run(browser)' method without parameters that provide the future experiment scenario execution")
    logger.Info('****************************************')
    logger.Info('process scenario: {0}', scenario)
    logger.Info('****************************************')
    
    start_time = time.time()
    
    if options.nb_browser < 2:
        execute = localexecute
    else:
        execute = processexecute
    execute = localexecute #TODO use multi process
    try:
        execute(scenario, options.debug, options.nb_browser, options.launch_delay, options.keep_alive, options.random_time, options.headless)
    finally:
        elapsed_time = time.time() - start_time
        logger.Info('****************************************')
        logger.Info("scenarion [{0}] processed in {1}s", scenario, elapsed_time)
        logger.Info('****************************************')

if __name__=='__main__':
    main()
