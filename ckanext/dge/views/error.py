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
from flask import Blueprint

import ckan.lib.base as base
from ckanext.dge_dataservice.utils import DATASERVICE_TYPE_NAME

render = base.render

error = Blueprint(
    'error',
    __name__,
)

extra_vars = {u'code': [401], u'content': u'You are not authorized to access this page.', u'name': u'Access denied'}

def error1(id, revision):
    return render('error_document_template.html', extra_vars=extra_vars)

def error2(id, offset):
    return render('error_document_template.html', extra_vars=extra_vars)

def error3(id, resource_id):
    return render('error_document_template.html', extra_vars=extra_vars)

def error4(id, resource_id, view_id):
    return render('error_document_template.html', extra_vars=extra_vars)

def error5():
    """Render the error document"""
    return render('error_document_template.html', extra_vars=extra_vars)

def error6(offset):
    return render('error_document_template.html', extra_vars=extra_vars)

def error7(action):
    return render('error_document_template.html', extra_vars=extra_vars)

def error8(lang):
    return render('error_document_template.html', extra_vars=extra_vars)

def error9(id):
    return render('error_document_template.html', extra_vars=extra_vars)

def error10(label):
    return render('error_document_template.html', extra_vars=extra_vars)

error.add_url_rule('/catalogo/history/<id>/<revision>', view_func=error1)


error.add_url_rule('/catalogo/history/<id>', view_func=error9)
error.add_url_rule('/catalogo/history_ajax/<id>', view_func=error9)
error.add_url_rule('/catalogo/follow/<id>', view_func=error9)
error.add_url_rule('/catalogo/activity/<id>', view_func=error9)
error.add_url_rule('/catalogo/groups/<id>', view_func=error9)
error.add_url_rule('/catalogo/unfollow/<id>', view_func=error9)
error.add_url_rule('/catalogo/download_csv/<id>', view_func=error9)


error.add_url_rule('/catalogo/followers/<id>', 'dataset_followers', view_func=error9)


error.add_url_rule('/catalogo/activity/<id>', 'dataset_activity', view_func=error9)


error.add_url_rule('/catalogo/activity/<id>/<offset>', view_func=error2)

error.add_url_rule('/catalogo/groups/<id>', 'dataset_groups', view_func=error9)


error.add_url_rule('/catalogo/<id>/resource/<resource_id>/embed', view_func=error3)

error.add_url_rule('/catalogo/<id>/resource/<resource_id>/viewer', view_func=error3)
error.add_url_rule('/catalogo/<id>/resource/<resource_id>/preview', view_func=error3)
error.add_url_rule('/catalogo/<id>/resource/<resource_id>/views', 'views',  view_func=error3)
error.add_url_rule('/catalogo/<id>/resource/<resource_id>/new_view', 'new_view', view_func=error3)
error.add_url_rule('/catalogo/<id>/resource/<resource_id>/edit_view/<view_id>', 'edit_view', view_func=error4)


error.add_url_rule('/catalogo/<id>/resource/<resource_id>/view/<view_id>', 'resource_view', view_func=error4)
error.add_url_rule('/catalogo/<id>/resource/<resource_id>/view', view_func=error3)


error.add_url_rule('/group', 'group_index', view_func=error5)


error.add_url_rule('/group/list', 'group_list', view_func=error5)
error.add_url_rule('/group/new', 'group_new', view_func=error5)
error.add_url_rule('/group/edit/<id>', 'group_action',view_func=error9)
error.add_url_rule('/group/delete/<id>', 'group_action',view_func=error9)
error.add_url_rule('/group/member_new/<id>', 'group_action', view_func=error9)
error.add_url_rule('/group/member_delete/<id>', 'group_action', view_func=error9)
error.add_url_rule('/group/history/<id>', 'group_action', view_func=error9)
error.add_url_rule('/group/followers/<id>', 'group_action', view_func=error9)
error.add_url_rule('/group/follow/<id>', 'group_action', view_func=error9)
error.add_url_rule('/group/unfollow/<id>', 'group_action', view_func=error9)
error.add_url_rule('/group/admins/<id>', 'group_action', view_func=error9)
error.add_url_rule('/group/activity/<id>', 'group_action', view_func=error9)


error.add_url_rule('/group/about/<id>', 'group_about', view_func=error9)
error.add_url_rule('/group/edit/<id>', 'group_edit', view_func=error9)
error.add_url_rule('/group/members/<id>', 'group_members', view_func=error9)
error.add_url_rule('/group/activity/<id>', 'group_activity', view_func=error9)
error.add_url_rule('/group/read/<id>', 'group_read', view_func=error9)


error.add_url_rule('/organization/list', view_func=error5)
error.add_url_rule('/organization/new', view_func=error5)
error.add_url_rule('/organization/activity/<id>/<offset>', 'organization_activity', view_func=error2)
error.add_url_rule('/organization/about/<id>', 'organization_about', view_func=error9)
error.add_url_rule('/organization/edit/<id>', 'organization_edit', view_func=error9)
error.add_url_rule('/organization/members/<id>', 'organization_members', view_func=error9)
error.add_url_rule('/organization/bulk_process/<id>', 'organization_bulk_process', view_func=error9)

error.add_url_rule('/organization/delete/<id>', view_func=error9)
error.add_url_rule('/organization/admins/<id>', view_func=error9)
error.add_url_rule('/organization/member_new/<id>', view_func=error9)
error.add_url_rule('/organization/member_delete/<id>', view_func=error9)
error.add_url_rule('/organization/history/<id>', view_func=error9)


error.add_url_rule('/about', 'about', view_func=error5)


error.add_url_rule('/tag', view_func=error5)
error.add_url_rule('/tag/<id>', view_func=error9)


error.add_url_rule('/user/register', 'register', view_func=error5)
error.add_url_rule('/user/login', 'login', view_func=error5)
error.add_url_rule('/user/_logout', view_func=error5)
error.add_url_rule('/user/logged_in', view_func=error5)
error.add_url_rule('/user/logged_out', view_func=error5)
error.add_url_rule('/user/logged_out_redirect', view_func=error5)

error.add_url_rule('/user/register', 'register', view_func=error5)
error.add_url_rule('/user/login', 'login', view_func=error5)
error.add_url_rule('/user/_logout', view_func=error5)
error.add_url_rule('/user/logged_in', view_func=error5)
error.add_url_rule('/user/logged_out', view_func=error5)
error.add_url_rule('/user/logged_out_redirect', view_func=error5)

error.add_url_rule('/user/edit', view_func=error5)


error.add_url_rule('/user/generate_key/<id>', 'user_generate_apikey', view_func=error9)
error.add_url_rule('/user/generate_key/<id>/<offset>', view_func=error2)
error.add_url_rule('/user/activity/<id>', 'user_activity_stream', view_func=error9)

error.add_url_rule('/user/edit', view_func=error5)

error.add_url_rule( '/dashboard', 'user_dashboard', view_func=error5)
error.add_url_rule( '/dashboard/datasets', 'user_dashboard_datasets',
            view_func=error5)
error.add_url_rule( '/dashboard/groups', 'user_dashboard_groups',
            view_func=error5)
error.add_url_rule( '/dashboard/organizations', 'user_dashboard_organizations',
            view_func=error5)

error.add_url_rule('/dashboard/<offset>', view_func=error6)
error.add_url_rule('/user/follow/<id>', 'user_follow', view_func=error9)
error.add_url_rule('/user/unfollow/<id>', view_func=error9)

error.add_url_rule('/user/followers/<id>', 'user_followers', 
            view_func=error9)


error.add_url_rule('/user/delete/<id>', 'user_delete', view_func=error9)
error.add_url_rule('/user/reset/<id>', view_func=error9)
error.add_url_rule('/user/reset', view_func=error5)
error.add_url_rule('/user/me', view_func=error5)
error.add_url_rule('/user/set_lang/<lang>', view_func=error8)

error.add_url_rule('/user/<id>', 'user_datasets', view_func=error9)

error.add_url_rule('/user', 'user_index', view_func=error5)

error.add_url_rule('/revision', view_func=error5)
error.add_url_rule('/revision/edit/<id>', view_func=error9)
error.add_url_rule('/revision/diff/<id>', view_func=error9)
error.add_url_rule('/revision/list', view_func=error5)
error.add_url_rule('/revision/<id>', view_func=error9)

error.add_url_rule('/feeds/group/<id>.atom', view_func=error9)
error.add_url_rule('/feeds/organization/<id>.atom', view_func=error9)
error.add_url_rule('/feeds/tag/<id>.atom', view_func=error9)
error.add_url_rule('/feeds/custom.atom', view_func=error5)

error.add_url_rule( '/ckan-admin', 'ckanadmin_index', view_func=error5)
error.add_url_rule( '/ckan-admin/config', 'ckanadmin_config', view_func=error5)
error.add_url_rule( '/ckan-admin/trash', 'ckanadmin_trash', view_func=error5)
error.add_url_rule( '/ckan-admin/<action>', 'ckanadmin', view_func=error7)


error.add_url_rule( '/storage/f/<label>', 'storage_file', view_func=error10)
error.add_url_rule( '/i18n/strings_<lang>.js', view_func=error8)
error.add_url_rule( '/util/redirect', view_func=error5)