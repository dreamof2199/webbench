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

import org.openqa.selenium.Alert;

/**
 * @author Romain Gilles
 */
public class WebBenchAlertWrapper implements WebBenchAlert {
    private final Alert delegate;

    private WebBenchAlertWrapper(Alert delegate) {
        this.delegate = delegate;
    }

    public static WebBenchAlert newAlert(Alert delegate) {
        return new WebBenchAlertWrapper(delegate);
    }

    public void dismiss() {
        delegate.dismiss();
    }

    public void accept() {
        delegate.accept();
    }

    public String getText() {
        return delegate.getText();
    }

    public void sendKeys(String s) {
        delegate.sendKeys(s);
    }
}
