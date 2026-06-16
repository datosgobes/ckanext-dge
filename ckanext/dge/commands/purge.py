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
import logging
from configparser import ConfigParser

from purgers import DataSetPurger, DistributionsPurger, FederationsPurger
from report import Report
from sender import EmailSender

log = logging.getLogger('ckan.logic')

if __name__ == '__main__':
    production_config = ConfigParser()
    production_config.read('/etc/ckan/default/ckan.ini')

    email_sender = EmailSender(production_config)
    report = Report()

    # Purge data sets
    dataset_purger = DataSetPurger(production_config, report)
    dataset_purger.purge()

    # Purge distributions
    dist_purger = DistributionsPurger(production_config)
    dist_purger.purge()

    # Purge federations
    federations_purger = FederationsPurger(production_config)
    federations_purger.purge()

    if email_sender.smtp_enabled:
        default_report_text = '<p class="mb10">Se ha ejecutado el purgado, no existen elementos a purgar.</p>'
        full_report = report.get_report(default_report_text)
        email_sender.send(full_report)
    else:
        log.warning(f'INFO: SMTP is disabled, so the purge report will not be sent')
