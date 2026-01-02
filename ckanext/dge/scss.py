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

import os
import sass
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def compile_scss():
    log.info('COMPILING SCSS')
    scss_dir = os.path.join(os.path.dirname(__file__), 'assets', 'scss')
    css_dir = os.path.join(os.path.dirname(__file__), 'assets', 'css')

    log.info(f"SCSS directory: {scss_dir}")
    if os.path.exists(scss_dir):
        log.info(f"Contents: {os.listdir(scss_dir)}")
    else:
        log.error(f"SCSS directory does not exist: {scss_dir}")
        return

    if not os.path.exists(css_dir):
        os.makedirs(css_dir)
        log.info(f"Created CSS directory: {css_dir}")
    else:
        log.info(f"CSS directory exists: {css_dir}")

    for root, dirs, files in os.walk(scss_dir):
        relative_path = os.path.relpath(root, scss_dir)

        output_dir = os.path.join(css_dir, relative_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for file in files:
            if file.endswith('.scss'):
                scss_file = os.path.join(root, file)
                css_file_name = file.replace('.scss', '.css')

                css_file = os.path.join(output_dir, css_file_name)

                try:
                    compiled_css = sass.compile(filename=scss_file)
                    log.info(f"Compiled CSS content for {scss_file}: {compiled_css[:100]}...")

                    with open(css_file, 'w') as f:
                        f.write(compiled_css)

                    log.info(f"Compiled SCSS: {scss_file} -> {css_file}")
                except Exception as e:
                    log.error(f"Error compiling {scss_file}: {str(e)}")
                except IOError as io_error:
                    log.error(f"File write error for {css_file}: {str(io_error)}")

if __name__ == '__main__':
    compile_scss()