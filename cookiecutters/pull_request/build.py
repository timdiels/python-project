from pybuilder.core import use_plugin, init, Author, task, before, depends, after
from pybuilder.errors import BuildFailedException

@task
def tmp_stuff(project):
    for name, value in project.properties.items():
        if 'src' in str(value):
            print(name, value)
            
default_task = ['clean', 'package']

name = 'pybuilder-pip-tools'
version = '1.0.7'
summary = 'PyBuilder plugin to generate and install requirements.txt files from project (build) dependencies'
url = 'https://github.com/timdiels/pybuilder-pip-tools'  # Project home page
license = 'LGPLv3'
authors = [
    Author('VIB/BEG/UGent', 'info@psb.ugent.be'),  # Note: an email is required
    Author('Tim Diels', 'timdiels.m@gmail.com'),
]
            
use_plugin('python.core')
use_plugin('python.install_dependencies')
use_plugin('python.distutils')
use_plugin('copy_resources')
use_plugin('filter_resources')
use_plugin('source_distribution')

################################
# pybuilder_chicken_turtle
#
# PyBuilder plugin which enforces a workflow for Python project using pull requests and build servers
'''
Assumes python.distutils is used
'''
import re
import os
import sys
import shutil
from glob import glob

from pybuilder.plugins.filter_resources_plugin import ProjectDictWrapper

readme_file = 'src/project/README.rst'

@init()
def main_init(project, logger): #TODO rm prefix
    project.plugin_depends_on('string')
    project.plugin_depends_on('GitPython')
    project.plugin_depends_on('Versio')
    project.plugin_depends_on('twine')
    project.plugin_depends_on('plumbum')
    
    # Sphinx doc
    project.plugin_depends_on('sphinx')
    project.plugin_depends_on('numpydoc')
    project.plugin_depends_on('sphinx-rtd-theme')
    project.set_property_if_unset('dir_source_doc', 'src/doc')
    
    # Set is_release
    tag = os.environ.get('TRAVIS_TAG')
    if project.has_property('is_release'):
        project.set_property('is_release', project.get_property('is_release').lower() in ('true', 'yes'))
    else:
        project.set_property('is_release', bool(tag))
    
    # Project version: add .dev if not release. Using the root setup.py will add
    # a datetime as well, iff dev.
    if not project.get_property('is_release'):
        project.version += '.dev'
    
    #TODO validate here or later step?
    # Validate project name: pybuilder_validate_name, _mode=strict|lenient. No off, that's what #use_plugin is for
    if re.search('\s', project.name):
        raise BuildFailedException('Project name may not contain whitespace, use dashes instead')
    if re.search('_', project.name): #TODO also raise on underscores and upper case unless project.set_property('pybuilder_chicken_turtle_name_validation', 'lenient') # default = 'strict'. When lenient, do not even warn; either raise or don't. This also means the name check needs to happen after init, so user can set this property
        raise BuildFailedException('Project name contains underscores, use dashes instead')
    if project.name.lower() != project.name:
        raise BuildFailedException('Project name contains upper case characters, use lower case instead')
    
    # Assert required files exist
    for file in ['LICENSE.txt', readme_file]:
        if not os.path.exists(file):
            raise BuildFailedException('Missing required file: {}'.format(file))
        
    # Files not to include in source distribution 
    project.get_property('source_dist_ignore_patterns').extend([
        '.project',
        '.pydevproject',
        '.settings'
    ])

    # Files to copy to dist root
    # Copies at @task('package')
    project.set_property('copy_resources_target', '$dir_dist')
    project.get_property('copy_resources_glob').extend([
        'README.rst',
        'LICENSE.txt',
    ])
    
    # setup.py
    project.set_property('distutils_readme_file', 'README.rst')  # readme file name, should be at the root (like build.py). Defaults to README.md
    
    # project.author
    project.author = ', '.join(author.name for author in project.authors)
    
    # Twine upload config
    project.set_property('distutils_upload_repository', 'https://pypi.python.org/pypi')
    
@before(['prepare'])
def before_prepare(project):
    coverage_report = project.get_property('coverage_report', None)
    pytest_args = project.get_property('pytest', None)
    
    # Ensure coverage_report and pytest are mutually exclusive
    if coverage_report and pytest_args:
        raise BuildFailedException(
            'Both coverage_report and pytest property are given. They are mutually exclusive. Remove one.'
        )
        
    # coverage_report property
    if coverage_report:
        if coverage_report == 'travis':
            args = (
                '--cov {source_main} --cov-report term-missing {source_unittest}'
                .format(
                    source_main=project.expand_path('$dir_source_main_python'),
                    source_unittest=project.expand_path('$dir_source_unittest_python')
                )
            )
        else:
            raise BuildFailedException(
                'Invalid value for coverage_report: {}. '
                'Expected "travis".'
                .format(coverage_report)
            )
    else:
        # pytest property 
        if project.has_property('pytest'):
            args = pytest_args
        else:
            args = '--maxfail 1 -v --lf ' + project.expand_path('$dir_source_unittest_python')
    project.set_property('pybuilder_pytest_args', args)
    
@task('compile_sources')
def main_compile_sources(project, logger): #TODO rm prefix
    import string
    
    # Overwrite src/doc/conf.py with src/doc/_conf.py
    # and substitute $version, ... in the process.
    _conf_py = 'src/doc/_conf.py'
    conf_py = 'src/doc/conf.py'
    with open(_conf_py) as f:
        contents = f.read()
    contents = string.Template(contents).safe_substitute(ProjectDictWrapper(project, logger))
    contents = '# Generated by pyb, do not edit, edit _conf.py instead.\n\n' + contents
    with open(conf_py, 'w') as f:
        f.write(contents)
        
    # README.rst
    # - Overwrite README.rst with src/project/README.rst with $version substituted for project.version or 'latest'
    # - Set project.description
    with open(readme_file) as f:
        contents = f.read()
    contents = string.Template(contents).safe_substitute({
        'latest_or_version': project.version if project.get_property('is_release') else 'latest',
        'master_or_version': project.version if project.get_property('is_release') else 'master'
    })
    with open('README.rst', 'w') as f:
        f.write(contents)
    project.description = contents

@task(description='Upload distutils packages with twine')
@depends('publish')
def twine_upload(project, logger):
    import plumbum as pb
    
    repo = _get_repo()
    
    # If current commit has no tag, fail
    commit = repo.commit()
    for tag in repo.tags:
        if tag.commit == commit:
            break
    else:
        raise BuildFailedException(
            'Current commit has no tag. '
            'To publish, it should have a tag named "{version}".'
        )
    
    # If tag is not a version tag or is different from project.version, fail
    try:
        if project.version != _version_from_tag(tag):
            raise BuildFailedException(
                'Version tag ({}) of current commit does not equal project.version ({}).'
                .format(tag.name, project.version)
            )
    except ValueError:
        raise BuildFailedException(
            'Current commit has tag ({}). '
            'To release, it should have a tag named "{version}".'
            .format(tag.name)
        )
        
    # If version < newest ancestor version, warn
    ancestors = list(repo.commit().iter_parents())
    versions = []
    for tag in repo.tags:
        if tag.commit in ancestors:
            try:
                versions.append(_version_from_tag(tag))
            except ValueError:
                pass
    newest_ancestor_version = max(versions, default=Version('0.0.0'))
             
    if project.version < newest_ancestor_version:
        logger.warn(
            'project.version ({}) is less than that of an ancestor commit ({})'
            .format(project.version, newest_ancestor_version)
        )
        
    # Upload
    logger.info('Uploading to PyPI')
    distributions = tuple(glob(project.expand_path('$dir_dist/dist/*')))
    repository = project.get_property('distutils_upload_repository')
    pb.local['twine'].__getitem__(('upload', '--repository', repository, '--repository-url', repository) + distributions) & pb.FG
    
def Version(*args, **kwargs):
    import versio.version
    import versio.version_scheme
    return versio.version.Version(*args, scheme=versio.version_scheme.Pep440VersionScheme, **kwargs)

def _get_repo():
    import git
    return git.Repo('.git')

def _version_from_tag(tag):
    '''
    Get version from version tag
     
    Returns
    -------
    str
        The version the version tag represents 
     
    Raises
    ------
    ValueError
        If tag name is not of format {version}, i.e. not a version tag
    '''
    name = tag.name.split(os.sep)[-1]
    if name.startswith('v'):
        version = name[1:]
    else:
        version = name
    #TODO what if it's not a version tag? We should check. Does Version raise when it's not valid?
    #raise ValueError('{} is not a version tag'.format(tag))
    #TODO probably just return an actual Version instance instead of str
    return version

@task
@depends('prepare')
def generate_documentation(project):
    import plumbum as pb
    cpus_available = len(os.sched_getaffinity(0))  # number of cpus
    pb.local['sphinx-build']['-j', cpus_available, '-b', 'html', project.expand_path('$dir_source_doc'), project.expand_path('$dir_target/doc')] & pb.FG

################################
# pybuilder_pytest
#

'''
PyBuilder plugin which runs pytest on ``$dir_source_unittest_python``.

At task `run_unit_tests`, runs pytest on ``$dir_source_unittest_python``. The
latter defaults to ``src/unittest/python``. (`PYTHONPATH` is set to include
``$dir_source_main_python`` and ``$dir_source_unittest_python``)

To configure pytest, `write a pytest.ini or setup.cfg file`__ as usual.

.. __: http://doc.pytest.org/en/latest/customize.html
'''

import os

# python: 2.6 (because py.test and plumbum)

@init
def pytest_init(project):  #TODO rm prefix
    project.plugin_depends_on('plumbum')
    project.plugin_depends_on('pytest')
    project.plugin_depends_on('future')
    project.set_property_if_unset('dir_source_unittest_python', 'src/unittest/python')
    project.set_property_if_unset('pybuilder_pytest_args', project.expand_path('$dir_source_unittest_python'))
    
@task('run_unit_tests')
def pytest_run_unit_tests(project, logger):  #TODO rm prefix
    import plumbum as pb
    from future.utils import raise_from
    
    # PYTHONPATH
    path_parts = []
    if 'PYTHONPATH' in pb.local.env:
        path_parts.append(pb.local.env['PYTHONPATH'])
    path_parts.append(project.expand_path('$dir_source_main_python'))
    dir_source_unittest_python = project.expand_path('$dir_source_unittest_python')
    path_parts.append(dir_source_unittest_python)
    PYTHONPATH = os.pathsep.join(path_parts)
    
    # Run
    with pb.local.env(PYTHONPATH=PYTHONPATH):
        try:
            args = tuple(project.get_property('pybuilder_pytest_args').split())
            pb.local['py.test'].__getitem__(args) & pb.FG
        except pb.ProcessExecutionError as ex:
            raise_from(BuildFailedException('py.test failed'), ex)


################################

@init()
def build_dependencies(project):
    # PyBuilder
    project.build_depends_on('pybuilder') #TODO >=0.11.10 < 1.0.0 once available. There are 0.11.10.dev* releases though, maybe we could set directly to that
#     project.get_property('pybuilder_pip_tools_build_urls').extend([
#         'git+https://github.com/pybuilder/pybuilder.git#egg=pybuilder-0'
#     ])
    
    # Testing
    project.build_depends_on('python-coveralls')
    project.build_depends_on('pytest-env')
    project.build_depends_on('pytest-cov')
    project.build_depends_on('pytest-timeout')
    project.build_depends_on('pytest-mock')
    
    # pybuilder test lib (TODO)
    project.build_depends_on('plumbum')
    project.build_depends_on('vex')
    
@init()
def initialize(project):
    # Package data
    # E.g. project.include_file('the.pkg', 'relative/to/pkg/some_file')

    # Files in which to replace placeholders like ${version}
    # Filters at @after('package')
    project.get_property('filter_resources_glob').extend([
        '**/pybuilder_pip_tools/__init__.py',
    ])

    # setup.py
    project.set_property('distutils_console_scripts', [  # entry points
    ])
    project.set_property('distutils_setup_keywords', 'pybuilder plugin pip-tools requirements.txt')
    project.set_property('distutils_classifiers', [  # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',  # pip-tools does not support 2.6, 3.2, 3.3.  2.7 lacks textwrap.indent
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Build Tools',
    ])
