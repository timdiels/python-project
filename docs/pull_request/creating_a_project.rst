Creating a project
==================
To create a project with the aforementioned structure, follow these
instructions. Ensure you have read about the `project structure`_ first.

Create from template
--------------------
First,
TODO cookiecutter template
- adjust each file in template to match (cookiecutter may resolve this)

Initialize git
--------------
Initialize git and push first commit to GitHub/GitLab::

    git init
    git add .
    git commit -m 'Initial commit, from template'
    git remote add origin $repo_url
    git push -u origin master

Set up a local development environment
--------------------------------------
See `setting up a local development environment <setup development
environment cloned_>`_.

Generate requirements.txt files
-------------------------------
Run::

    pyb pip_sync
    git add .
    git commit -m 'Add requirements.txt files'

This will have created 4 files:

- requirements.txt
- build_requirements.txt
- requirements_development.txt
- build_requirements_development.txt

Only the non-development ones are tracked by git (``.gitignore`` takes care of
that).

Compile README, ...
-------------------
Run::

    pyb compile_sources
    git add .
    git commit -m 'Add compiled README, src/doc/conf.py'

Test coverage
-------------

If it's a GitHub project, set up coveralls, else TODO.

coveralls (GitHub)
------------------
todo goto website, click enable, yay

? (GitLab)
----------

Build / continuous-integration (CI) server
------------------------------------------

If it's a GitHub project, set up Travis with the instructions below, else set
up GitLab CI.

Travis (GitHub)
^^^^^^^^^^^^^^^
``.travis.yml`` uses scripts from the travis-files repository, add it as a
subtree::

    git subtree add --prefix travis_files https://github.com/timdiels/travis-files.git master --squash

Next, log into the `Travis CI web user interface`_ and enable Travis on
the project (should be a simple click of a button).

Next, while still in the web user interface, go to the settings and add 2
environment variables with "Display value in build log" off (the default):
TWINE_USERNAME, TWINE_PASSWORD for respectively the username and password to
upload with to PyPI on release. These values will be inserted verbatim during
the build, e.g. ``export TWINE_PASSWORD=super password``, so you need to shell
escape the values, e.g. ``super\ password`` or simply ``'super password'``.

Finally, on the same settings page, ensure build is enabled on push and pull
requests.

.. _travis ci web user interface: https://travis-ci.org/auth

.. TODO
   
   also set COVERALLS_REPO_TOKEN

GitLab CI
^^^^^^^^^
TODO

Documentation
-------------

(When making a new project, be sure to first register it on
https://readthedocs.io, simply adding the hook won't work).

Notes
-----
This documents why the project is created according to the above instructions,
i.e. compares alternatives.

It is recommended to `use git subtree instead of submodule`, hence we use
subtree.

.. _project structure: project_structure.rst
.. _use git subtree instead of submodule: http://blogs.atlassian.com/2013/05/alternatives-to-git-submodule-git-subtree/
.. _setup development environment cloned: todo #create_venv
