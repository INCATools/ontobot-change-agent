First Run
=========

Firstly, generate a personalized token as instructed `here <https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token>`_
and save it in :code:`src/onto_crawler/token.txt`.

Next, run:

.. code-block:: shell

    $ poetry run ocrawl issues --label synonym

This should return a list of issue titles tagged with the label `synonym`. 
By default, we've chosen the `mondo repository <https://github.com/monarch-initiative/mondo>`_ .
If you need to test with another repository, add an option :code:`-r` and 
follow it with the :code:`organization/repository_name`.