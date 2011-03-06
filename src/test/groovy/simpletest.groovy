import org.openqa.selenium.WebDriver
import org.openqa.selenium.WebElement
import org.openqa.selenium.By
import org.openqa.selenium.ie.InternetExplorerDriver
import org.webbench.WebBenchDriver

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

/**
 * @author Romain Gilles
 */

// Create a new instance of the Firefox driver
// Notice that the remainder of the code relies on the interface,
// not the implementation.
WebBenchDriver driver = WebBenchDriver.Factory.newWebBenchDriver(new InternetExplorerDriver())
//WebDriver driver = new InternetExplorerDriver()

// And now use this to visit Google
driver.get("http://www.google.com");

// Find the text input element by its name
WebElement element = driver.findElement(By.name("q"));

// Enter something to search for
element.sendKeys("Cheese!");

// Now submit the form. WebDriver will find the form for us from the element
element.submit();

// Check the title of the page
System.out.println("Page title is: " + driver.getTitle());

//Close the browser
driver.quit();