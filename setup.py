import subprocess
import os
import re
from distutils.core import setup, Command
from distutils.command.sdist import sdist as _sdist
from distutils.errors import DistutilsSetupError

VERSION_PY = """\
# This file is originally generated from Git information by running
#     $ python3 setup.py version
# Distribution tarballs contain a pre-generated copy of this file.

__version__ = '{:s}'
"""

VERSION_ERR_MSG = """\
Unexpected version number: {:s}.
Git tags should be set properly, e.g., v0.1.0
"""

VER_PATH = 'nextbiopy/_version.py'

def update_version_py():
    if not os.path.exists('.git'):
        print("This does not appear to be a Git repository.")
        return
    try:
        p = subprocess.Popen(
            ["git", "describe", "--tags", "--dirty", "--always"],
            stdout=subprocess.PIPE
        )
    except EnvironmentError:
        print("unable to run git, leaving _version.py alone".format(VER_PATH))
        return
    stdout = p.communicate()[0].decode('utf8').rstrip()
    if p.returncode != 0:
        print("unable to run git, leaving _version.py alone")
        return
    # we use tags like "v0.5", so strip the prefix "v"
    if not stdout.startswith('v'):
        raise DistutilsSetupError(VERSION_ERR_MSG.format(stdout))
    ver = stdout[len('v'):]
    # write version to _version.py
    with open(VER_PATH, 'w') as f:
        f.write(VERSION_PY.format(ver))
    print("set {:s} to '{:s}'".format(VER_PATH, ver))


def get_version():
    try:
        f = open(VER_PATH)
    except EnvironmentError:
        return None
    for line in f.readlines():
        mo = re.match("__version__ = '([^']+)'", line)
        if mo:
            ver = mo.group(1)
            return ver
    return None


class Version(Command):
    description = "update _version.py from git repo"
    user_options = []
    boolean_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        update_version_py()
        ver = get_version()
        print("Version is now", ver)
        if ver.endswith('-dirty'):
            print('You are in DEV mode, '
                  'not all code changes have been committed')


class sdist(_sdist):
    def run(self):
        # regenerate version number for every release
        update_version_py()
        self.distribution.metadata.version = get_version()
        return _sdist.run(self)


setup(
    name='nextbiopy',
    license='MIT',
    version=get_version(),
    description='Next bio python utility library',
    author=['Liang Bo Wang', 'Wen Wei Liao'],
    author_email=['b98901114@ntu.edu.tw', 'gattacaliao@gmail.com'],
    maintainer=['Liang Bo Wang', 'Wen Wei Liao'],
    maintainer_email=['b98901114@ntu.edu.tw', 'gattacaliao@gmail.com'],
    url='https://github.com/nextbiopy/nextbiopy',
    packages=['nextbiopy'],
    package_data={
        # if any packages contains *.txt or *.rst, include them
        '': ['*.txt', '*.rst'],
    },
    scripts=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Topic :: Utilities',
    ],
    cmdclass={"version": Version, "sdist": sdist},
)