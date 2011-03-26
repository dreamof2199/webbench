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
'''
This module aims to provide common method launcher.
'''

import optparse
import os.path  
import time
import shlex
import threading
import subprocess
#from threading import Thread
import clr
import ConfigParser

clr.AddReference('NLog')
import webbench
from webbench.driver import action
from NLog import Logger
from NLog import LogManager
from NLog import LogLevel
from NLog.Config import LoggingConfiguration
from NLog.Targets import ColoredConsoleTarget
from NLog.Targets import FileTarget
from NLog.Config import LoggingRule
from NLog.Layouts import CsvLayout
from NLog.Layouts import CsvColumn

RUN_METHOD = 'run'
SETUP_METHOD = 'setup'
counter = None

logger = LogManager.GetLogger("webbench.runner")

def getoption(config, section, option, default):
    try :
        return config.get(section, option)
    except ConfigParser.NoOptionError:
        return default

def subprocessexecute(scenario_path, debug, nb_browser, launch_delay, timeout, random_time):
    from subprocess import Popen
    (configpath, logpath, csvpath) = getfilepaths(scenario_path)
    config = loadconfig(configpath)
    env = getoption(config,'DEFAULT', 'env','DEFAULT')
    command_line = 'ipy {0}'.format(getoption(config, env, 'runner', 'wbench.py'))
    
    processes = []
    
    if debug:
        command_line = '{0} --debug'.format(command_line)
    
    for i in xrange(1, nb_browser + 1):
        if i > 1 and launch_delay > 0:
            time.sleep(launch_delay)
        child_command_line = '{0} --nb-browser {1} {2}'.format(command_line, i, scenario_path)
        sub_log_path = '{0}-sub-{1}.log'.format(logpath[:logpath.find('.log')],i)
        log_file = open( sub_log_path, 'wb')
        logger.Debug('execute sub process: {0} > {1}', child_command_line, sub_log_path)
        process = subprocess.Popen( shlex.split(child_command_line), stdout=log_file,stderr=subprocess.STDOUT)
        processes.append(process)
    
    interval = timeout/10
    logger.Debug('test subprocesses existance every {0}s, 10 times for a total time of {1}', interval, timeout)
    dead = 0
    for i in xrange(0, 10):
        logger.Debug('poll {0} subprocesses for the {1} time', len(processes), i)
        dead = 0
        for process in processes:
            logger.Debug('poll subprocess: {0}', process.pid)
            if process.poll() is not None:
                logger.Debug('subprocess {0} is dead', process.pid)
                dead = dead + 1
        if dead == len(processes):
            logger.Debug('all subprocesses are terminated in time')
            dead = -1
            break
        time.sleep(interval)
    if dead != -1:
        logger.Debug('timeout of {0} has been riched then kill all {1} subprocesses', timeout, len(processes))
        for process in processes:
            try:
                if process.poll() is None:
                    process.kill()
            except:
                logger.Error('error when kill process: {0}', process.pid)
            
def processexecute(scenario_path, debug, nb_browser, launch_delay, keep_alive, random_time):
    from multiprocessing import Process
    from multiprocessing import Event
    processes = []
    fire_synchro_end = Event()
    for process_number in xrange(0, nb_browser):
        fire_instanciation_end = Event() 
        process = Process(target=doinprocess, args=(scenario_path, debug, process_number, launch_delay, keep_alive, random_time, fire_instanciation_end, fire_synchro_end,),name='scenario-' + process_number)
        fire_instanciation_end.wait() #todo add timeout
    fire_synchro_end.set(True)
    for process in processes:
        process.join()

def doinprocess(scenario_path, debug, nb_browser, launch_delay, keep_alive, random_time, fire_instanciation_end, fire_synchro_end):
    (run_method, browser) = instanciate(scenario_path, nb_browser)
    run(run_method, browser, launch_delay)
    fire_instanciation_end.set(True) #interprocess barrier simulation
    fire_synchro_end.wait() #todo add timeout
    close_browser(browser)

def loadconfig (configpath):
    config = ConfigParser.SafeConfigParser()        
    if os.path.isfile(configpath) :
        logger.Debug('load configuration at: {0}', configpath)
        with open(configpath) as configfile:
            config.readfp(configfile)
    return config

def instanciate(scenario_path, nb_browser):
    (configpath, logpath, csvpath) = getfilepaths(scenario_path)
    config = loadconfig(configpath)
    logger.Debug('create browser {0} instance', nb_browser)
    browser_name = 'client-{0}'.format(nb_browser)
    browser = webbench.Ie(browser_name)
    (run_method, setup_method) = getscenariomethodes(scenario_path, browser_name)
    if setup_method:
        setup_method(config)
    browser.run()
    return (run_method, browser)

def run(run_method, browser, launch_delay):
    logger.Debug('run scenario {0} with delay of {1}', browser.name, launch_delay)
    time.sleep(launch_delay)
    run_method(browser)

def localexecute(scenario_path, debug, nb_browser, launch_delay, keep_alive, random_time):
    logger.Debug('local execution')
    (configpath, logpath, csvpath) = getfilepaths(scenario_path, 'client-{0}'.format(nb_browser))
    if os.path.exists(logpath):
        os.remove(logpath)
    if os.path.exists(csvpath):
        os.remove(csvpath)
    initlogger(debug, csvpath, logpath)
    (run_method, browser) = instanciate(scenario_path, nb_browser)
    run(run_method, browser, launch_delay)
    if not(keep_alive):
        close_browser(browser)

def close_browser (browser):
    logger.Debug('close browser: {0}', browser.name)
    browser.quit()

def debug(message):
    logger.Debug(message)

def info(message):
    logger.Info(message)

def initconsollogger(debug):
    # Step 1. Create configuration object 
    config = LoggingConfiguration()
    # Step 2. Create targets and add them to the configuration 
    consoleTarget = ColoredConsoleTarget()
    config.AddTarget("console", consoleTarget)
    # Step 3. Set target properties 
    consoleTarget.Layout = "[${level}] | ${threadid} (${logger}) | ${message}"
    # Step 4. Define rules
    rule1 = LoggingRule("*", getloglevel(debug), consoleTarget)
    config.LoggingRules.Add(rule1)
    # Step 5. Activate the configuration
    LogManager.Configuration = config

def getloglevel(debug):
    return LogLevel.Debug if debug else LogLevel.Info

def initlogger(debug, csvpath, logpath):
    logger.Debug('csv path: %r' % csvpath)
    logger.Debug('log path: %r' % logpath)

    #logger configuration
    #doc at: 
    #  - http://nlog-project.org/wiki/Configuration_API
    #  - http://nlog-project.org/wiki/Event-context_layout_renderer
    # Step 1. Create configuration object 
    config = LogManager.Configuration
    
    # Step 2. Create targets and add them to the configuration 
    #file
    fileTarget = FileTarget()
    config.AddTarget("file", fileTarget)
    #csv
    csvTarget = FileTarget()
    config.AddTarget("csv", csvTarget);
    
    # Step 3. Set target properties 
    fileTarget.FileName = logpath
    fileTarget.Layout = "${date:format=HH\\:MM\\:ss} | ${level} | [${threadid}] - ${message}"
    
    csvTarget.FileName = csvpath
    #csvTarget.Layout = "${date:format=HH\\:MM\\:ss}, ${threadid}, ${message}"
    csvLayout = CsvLayout()
    csvLayout.WithHeader = True
    csvLayout.Columns.Add(CsvColumn("date", "${date:format=HH\\:MM\\:ss.fffffff}"));
    #csvLayout.Columns.Add(CsvColumn("thread", "${threadid}"))
    csvLayout.Columns.Add(CsvColumn("client", "${event-context:item=client}"))
    csvLayout.Columns.Add(CsvColumn("actionId", "${event-context:item=actionId}"))
    csvLayout.Columns.Add(CsvColumn("action", "${event-context:item=action}"))
    csvLayout.Columns.Add(CsvColumn("elapsed", "${event-context:item=elapsed}"))
    csvLayout.Columns.Add(CsvColumn("url", "${event-context:item=url}"))
    csvTarget.Layout = csvLayout;
    
    # Step 4. Define rules
    log_level = getloglevel(debug)
    rule2 = LoggingRule("*", log_level, fileTarget)
    config.LoggingRules.Add(rule2)
    
    #rule3 = LoggingRule("webbench.action", LogLevel.Info, csvTarget)
    rule3 = LoggingRule("webbench.action", log_level, csvTarget)
    config.LoggingRules.Add(rule3);
    # Step 5. Activate the configuration
    LogManager.Configuration = config
    

def getfilepaths(scenariopath, browser_name='main'):
    filename = os.path.basename(scenariopath)
    if filename.find('.') > -1:
        filename = filename[:filename.find('.')]
    basedir = os.path.dirname(scenariopath)
    basedir = '.' if len(basedir) == 1 else basedir
    filename = os.path.join(basedir,filename)
    csvpath = '{0}-{1}.csv'.format(filename,browser_name)
    configpath = filename + '.cfg'
    logpath = '{0}-{1}.log'.format(filename,browser_name)
    return (configpath, logpath, csvpath)

def getscenariomethodes(scenariopath, browser_name):
    scenario_logger = LogManager.GetLogger(browser_name)
    global_ = {'debug': scenario_logger.Debug, 'info': scenario_logger.Info, 'warn': scenario_logger.Warn, 'error': scenario_logger.Error, 'action': action}
    local = global_ #dict()
    execfile(scenariopath, global_, local)
    setup_method = local.get(SETUP_METHOD, None)
    run_method = local.get(RUN_METHOD, None)
    return (run_method, setup_method)
