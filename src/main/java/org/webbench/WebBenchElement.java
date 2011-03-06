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
import org.openqa.selenium.WebElement;

import java.util.List;

/**
 * Created by IntelliJ IDEA.
 * User: romain.gilles
 * Date: 2/22/11
 * Time: 6:57 AM
 * To change this template use File | Settings | File Templates.
 */
public interface WebBenchElement extends WebElement, WebBenchSearchContext {
    void click(ValidationCallback callback);

    void submit(ValidationCallback callback);

    boolean toggle(ValidationCallback callback);

    void setSelected(ValidationCallback callback);

    void sendKeys(ValidationCallback callback, CharSequence... charSequences);

    void click(String action, ValidationCallback callback);

    void submit(String action, ValidationCallback callback);

    boolean toggle(String action, ValidationCallback callback);

    void setSelected(String action, ValidationCallback callback);

    void sendKeys(String action, ValidationCallback callback, CharSequence... charSequences);
}
