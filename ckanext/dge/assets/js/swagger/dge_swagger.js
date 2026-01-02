/*
* Copyright (C) 2025 Entidad Pública Empresarial Red.es
*
* This file is part of "dge (datos.gob.es)".
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program. If not, see <http://www.gnu.org/licenses/>.
*/

// Enable JavaScript's strict mode. Strict mode catches some common
// programming errors and throws exceptions, prevents some unsafe actions from
// being taken, and disables some confusing and bad JavaScript features.
"use strict";

//$(function () {
ckan.module('dge_swagger', function ($, _) {
  return {
    initialize: function () {
  var url = window.location.search.match(/url=([^&]+)/);
  if (url && url.length > 1) {
    url = decodeURIComponent(url[1]);
  } else {
    url = this.options.url;
  }
  $("#header").hide();

  // Pre load translate...
  if(window.SwaggerTranslator) {
    window.SwaggerTranslator.translate();
  }
  window.swaggerUi = new SwaggerUi({
    url: url,
    dom_id: "swagger-ui-container",
    supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],

    onComplete: function(swaggerApi, swaggerUi){
      if(typeof initOAuth == "function") {
        initOAuth({
          clientId: "your-client-id",
          clientSecret: "your-client-secret-if-required",
          realm: "your-realms",
          appName: "your-app-name", 
          scopeSeparator: ",",
          additionalQueryStringParams: {}
        });
      }

      if(window.SwaggerTranslator) {
        window.SwaggerTranslator.translate();
      }

      $('pre code').each(function(i, e) {
        hljs.highlightBlock(e)
      });

      addApiKeyAuthorization();
    },

    onFailure: function(data) {
      log("Unable to Load SwaggerUI");
    },

    docExpansion: 'list',
    jsonEditor: false,
    apisSorter: "alpha",
    defaultModelRendering: 'schema',
    showRequestHeaders: false
  });

  function addApiKeyAuthorization(){
    var key = encodeURIComponent($('#input_apiKey')[0].value);
    if(key && key.trim() != "") {
    var apiKeyAuth = new SwaggerClient.ApiKeyAuthorization("api_key", key, "query");
      window.swaggerUi.api.clientAuthorizations.add("api_key", apiKeyAuth);
      log("added key " + key);
    }
  }

  $('#input_apiKey').change(addApiKeyAuthorization);


  window.swaggerUi.load();

  function log() {
    if ('console' in window) {
      console.log.apply(console, arguments);
    }
  }
    } };
});