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

import org.openqa.selenium.By;
import org.openqa.selenium.SearchContext;
import org.openqa.selenium.WebElement;

import java.util.List;

/**
 * Created by IntelliJ IDEA.
 * User: romain.gilles
 * Date: 2/22/11
 * Time: 11:23 AM
 * To change this template use File | Settings | File Templates.
 */
public interface WebBenchSearchContext extends SearchContext {
    List<WebBenchElement> findElements2(By by);

    WebBenchElement findElement(By by);
}

