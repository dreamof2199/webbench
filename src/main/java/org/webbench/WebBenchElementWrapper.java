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

import java.util.Arrays;
import java.util.List;

/**
 * @author Romain Gilles
 */
public class WebBenchElementWrapper implements WebBenchElement {
    private final WebElement delegate;

    private WebBenchElementWrapper(WebElement delegate) {
        this.delegate = delegate;
    }

    static String getDefaultAction(String method) {
        return WebBenchDriverWrapper.getDefaultAction(method, "");
    }
    static String getDefaultAction(String method, String params) {
        return WebBenchDriverWrapper.getDefaultAction(method, params);
    }


    static WebBenchElement newElement(WebElement delegate) {
        return new WebBenchElementWrapper(delegate);
    }
    public void click() {
        click(ValidationCallback.ALWAYS_TRUE);
    }

    public void submit() {
        submit(ValidationCallback.ALWAYS_TRUE);
    }

    public String getValue() {
        return delegate.getValue();
    }

    public void sendKeys(CharSequence... charSequences) {
        sendKeys(ValidationCallback.ALWAYS_TRUE,charSequences);
    }

    public void clear() {
        delegate.clear();
    }

    public String getTagName() {
        return delegate.getTagName();
    }

    public String getAttribute(String s) {
        return delegate.getAttribute(s);
    }

    public boolean toggle() {
        return delegate.toggle();
    }

    public boolean isSelected() {
        return delegate.isSelected();
    }

    public void setSelected() {
        setSelected(ValidationCallback.ALWAYS_TRUE);
    }

    public boolean isEnabled() {
        return delegate.isEnabled();
    }

    public String getText() {
        return delegate.getText();
    }

    public List<WebElement> findElements(By by) {
        return delegate.findElements(by);
    }

    public WebBenchElement findElement(By by) {
        return newElement(delegate.findElement(by));
    }

    public void click(ValidationCallback callback) {
        click(getDefaultAction("click"),callback);
    }

    public void submit(ValidationCallback callback) {
        submit(getDefaultAction("submit"),callback);
    }

    public boolean toggle(ValidationCallback callback) {
        return toggle(getDefaultAction("toggle"),callback);
    }

    public void setSelected(ValidationCallback callback) {
        setSelected(getDefaultAction("setSelected"),callback);
    }

    public void sendKeys(ValidationCallback callback, CharSequence... charSequences) {
        sendKeys(getDefaultAction("sendKeys", Arrays.asList(charSequences).toString()),callback,charSequences);
    }

    public List<WebBenchElement> findElements2(By by) {
        return WebBenchDriverWrapper.wrap(findElements(by));
    }

    public void click(String action, ValidationCallback callback) {
        new Timer<Void> () {
            @Override
            protected Void doExecute() {
                delegate.click();
                return null;
            }
        }.execute(action, callback);
    }

    public void submit(String action, ValidationCallback callback) {
        new Timer<Void> () {
            @Override
            protected Void doExecute() {
                delegate.submit();
                return null;
            }
        }.execute(action, callback);
    }

    public boolean toggle(String action, ValidationCallback callback) {
        return new Timer<Boolean> () {
            @Override
            protected Boolean doExecute() {
                return delegate.toggle();
            }
        }.execute(action, callback);
    }

    public void setSelected(String action, ValidationCallback callback) {
        new Timer<Void> () {
            @Override
            protected Void doExecute() {
                delegate.setSelected();
                return null;
            }
        }.execute(action, callback);
    }

    public void sendKeys(String action, ValidationCallback callback, final CharSequence... charSequences) {
        new Timer () {
            @Override
            protected Void doExecute() {
                delegate.sendKeys(charSequences);
                return null;
            }
        }.execute(action, callback);
    }
}
