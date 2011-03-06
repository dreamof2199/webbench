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

package org.webbench;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.LoggerContext;
import ch.qos.logback.classic.PatternLayout;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.classic.util.ContextInitializer;
import ch.qos.logback.core.FileAppender;
import ch.qos.logback.core.OutputStreamAppender;
import groovy.lang.Binding;
import groovy.lang.GroovyShell;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

/**
 * Initialize the environment and execute the script.
 *
 * @author Romain Gilles
 */
public abstract class AbstractScenario implements Scenario {
    private static final Logger logger = LoggerFactory.getLogger("webbench.scenario");
    /**
     * the name used to register the logger that can be used by groovy script
     */
    public static final String LOGGER_BIND_VAR_NAME = "logger";
    static final String CLIENT = "webbench.client";
    static final String NAME = "webbench.scenario";
    private static final String LOG_PATTERN_LAYOUT = String.format("%d{yyyy/MM/dd HH:mm:ss.SSS} [webbench] (scenario: %X{%s}, client: %X{%s}) - %m%n", NAME, CLIENT);
    private static final String FILE_APPENDER_NAME = "webbench.file";

    private final int nbClients;
    private final String name;
    private final File outputFolder;

//    private static final String LOGGER_CONSOLE_NAME = "webbench.console";


    private void initLog(String logPath) {
        ch.qos.logback.classic.Logger timeLogger = (ch.qos.logback.classic.Logger) Timer.getLogger();
        LoggerContext lc = (LoggerContext) LoggerFactory.getILoggerFactory();
        if (new ContextInitializer(lc).findURLOfDefaultConfigurationFile(false) == null) {
            //deseable basic configuration: see ch.qos.logback.classic.util.ContextInitializer#autoConfig()
            //see ch.qos.logback.classic#BasicConfigurator
            ch.qos.logback.classic.Logger rootLogger = lc.getLogger(ch.qos.logback.classic.Logger.ROOT_LOGGER_NAME);
            rootLogger.setLevel(Level.OFF);
            rootLogger.detachAndStopAllAppenders();
        }
        timeLogger.setLevel(Level.INFO);
        if (!(timeLogger.getAppender(FILE_APPENDER_NAME) instanceof OutputStreamAppender<?>)) {
            FileAppender<ILoggingEvent> fileAppender = new FileAppender<ILoggingEvent>();
            fileAppender.setContext(lc);
            timeLogger.addAppender(fileAppender);
            fileAppender.setName(FILE_APPENDER_NAME);
            fileAppender.setAppend(false);
            fileAppender.setFile(logPath);
            PatternLayout pl = new PatternLayout();
            pl.setPattern(LOG_PATTERN_LAYOUT);
            pl.setContext(lc);
            pl.start();
            fileAppender.setLayout(pl);
            fileAppender.start();
        }
//            if (ConfigUtil.isConsoleEnable()
//                    && !(logger.getAppender(LOGGER_CONSOLE_NAME) instanceof OutputStreamAppender<?>)) {
//                logger.setAdditive(true);
//                ConsoleAppender<ILoggingEvent> appender = new ConsoleAppender<ILoggingEvent>();
//                appender.setContext(lc);
//                logger.addAppender(appender);
//                appender.setName(LOGGER_CONSOLE_NAME);
//                appender.setLayout(createPatternLayout(lc));
//                appender.start();
//            }
    }


    AbstractScenario(String name, int nbClients, File outputFolder) {
        this.nbClients = nbClients;
        this.name = name;
        this.outputFolder = outputFolder == null ? new File(".") : outputFolder;
    }

    @Deprecated
    AbstractScenario(int nbClients) {
        this(null, nbClients, null);

    }

    public static Scenario newScenario(String scenarioName, int nbClient) {
        return new SimpleScenario(nbClient);
    }

    public static Scenario newDelayScenario(String scenarioName, int nbClient, long delay, TimeUnit unit) {
        if (delay < 1) {
            return new SimpleScenario(nbClient);
        } else {
            return new DelayScenario(nbClient, delay, unit);
        }
    }

    abstract void execute(List<Callable<Void>> tasks);

    public void execute(String scenarioPath) {
        File scenarioFile = new File(scenarioPath);
        execute(scenarioFile);
    }

    public void execute(File scenarioFile) {
        if (!scenarioFile.isFile()) {
            throw new ScenarioException(String.format("cannot find the file: %s", scenarioFile.getAbsolutePath()));
        }
        if (!scenarioFile.canRead()) {
            throw new ScenarioException(String.format("cannot read the file: %s", scenarioFile.getAbsolutePath()));
        }

        String scenarioName = getScenarioName(scenarioFile);
        initLog(outputFolder.getAbsolutePath());
        List<Callable<Void>> tasks = new ArrayList<Callable<Void>>();
        for (int i = 0; i < nbClients; i++) {
            tasks.add(new Client(scenarioName, i, scenarioFile));
        }

        ExecutorService executorService = Executors.newFixedThreadPool(nbClients);
        try {
            List<Future<Void>> results = executorService.invokeAll(tasks);
            for (Future<Void> result : results) {
                try {
                    result.get();
                } catch (ExecutionException e) {
                    logger.error("task execution in error", e);
                }
            }
        } catch (InterruptedException e) {
            logger.error("cannot execute the {} tasks", nbClients, e);
        }
    }

    private String getScenarioName(File scenarioFile) {
        return (name != null ? name : scenarioFile.getName());
    }


    private static class Client implements Callable<Void> {
        private final int clientNumber;
        private final File scenarioFile;
        private final String name;

        private Client(String name, int clientNumber, File scenarioFile) {
            this.name = name;
            this.clientNumber = clientNumber;
            this.scenarioFile = scenarioFile;
        }

        public Void call() throws Exception {
            MDC.put(CLIENT, String.valueOf(clientNumber));
            MDC.put(NAME, name);
            Binding binding = new Binding();
            binding.setVariable(LOGGER_BIND_VAR_NAME, logger);
            GroovyShell shell = new GroovyShell(binding);
            shell.evaluate(scenarioFile);
            return null;
        }
    }
}
