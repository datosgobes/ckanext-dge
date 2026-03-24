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
import ckan.model as model
import ckan.lib.base as base
import ckan.lib.helpers as h
from ckan.logic.action.create import _check_access

from flask import Blueprint, url_for
import ckan.views.dataset as Dataset
import ckanext.dge.views.package as Package
import ckan.authz as authzCkan
import ckan.plugins.toolkit as toolkit
from ckan.common import request, c, _
import ckanext.dge_dataservice.views as dge_dataservice_views
from ckanext.dge.views.util import dge_download_csv

import logging
log = logging.getLogger(__name__)

dgePackage = Blueprint(
    'dgePackage',
    __name__,
)

def _guess_package_type(expecting_name=False):
    """
        Guess the type of package from the URL handling the case
        where there is a prefix on the URL (such as /data/package)
    """

    if request.path == '/':
        return 'dataset'
    parts = [x for x in request.path.split('/') if x]
    idx = -1
    if expecting_name:
        idx = -2
    pt = parts[idx]
    if pt == 'package' or pt == 'catalogo':
        pt = 'dataset'
    if pt == 'servicios-datos':
        pt = 'dataservice'
    return pt

def _get_package_owner_org(id):
    """
    Given the id of a package this method will return the owner_org_ id of the
    package, or 'dataset' if no type is currently set
    """
    pkg = model.Package.get(id)
    if pkg:
        return pkg.owner_org or None 
    return None

def search():
    from ckan.lib.search import SearchError
    
    package_type = _guess_package_type()
    if (package_type == 'harvest'):
        user = authzCkan.get_user_id_for_username(c.user, allow_none=True)
        if not user:
            base.abort(401, _('Not authorized to see this page'))
    elif package_type == 'dataservice':
        return dge_dataservice_views.search()
    return Dataset.search(package_type)

def history(id):
    context = {'model': model, 'session': model.Session,
                'user': c.user or c.author, 'auth_user_obj': c.userobj}
    data_dict = {'id': id}
    package_type = Package._get_package_type(id)
    try:
        if (package_type == 'harvest'):
            data_dict['owner_org'] = _get_package_owner_org(id)
            _check_access('dge_harvest_source_show', context, data_dict)
    except toolkit.NotAuthorized:
        base.abort(401, _('Not authorized to see this page'))
    return Dataset.history(package_type, id)

def download_csv():
    package_type = 'harvest'
    return dge_download_csv(package_type)

dgePackage.add_url_rule('/harvest', 'harvest_search', view_func=search)
dgePackage.add_url_rule('/harvest/new', 'harvest_new', defaults={u'package_type': u'harvest'}, view_func=Dataset.CreateView.as_view(str(u'new')))
dgePackage.add_url_rule('/harvest/history<id>', 'harvest_history', view_func=history)
dgePackage.add_url_rule('/harvest/download_csv', 'download_csv', view_func=download_csv)

#Redirect to catalogo/
def index():
    package_type = _guess_package_type()
    if package_type == 'dataservice':
        return dge_dataservice_views.index
    return h.redirect_to('/' + h.lang() + url_for('package.search') + _get_query_string())

def catalogo(path=None):
    return h.redirect_to('/' + h.lang() + url_for('package.search') + '/' + path)

def newResource(id):
    return h.redirect_to('/' + h.lang() + url_for('package.new_resource', id=id))

def editResource(id,resource_id):
    return h.redirect_to('/' + h.lang() + url_for('package.resource_edit', id=id, resource_id=resource_id))

def deleteResource(id,resource_id):
    return h.redirect_to('/' + h.lang() + url_for('package.resource_delete', id=id, resource_id=resource_id))

dgePackage.add_url_rule('/', view_func=index)

dgePackage.add_url_rule('/packages/', view_func=index)
dgePackage.add_url_rule('/packages/<path:path>', view_func=catalogo)

dgePackage.add_url_rule('/package/', view_func=index)
dgePackage.add_url_rule('/package/<path:path>', view_func=catalogo)

dgePackage.add_url_rule('/dataset/', view_func=index)
dgePackage.add_url_rule('/dataset/<id>/resource/new', view_func=newResource)
dgePackage.add_url_rule('/dataset/<id>/resource/<resource_id>/edit', view_func=editResource)
dgePackage.add_url_rule('/dataset/<id>/resource/<resource_id>/delete', view_func=deleteResource)
dgePackage.add_url_rule('/dataset/<path:path>', view_func=catalogo)

dgePackage.add_url_rule('/dashboard/<path:path>', view_func=catalogo)

def _get_query_string():
    query_string = ''
    _query_string = request.query_string.decode('utf-8')
    if _query_string:
        query_string = f'?{_query_string}'
    return query_string
