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

/**
 * @author Romain Gilles
 */
public abstract class Timer<T> {
    private static final Logger logger = LoggerFactory.getLogger("webbench.timer");

    static Logger getLogger() {
        return logger;
    }


    final T execute(String action, ValidationCallback callback) {
        long start = System.nanoTime();
        T result = doExecute();
        long end = System.nanoTime();
        log(action, callback,start, end);
        return result;
    }

    private void log(String action, ValidationCallback callback, long start, long end) {
        if (logger.isInfoEnabled()) {
            logger.info("action: {}, executed in {}ns, start: {}ns, end: {}ns, successfully: {}"
                    , new Object[]{action, Long.valueOf(end - start), Long.valueOf(start)
                            , Long.valueOf(end), String.valueOf(callback.validate())});
        }
    }

    protected abstract T doExecute();
}
