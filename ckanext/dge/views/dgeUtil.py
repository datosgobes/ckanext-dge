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
from urllib.parse import urlencode
import ckan.lib.helpers as h

from flask import Blueprint
from ckantoolkit import config
import ckan.plugins.toolkit as toolkit
from ckan.common import g, request

from flask import render_template
import requests
from ckan.plugins import SingletonPlugin, implements
from ckan.plugins import IRoutes, IConfigurer
from ckan.views.feed import _package_search, _create_atom_id, CKANFeed

from ckanext.dge.helpers import getTabsFromApiDrupal,descargar_csv

import ckan.model as model
import ckan.logic as logic
from ckan import plugins
from ckan.logic import get_action

dgeUtil = Blueprint(
    'dgeUtil',
    __name__,
)

def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, str) else str(v)) for k, v in params]


def url_with_params(url, params):
    params = _encode_params(params)
    print(params)
    return url + '?' + urlencode(params)

def isCkan(search_filter):
    drupal_sections = ['custom_content_type_ckan'] 
   
    return search_filter in drupal_sections


def fetch_content_from_ckan(search_term):
    context = {u'model': model, u'session': model.Session,
                   u'user': g.user, u'auth_user_obj': g.userobj}
    data_dict = {u'q': search_term,
                    u'facet.field': h.facets(),
                    u'rows': 0,
                    u'start': 0,
                    u'sort': u'view_recent desc',
                    u'fq': u'capacity:"public"'}

    try:
        
        query = logic.get_action(u'package_search')(context, data_dict)
        item_count = query['count']
        return item_count  
    except Exception as e:
        print(f"Error al buscar en CKAN: {e}")
        return None



def redirect_search():
    ''' redirect to the url parameter. '''
    search_filter = request.form.get('search_filter')
    search_block_form = request.form.get('search_block_form')

    def redirect_to_catalogo():
        params = (('q', search_block_form), ('sort', 'score desc, metadata_created desc'))
        return h.redirect_to(url_with_params('/' + h.lang() + '/catalogo', params))

    def redirect_to_catalogo_with_tab():
        params = (('q', search_block_form), ('sections_catalog', ''))
        return h.redirect_to(url_with_params('/' + h.lang() + '/catalogo', params))    

    def redirect_to_buscador():
        params = (('keys', search_block_form), ('content_type', search_filter))
        return h.redirect_to(url_with_params('/' + h.lang() + '/buscador', params))

    if not search_filter:
        content = fetch_content_from_ckan(search_block_form)
        
        if content is not None and content > 0 :
            return redirect_to_catalogo()

        drupal_api_result = getTabsFromApiDrupal(h.lang(), search_block_form)
       
        if drupal_api_result is not None and drupal_api_result.get('#tabs'):
            return redirect_to_buscador()
        
        return redirect_to_catalogo()

    if not isCkan(search_filter):
        return redirect_to_buscador()

    return redirect_to_catalogo_with_tab()

dgeUtil.add_url_rule('/util/redirect_search', view_func=redirect_search, methods=(u'POST',))
dgeUtil.add_url_rule('/dashboard/more-view-dataset', view_func=descargar_csv, methods=(u'GET',))
dgeUtil.add_url_rule('/dashboard/content-dataset-evolution', view_func=descargar_csv, methods=(u'GET',))
dgeUtil.add_url_rule('/dashboard/content-dataset-distributions', view_func=descargar_csv, methods=(u'GET',))
dgeUtil.add_url_rule('/dashboard/content-comments-received', view_func=descargar_csv, methods=(u'GET',))
dgeUtil.add_url_rule('/dashboard/users-by-organization', view_func=descargar_csv, methods=(u'GET',))
dgeUtil.add_url_rule('/dashboard/content-data-request-by-state', view_func=descargar_csv, methods=(u'GET',))