import mock
import pytest

from ulauncher.api.shared.action.LaunchAppAction import LaunchAppAction


class TestLaunchAppAction:

    @pytest.fixture
    def filename(self):
        return mock.Mock()

    @pytest.fixture
    def action(self, filename):
        return LaunchAppAction(filename)

    @pytest.fixture(autouse=True)
    def AppLaunchContext(self, mocker):
        return mocker.patch('ulauncher.api.shared.action.LaunchAppAction.Gio.AppLaunchContext')

    @pytest.fixture(autouse=True)
    def read_desktop_file(self, mocker):
        return mocker.patch('ulauncher.api.shared.action.LaunchAppAction.read_desktop_file')

    @pytest.fixture(autouse=True)
    def is_wayland(self, mocker):
        return mocker.patch('ulauncher.api.shared.action.LaunchAppAction.is_wayland')

    @pytest.fixture(autouse=True)
    def is_wayland_compatibility_on(self, mocker):
        return mocker.patch('ulauncher.api.shared.action.LaunchAppAction.is_wayland_compatibility_on')

    @pytest.fixture(autouse=True)
    def gdk_backend(self, mocker):
        return mocker.patch('ulauncher.api.shared.action.LaunchAppAction.gdk_backend')

    def test_keep_app_open(self, action):
        assert not action.keep_app_open()

    def test_run(self, action, filename, read_desktop_file, AppLaunchContext):
        action.run()
        read_desktop_file.assert_called_with(filename)
        read_desktop_file.return_value.launch.assert_called_with(None, AppLaunchContext.return_value)

    def test_run__is_wayland__unset_env_var(self, action, AppLaunchContext, is_wayland, gdk_backend,
                                            is_wayland_compatibility_on):
        is_wayland.return_value = True
        gdk_backend.return_value.lower.return_value = 'x11'
        is_wayland_compatibility_on.return_value = False

        action.run()

        AppLaunchContext.return_value.unsetenv.assert_called_with('GDK_BACKEND')
