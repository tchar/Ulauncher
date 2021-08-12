import sys
import os
from typing import Optional
import logging
from shutil import rmtree
from subprocess import Popen, PIPE

logger = logging.getLogger(__name__)


class ExtensionDependenciesDownloader:
    def __init__(self, ext_path: str) -> None:
        self.ext_path = ext_path
        self.venv_path: Optional[str] = None

    @property
    def executable(self):
        """Path of the python executable"""
        if self.venv_path is None:
            return sys.executable
        return os.path.join(self.venv_path, 'bin', 'python')

    @property
    def requirements_file(self) -> str:
        """Path of requirements file"""
        return os.path.join(self.ext_path, 'requirements.txt')

    def needs_venv(self) -> bool:
        """Returns True if requirements file is found, False otherwise"""
        requirements_file = self.requirements_file
        if not os.path.isfile(requirements_file):
            return False

        logger.debug('Requirements file found: %s', requirements_file)
        return True

    def create_venv(self) -> Optional[str]:
        """Creates venv and returns the venv path if venv is created, None otherwise"""
        if self.venv_path is not None:
            return self.venv_path

        venv_name = os.path.basename(self.ext_path) + '_venv'
        venv_path = os.path.join(self.ext_path, venv_name)
        if os.path.exists(venv_path):
            logger.warning('Venv path already exists: %s', venv_path)
            return None

        args = [sys.executable, '-m', 'venv', '--system-site-packages', venv_path]
        try:
            proc = Popen(args, stdout=PIPE, stderr=PIPE)
        except FileNotFoundError as e:
            logger.exception(e)
            return None

        out, err = proc.communicate()
        if out:
            logger.debug(out.decode('utf-8'))
        if err:
            logger.warning(err.decode('utf-8'))

        if proc.returncode != 0:
            logger.debug('%s returned %d', ' '.join(args), proc.returncode)
            return None
        logger.debug('Created venv %s', venv_path)
        self.venv_path = venv_path
        return venv_path

    def remove_venv(self) -> None:
        """Removes the venv created"""
        if self.venv_path is None:
            return
        rmtree(self.venv_path)
        self.venv_path = None

    def download(self) -> bool:
        """Downloads dependencies if needed and returns True if downloaded, False otherwise"""
        if not self.needs_venv() or not self.create_venv():
            return False

        args = [self.executable, '-m', 'pip', 'install', '-r', self.requirements_file]
        try:
            proc = Popen(args, stdout=PIPE, stderr=PIPE)
        except FileNotFoundError as e:
            logger.exception(e)
            self.remove_venv()
            return False

        out, err = proc.communicate()
        if out:
            logger.debug(out.decode('utf-8'))
        if err:
            logger.warning(err.decode('utf-8'))

        if proc.returncode != 0:
            self.remove_venv()
            return False

        return True
