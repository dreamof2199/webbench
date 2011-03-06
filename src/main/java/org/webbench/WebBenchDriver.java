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


import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;

import java.net.URL;


/**
 * @author Romain Gilles
 */
public interface WebBenchDriver extends WebDriver, WebBenchSearchContext {

    class Factory {
        public static WebBenchDriver newWebBenchDriver(WebDriver driver) {
            return WebBenchDriverWrapper.newDriver(driver);
        }
    }

    interface WebBenchNavigation extends Navigation {
        void back(ValidationCallback callback);

        void forward(ValidationCallback callback);

        void to(String s, ValidationCallback callback);

        void to(URL url, ValidationCallback callback);

        void refresh(ValidationCallback callback);

        void back(String action, ValidationCallback callback);

        void forward(String action, ValidationCallback callback);

        void to(String s, String action, ValidationCallback callback);

        void to(URL url, String action, ValidationCallback callback);

        void refresh(String action, ValidationCallback callback);
    }

    interface WebBenchTargetLocator extends TargetLocator{
        WebBenchDriver frame(int i);

        WebBenchDriver frame(String s);

        WebBenchDriver frame(WebElement webElement);

        WebBenchDriver window(String s);

        WebBenchDriver defaultContent();

        WebBenchElement activeElement();

        WebBenchAlert alert();
    }

    void get(String s, ValidationCallback callback);
    void get(String s, String action, ValidationCallback callback);

    WebBenchNavigation navigate();

    WebBenchTargetLocator switchTo();

}
