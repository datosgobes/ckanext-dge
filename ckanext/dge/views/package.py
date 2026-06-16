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
from flask import Blueprint, redirect, request
from ckan.views.dataset import CreateView, DeleteView, EditView, resources, search,  _get_pkg_template
from ckan.views.dataset import read as readDataset
import ckan.logic as logic
from ckan.common import _, request, c
from ckan.plugins.toolkit import config
import ckan.plugins.toolkit as toolkit
import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as p
import ckan.lib.helpers as h
from ckanext.dge import helpers
import ckan.lib.datapreview as datapreview
from ckan.lib.plugins import lookup_package_plugin
from ckan.views import LazyView
import ckan.plugins.toolkit as tk
from ckanext.dge.views.util import dge_download_csv
import ckan.lib.navl.dictization_functions as dict_fns

log = logging.getLogger(__name__)

backend = config.get('ckanext.dge.backend.filepath')
render = base.render
abort = base.abort

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = tk.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key

URL_PREFIX = u'/catalogo'
DEFAULT_DATASET_PAGE = u'/conjuntos-datos'

package = Blueprint(
    'package',
    __name__,
    url_prefix=URL_PREFIX,
    url_defaults={u'package_type': u'dataset'}
)


def download_csv(package_type):
    return dge_download_csv(package_type)

def _get_package_type(id):
    """
    Given the id of a package this method will return the type of the
    package, or 'dataset' if no type is currently set
    """
    pkg = model.Package.get(id)
    if pkg:
        return pkg.type or 'dataset'
    return None


def read_ajax(id, revision=None):
    context = {'model': model, 'session': model.Session,
                'user': c.user or c.author, 'auth_user_obj': c.userobj,
                'revision_id': revision}
    try:
        data = get_action('package_show')(context, {'id': id})
    except NotAuthorized:
        abort(401, _('Unauthorized to read package %s') % '')
    except NotFound:
        abort(404, _('Dataset not found'))

    data.pop('tags')
    data = flatten_to_string_key(data)
    toolkit.response.headers['Content-Type'] = 'application/json;charset=utf-8'
    return h.json.dumps(data)



def _resource_preview(data_dict):
    '''Deprecated in 2.3'''
    return bool(datapreview.get_preview_plugin(data_dict,
                                                return_first=True))

def _resource_template(package_type):
    plugin = lookup_package_plugin(package_type)
    if hasattr(plugin, 'resource_template'):
        result = plugin.resource_template()
        if result is not None:
            return result
    return lookup_package_plugin().resource_template()

def resource_read(id, resource_id, package_type='dataset'):
    context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'auth_user_obj': c.userobj,
                   'for_view': True}
    try:
        c.package = get_action('package_show')(context, {'id': id})
    except NotFound:
        abort(404, _('Dataset not found'))
    except NotAuthorized:
        abort(401, _('Unauthorized to read dataset %s') % id)

    c.resource = None
    for resource in c.package.get('resources', []):
        if resource['id'] == resource_id:
            c.resource = resource
            break
    if not c.resource:
        abort(404, _('Resource not found'))

    c.pkg = context['package']
    c.pkg_dict = c.package
    dataset_type = c.pkg.type or 'dataset'

    license_id = c.package.get('license_id')
    try:
        c.package['isopen'] = model.Package. \
            get_license_register()[license_id].isopen()
    except KeyError:
        c.package['isopen'] = False

    c.datastore_api = '%s/api/action' % \
                        config.get('ckan.site_url', '').rstrip('/')

    c.resource['can_be_previewed'] = _resource_preview(
        {'resource': c.resource, 'package': c.package})

    resource_views = get_action('resource_view_list')(
        context, {'id': resource_id})
    c.resource['has_views'] = len(resource_views) > 0

    current_resource_view = None
    view_id = request.args.get(u'view_id')
    if c.resource['can_be_previewed'] and not view_id:
        current_resource_view = None
    elif c.resource['has_views']:
        if view_id:
            current_resource_view = [rv for rv in resource_views
                                        if rv['id'] == view_id]
            if len(current_resource_view) == 1:
                current_resource_view = current_resource_view[0]
            else:
                abort(404, _('Resource view not found'))
        else:
            current_resource_view = resource_views[0]

    vars = {'resource_views': resource_views,
            'current_resource_view': current_resource_view,
            'dataset_type': dataset_type,
            'package': c.package,
            'resource': c.resource,
            'pkg_dict': c.package,
            }

    template = _resource_template(dataset_type)
    return render(template, extra_vars=vars)

def resource_delete(id, resource_id, package_type):
    context = {'model': model, 'session': model.Session,
                'user': c.user or c.author, 'auth_user_obj': c.userobj}
    is_editable = helpers.dge_is_editable(get_action('package_show')(context, {'id': id}))
    if not is_editable:
        return h.redirect_to('package.dataset_read', id=id)
    if 'cancel' in request.params:
        return h.redirect_to('package.resource_edit',
                        resource_id=resource_id, id=id)

    try:
        check_access('package_delete', context, {'id': id})
    except NotAuthorized:
        abort(401, _('Unauthorized to delete package %s') % '')
    pkg_id = None
    resource_dict = None
    try:
        if request.method == 'POST':
            if u'cancel' in request.form:
                return h.redirect_to('package.resource_edit', resource_id=resource_id, id=id)
            
            get_action('resource_delete')(context, {'id': resource_id})
            h.flash_notice(_('Resource has been deleted.'))
            return h.redirect_to('package.dataset_resources', package_type=package_type, id=id)
            
        c.resource_dict = resource_dict = get_action('resource_show')(
            context, {'id': resource_id})
        c.pkg_id = pkg_id = id
    except NotAuthorized:
        abort(401, _('Unauthorized to delete resource %s') % '')
    except NotFound:
        abort(404, _('Resource not found'))
    return render('package/confirm_delete_resource.html',
                    {'dataset_type': _get_package_type(id),
                     'resource_dict': resource_dict,
                     'pkg_id': pkg_id})

def resource_download(id, resource_id, filename=None):
    """
    Provides a direct download by either redirecting the user to the url
    stored or downloading an uploaded file directly.
    """
    context = {'model': model, 'session': model.Session,
                'user': c.user or c.author, 'auth_user_obj': c.userobj}

    try:
        rsc = get_action('resource_show')(context, {'id': resource_id})
        get_action('package_show')(context, {'id': id})
    except NotFound:
        abort(404, _('Resource not found'))
    except NotAuthorized:
        abort(401, _('Unauthorized to read resource %s') % id)

    h.redirect_to(rsc['url'])

"""
ENDPOINTS
"""

def dge_has_edit_view(func):
    '''
    :param func: Endpoint view function
    
    Redirect to package view if package is not editable.
    Return endpoint view function otherwise
    '''
    def wrapper(*args, **kwargs):
        pkg_id = kwargs.get('id')
        context = {'model': model, 'session': model.Session,
                    'user': c.user or c.author, 'auth_user_obj': c.userobj}
        try:
            is_editable = helpers.dge_is_editable(get_action('package_show')(context, {'id': pkg_id}))
        except NotAuthorized:
            is_editable = False
        if not is_editable:
            return h.redirect_to('package.dataset_read', id=pkg_id)
        return func(*args, **kwargs)
    return wrapper

def redirect_search(**kwargs):
    base_url = f'{URL_PREFIX}{DEFAULT_DATASET_PAGE}'
    query_string = request.query_string.decode('utf-8')
    if query_string:
        final_url = f'{base_url}?{query_string}'
    else:
        final_url = base_url
    return redirect(h.lang() + final_url, code=301)


package.add_url_rule('', 'catalogo_redirect_search', view_func=redirect_search)

package.add_url_rule('/download_csv', 'redirect_download_csv', redirect_to=f'{DEFAULT_DATASET_PAGE}/download_csv/')

package.add_url_rule(f'{DEFAULT_DATASET_PAGE}/download_csv', 'download_csv', view_func=download_csv)

package.add_url_rule(f'{DEFAULT_DATASET_PAGE}', 'search', view_func=search)

package.add_url_rule('/new', 'add dataset', view_func=CreateView.as_view(str(u'new')))

package.add_url_rule('/search', view_func=search)

package.add_url_rule('/read/<id>/<revision>', view_func=read_ajax)
package.add_url_rule('/edit/<id>/<revision>', view_func=read_ajax)

'''
   Prepare and Display Resource Form
'''
def resource_new(id, package_type='dataset', resource_id=None, data=None, errors=None, error_summary=None):

    context = {'model': model, 'session': model.Session,'user': c.user or c.author,'auth_user_obj': c.userobj}
    errors = errors or {}
    error_summary = error_summary or {}
    save_action = request.form.get(u'save')

    if save_action: 
        data = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(request.form))))
        data.update(clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(request.files)))))
        del data[u'save']
        resource_id = data.pop(u'id')
        data[u'package_id'] = id
        pkg_dict = get_action(u'package_show')(context, {u'id': id})
        
        if 'resources' not in pkg_dict:pkg_dict['resources'] = []

        pkg_dict = get_action(u'package_show')(context, {u'id': id})
        
        try:
            if resource_id:
                data[u'id'] = resource_id
                get_action(u'resource_update')(context, data)
            else:
                get_action(u'resource_create')(context, data)
            # After Saving action performed, redirect accordingly
            if save_action == u'go-metadata':
                # XXX race condition if another user edits/deletes
                data_dict = get_action(u'package_show')(context, {u'id': id})
                get_action(u'package_update')(dict(context, allow_state_change=True),dict(data_dict, state=u'active'))
                return h.redirect_to(u'{}.read'.format(package_type), id=id)
            elif save_action == u'go-dataset':
                return h.redirect_to(u'{}.edit'.format(package_type), id=id)
            elif save_action == u'go-dataset-complete':
                return h.redirect_to(u'{}.read'.format(package_type), id=id)
            else:
                return h.redirect_to(u'{}_resource.new'.format(package_type),id=id)
           
        except ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            if len(errors) == 0:
                errors['error_data'] = " Error Saving Resource"
                error_summary['error_data'] = "Error Saving Resource"

            if data.get(u'url_type') == u'upload' and data.get(u'url'):
                data[u'url'] = u''
                data[u'url_type'] = u''
                data[u'previous_upload'] = True

        except NotAuthorized:
             raise Exception(u'Unauthorized to create a resource')
        except NotFound:
                raise Exception( _(u'The dataset {id} could not be found.').format(id=id))
    else: 
        if resource_id:
            data = get_action(u'resource_show')(context, { u'id': resource_id })

    try:
        pkg_dict = get_action(u'package_show')(context, {u'id': id})
    except NotFound:
        return base.abort(404, _(u'The dataset {id} could not be found.').format(id=id))
    try:
        check_access(u'resource_create', context, {u"package_id": pkg_dict["id"]})
    except NotAuthorized:
            return base.abort( 403, _(u'Unauthorized to create a resource for this package'))

    # Retrieve the others Resouces of the dataset package, for print in the new resource form page
    c.package = toolkit.get_action('package_show')(context, {u'id': id})
    resources = []
    for resource in c.package.get('resources', resources):
        resources.append(resource)

    extra_vars = {
            u'data': data,
            u'errors': errors,
            u'error_summary': error_summary,
            u'action': u'new',
            u'resource_form_snippet': _get_pkg_template(
                u'resource_form', package_type
            ),
            u'dataset_type': package_type,
            u'pkg_name': id,
            u'pkg_dict': pkg_dict,
            u'other_resources': resources
        }
    
    template = u'package/new_resource_not_draft.html'
    if pkg_dict[u'state'].startswith(u'draft'):
            extra_vars[u'stage'] = ['complete', u'active']
            template = u'package/new_resource.html'

    return base.render(template, extra_vars)


'''
   Prepare and Display edit Resource Form
'''
def resource_edit(package_type, id, resource_id, data=None, errors=None, error_summary=None):

    context = { u'model': model, u'session': model.Session,  u'api_version': 3, u'for_edit': True, u'user':c.user, u'auth_user_obj': c.userobj }
    errors = errors or {}
    error_summary = error_summary or {}
    save_action = request.form.get(u'save')

    if save_action: 
        data = clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(request.form))))
        data.update(clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(request.files)))))
        del data[u'save']
        resource_id = data.pop(u'id')
        data[u'package_id'] = id
        try:
            if resource_id:
                data[u'id'] = resource_id
                get_action(u'resource_update')(context, data)
            else:
                get_action(u'resource_create')(context, data)

            # After Saving action performed, redirect accordingly
            if save_action == u'go-metadata':
                # XXX race condition if another user edits/deletes
                data_dict = get_action(u'package_show')(context, {u'id': id})
                get_action(u'package_update')(dict(context, allow_state_change=True),dict(data_dict, state=u'active'))
                return h.redirect_to(u'{}.read'.format(package_type), id=id)
            else:
                return h.redirect_to(u'{}_resource.new'.format(package_type),id=id)
                
        except ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            if len(errors) == 0:
                errors['error_data'] = " Error Saving Resource"
                error_summary['error_data'] = "Error Saving Resource"
            if data.get(u'url_type') == u'upload' and data.get(u'url'):
                    data[u'url'] = u''
                    data[u'url_type'] = u''
                    data[u'previous_upload'] = True
        except NotAuthorized:
             raise Exception(u'Unauthorized to create a resource')
        except NotFound:
                raise Exception( _(u'The dataset {id} could not be found.').format(id=id))
    else: 
        if resource_id:
            data = get_action(u'resource_show')(context, { u'id': resource_id })
    try:
        check_access(u'package_update', context, {u'id': id})
    except NotAuthorized:
        return base.abort(403, _(u'User %r not authorized to edit %s') % (c.user, id))
    pkg_dict = get_action(u'package_show')(context, {u'id': id})

    try:
        resource_dict = get_action(u'resource_show')(context, { u'id': resource_id })
    except NotFound:
        return base.abort(404, _(u'Resource not found'))

    if pkg_dict[u'state'].startswith(u'draft'):
        return h.redirect_to(u'{}_resource.new'.format(package_type),id=id)

    resource = resource_dict
    if package_type == 'dataset':
            form_action = h.url_for(u'package.resource_edit',resource_id=resource_id, id=id)
    else: form_action = h.url_for(u'{}_resource.edit'.format(package_type),resource_id=resource_id, id=id)
    
    if not data:
        data = resource_dict
    package_type = pkg_dict[u'type'] or package_type

    # Retrieve the others Resouces of the dataset, for print in the edit resource form page
    c.package =  toolkit.get_action('package_show')(context, {u'id': id})
    resources = []
    for resource in c.package.get('resources', resources):
        resources.append(resource)

    errors = errors or {}
    error_summary = error_summary or {}
    extra_vars = {
            u'data': data,
            u'errors': errors,
            u'error_summary': error_summary,
            u'action': u'edit',
            u'resource_form_snippet': _get_pkg_template(
                u'resource_form', package_type
            ),
            u'dataset_type': package_type,
            u'resource': resource,
            u'pkg_dict': pkg_dict,
            u'form_action': form_action,
            u'other_resources': resources
        }
    return base.render(u'package/resource_edit.html', extra_vars)

def package_delete(package_type, id):
    context = {'model': model, 'session': model.Session ,'user': c.user ,'auth_user_obj': c.userobj}

    if request.method == 'POST':
        if u'cancel' in request.form:
            return h.redirect_to(u'package.dataset_edit'.format(package_type), id=id)
        try:
            get_action(u'package_delete')(context, {u'id': id})
        except NotFound:
            return base.abort(404, _(u'Dataset not found'))
        except NotAuthorized:
            return base.abort(
                403,
                _(u'Unauthorized to delete package %s') % u''
            )

        h.flash_notice(_(u'Dataset has been deleted.'))
        return h.redirect_to(package_type + u'.search')

    try:
        pkg_dict = get_action(u'package_show')(context, {u'id': id})
    except NotFound:
        return base.abort(404, _(u'Dataset not found'))
    except NotAuthorized:
        return base.abort( 403,  _(u'Unauthorized to delete package %s') % u'')

    dataset_type = pkg_dict[u'type'] or package_type
    pkg_name = pkg_dict[u'name']
    pkg_id = id

    return base.render( u'package/confirm_delete.html', { u'pkg_dict': pkg_dict, u'dataset_type': dataset_type, u'pkg_name': pkg_name, u'pkg_id': pkg_id})


package_add_resource_view = LazyView(u'ckan.views.resource.CreateView', str(u'new_resource'))
package_add_resource_view = dge_has_edit_view(package_add_resource_view)
package.add_url_rule('/new_resource/<id>', 'new_resource', view_func=resource_new, methods=['GET', 'POST'])
package.add_url_rule('/<id>/resource_edit_draft/<resource_id>', 'resource_edit_draft', view_func=resource_new, methods=['GET', 'POST'])

package.add_url_rule('/read_ajax/<id>', 'read_ajax', view_func=read_ajax)



package.add_url_rule('/delete/<id>', 'delete', view_func=dge_has_edit_view(package_delete), methods=['GET', 'POST'])

package_edit_view = EditView.as_view(str(u'edit'))
package_edit_view = dge_has_edit_view(package_edit_view)
package.add_url_rule('/edit/<id>', 'dataset_edit', view_func=package_edit_view, methods=['GET', 'POST'])

package_resource_admin_view = resources
package_resource_admin_view = dge_has_edit_view(package_resource_admin_view)
package.add_url_rule('/resources/<id>', 'dataset_resources', view_func=package_resource_admin_view)

package.add_url_rule('/<id>', 'dataset_read', view_func=readDataset)
package.add_url_rule('/<id>/resource/<resource_id>', view_func=resource_read)

package.add_url_rule('/<id>/resource_delete/<resource_id>', 'resource_delete', view_func=resource_delete, methods=['GET', 'POST'])

package_resource_edit_view = LazyView(u'ckan.views.resource.EditView', str(u'edit_resource') )
package_resource_edit_view = dge_has_edit_view(package_resource_edit_view)
package.add_url_rule('/<id>/resource_edit/<resource_id>', 'resource_edit', view_func=resource_edit, methods=['GET', 'POST'])

package.add_url_rule('/<id>/resource/<resource_id>/download', view_func=resource_download)
package.add_url_rule('/<id>/resource/<resource_id>/download/<filename>', view_func=resource_download)

package.add_url_rule(f'{DEFAULT_DATASET_PAGE}/<id>', 'redirect_to_catalog', redirect_to=f'{URL_PREFIX}/<id>')
