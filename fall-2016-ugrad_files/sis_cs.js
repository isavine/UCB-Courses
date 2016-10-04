(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
(function() {
  'use strict';

  module.exports = {
    util: require('./util.js')
  };
})();

},{"./util.js":2}],2:[function(require,module,exports){
(function() {
  'use strict';

  /**
   * Get all the URL Parameters from the querystring
   * Base code is at http://stackoverflow.com/a/2880929
   * @return {Object} Object with key/value pairs for the querystring
   */
  var urlParams = function() {
    var urlParams = {};
    var match;
    var pl = /\+/g;  // Regex for replacing addition symbol with a space
    var search = /([^&=]+)=?([^&]*)/g;
    var decode = function(s) {
      return decodeURIComponent(s.replace(pl, ' '));
    };
    var query = window.location.search.substring(1);

    /* jshint -W084 */
    while (match = search.exec(query)) {
      urlParams[decode(match[1])] = decode(match[2]);
    }
    /* jshint +W084 */

    return urlParams;
  };

  module.exports = {
    urlParams: urlParams
  };
})();

},{}],3:[function(require,module,exports){
require('./navbar.js');

},{"./navbar.js":4}],4:[function(require,module,exports){
'use strict';

var api = require('./api');

var interval;

/**
 * See whether the current page is loaded within an iframe
 * http://stackoverflow.com/a/326076
 */
var isInIframe = function() {
  try {
    return window.self !== window.top;
  } catch (e) {
    return true;
  }
};

/**
 * Prepend an HTML node to another one
 */
var prependChild = function(parent, child) {
  parent.insertBefore(child, parent.firstChild);
};

/**
 * Remove the native Oracle bar
 */
var removeNativeBar = function() {
  var nativeBar = document.querySelector('#PT_HEADER');
  if (nativeBar) {
    nativeBar.parentNode.removeChild(nativeBar);
  }
};

/**
 * Decode a parameter until it no longer needs any decoding
 * @param {String} param The param you would like to decode
 * @return {String} Decoded param
 */
var decodeParam = function(param) {
  if (param && param.indexOf('%') !== -1) {
    return decodeParam(decodeURIComponent(param));
  }

  return param;
};

/**
 * Create the CalCentral bar
 * Example URL:
 * https://bcs-web-dev-03.is.berkeley.edu:8443/psc/bcsdev/EMPLOYEE/HRMS/c/UC_KITCHEN_SINK_FL.UC_FL_KITCHSINK_FL.GBL?ucFrom=CalCentral&ucFromLink=https://calcentral.berkeley.edu&ucFromText=Financial%20Aid
 * @param {Object} params Parameters passed through from the URL
 */
var createCalCentralBar = function(params) {
  var ucFromText = decodeParam(params.ucFromText);
  var text = ucFromText ? 'Return to ' + ucFromText : 'Return';
  var ucFromLink = decodeParam(params.ucFromLink);
  var calcentralBar = '<div class="uc-calcentral-logo-container">' +
    '<a href="' + ucFromLink + '" class="uc-calcentral-logo">' +
      'Back to CalCentral' +
    '</a>' +
  '</div>' +
  '<div class="uc-calcentral-back-container">' +
    '<a href="' + ucFromLink + '" class="uc-calcentral-back">' +
      text +
    '</a>' +
  '</div>';

  var wrapper = document.createElement('div');
  wrapper.setAttribute('class', 'uc-calcentral-header');
  wrapper.innerHTML = calcentralBar;

  return wrapper;
};

/**
 * Add the CalCentral bar to the page
 * @param {Object} params Parameters passed through from the URL
 */
var addCalCentralBar = function(params) {
  var body = document.querySelector('body');
  var calcentralBar = createCalCentralBar(params);
  prependChild(body, calcentralBar);
};

/**
 * Create the Berkeley bar
 * Example URL:
 * https://bcs-web-dev-03.is.berkeley.edu:8443/psc/bcsdev/EMPLOYEE/HRMS/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL?ucFrom=berkeley
 */
var createBerkeleyBar = function() {
  var calcentralBar = '<div class="uc-berkeley-logo-container">' +
    '<div class="uc-berkeley-logo"></div>' +
  '</div>';

  var wrapper = document.createElement('div');
  wrapper.setAttribute('class', 'uc-berkeley-header');
  wrapper.innerHTML = calcentralBar;

  return wrapper;
};

/**
 * Add the Berkeley bar to the page
 */
var addBerkeleyBar = function() {
  var body = document.querySelector('body');
  var calcentralBar = createBerkeleyBar();
  prependChild(body, calcentralBar);
};

/**
 * Add this class to the body so we know that the CalCentral bar has been added
 */
var addCalCentralCSSClass = function() {
  var body = document.querySelector('body');
  body.className += ' uc-calcentral-header-added';
};

/**
 * Load the bar when the correct query params are being passed through
 */
var loadBar = function() {
  var params = api.util.urlParams();
  var checkParamsCalCentral = (params.ucFrom && params.ucFromLink);

  // Make sure we check the params and only add it when it hasn't been added before
  // Also make sure we don't load the bar within a pop-up (iframe)
  if (checkParamsCalCentral && !document.querySelector('.uc-calcentral-header') && !isInIframe()) {
    removeNativeBar();
    addCalCentralBar(params);
    addCalCentralCSSClass();
  }

  if (params.ucFrom && params.ucFrom === 'berkeley') {
    removeNativeBar();
    addBerkeleyBar();
    addCalCentralCSSClass();
  }
};

/**
 * We need to stop the interval when the DOM is loaded correctly
 */
var stopInterval = function() {
  clearInterval(interval);
};

/**
 * Check whether the body element exists
 */
var checkBody = function() {
  var body = document.querySelector('body');
  if (body) {
    stopInterval();
    loadBar();
  }
};

interval = setInterval(checkBody, 1);

},{"./api":1}]},{},[3]);
