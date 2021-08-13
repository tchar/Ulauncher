from typing import Callable, BinaryIO
from types import SimpleNamespace
import os
from shutil import rmtree
import sys
import venv
import logging
from subprocess import Popen, PIPE, CalledProcessError
from ulauncher.utils.decorator.run_async import run_async

logger = logging.getLogger(__name__)


class ExtensionDependenciesDownloader(venv.EnvBuilder):
    def __init__(self, ext_path: str) -> None:
        super().__init__(
            system_site_packages=True,
            clear=False,
            upgrade=False,
            symlinks=True,
            with_pip=True,
        )
        self.executable = sys.executable
        self.ext_path = os.path.abspath(ext_path)

    @property
    def requirements_file(self) -> str:
        return os.path.join(self.ext_path, 'requirements.txt')

    @run_async
    def reader(self, stream: BinaryIO, log_cb: Callable[[str], None]) -> None:
        """
        Read lines from a subprocess' output stream and log it
        """
        while True:
            s = stream.readline()
            if not s:
                break
            log_cb(s.decode('utf-8').rstrip('\n'))
        stream.close()

    def post_setup(self, context: SimpleNamespace) -> None:
        """
        Installs requirements
        """
        args = [context.env_exe, '-m', 'pip', 'install', '-r', self.requirements_file]
        proc = Popen(args, stdout=PIPE, stderr=PIPE)
        t1 = self.reader(proc.stdout, logger.info)
        t2 = self.reader(proc.stderr, logger.warning)
        proc.wait()
        t1.join()
        t2.join()
        if proc.returncode:
            raise CalledProcessError(proc.returncode, args)
        self.executable = context.env_exe

    def download(self) -> None:
        """
        Downloads dependencies if required. After download is called and if any dependencies
        were installed, self.executable will point to the python executable inside the venv.
        """
        ext_basename = os.path.basename(self.ext_path)
        env_dir = os.path.join(self.ext_path, ext_basename + '_venv')
        if os.path.exists(env_dir) or not os.path.exists(self.requirements_file):
            return
        try:
            self.create(env_dir)
        # This catch is also used for self._setup_pip() in case ensurepip is missing
        except CalledProcessError as e:
            self.executable = sys.executable
            if os.path.isdir(env_dir):
                rmtree(env_dir)
            logger.error(e)
