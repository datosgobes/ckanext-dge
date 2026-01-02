# Copyright (C) 2025 Entidad Pública Empresarial Red.es
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

# coding=utf-8
import os

NL = os.linesep
NL2 = NL * 2


class DataSetPurgeReport:
    template = ('<p class="ml10">Datasets en estado deleted: {}</p>' +
                '<p class="ml10">Datasets purgados: {}</p>' +
                '<p class="ml10 mb10">Datasets no purgados: {}</p>' +
                '{}' +
                '<p class="ml10 mb10">****************</p>' +
                '<p>Listado de errores:</p>' + 
                '{}' +
                '<p>&nbsp;</p>' +
                '<p class="mb10">Un saludo.</p>')

    def __init__(self, datasets_count):
        self.datasets_count = datasets_count
        self.purged_datasets = []
        self.not_purged_datasets = []

    def purge_correct(self, dataset):
        self.purged_datasets += [dataset]

    def purge_failed(self, dataset, error):
        dataset_id, dataset_name = dataset
        self.not_purged_datasets += [(dataset_id, dataset_name, error)]

    def get_report(self):
        not_purged, error_list = '', ''
        for dataset_id, dataset_name, error in self.not_purged_datasets:
            not_purged += ('Id: {}, Nombre: {}' + NL).format(dataset_id, dataset_name)
            error_list += '<p>' + error + '</p>'
        purged = ''.join(
            '<p class="ml10">Id: {}</p>'.format(dataset_id)
            for dataset_id, dataset_name in self.purged_datasets)

        return self.template.format(self.datasets_count,
                                    len(self.purged_datasets),
                                    len(self.not_purged_datasets),
                                    purged, error_list)


class DistributionsPurgeReport:
    def __init__(self):
        pass

    def get_report(self):
        pass


class FederationsPurgeReport:
    def __init__(self):
        pass

    def get_report(self):
        pass


class Report:

    def __init__(self):
        self.dataset_report = None
        self.distributions_report = None
        self.federations_report = None

    def get_report(self, default_report):
        self.datos_ = ('<p class="mb10">Estimado/a.</p>' +
                        '<p>Ha finalizado el proceso de purgado de datasets:</p>')
        full_report = self.datos_
        reports = (('DataSets', self.dataset_report), ('Distribuciones', self.distributions_report),
                   ('Federaciones', self.federations_report))
        give_report = False
        for name, report in reports:
            if report is not None:
                give_report = True
                full_report += ('{}').format(report.get_report())

        if give_report:
            return full_report
        return default_report
