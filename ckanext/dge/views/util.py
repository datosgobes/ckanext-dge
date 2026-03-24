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
from flask import Blueprint, send_file
import re
import datetime
import logging
import csv
import ckan.lib.base as base
import ckan.lib.i18n as i18n
import ckan.logic as logic
import ckan.model as model
from ckan.views.util import internal_redirect
from ckan.plugins.toolkit import config
from ckan.common import _, request, c, g
from ckan.lib.search import SearchError
import ckan.plugins as p
import ckan.plugins.toolkit as tk
import ckan.lib.helpers as h
from collections import OrderedDict
from urllib.parse import urlencode
from urllib.request import urlopen

log = logging.getLogger(__name__)

util_bl = Blueprint(
    'util_bl',
    __name__,
)

backend = config.get('ckanext.dge.backend.filepath')
render = base.render
abort = base.abort
check_access = logic.check_access
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = tk.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key

VERIFY_RECAPTCHA_URL = 'https://www.google.com/recaptcha/api/siteverify'
RECAPTCHA_RESPONSE_PARAM = 'g-recaptcha-response'

def i18_js_strings(lang):
    ''' This is used to produce the translations for javascript. '''
    i18n.set_lang(lang)
    html = base.render('js_strings.html', cache_force=True)
    html = re.sub('<[^\>]*>', '', html)
    header = "text/javascript; charset=utf-8"
    base.response.headers['Content-type'] = header
    return html

util_bl.add_url_rule('/util/redirect', view_func=internal_redirect, methods=(u'GET', u'POST',))
util_bl.add_url_rule('/i18n/strings_<lang>.js', view_func=i18_js_strings)

@staticmethod
def _verify_recaptcha(g_response):
    import json
    if g_response:
        r = urlopen(VERIFY_RECAPTCHA_URL, urlencode({
            'secret': config.get('ckan.recaptcha.privatekey', ''),
            'response': g_response
        }, True)).read()
        if json.loads(r).get('success'):
            return

    raise NotAuthorized()

def dge_download_csv(package_type):
    global backend
    context = {'model': model, 'user': c.user or c.author,
                'auth_user_obj': c.userobj}
    try:
        check_access('site_read', context)
    except NotAuthorized:
        abort(401, 'La descarga del CSV no fue autorizada')

    q = request.params.get('q', '')
    # page will be always 1 because csv file needs to contain the whole search
    page = 1
    limit = int(config.get('download_csv_limit', '50'))
    ui_limit = g.datasets_per_page
    sort_by = request.params.get('sort', None)
    search_result = None
    try:
        search_extras = {}
        fq = ''
        for (param, value) in list(request.params.items()):
            if param not in ['q', 'page', 'sort', RECAPTCHA_RESPONSE_PARAM] \
                    and len(value) and not param.startswith('_'):
                if not param.startswith('ext_'):
                    if '[' in value and ']' in value:
                        value = value.replace('[', '').replace(']', '')
                        value = value.split(',')
                        for item in value:
                            fq += ' %s:"%s"' % (param, item)
                    else:
                        fq += ' %s:"%s"' % (param, value)
                else:
                    search_extras[param] = value
        if package_type == 'dataset':
            fq += ' +dataset_type:dataset'
        elif package_type == 'dataservice':
            fq += ' +dataset_type:dataservice'
        else:
            fq += ' +dataset_type:harvest'

        context = {'model': model, 'session': model.Session, 'for_view': True,
                    'user': c.user or c.author, 'auth_user_obj': c.userobj}

        facets = OrderedDict()
        default_facet_titles = {
            'organization': _('Organizations'),
            'groups': _('Groups'),
            'tags': _('Tags'),
            'res_format': _('Formats'),
            'license_id': _('Licenses'),
        }

        for facet in g.facets:
            if facet in default_facet_titles:
                facets[facet] = default_facet_titles[facet]
            else:
                facets[facet] = facet

        for plugin in p.PluginImplementations(p.IFacets):
            facets = plugin.dataset_facets(facets, package_type)

        data_dict = {
            'q': q,
            'fq': fq.strip(),
            'facet.field': list(facets.keys()),
            'rows': limit,
            'start': (page - 1) * ui_limit,
            'sort': sort_by,
            'extras': search_extras,
            'include_private': True
        }

        search_result = get_action('package_search')(context, data_dict)
        if search_result['count'] == 0:
            raise SearchError('Package search returns zero results')
    except SearchError:
        abort(400, "Solicitud de descarga incorrecta")

    filename = '{}-{}_{}.csv'.format("Resultado_Descarga",
                                        '_'.join(re.findall(r'\w+',
                                                            ''.join(re.findall(r'[\w\s]', q)))[:4]),
                                        datetime.datetime.now().strftime("%d-%m-%Y"))
    path = backend + filename
    file = open(path, 'w')
    writer = csv.writer(file)
    _write_download_csv_header(writer, package_type)
    for package in search_result['results']:
        if package_type == 'dataset':
            _write_download_csv_row(writer, package)
        elif package_type == 'dataservice':
            _write_download_csv_row_dataservice(writer, package)
        else:
            _write_download_csv_row_harvest(writer, package)
    file.close()
    return send_file(path, as_attachment=True, attachment_filename=filename)

def _get_page_number(params, key='page', default=1):
    """
    Returns the page number from the provided params after
    verifies that it is an integer.

    If it fails it will abort the request with a 400 error
    """
    p = params.get(key, default)

    try:
        p = int(p)
        if p < 1:
            raise ValueError("Negative number not allowed")
    except ValueError as e:
        abort(400, ('"page" parameter must be a positive integer'))

    return p


def _write_download_csv_header(writer, package_type):
    if package_type == 'dataset':
        writer.writerow([
            'URL', 'Título', 'Descripción',
            'Temáticas', 'Etiquetas', 'Fecha de creación',
            'Fecha de última modificación', 'Frecuencia de actualización',
            'Idiomas', 'Órgano Publicador',
            'Condiciones de uso', 'Cobertura geográfica',
            'Cobertura temporal', 'Vigencia del recurso',
            'Recursos relacionados', 'Normativa',
            'Distribuciones'
        ])
    elif package_type == 'dataservice':
        writer.writerow([
            'URL', 'Título', 'Descripción',
            'Temáticas', 'Etiquetas',
            'Órgano Publicador', 'Condiciones de uso',
            'URL del punto de acceso', 'Descripción del punto de acceso',
            'Derechos de acceso', 'Punto de contacto',
            'Legislación HVD aplicable', 'Categoría de HVD',
            'Documentación'
        ])
    else:
        writer.writerow([
            'Nombre', 'Frecuencia',
            'Tipo de Federación', 'Descripción',
            'Organización'
        ])

def _write_download_csv_row(writer, package):
    name = package.get('name') or ''
    title_translated = package.get('title_translated') or {}
    description = package.get('description') or {}
    theme = package.get('theme') or []
    tags = package.get('tags') or []
    metadata_created = package.get('metadata_created') or ''
    metadata_modified = package.get('metadata_modified') or ''
    frequency = package.get('frequency') or {'value': '', 'type': ''}
    language = package.get('language') or ''
    organization = package.get('organization') or {'title': '', 'name': ''}
    license_title = package.get('license_title') or ''
    reference = package.get('reference') or []
    conforms_to = package.get('conforms_to') or []
    resources = package.get('resources') or []
    distributions = [(
        res.get('url') or '',
        res.get('format') or '',
        ' '.join(re.findall(r'[^\n\r]+', res.get('description') or '')),
        ', '.join(['[{}]{}'.format(k, str(v)) for k, v in list((res.get('name_translated') or {}).items()) if v])
    ) for res in resources]

    row = [
        str(
            h.url_for('package.dataset_read', id=name, qualified=True)
        ),
        ' '
            .join(['[{}]{}'.format(k, ' '.join(re.findall(r'[^\n\r]+', str(v))))
                    for k, v in list(title_translated.items()) if v])
            ,
        ' '
            .join(['[{}]{}'.format(k, ' '.join(re.findall(r'[^\n\r]+', str(v))))
                    for k, v in list(description.items()) if v])
            ,
        ' '.join([str(url) for url in theme]),
        ' '.join([str(tag.get('display_name', '')) for tag in tags]),
        str(metadata_created),
        str(metadata_modified),
        '{} {}'
            .format(frequency['value'],
                    frequency['type'])
            ,
        ', '.join(language),
        '{} {}'
            .format(str(organization['title']), str(organization['name']))
            ,
        str(license_title),
        '',
        '',
        '',
        ' '.join([str(url) for url in reference]),
        ' '.join([str(url) for url in conforms_to]),
        ' '
            .join(['{} {} {} {}'.format(str(u), f, str(d), n) for u, f, d, n in distributions])

    ]

    writer.writerow(row)
    
def _write_download_csv_row_dataservice(writer, package):
    name = package.get('name') or ''
    title_translated = package.get('title_translated') or {}
    description = package.get('description') or {}
    theme = package.get('theme') or []
    tags = package.get('tags') or []
    organization = package.get('organization') or {'title': '', 'name': ''}
    license_title = package.get('license_title') or ''
    endpoint_url = package.get('endpoint_url') or []
    endpoint_description = package.get('endpoint_description') or []
    access_rights = package.get('access_rights') or ''
    contact_point_list = package.get('contact_point') or []
    hvd_applicable_legislation = package.get('hvd_applicable_legislation') or []
    hvd_category = package.get('hvd_category') or []
    page = package.get('page') or []
    contact_points = [(
        ', '.join(['[{}]{}'.format(k, str(v)) for k, v in list((contact_point.get('fn_translated') or {}).items()) if v]),
        ', '.join([str(email) for email in (contact_point.get('has_email') or [])]),
        ', '.join([str(email) for email in (contact_point.get('has_telephone') or [])]),
        contact_point.get('has_uid') or '',
        ', '.join([str(email) for email in (contact_point.get('has_url') or [])]),
        ', '.join(['[{}]{}'.format(k, str(v)) for k, v in list((contact_point.get('organization-name_translated') or {}).items()) if v])
    ) for contact_point in contact_point_list]

    row = [
        str(
            h.url_for('package.dataset_read', id=name, qualified=True)
        ),
        ' '
            .join(['[{}]{}'.format(k, ' '.join(re.findall(r'[^\n\r]+', str(v))))
                    for k, v in list(title_translated.items()) if v])
            ,
        ' '
            .join(['[{}]{}'.format(k, ' '.join(re.findall(r'[^\n\r]+', str(v))))
                    for k, v in list(description.items()) if v])
            ,
        ' '.join([str(url) for url in theme]),
        ' '.join([str(tag.get('display_name', '')) for tag in tags]),
        '{} {}'
            .format(str(organization['title']), str(organization['name']))
            ,
        str(license_title),
        ' '.join([str(url) for url in endpoint_url]),
        ' '.join([str(url) for url in endpoint_description]),
        str(access_rights),
        ' // '.join(['Denominación de área o persona: {} || Email: {} || Teléfono: {} || Identificador: {} || URL: {} || Nombre del organismo: {}'.format(f, e, t, str(i), u, o) for f, e, t, i, u, o  in contact_points]),
        ' '.join([str(url) for url in hvd_applicable_legislation]),
        ' '.join([str(url) for url in hvd_category]),
        ' '.join([str(url) for url in page]),

    ]

    writer.writerow(row)

def _write_download_csv_row_harvest(writer, package):
    title = package.get('title') or ''
    frequency = package.get('frequency') or ''
    source_type = package.get('source_type') or ''
    description = package.get('notes') or ''
    organization = package.get('organization') or {'title': ''}

    row = [
        str(title),
        str(frequency),
        str(_(source_type)),
        str(description),
        '{}'.format(str(organization['title']))
    ]

    writer.writerow(row)