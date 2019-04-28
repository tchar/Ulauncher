import logging
from gi.repository import Gio

from ulauncher.util.desktop.reader import read_desktop_file
from ulauncher.util.string import force_unicode
from ulauncher.config import is_wayland, is_wayland_compatibility_on, gdk_backend
from .BaseAction import BaseAction
logger = logging.getLogger(__name__)


class LaunchAppAction(BaseAction):
    """
    Launches app by given `.desktop` file path

    :param str filename: path to .desktop file
    """

    def __init__(self, filename):
        self.filename = filename

    def keep_app_open(self):
        return False

    def run(self):
        app = read_desktop_file(self.filename)
        logger.info('Run application %s (%s)' % (force_unicode(app.get_name()), self.filename))
        context = Gio.AppLaunchContext()

        # Unset GDK_BACKEND if we forced a user to set it
        if is_wayland() and gdk_backend().lower() == 'x11' and not is_wayland_compatibility_on():
            context.unsetenv('GDK_BACKEND')

        app.launch(None, context)
