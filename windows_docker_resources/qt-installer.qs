/* eslint-disable no-alert, no-console, no-var, linebreak-style, prefer-arrow-callback,
   prefer-template, no-restricted-syntax, quote-props, prefer-destructuring */
// eslint disables were chosen because they are incompatible with the Qt JavaScript Engine

// Copyright 2016 Ben Lau
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// File adapted and modified from the following examples
// https://github.com/benlau/qtci/blob/master/bin/extract-qt-installer
// Modified from shell script to .qs file, and adapted to specific ros2/ci use

// Command line usage
// qt-unified-windows-x86-3.1.1-online.exe --verbose --script qt-installer.qs [Option=Value]
// Options:
//    MsvcVersion=[2015,2017,2019,...]
//    TargetQt5Version=['5.12.7', '5.12.5', '5.12.*', '5.12.[1-5]', or '' (for latest LTS)]
//    ErrorLogArgName='C:\Path\To\Writeable\Logfile'

/* global installer:writeable, gui:writeable, buttons, QMessageBox */

var DefaultQt5Version = '';
var DefaultMsvcVersion = '2019';
var BuildToolsPrefix = 'win64_msvc';
var BuildToolsSuffix = '_64';
var Qt5ComponentPrefix = 'qt.qt5.';
var ErrorLogArgName = 'ErrorLogname';
var MsvcVersionArgName = 'MsvcVersion';
var TargetQt5VersionArgName = 'TargetQt5Version';

var CheckCategory = function CheckCategory(gui, category, shouldCheck) {
  var page = gui.pageWidgetByObjectName('ComponentSelectionPage');
  var checkBox = gui.findChild(page, category);
  if (checkBox) {
    if (checkBox.checked !== shouldCheck) {
      checkBox.click();
    }
  }
};

var FindLatestCompatibleVersion = function FindLatestCompatibleVersion(regex, filterFn) {
  var versions = [];
  var components = installer.components();
  var id;
  var matchResult;

  for (id in components) {
    if (Object.prototype.hasOwnProperty.call(components, id)) {
      // Documentation about QtQmL regex https://doc.qt.io/qt-5/qregexp.html
      matchResult = components[id].name.match(regex);
      if (matchResult && filterFn(matchResult[1])) {
        console.log('Match result: ' + matchResult[1]);
        versions.push(matchResult[1]);
      }
    }
  }
  if (versions.length === 0) {
    return null;
  }
  // We want latest, so sort in descending order
  versions.sort(function DescendingOrder(a, b) { return b - a; });
  return versions[0];
};

var FindMostRecentLTS = function FindMostRecentLTS(targetQt5Version) {
  var regex = '(?:qt.qt5.)';
  if (targetQt5Version !== '') {
    // Match only the target versions. Since it's regex all the way down, patterns with
    // 5.12.*/5.12.[1-5] will also work.
    // String replace uses regex syntax in javascript, this replaces the '.' with ''
    regex += '(' + targetQt5Version.replace(/\./g, '') + ')$';
  }
  else {
    regex += '(\\d+)$';
  }
  // Match component names of the form qt.qt5.5xyz and capture just the 5xyz
  console.log('Regex: ' + regex);
  return FindLatestCompatibleVersion(regex, function IncludeAll() { return true; });
};

var FindMostRecentBuildTools = function FindMostRecentBuildTools(prefix, desiredMsvcYear) {
  var regex = '(?:' + prefix + '.' + BuildToolsPrefix + ')(\\d{4})(?:' + BuildToolsSuffix + ')$';
  var filter = function LessThanOrEqualTo(value) { return Number(value) <= desiredMsvcYear; };
  return FindLatestCompatibleVersion(regex, filter);
};

var SelectQtComponent = function SelectQtComponent() {
  var widget = gui.currentPageWidget();

  var targetQt5Version = installer.value(TargetQt5VersionArgName, DefaultQt5Version);

  var latestVersion = FindMostRecentLTS(targetQt5Version);
  var targetBuildVersion = installer.value(MsvcVersionArgName, DefaultMsvcVersion);

  var prefix;
  var buildToolsVersion;
  var componentId;
  var emptyDiskSpace;

  if (!latestVersion) {
    throw new Error('Finding latest version failed');
  }
  prefix = Qt5ComponentPrefix + latestVersion;

  console.log('Target MSVC Version ' + targetBuildVersion);
  buildToolsVersion = FindMostRecentBuildTools(prefix, targetBuildVersion);
  if (!buildToolsVersion) {
    throw new Error('Finding a component compatibile with the desired buildtools version (' + targetBuildVersion + '}) failed');
  }
  console.log('Available Buildtools version: ' + buildToolsVersion);

  // Should be of the form qt.qt5.5126.win64_msvc2017_64
  componentId = prefix + '.' + BuildToolsPrefix + buildToolsVersion + BuildToolsSuffix;
  console.log('Attempting to check ' + componentId);
  widget.deselectAll();
  emptyDiskSpace = installer.requiredDiskSpace();
  widget.selectComponent(componentId);
  if (emptyDiskSpace === installer.requiredDiskSpace()) {
    throw new Error('Selecting component ' + componentId + ' failed');
  }
  return { 'latestVersion': latestVersion, 'buildToolsVersion': buildToolsVersion };
};

var GetDirectoryFromVersion = function GetDirectoryFromVersion(version) {
  // The versions are of the form 5123, where the first character is the 4/5 version
  // and the last character is the minor version (even if 0), and the middle characters
  // are the major version
  var versionString = String(version);
  var length = version.length;
  if (length < 3 || length > 4) {
    throw new Error('Assertion failed: (version.length < 3 || version.length > 4)');
  }
  return versionString[0] + '.' + versionString.slice(1, length - 1) + '.' + versionString[length - 1];
};


function Controller() {
  installer.installationFinished.connect(function ClickNext() {
    gui.clickButton(buttons.NextButton);
  });
  // If any message boxes need to be rejected, they'll need custom callbacks
  installer.autoAcceptMessageBoxes();
  installer.setMessageBoxAutomaticAnswer('OverwriteTargetDirectory', QMessageBox.Yes);
  installer.setMessageBoxAutomaticAnswer('installationErrorWithRetry', QMessageBox.Ignore);
}

Controller.prototype.WelcomePageCallback = function WelcomePageCallback() {
  // Connects with Qt over internet
  gui.clickButton(buttons.NextButton, 3000);
};

Controller.prototype.CredentialsPageCallback = function CredentialsPageCallback() {
  gui.clickButton(buttons.CommitButton);
};

Controller.prototype.ComponentSelectionPageCallback = function ComponentSelectionPageCallback() {
  var page = gui.pageWidgetByObjectName('ComponentSelectionPage');
  var fetchButton = gui.findChild(page, 'FetchCategoryButton');
  var path = installer.value(ErrorLogArgName, '%temp%\\installer.err');
  var qt5Path;
  // These should be the defaults, but just in case...
  CheckCategory(gui, 'LTS', true);
  CheckCategory(gui, 'Archive', false);
  CheckCategory(gui, 'Latest releases', false);
  CheckCategory(gui, 'Preview', false);
  if (fetchButton) {
    // Refresh components if any of the checkboxes above changed
    fetchButton.click();
  }

  try {
    this.installedVersion = SelectQtComponent();
    if (typeof this.installedVersion !== 'undefined') {
      qt5Path = '@TargetDir@\\' + GetDirectoryFromVersion(this.installedVersion.latestVersion)
        + '\\msvc' + this.installedVersion.buildToolsVersion + '_64';
      console.log('Setting Qt5_DIR Environment Variable to ' + qt5Path);
      installer.performOperation('EnvironmentVariable', ['Qt5_DIR', qt5Path, true, false]);
    }
  } catch (err) {
    // Cancel install if any error is encountered
    console.log(err.fileName + ':' + err.lineNumber + ' ' + err.message);
    console.log('Writing error to file ' + path);
    installer.performOperation('AppendFile', [path, err.message]);
    gui.clickButton(buttons.CancelButton, 5000);
    throw err;
  }

  gui.clickButton(buttons.NextButton);
};

Controller.prototype.IntroductionPageCallback = function IntroductionPageCallback() {
  console.log('Retrieving meta information from remote repository');
  gui.clickButton(buttons.NextButton);
};

Controller.prototype.TargetDirectoryPageCallback = function TargetDirectoryPageCallback() {
  // Default location is C:\Qt\Qt5.12.6
  gui.clickButton(buttons.NextButton);
};

Controller.prototype.ObligationsPageCallback = function ObligationsPageCallback() {
  var widget = gui.currentPageWidget();
  widget.obligationsAgreement.click();
  for (var id in widget.obligationsAgreement) {
    console.log(id);
  }

  gui.clickButton(buttons.NextButton);
};

Controller.prototype.LicenseAgreementPageCallback = function LicenseAgreementPageCallback() {
  var widget = gui.currentPageWidget();
  if (widget != null) {
    widget.AcceptLicenseRadioButton.setChecked(true);
  }
  gui.clickButton(buttons.NextButton);
};

Controller.prototype.ReadyForInstallationPageCallback = function ReadyForInstallPageCallback() {
  gui.clickButton(buttons.CommitButton);
};

Controller.prototype.FinishedPageCallback = function FinishedPageCallback() {
  var widget = gui.currentPageWidget();
  if (widget.LaunchQtCreatorCheckBoxForm) {
    // No this form for minimal platform
    widget.LaunchQtCreatorCheckBoxForm.launchQtCreatorCheckBox.setChecked(false);
  }

  gui.clickButton(buttons.FinishButton);
};

// Telemetry disabled
Controller.prototype.DynamicTelemetryPluginFormCallback = function DynamicTelemetryFormCallback() {
  var page = gui.pageWidgetByObjectName('DynamicTelemetryPluginForm');
  page.statisticGroupBox.disableStatisticRadioButton.setChecked(true);
  gui.clickButton(buttons.NextButton);
};

Controller.prototype.StartMenuDirectoryPageCallback = function StartMenuDirectoryPageCallback() {
  gui.clickButton(buttons.NextButton);
};
