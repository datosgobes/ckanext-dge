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


ckan.module('dge_glue', function ($, _) {
  return {
    initialize: function () {
      var sparqlQuery = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"+
        "select distinct ?x ?label where\n"+
        "{\n"+
        " ?x rdfs:label2 ?label\n"+		
        "}\nORDER BY ?label\n"+
        "LIMIT 100\n";

      var yasqe = YASQE(document.getElementById("yasqe"), {
        sparql: {
          showQueryButton: true,
          endpoint: this.options.endpoint
        }
      });

      var yasqeTextArea = document.getElementsByTagName("textarea")[0];
      if (yasqeTextArea && yasqeTextArea.getAttribute('tabIndex') &&  yasqeTextArea.getAttribute('tabIndex') == 0){
        yasqeTextArea.tabIndex = -1;
      }

      var yasr = YASR(document.getElementById("yasr"), {
        //this way, the URLs in the results are prettified using the defined prefixes in the query
        getUsedPrefixes: yasqe.getPrefixesFromQuery
      });
 

      yasqe.options.sparql.callbacks.complete = yasr.setResponse;

      yasqe.setValue(sparqlQuery)

      sparqlQuery = "PREFIX dct: <http://purl.org/dc/terms/>\n"+
        "select distinct ?nombre ?dataset where\n"+
        "{\n"+
        " ?dataset dct:title ?nombre\n"+
        "}\n"+
        "LIMIT 100\n";

      yasqe.query();

      yasqe.setValue(sparqlQuery)
    }
  };
});
