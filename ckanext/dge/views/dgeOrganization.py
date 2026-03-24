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
from ckan.common import c, _
import ckan.model as model
import ckan.lib.base as base

from flask import Blueprint

from ckantoolkit import config
import ckan.views.group as Group
import ckan.plugins.toolkit as toolkit

dgeOrganization = Blueprint(
    'dgeOrganization',
    __name__,
)

def index():
    context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'with_private': False}
    try:
        Group._check_access('sysadmin', context)
    except toolkit.NotAuthorized:
        base.abort(401, _('Not authorized to see this page'))

    return Group.index('organization', True)

dgeOrganization.add_url_rule('/organization', 'organizations_index', view_func=index)
