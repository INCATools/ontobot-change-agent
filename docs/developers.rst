For Developers
==============

Development Installation
------------------------

To install in development mode, use the following:

.. code-block:: shell

    $ pip install poetry
    $ git clone git+https://github.com/INCATools/ontobot-change-agent.git
    $ cd ontobot-change-agent
    $ poetry install

Testing
-------

After cloning the repository and installing :code:`tox` with :code:`pip install tox`, 
the unit tests in the :code:`tests/` folder can be run reproducibly with:

.. code-block:: shell

    $ tox

Additionally, these tests are automatically re-run with each commit in a `GitHub Action <https://github.com/INCATools/ontobot-change-agent/actions?query=workflow%3ATests>`_.