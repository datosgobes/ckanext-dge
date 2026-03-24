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
import pytz

from ckan.views.feed import _package_search, _create_atom_id, CKANFeed
from ckan.common import g
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as h

from flask import Blueprint, make_response
import ckan.views.feed as Feed
from ckantoolkit import config
import ckan.plugins as plugins

dgeFeed = Blueprint(
    'dgeFeed',
    __name__,
)

BASE_URL = config.get(u'ckan.site_url')

def _dge_date_str_to_datetime(date_str):
        try: 
            datetime_ = h.date_str_to_datetime(date_str)
        except TypeError:
            return None
        except ValueError:
            return None

        from_timezone = pytz.timezone('Europe/Madrid')
        to_timezone = pytz.timezone('UTC')
        datetime_ = from_timezone.localize(datetime_)

        return datetime_
    
def _alternate_url(params, **kwargs):
    search_params = params.copy()
    search_params.update(kwargs)

    search_params.pop('page', None)
    return Feed._feed_url(search_params,
                            controller='dgePackage',
                            action='harvest_search')

def general():
    data_dict, params = Feed._parse_url_params()
    data_dict['q'] = '*:*'

    item_count, results = _package_search(data_dict)

    navigation_urls = Feed._navigation_urls(params,
                                            item_count=item_count,
                                            limit=data_dict['rows'],
                                            controller='dgeFeed',
                                            action='general')

    feed_url = Feed._feed_url(params,
                                controller='dgeFeed',
                                action='general')

    alternate_url = _alternate_url(params)
    return output_feed(results,
                            feed_title=g.site_title,
                            feed_description= 'Conjuntos de datos recientemente creados o actualizados en %s' % g.site_title,
                            feed_link=alternate_url,
                            feed_guid=_create_atom_id
                            ('/feeds/dataset.atom'),
                            feed_url=feed_url,
                            navigation_urls=navigation_urls)

def output_feed(results, feed_title, feed_description,
                feed_link, feed_url, navigation_urls, feed_guid):
    author_name = config.get('ckan.feeds.author_name', '').strip() or \
        config.get('ckan.site_id', '').strip()
    
    feed_class = CKANFeed
    for plugin in plugins.PluginImplementations(plugins.IFeed):
        if hasattr(plugin, u'get_feed_class'):
            feed_class = plugin.get_feed_class()

    feed = feed_class(
        feed_title=feed_title,
        feed_link=feed_link,
        feed_description=feed_description,
        language='es',
        author_name=author_name,
        feed_guid=feed_guid,
        feed_url=feed_url,
        previous_page=navigation_urls['previous'],
        next_page=navigation_urls['next'],
        first_page=navigation_urls['first'],
        last_page=navigation_urls['last'],
    )
    
    for pkg in results:
        description= pkg.get('description', '').get('es', '')
        feed.add_item(
            title=pkg.get('title', ''),
            link=BASE_URL + h.url_for('package.dataset_read',
                                            id=pkg['name']),
            description=description,
            updated=_dge_date_str_to_datetime(pkg.get('metadata_modified')),
            published=_dge_date_str_to_datetime(pkg.get('metadata_created')),
            unique_id=_create_atom_id('/catalogo/%s' % pkg['name']),
            author_name=pkg.get('author_name', ''),
            author_email=pkg.get('author_email', ''),
            categories=[t['name'] for t in pkg.get('tags', [])],
            enclosure=None,
            )

    resp = make_response(feed.writeString(u'utf-8'), 200)
    resp.headers['Content-Type'] = u'application/atom+xml'
    return resp

dgeFeed.add_url_rule('/feeds/dataset.atom', view_func=general)
