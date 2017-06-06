Development and maintenance tasks
=================================
This page documents some frequent and/or non-trivial tasks. Ensure you have
read about the `project structure`_ first.

.. TODO ensure there is a toctree in sidebar or main body to the tasks below

Setting up a local development environment
------------------------------------------

We will go through the steps of contributing in chronological order, starting
from scratch.

Clone the project
^^^^^^^^^^^^^^^^^
As discussed in project structure, each contributor works on their own
GitHub/GitLab and uses pull requests to the main repository to contribute their
work. 

First, go to the GitHub/GitLab webpage of the project, ensure you are logged
in, and hit the clone button to get your own repository.

Next, locally clone your repository. `$project_root` will refer to the
directory created by the ``git clone``, i.e. where `.git` is.

Create venv
^^^^^^^^^^^
Development requires and happens in a virtual environment (venv). To create
one, run::

    cd $project_root
    python -m venv venv  # create venv. Be sure to use the python version you want to test with, e.g. python3.5
    . venv/bin/activate  # enter the venv
    pip install -U pip setuptools wheel  # upgrade essentials, the (potentially ancient) system-wide version is installed by default

You can exit the venv with ``deactivate``, but from now on the instructions
will assume you are in the venv. 

Installing pybuilder
^^^^^^^^^^^^^^^^^^^^
As discussed in `Project structure`_, we use PyBuilder, a build tool like
Maven.

To install the latest development version (we've used fancy new PyBuilder
features, so we need the dev version), run::

    pip install pybuilder==0.11.10.dev20170116220145  # temporarily need this version to be able to install github version

Now you can run `pyb`::

    $ pyb --version
    pyb 0.11.10.dev20170123223255

Finally, the first time you use `pyb` on the project, you must run::

    pyb install_build_dependencies

Contributing
^^^^^^^^^^^^
To contribute changes:

- `Set up your local development environment <setup development environment_>`_
  according to the above instructions

- Update your repository's master to that of the main repository::

      git checkout master
      git pull ???/master

  **TODO**

- Create a branch to work on to make the desired change (a new feature or bug
  fix)::

      git checkout -b $branch_name

  Replace `$branch_name` with something descriptive for yourself. E.g.
  `add_foo_output`. (Do not name it ``'release'``)

- Add/adjust tests for the change you would like to make (See `Project
  structure: testing`_). If your change is a bug fix, add a test that fails on the bug.
  Aspects that are extremely difficult to write a test for may be tested
  manually, but be sure to mention this in the pull request.

- Run ``pyb`` to run the tests.
- Ensure the added/changed tests fail and the others do not.
- Implement the change.
- Run ``pyb`` again. If tests do not pass, fix and try again.
- If you have touched any documentation or docstrings:
  
  - ``pyb generate_documentation``
  - `review your changes to the documentation <review documentation_>`_ by
    browsing the relevant parts with ``firefox target/doc/index.html`` (or a
    different browser)

- Tidy your commits with:
  
  - ``git commit --amend`` (if just one commit)
  - or ``git rebase --preserve-merges -i master`` (roughly put, shows all
    commits added since master)

- If the main repository's master has changed in the meantime:

  - Update your master again (see above) 
  - Rebase your branch to the changes to master. This will make it as if you
    did your work on the updated master instead::

        git checkout $branch_name
        git rebase master

- Push your branch::

      git push origin $branch_name

- Make a pull request:

  Go to the project's GitHub/GitLab page, click the pull requests tab. Select
  your repository and (feature/bug-fix) branch. Add a quick description of what
  it changes if it is not immediately clear from the commit messages; or
  anything else that helps the reviewer of the pull request.

- If the pull request is rejected, repeat the steps starting from "Implement
  the change", do not make a new pull request, and use ``git push --force``
  instead when pushing your branch.

  **TODO** need notify the reviewer?

- If the pull request is accepted, you may delete your branch::

      git push origin --delete $branch_name  # delete remotely
      git branch -d $branch_name  # delete locally

Please also adhere to the code and commit guidelines below.
  
Commit guidelines
^^^^^^^^^^^^^^^^^
**TODO**

Code guidelines
^^^^^^^^^^^^^^^
**TODO**

Accepting pull requests
-----------------------

Workflow for accepting a pull request:

- Check build succeeds
- Review code:

  - follows code guidelines?
  - is covered by tests?

- Review commits: follows commit guidelines?
- Review parts of the readme that have changed, as displayed on GitHub/GitLab,
  if any:

  - Formatting errors?
  - Dead links?

- If all the above is in order, accept

Post-accept checks:

- Review documentation:

  - Open latest doc http://{project}.readthedocs.io/en/latest/,
  - Refresh until it reflects the right commit
  - `Review the parts changed by the pull request`_

- Ensure build on master succeeds as well
- If any of the above fails, follow contributor workflow to contribute fixes
  via a new pull request

Reviewing documentation (Sphinx)
--------------------------------
look at areas that likely have changed (see changelog and commits starting
with ``Doc:``)

- Formatting errors?
- Dead links?
- Any todos or half-written pieces?
- Up to date? I.e. was it adjusted to reflect the latest changes?

Changing dependencies
---------------------
TODO put this in the pybuilder_pip_tools plugin's doc, then refer to it here.

In short:

1. Edit `build.py`
2. ``pyb pip_sync``

.. warning::

   ``pyb pip_sync`` uninstalls anything that is not a project dependency. This
   is fine iff you are in the development venv. To avoid forgetting, uninstall
   pybuilder from the system/user install directory (if you have installed it
   outside a venv before); then running pyb outside the venv will only result
   in ``pyb not found``.


To change dependencies, edit `build.py`'s `project.depends_on` and
`project.build_depends_on` lines.  Constrain at least to the major version
``pkg[opt,...]==2.*``. (When major version changes, backwards
compatibility is broken, and so our package might break by consequence when
updating to a different major version.

During development, you may want to install some dependencies from elsewhere
than PyPI, e.g. from their GitHub/GitLab or from a local filesystem location.
You can't use `*depends_on` for this. Instead, add them to
``project.set_property('pybuilder_pip_tools_urls', ...)``. These urls must have
a fragment containing ``egg=pkg-name-version``; version is unused and can be
set to ``0``. Note that they will be ignored on release, when creating
installers, or when used on Travis; they're only intended for development.
These urls are complementary to what you specify in `*depends_on`. For
example::

    project.depends_on('magic[opt1,opt2]', '==2.*')
    project.get_property('pybuilder_pip_tools_urls').extend([
        'git+https://github.com/someone.git#egg=magic-2.5.0.dev1',
    ])
    # use pybuilder_pip_tools_build_urls for build dependencies

Would create a `requirements.txt` containing::

    git+https://github.com/someguy/magic.git#egg=magic-2.5.0.dev1[opt1,opt2]==2.*

Finally, you must run the following to update the `*requirements*.txt` files
and the installed packages in the venv::

    pyb pip_sync

Note: pip_sync isn't ran by default as it can take a while to finish. When
forgotten, Travis will still test with the right versions installed; so in the
worst case you'll only lose time due to a failed Travis build.

Releasing
---------

Workflow for releasing a new version:

#. If you have more changes to include in the release, `contribute them
   first <contributing_>`_. 
   
#. Switch to local clone of main repo (e.g. ``git clone ssh://...$mainrepo``)
   
   Unlike when contributing, the next steps need to be done on a local clone of
   the main repo (not a local clone of your GitHub/GitLab clone of the main
   repo). This is because tags cannot be pulled in via pull requests but must
   be pushed directly.

#. Ensure your working tree is clean and you are on the master branch: ``git
   checkout master && git status``

#. Update changelog in `src/doc/changelog.rst` by reviewing commit messages
   since last release
#. `Review changes to changelog <review documentation_>`_ via:: 
   
       pyb generate_documentation && firefox target/doc/index.html

    or review them on RTD after pushing them in the steps below

#. `Set the release version <change version_>`_
#. Push commit: ``git push``
#. Wait for CI build (`Travis <travis build_>`_, `GitLab <gitlab build_>`_) to succeed
#. Wait for `RTD latest build <rtd projects_>`_ to pass, then review it briefly:
   
   - Review any warnings in the RTD build log
   - Open a random page and at a glance verify it looks right

#. Version tag the release commit and push it::
   
       git tag {version} && git push origin {version}

#. Activate the version just released at `RTD <rtd projects_>`_
#. Wait for RTD build to finish and review it as well
#. Wait for CI build of tag (`Travis <travis build_>`_, `GitLab <gitlab
   build_>`_) to finish
#. Review any warnings in the CI build log
#. Review `PyPI <pypi project_>`_

   - At first glance, looks correct
   - Homepage link is not dead
   - Documentation link links to correct version at RTD

#. `Set version to a non-release version with bumped patch version <change version_>`_
#. and push it: ``git push``

Note: a tool for automatically checking for dead links probably exists, feel
free to look into it.

.. _travis build: https://travis-ci.org
.. _rtd projects: https://readthedocs.org/dashboard
.. _pypi project: https://pypi.python.org/pypi/$project

Changing the version
--------------------
- Set `version` in `build.py`
- If you want a development version (``.dev`` suffix will be added):

  - Run ``pyb compile_sources`` to update any files that reference the project
    version (e.g. the README.rst)
  - Commit changes with message ``Version {version}.dev``.

- Else, you want a release version:

  - Run ``pyb -P is_release=True compile_sources``
  - Commit changes with message ``Version {version}``.


Changing README.rst or src/doc/conf.py
--------------------------------------
``pyb compile_sources`` compiles:

- ``src/project/README.rst`` into ``README.rst``
- ``src/doc/_conf.py`` into ``src/doc/conf.py``

So:

- Edit the source file, not the compiled file. 
- Run ``pyb compile_sources`` when done.

Update $project_root/travis_scripts
-----------------------------------
If you want to update to a new version of travis-scripts, run::

    git subtree pull --prefix travis_files https://github.com/timdiels/travis-files.git master --squash

Notes
-----
Note: don't use depends_on_requirements. All *depends_on* get added to
setup.py and we don't want pinned versions from requirements.txt inside
setup.py

Release commits are best tagged as {version}, not v{version}. semver1 suggested
v{version} but semver2 no longer does. Historically the v prefix was used
because tags had to be valid identifiers, i.e. had to start with alphabetic
character. (`Source`__)

Cannot have git call ``pyb compile_sources`` automatically. `pre-commit` hook is
insufficient; it does not trigger when a rebase edits/replaces a commit and
there are no hooks to hook into those edits.

.. __: http://stackoverflow.com/questions/2006265/is-there-a-standard-naming-convention-for-git-tags

.. _project structure: project_structure.rst
