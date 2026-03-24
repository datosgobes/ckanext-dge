# Copyright (C) 2026 Entidad Pública Empresarial Red.es
#
# This file is part of "dge (datos.gob.es)".
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-

import json
import urllib
import logging

import ckan.views.dataset as Dataset

from flask import Blueprint, make_response

from ckantoolkit import config
import ckan.lib.base as base
import ckan.plugins.toolkit as toolkit
from ckan.common import c, request
import ckan.model as model
from ckanext.dcat.utils import check_access_header


log = logging.getLogger(__name__)
render = base.render

CONTENT_TYPES = {
    'rdf': 'application/rdf+xml',
    'xml': 'application/rdf+xml',
    'n3': 'text/n3',
    'ttl': 'text/turtle',
    'jsonld': 'application/ld+json',
    'csv': 'text/csv'
}

dge = Blueprint(
    'dge',
    __name__,
)

def yasgui():
    return render('yasgui/sparql.html')

def swagger():
    return render('apidata/apidata.html')

def accessible_swagger():
    return render('apidata/accessible-apidata.html')

def organism():
    organization_list = []
    try:
        prefix = config.get('ckanext.dge.organism.uri', 'http://datos.gob.es/recurso/sector-publico/org/Organismo')
        sql = '''select g.title, ge.value, ge.value
                    from "group" g, group_extra ge
                    where ge.key like 'C_ID_UD_ORGANICA'
                    and ge.group_id LIKE g.id
                    and g.type like 'organization'
                    and ge.state like 'active'
                    and g.state like 'active'
                    order by g.title asc;'''
        result = model.Session.execute(sql)
        for row in result:
            org_name = row[0] if row[0] else None
            dir3 = row[1] if row[1] else None
            if org_name and dir3:
                organization_list.append({
                                            'title': org_name,
                                            'dir3': dir3,
                                            'uri': '%s/%s' % (prefix, dir3)
                                            }) 
    except Exception as e:
        log.error('Exception in organism: %s', e)
    c.organization_list = organization_list
    return render('static/organism.html')

def default_spatial_coverage():
    return render('static/default_spatial_coverage.html')

def spatial_coverage(type, name):
    spatial_dict = {}
    data = None
    item = None
    apidatahost = config.get('ckanext.dge.apidata.host', None)
    apidataurl = config.get('ckanext.dge.apidata.url.spatial', None)
    apidatatype = None
    if type:
        if type == 'Provincia':
            apidatatype = 'Province'
        elif type == 'Autonomia':
            apidatatype = 'Autonomous-region'
        elif type == 'Pais':
            apidatatype = 'Country'
        else:
            apidatatype = None
    if apidatahost and apidataurl and apidatatype and name:
        url = '%s/%s/%s/%s' % (apidatahost, apidataurl, apidatatype, name)
        if url:
            url = urllib.parse.quote(url.encode('utf8'), ':/')
            response = urllib.request.urlopen(url)
            if response:
                data = json.loads(response.read())
        if data:
            items = data.get('result', {}).get('items', {})
            if items and items[0]:
                item = items[0]
    spatial_dict['type'] = type
    spatial_dict['name'] = name
    spatial_dict['label'] = name
    if item:
        spatial_dict['label'] = item.get('label', '')
        spatial_dict['about'] = item.get('_about', '')
        rows = []
        rows.append({'key': 'rdfs:label', 'value': item.get('label', '')})
        if type == 'Provincia':
            rows.append({'key': 'esadm:autonomia', 'value': item.get('autonomia', '')})
        if type == 'Provincia' or type == 'Autonomia':
            rows.append({'key': 'esadm:pais', 'value': item.get('pais', '')})
            rows.append({'key': 'owl:sameAs', 'value': item.get('sameAs', '')})
        complete_type = item.get('type', '')
        if complete_type:
            s_type = complete_type.split('#')
            type = s_type[-1] if s_type else type
        rows.append({'key': 'rdf:type', 'value': 'esadm:%s' % type})
        spatial_dict['rows'] = rows
    c.spatial_dict = spatial_dict
    request.environ['PATH_INFO'] = urllib.parse.quote(request.environ['PATH_INFO'])
    return render('static/spatial-coverage.html')

def default_theme():
    return render('static/default_theme.html')

def theme(name):
    apidatahost = config.get('ckanext.dge.apidata.host', None)
    apidataurl = config.get('ckanext.dge.apidata.url.sector', None)
    data = None
    theme_dict = {}
    item = None
    if apidatahost and apidataurl and name:
        url = '%s/%s/%s' % (apidatahost, apidataurl, name)
        if url:
            error_loading_data = False
            response = urllib.request.urlopen(url)
            if response:
                data = json.loads(response.read())
        if data:
            items = data.get('result', {}).get('items')
            if items and items[0]:
                item = items[0]
    theme_dict['name'] = name
    theme_dict['type'] = 'sector'
    theme_dict['label'] = name
    if item:
        theme_dict['label'] = item.get('prefLabel', '')
        theme_dict['about'] = item.get('_about', '')
        rows = []
        rows.append({'key': 'skos:inScheme', 'value': item.get('inScheme', '')})
        rows.append({'key': 'skos :prefLabel', 'value': item.get('prefLabel', '')})
        complete_type = item.get('type', '')
        type = ''
        if complete_type:
            s_type = complete_type.split('#')
            type = s_type[-1] if s_type else 'Concept'
        rows.append({'key': 'rdf:type', 'value': 'skos:%s' % (type)})
        theme_dict['rows'] = rows
    c.theme_dict = theme_dict
    return render('static/theme.html')

def read_package(_id,_format):
    formats='xml|rdf|n3|ttl|jsonld|csv'
    default_format = 'xml'
    if formats.find(_format) != -1:
        if not _format:
            _format = check_access_header()
        if not _format:
            _format = default_format

        response = make_response()
        response.headers.update(
            {'Content-type': CONTENT_TYPES[_format]})
        try:
            result = toolkit.get_action('dge_harvest_package_show')({}, {'id': _id,
                                                                         'format': _format})
        except toolkit.ObjectNotFound:
            toolkit.abort(404)

        return result

dge.add_url_rule('/sparql', 'yasgui', view_func=yasgui)
dge.add_url_rule('/apidata', 'swagger', view_func=swagger)
dge.add_url_rule('/accessible-apidata', 'accessible_swagger', view_func=accessible_swagger)
dge.add_url_rule('/recurso/sector-publico/org/Organismo', 'organism', view_func=organism)
dge.add_url_rule('/recurso/sector-publico/territorio', 'default_spatial_coverage', view_func=default_spatial_coverage)
dge.add_url_rule('/recurso/sector-publico/territorio/<type>/<name>', 'spatial_coverage', view_func=spatial_coverage)
dge.add_url_rule('/kos/sector-publico/sector', 'default_theme', view_func=default_theme)
dge.add_url_rule('/kos/sector-publico/sector/<name>', 'theme', view_func=theme)
dge.add_url_rule('/catalogo/<_id>.<_format>', 'dge_package', view_func=read_package)