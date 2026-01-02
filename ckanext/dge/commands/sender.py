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
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader


class EmailSender:
    def __init__(self, config):
        if config.has_option('app:main', 'smtp.server'):
            smtp_config = config.get('app:main', 'smtp.server')
            self.host, self.port = smtp_config.split(':', 1) if ':' in smtp_config else (smtp_config, 25)
            self.port = int(self.port)
            self.starttls = eval(config.get('app:main', 'smtp.starttls'))
            self.username, self.password = None, None
            self.path = config.get('app:main', 'ckanext.dge.template.path_emails')
            self.url = config.get('app:main', 'ckanext.comments.url.images.drupal')
            self.url_logos = config.get('app:main', 'ckanext.comments.url.image.logos')
            self.url_image_subscribe = config.get('app:main', 'ckanext.comments.url.image.subscribe')
            self.url_subscribe = config.get('app:main', 'ckanext.comments.url.subscribe')
            if config.has_option('app:main', 'smtp.user') and config.has_option('app:main', 'smtp.password'):
                self.username = config.get('app:main', 'smtp.user')
                self.password = config.get('app:main', 'smtp.password')
            if config.has_option('app:main', 'smtp.mail_from') and config.has_option('app:main', 'smtp.purge_to'):
                self.from_addr = config.get('app:main', 'smtp.mail_from')
                self.to = config.get('app:main', 'smtp.purge_to')

    def __fill_common_headers(self, msg):
        if hasattr(self, 'from_addr') and hasattr(self, 'to'):
            msg['From'] = self.from_addr
            msg['To'] = self.to

    def __connect(self):
        if hasattr(self, 'host') and hasattr(self, 'port'):
            smtp_server = smtplib.SMTP(self.host, self.port)
            if self.starttls:
                smtp_server.starttls()
            if self.username and self.password:
                smtp_server.login(self.username, self.password)
            return smtp_server

    def send(self, text):
        path = self.path
        url = self.url
        url_logos = self.url_logos
        url_image_subscribe = self.url_image_subscribe
        url_subscribe = self.url_subscribe        
        
        env = Environment(loader=FileSystemLoader(path))
        template_purge = env.get_template('purge_email.html')
        body = template_purge.render(url=url, url_logos=url_logos, url_image_subscribe=url_image_subscribe, url_subscribe=url_subscribe, email=self.from_addr, mensaje=text )
        msg = MIMEText(body, 'html')
        self.__fill_common_headers(msg)
        msg['Subject'] = 'Reporte de purgado ({:%d/%b/%Y})'.format(datetime.now())

        smtp_server = self.__connect()
        if smtp_server:
            to = self.to
            if ',' in to:
                to = to.split(',')
            smtp_server.sendmail(self.from_addr, to, msg.as_string())
            smtp_server.quit()
