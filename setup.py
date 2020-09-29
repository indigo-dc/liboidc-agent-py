import io
import os
import re

from setuptools import find_packages
from setuptools import setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(
            text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())


def get_property(prop, project):
    """Get certain property from project folder."""
    with open(os.path.join(project, '__init__.py')) as f:
        result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop),
                           f.read())
    return result.group(1)


PROJECT = "liboidcagent"

setup(
    name=PROJECT,
    version=get_property('__version__', PROJECT),
    url="https://github.com/indigo-dc/liboidc-agent-py",
    project_urls={
        'Source': 'https://github.com/indigo-dc/liboidc-agent-py',
        'Tracker': 'https://github.com/indigo-dc/liboidc-agent-py/issues',
        'Documentation':
        'https://indigo-dc.gitbooks.io/oidc-agent/api-py.html',
    },
    license='MIT',
    author=get_property('__author__', PROJECT),
    author_email=get_property('__author_email__', PROJECT),
    description=
    "A python library for requesting OpenID Connect access tokens from oidc-agent.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=('tests', )),
    install_requires=['PyNaCl>=1.2.0'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: Unix',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: Utilities',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'Environment :: Console',
        'Natural Language :: English',
    ],
)
