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

import org.openqa.selenium.Capabilities;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import org.openqa.selenium.remote.RemoteWebDriver;

import java.net.URL;

/**
 * Created by IntelliJ IDEA.
 * User: romain.gilles
 * Date: 2/25/11
 * Time: 11:19 AM
 * To change this template use File | Settings | File Templates.
 */
public class SeleniumServerRun {
    public static void main(String[] args) throws Exception {
        // We could use any driver for our tests...
        DesiredCapabilities capabilities = DesiredCapabilities.internetExplorer();
        // ... but only if it supports javascript
        capabilities.setJavascriptEnabled(true);

        // Get a handle to the driver. This will throw an exception
        // if a matching driver cannot be located
        WebDriver driver1 = new RemoteWebDriver(new URL("http://127.0.0.1:4444/wd/hub"), capabilities);

        // Query the driver to find out more information
//        Capabilities actualCapabilities = ((RemoteWebDriver) driver1).getCapabilities();

        // And now use it
        driver1.get("http://www.google.com");

//        WebDriver driver2 = new RemoteWebDriver(new URL("http://127.0.0.1:4444/wd/hub"), capabilities);
//        driver2.get("http://www.google.com");

//        Thread.sleep(60000);
        driver1.close();
//        driver2.close();
    }
}
