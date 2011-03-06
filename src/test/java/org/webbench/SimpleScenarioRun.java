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
import org.openqa.selenium.ie.InternetExplorerDriver;
//import org.openqa.selenium.ie.InternetExplorerDriver;

/**
 * @author Romain Gilles
 */
public class SimpleScenarioRun {
    public static void main (String args[]) throws Exception {
        WebDriver driver1 = null;
        WebDriver driver2 = null;
        try{
        driver1 = new InternetExplorerDriver();
        driver1.get("http://www.google.com");
        Thread.sleep(5000);
        System.out.println("launch 2sd ie");
        driver2 = new InternetExplorerDriver();
        driver2.get("http://www.google.com");
        Thread.sleep(5000);
        } finally {
            if (driver1 != null) {
                System.out.println("close 1th ie");
                driver1.quit();
            }
            if (driver2 != null) {
                System.out.println("close 2sd ie");
                driver2.quit();
            }
        }

        System.out.println("end");
    }
}
