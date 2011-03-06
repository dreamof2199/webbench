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
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;

import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/**
 * - TODO handle log file creation
 * - Create synchronization feature
 * - Provide a scenario name
 * @author Romain Gilles
 */
public class WebBenchDriverWrapper implements WebBenchDriver {

    private final WebDriver delegate;

    private WebBenchDriverWrapper(WebDriver delegate) {
        this.delegate = delegate;
    }

    static public WebBenchDriver newDriver(WebDriver delegate) {
        return new WebBenchDriverWrapper(delegate);
    }

    public void get(final String s) {
        get(s, ValidationCallback.ALWAYS_TRUE);
    }

    public void get(final String s, String action, ValidationCallback callback) {
        new Timer<Void> () {
            @Override
            protected Void doExecute() {
                delegate.get(s);
                return null;
            }
        }.execute(action, callback);
    }

    public void get(String s, ValidationCallback callback) {
        get(s, defaultGetAction(s), callback);
    }

    private static String defaultGetAction(String s) {
        String method = "get";
        return getDefaultAction(method, s);
    }

    static String getDefaultAction(String method, String params) {
        return String.format("%s(%s)", method, params);
    }

    static String getDefaultAction(String method) {
        return getDefaultAction(method, "");
    }

    public String getCurrentUrl() {
        return delegate.getCurrentUrl();
    }

    public String getTitle() {
        return delegate.getTitle();
    }

    public List<WebElement> findElements(By by) {
        return delegate.findElements(by);
    }

    public List<WebBenchElement> findElements2(By by) {
        return wrap(findElements(by));
    }

    static List<WebBenchElement> wrap(List<WebElement> elements) {
        List<WebBenchElement> result = new ArrayList<WebBenchElement>(elements.size());
        for (WebElement element : elements) {
            result.add(WebBenchElementWrapper.newElement(element));
        }
        return result;
    }

    public WebBenchElement findElement(By by) {
        return WebBenchElementWrapper.newElement(delegate.findElement(by));
    }

    public String getPageSource() {
        return delegate.getPageSource();
    }

    public void close() {
        delegate.close();
    }

    public void quit() {
        delegate.quit();
    }

    public Set<String> getWindowHandles() {
        return delegate.getWindowHandles();
    }

    public String getWindowHandle() {
        return delegate.getWindowHandle();
    }

    public WebBenchTargetLocator switchTo() {
        return new TargetLocatorWrapper(delegate.switchTo());
    }



    public WebBenchNavigation navigate() {
        return new NavigationWrapper(delegate.navigate());
    }

    public Options manage() {
        return delegate.manage();
    }

    class NavigationWrapper implements WebBenchNavigation {
        private final Navigation navigationDelegate;

        NavigationWrapper(Navigation navigationDelegate) {
            this.navigationDelegate = navigationDelegate;
        }

        public void back() {
            back(ValidationCallback.ALWAYS_TRUE);
        }

        public void forward() {
            forward(ValidationCallback.ALWAYS_TRUE);
        }

        public void to(String s) {
            to(s, ValidationCallback.ALWAYS_TRUE);
        }

        public void to(URL url) {
            to(url, ValidationCallback.ALWAYS_TRUE);
        }

        public void refresh() {
            refresh(ValidationCallback.ALWAYS_TRUE);
        }

        public void back(ValidationCallback callback) {
            back(getDefaultAction("back"), callback);
        }

        public void forward(ValidationCallback callback) {
            forward(getDefaultAction("forward"),callback);
        }

        public void to(String s, ValidationCallback callback) {
            to(s, getDefaultAction("to", s), callback);
        }

        public void to(URL url, ValidationCallback callback) {
            to(url, getDefaultAction("to", String.valueOf(url)), callback);
        }

        public void refresh(ValidationCallback callback) {
            refresh(getDefaultAction("refresh"),callback);
        }

        public void back(String action, ValidationCallback callback) {
            new Timer() {
                @Override
                protected Void doExecute() {
                    navigationDelegate.back();
                    return null;
                }
            }.execute(action, callback);
        }

        public void forward(String action, ValidationCallback callback) {
            new Timer() {
                @Override
                protected Void doExecute() {
                    navigationDelegate.forward();
                    return null;
                }
            }.execute(action, callback);
        }

        public void to(final String s, String action, ValidationCallback callback) {
            new Timer() {
                @Override
                protected Void doExecute() {
                    navigationDelegate.to(s);
                    return null;
                }
            }.execute(action, callback);
        }

        public void to(final URL url, String action, ValidationCallback callback) {
            new Timer() {
                @Override
                protected Void doExecute() {
                    navigationDelegate.to(url);
                    return null;
                }
            }.execute(action, callback);
        }

        public void refresh(String action, ValidationCallback callback) {
            new Timer() {
                @Override
                protected Void doExecute() {
                    navigationDelegate.refresh();
                    return null;
                }
            }.execute(action, callback);
        }
    }


    class TargetLocatorWrapper implements WebBenchTargetLocator {
        final TargetLocator targetLocatorDelegate;

        TargetLocatorWrapper(TargetLocator targetLocatorDelegate) {
            this.targetLocatorDelegate = targetLocatorDelegate;
        }

        public WebBenchDriver frame(int i) {
            return newDriver(targetLocatorDelegate.frame(i));
        }

        public WebBenchDriver frame(String s) {
            return newDriver(targetLocatorDelegate.frame(s));
        }

        public WebBenchDriver frame(WebElement webElement) {
            return newDriver(targetLocatorDelegate.frame(webElement));
        }

        public WebBenchDriver window(String s) {
            return newDriver(targetLocatorDelegate.window(s));
        }

        public WebBenchDriver defaultContent() {
            return newDriver(targetLocatorDelegate.defaultContent());
        }

        public WebBenchElement activeElement() {
            return WebBenchElementWrapper.newElement(targetLocatorDelegate.activeElement());
        }

        public WebBenchAlert alert() {
            return WebBenchAlertWrapper.newAlert(targetLocatorDelegate.alert());
        }

    }
}
