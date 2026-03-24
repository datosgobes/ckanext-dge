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
import logging
from flask import Blueprint
from ckan.common import _, request
import ckan.lib.helpers as h
from ckanext.dge.views.util import dge_download_csv
import ckanext.dge_dataservice.views as dge_dataservice_views

log = logging.getLogger(__name__)


URL_PREFIX = u'/catalogo'
DEFAULT_DATASERVICE_PAGE = u'{}/servicios-datos'.format(URL_PREFIX)

dge_dataservice_bp = Blueprint(
    'dgeDataservice',
    __name__
)

def download_csv(package_type):
    return dge_download_csv(package_type)

# Endpoints dataservice
def _get_query_string():
    query_string = ''
    _query_string = request.query_string.decode('utf-8')
    if _query_string:
        query_string = f'?{_query_string}'
    return query_string

def redirect_dataservice_search():
    url = h.redirect_to(f'/{h.lang()}{DEFAULT_DATASERVICE_PAGE}{_get_query_string()}')
    log.error(f'SSVG   URL = {url}')
    return url

def redirect_dataservice_view(id):
    return h.redirect_to(f'/{h.lang()}{URL_PREFIX}/{id}')

def download_csv():
    package_type = 'dataservice'
    return dge_download_csv(package_type)


dge_dataservice_bp.add_url_rule('/servicios-datos', 'redirect_dataservice_search', redirect_to='/catalogo/servicios-datos')
dge_dataservice_bp.add_url_rule('/servicios-datos/', 'redirect_dataservice_search', redirect_to='/catalogo/servicios-datos/')
dge_dataservice_bp.add_url_rule('/dataservice', view_func=redirect_dataservice_search)
dge_dataservice_bp.add_url_rule('/dataservice/', view_func=redirect_dataservice_search)
dge_dataservice_bp.add_url_rule('/dataservice/<id>', view_func=redirect_dataservice_view)
dge_dataservice_bp.add_url_rule('/dataservice/<id>/', view_func=redirect_dataservice_view)
dge_dataservice_bp.add_url_rule(f'{DEFAULT_DATASERVICE_PAGE}', 'search', view_func=dge_dataservice_views.search)
dge_dataservice_bp.add_url_rule(f'{DEFAULT_DATASERVICE_PAGE}/', 'search', view_func=dge_dataservice_views.search)
dge_dataservice_bp.add_url_rule(f'{DEFAULT_DATASERVICE_PAGE}/download_csv', 'download_csv', view_func=download_csv)
