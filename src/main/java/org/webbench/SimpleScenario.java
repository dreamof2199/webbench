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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.concurrent.*;

/**
 * @author Romain Gilles
 */
public class SimpleScenario extends AbstractScenario {
    private static final Logger logger = LoggerFactory.getLogger("webbench.scenario.simple");
    SimpleScenario(int nbClients) {
        super(nbClients);
    }

    @Override
    void execute(List<Callable<Void>> tasks) {
        try {
            ExecutorService executorService = Executors.newFixedThreadPool(tasks.size());
            List<Future<Void>> results = executorService.invokeAll(tasks);
            for (Future<Void> result : results) {
                try {
                    result.get();
                } catch (ExecutionException e) {
                    logger.error("task execution in error", e);
                }
            }
        } catch (InterruptedException e) {
            logger.error("cannot execute the {} tasks", tasks, e);
        }
    }
}
