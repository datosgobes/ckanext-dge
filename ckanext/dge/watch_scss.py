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

import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

class SCSSHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.scss'):
            log.info(f"Detected change in: {event.src_path}")
            self.compile_scss()

    def on_created(self, event):
        if event.src_path.endswith('.scss'):
            log.info(f"New SCSS file detected: {event.src_path}")
            self.compile_scss()

    def compile_scss(self):
        try:
            log.info("Running SCSS compilation...")
            scss_script_path = '/ckanext/ckanext-dge/ckanext/dge/scss.py'
            result = subprocess.run(['python', scss_script_path], capture_output=True, text=True)
            log.info(result.stdout)
            if result.stderr:
                log.error(result.stderr)
        except Exception as e:
            log.error(f"Error running SCSS compilation: {str(e)}")

if __name__ == "__main__":
    scss_dir = '/ckanext/ckanext-dge/ckanext/dge/assets/scss'
    
    log.info(f"Watching SCSS directory: {scss_dir}")
    
    event_handler = SCSSHandler()
    observer = Observer()
    observer.schedule(event_handler, path=scss_dir, recursive=True)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()