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
from ckan.views.dataset import CreateView, EditView
import ckan.model as model
from ckan.common import g
import ckan.lib.base as base
import ckan.logic as logic
from ckan.lib.plugins import lookup_package_plugin
import ckan.lib.navl.dictization_functions as dict_fns


NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
clean_dict = logic.clean_dict
tuplize_dict = logic.tuplize_dict
parse_params = logic.parse_params
get_action = logic.get_action

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

def _get_pkg_template(template_type, package_type=None):
    pkg_plugin = lookup_package_plugin(package_type)
    method = getattr(pkg_plugin, template_type)
    try:
        return method(package_type)
    except TypeError as err:
        if u'takes 1' not in str(err) and u'takes exactly 1' not in str(err):
            raise
        return method()

def _setup_template_variables(context, data_dict, package_type=None):
    return lookup_package_plugin(package_type).setup_template_variables(
        context, data_dict
    )

def save_dataservice(package_type):
    context = {u'model': model,u'session': model.Session, u'user': g.user, u'auth_user_obj': g.userobj, u'save': u'save' in request.form}
    try:
        check_access(u'package_create', context)
    except NotAuthorized:
        return base.abort(403, _(u'Unauthorized to create a package'))
    try:
        data_dict = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(request.form))))
    except dict_fns.DataError:
        raise Exception (_(u'Integrity Error'))
    
    try:
        data_dict[u'type'] = package_type
        context[u'message'] = data_dict.get(u'log_message', u'')
        id = data_dict.get(u'pkg_name')
        if id:
            data_dict['id'] = id
            pkg = get_action(u'package_update')(context, data_dict)
        else:
            pkg = get_action(u'package_create')(context, data_dict)
        # redirect to view dataservice
        return h.redirect_to(u'{}.read'.format(package_type), id=pkg["id"])
    
    except ValidationError as e:
        errors = e.error_dict
        error_summary = e.error_summary

        form_vars = {
            u'data': data_dict,
            u'errors': errors,
            u'error_summary': error_summary,
            u'dataset_type': package_type,
            u'form_style': u'new'
        }

        errors_json = h.json.dumps(errors)
        
        _setup_template_variables(context, {}, package_type=package_type)
        form_snippet = _get_pkg_template(
            u'package_form', package_type=package_type
        )
        new_template = _get_pkg_template(u'new_template', package_type)

        return base.render(
            new_template,
            extra_vars={
                u'form_vars': form_vars,
                u'form_snippet': form_snippet,
                u'dataset_type': package_type,
                u'resources_json': {},
                u'form_snippet': form_snippet,
                u'errors_json': errors_json
            }
        )

def edit_dataservice(id, package_type, errors=None, error_summary=None):
    context = {u'model': model,u'session': model.Session, u'user': g.user, u'auth_user_obj': g.userobj }
    try:
        check_access(u'package_create', context)
    except NotAuthorized:
        return base.abort(403, _(u'Unauthorized to create a package'))
    
    try:
        data = get_action(u'package_show')(context, {u'id': id})
    except Exception:
        return base.abort(403, _(u'Unable to retrieve package'))    

    resources_json = h.json.dumps(data.get(u'resources', []))
    # convert tags if not supplied in data
    if data and not data.get(u'tag_string'):
        data[u'tag_string'] = u', '.join(h.dict_list_reduce(data.get(u'tags', {}), u'name'))
 
    errors = errors or {}
    form_snippet = _get_pkg_template( u'package_form', package_type=package_type)
    form_vars = {
        u'data': data,
        u'errors': errors,
        u'error_summary': error_summary,
        u'action': u'edit',
        u'dataset_type': package_type,
        u'form_style': u'edit'}
    errors_json = h.json.dumps(errors)

    _setup_template_variables(  context, {u'id': id}, package_type=package_type)
    pkg = context.get(u"package")

    edit_template = _get_pkg_template(u'edit_template', package_type)
    return base.render(
            edit_template,
            extra_vars={
                u'form_vars': form_vars,
                u'form_snippet': form_snippet,
                u'dataset_type': package_type,
                u'pkg_dict': data,
                u'pkg': pkg,
                u'resources_json': resources_json,
                u'form_snippet': form_snippet,
                u'errors_json': errors_json
            }
        )


dge_dataservice_bp.add_url_rule('/servicios-datos', 'redirect_dataservice_search', redirect_to='/catalogo/servicios-datos')
dge_dataservice_bp.add_url_rule('/servicios-datos/', 'redirect_dataservice_search', redirect_to='/catalogo/servicios-datos/')
dge_dataservice_bp.add_url_rule('/dataservice', view_func=redirect_dataservice_search)
dge_dataservice_bp.add_url_rule('/dataservice/', view_func=redirect_dataservice_search)
dge_dataservice_bp.add_url_rule('/dataservice/<id>', view_func=redirect_dataservice_view)
dge_dataservice_bp.add_url_rule('/dataservice/<id>/', view_func=redirect_dataservice_view)
dge_dataservice_bp.add_url_rule(f'{DEFAULT_DATASERVICE_PAGE}', 'search', view_func=dge_dataservice_views.search)
dge_dataservice_bp.add_url_rule(f'{DEFAULT_DATASERVICE_PAGE}/', 'search', view_func=dge_dataservice_views.search)
dge_dataservice_bp.add_url_rule(f'{DEFAULT_DATASERVICE_PAGE}/download_csv', 'download_csv', view_func=download_csv)
dge_dataservice_bp.add_url_rule(f'{DEFAULT_DATASERVICE_PAGE}/new', 'add_dataservice', defaults={u'package_type': u'dataservice'}, view_func=CreateView.as_view(str(u'new')))
dge_dataservice_bp.add_url_rule(f'{DEFAULT_DATASERVICE_PAGE}/edit/<id>', 'edit_dataservice', defaults={u'package_type': u'dataservice'}, view_func=edit_dataservice, methods=['GET'])
dge_dataservice_bp.add_url_rule(f'{DEFAULT_DATASERVICE_PAGE}/save', 'save_dataservice', defaults={u'package_type': u'dataservice'}, view_func=save_dataservice, methods=['POST'])