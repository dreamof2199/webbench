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

import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * A scenario runner of delayed sub-scenario tasks
 * where the sub-scenario task is executed when its delay has expired
 */
public class DelayScenario extends AbstractScenario {
    private final long delay;
    private final TimeUnit unit;

    DelayScenario(int nbClient, long delay, TimeUnit unit) {
        super(nbClient);
        this.delay = delay;
        this.unit = unit;
    }

    @Override
    void execute(List<Callable<Void>> tasks) {
        ScheduledExecutorService executorService = Executors.newScheduledThreadPool(tasks.size());
        for (int i = 0; i < tasks.size() ; i++) {
            executorService.schedule(tasks.get(i), delay * i, unit);
        }
    }

}
