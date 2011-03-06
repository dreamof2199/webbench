import org.webbench.WebBenchDriver
import org.openqa.selenium.ie.InternetExplorerDriver
import org.openqa.selenium.By
import org.openqa.selenium.WebElement
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
 * Created by IntelliJ IDEA.
 * User: romain.gilles
 * Date: 2/24/11
 * Time: 4:48 PM
 * To change this template use File | Settings | File Templates.
 */
WebBenchDriver driver = WebBenchDriver.Factory.newWebBenchDriver(new InternetExplorerDriver())
//WebDriver driver = new InternetExplorerDriver()

// And now use this to visit Google
driver.get("http://ptxs11290-a:8092/kplustp/");

// Find the text input element by its name
WebElement element = driver.findElement(By.name("j_username"));
// Enter something to search for
element.sendKeys("kplustp");

// Find the text input element by its name
element = driver.findElement(By.name("j_password"));
// Enter something to search for
element.sendKeys("kplustp20");
element.submit()


print 'end'
driver.quit()

//Thread.sleep(1000)
//driver = WebBenchDriver.Factory.newWebBenchDriver(new InternetExplorerDriver())

// And now use this to visit Google
//driver.get("http://ptxs11290-a:8092/kplustp/");