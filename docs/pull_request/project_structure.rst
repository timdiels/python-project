Project structure
=================

The structure of the project is explained below. The "Notes" section at the
bottom documents why this structure was chosen over any alternatives, as
well as which problems have been worked around.

Collaborative development model
-------------------------------
Each contributor has their own GitHub/GitLab clone of the main repository.
Changes to the main repository are only made via pull requests. A contributor
will keep their master in sync with that of the main repository and thus needs
to add changes on a separate branch (to avoid push --force to master). Before
making a pull request, the contributor should rebase to match the master branch
of the main repository.

Note: pull requests only pull in commits, never tags.

Build / continuous-integration (CI) server
------------------------------------------
When you make a pull request or push to the project's repository, a build is
triggered on a build server. When a commit is pushed, or a pull request is
made, the build will run tests. When a tag is pushed, the project is released
to `PyPI`_ (after rerunning tests).  The build server used depends on whether
the project is hosted on GitHub or GitLab.

.. _PyPI: pypi.python.org

GitHub projects
^^^^^^^^^^^^^^^
GitHub offers Travis CI for free. For a thorough introduction, start by reading
its `getting started`_ page.

Travis CI was enabled on the project through the `Travis CI web user interface`_.
It is mainly configured through the ``.travis.yml`` file in the root of the
project repository. A couple of options can only be configured via the web user
interface (or via the CLI).

If the installation step fails, the build is marked 'errored'. If the script
step fails, the build is marked 'failed'. The former is most often caused by an
error in build.py or dependencies, whereas the latter is more likely due to
a failing test, a bug in the code.

Consider reading about `pull requests with Travis CI <travis ci pull requests_>`_.

Environment variables can be set via ``.travis.yml`` and via the repository
settings. Use ``.travis.yml`` for variables specific to the current
commit/build and the repository settings for variables that should affect all
builds, e.g. PyPI password.

.. _getting started: https://docs.travis-ci.com/user/getting-started/
.. _travis ci web user interface: https://travis-ci.org/auth
.. _travis ci pull requests: https://docs.travis-ci.com/user/pull-requests/

GitLab projects
^^^^^^^^^^^^^^^
GitLab uses GitLab CI. GitLab.com offers free shared runners. GitLab Community
Edition (i.e. anywher other than gitlab.com) requires you to provide your own
runners.

TODO

Virtual environments
--------------------
All development is assumed to occur in a virtual environment, especially when
calling `pyb` (PyBuilder, see below).

PyBuilder
---------
`PyBuilder`_ is a local build tool, like Maven. It is configured by `build.py`,
which contains tasks to:

- run a subset of tests for quick local testing (the build server runs all
  tests), just to catch some errors early (i.e. before pushing)
- generate `*requirements.txt` files from the dependencies and uninstall
  anything not mentioned as a dependency. These `*requirements.txt` files are
  used to ensure the software is always tested or run using the exact same
  dependencies. (The user is free to pip install the package with different
  versions of dependencies at their own risk. Generated installers (**TODO**)
  install according to the requirements.txt files)
- generate a `setup.py` file and release to PyPI (To be used by the build
  server only!)
- replace placeholders such as `$version` in certain files
- ...

This is used during local development, as well as on the build server.

Documentation
-------------
Documentation is written as `reStructuredText`_ files (.rst) located in
``src/doc``. These get compiled by `Sphinx`_ into HTML, PDF and epub. When a
commit is added to the master on GitLab/GitHub, `Read the Docs (RTD) <rtd_>`_
is notified and starts a build of the documentation with Sphinx, after which it
hosts the result on its website, as the 'latest' version. RTD
does not generate documentation for a tag unless you tell it to (the release
workflow documents this).

The Sphinx configuration file is ``src/doc/_conf.py``.  This has some variables
in it such as ``$version``, which get substituted by ``pyb`` during the
``prepare`` task. The result is placed in ``src/doc/conf.py``.

Read the Docs can be configured per project on https://readthedocs.io or for
most options (but not all) in ``readthedocs.yml`` inside the project itself.

In addition to RTD, ``pyb generate_documentation`` can be used to build the
documentation locally. The output is in ``target/doc``.

Testing
-------
pytest is used for testing. Tests are located in src/unittest/python. To run
tests, run ``pyb`` (it includes the `clean` and `run_unit_tests` tasks). To
pass arguments to py.test, ``pyb -P`` **TODO**

Notes
-----

Documentation
^^^^^^^^^^^^^
There is no way (at time of writing) to get RTD to wait for
pyb to build before looking for ``conf.py``. A ``conf.py`` generated from
``_conf.py``, both included in the repository is the least ugly I could do.

Documentation hosting comparison: 

- pythonhosted.org: has been deprecated. One will no longer be able to upload
  to it in the future. (including ``setup.py upload_docs`` from setuptools)

  http://thread.gmane.org/gmane.comp.python.distutils.devel/23384/focus=23516
  
- Read the Docs (RTD): Our conf.py contains $variables, which need to be substituted
  by pyb. It appears docs and conf.py are collected (copied?) before setup.py
  is run, meaning we can't execute pyb first to substitute the variables.
  Because of this, we would need to rename conf.py to _conf.py and include a
  generated conf.py, also in src/doc in each commit (it assumes conf.py
  and doc sources are in the same directory).

  Or to keep the generated files outside the `src` dir, we could copy and
  modify the whole dir to `docs` where RTD will find them without any
  configuration required. Again, this whole directory would need to be included
  in the commit.

- GitHub pages (when project is on GitHub): Have to add generated docs to git;
  longer diffs, i.e. harder to read. Might forget to generate docs before
  comitting. Maybe a hook could be added to the repo itself to modify the
  commit to include freshly generated doc.

  One can upload the html doc to a separate branch called gh-pages. That would
  solve the problem of longer diffs, but working with 2 branches is more
  complex. E.g. how would pull requests work?

- GitLab pages (when project is on GitLab): not part of commit, can be
  automated via .gitlab-ci.yml, very flexible. Perfect, really.
