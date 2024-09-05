Installation
============
The most recent release can be installed from
`PyPI <https://pypi.org/project/ontobot_change_agent>`_ with:

.. code-block:: shell

    $ pip install ontobot_change_agent

The most recent code and data can be installed directly from GitHub with:

.. code-block:: shell

    $ pip install git+https://github.com/INCATools/ontobot-change-agent.git

To install in development mode, use the following:

.. code-block:: shell

    $ git clone git+https://github.com/INCATools/ontobot-change-agent.git
    $ cd ontobot-change-agent
    $ poetry install

New Features
------------

.. important::

    In order to make `ontobot-change-agent` capable of using llm models, you could install it with the optional
    dependency package `llm-change-agent`. This feature is in early development and is not yet ready for general use.

    To install using pip:

    .. code-block:: shell

        $ pip install ontobot_change_agent[llm]

    OR

    .. code-block:: shell

        $ pip install git+https://github.com/INCATools/ontobot-change-agent.git#egg=ontobot_change_agent[llm]


    To install in development mode, use the following:
    .. code-block:: shell

        $ poetry install --extras llm

.. note::

    To leverage the features of `llm-change-agent` package one would need to have any one or all of
    the environment variables set:

    - `OPENAI_API_KEY`
    - `ANTHROPIC_API_KEY`
    - `CBORG_API_KEY` (for LBNL users only)