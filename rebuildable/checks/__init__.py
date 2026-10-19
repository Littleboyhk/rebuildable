"""The eight checks in stable display order."""

from .dockerfile import run as dockerfile
from .git_repo import run as git_repo
from .lockfile import run as lockfile
from .paths import run as paths
from .readme import run as readme
from .runtime import run as runtime
from .settings import run as settings
from .test_command import run as test_command

CHECKS = (git_repo, lockfile, runtime, dockerfile, test_command, readme, settings, paths)
