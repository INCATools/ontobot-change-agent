Implementation
===============

The implementation of `ontobot-change-agent` is generally within a github workflow of a 
repository for any ontology. The template for the workflow is provided by 
`this repository <https://github.com/hrshdhgd/ontobot-change-agent/blob/main/.github/workflows/new-pr.yml>`_.
Just uncomment the code and change the follwing:

1. Change the resource to the `*.obo` file in the ontology's repository.

.. code-block:: shell

    run: |
        echo "resource=src/ontology/YOUR-RESOURCE-FILENAME.obo" >> $GITHUB_ENV

2. `Create a personal access token <https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token>`_ 
and enter it in the "Secrets" section of the ontology repository `as explained here <https://docs.github.com/en/actions/security-guides/encrypted-secrets>`_.

Note: The variable name could be either :code:`GH_TOKEN` or anything else. But the variable names must match
in the workflow (:code:`${{ secrets.GH_TOKEN }}`)and the repository secret section.