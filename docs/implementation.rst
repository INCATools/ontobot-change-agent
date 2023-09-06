Implementation
===============

The implementation of :code:`ontobot-change-agent` is generally within a github workflow of an ontology 
repository.

1.
a. **OBO Resource**: The template for the workflow is provided by `this YAML file <https://github.com/hrshdhgd/ontobot-change-agent/blob/main/.github/workflows/new-pr.yml>`_.
Just uncomment the code and change the following:

Update the resource (:code:`*.obo` file) path in the ontology's repository.

.. code-block:: shell

    run: |
        echo "resource=src/ontology/YOUR-RESOURCE-FILENAME.obo" >> $GITHUB_ENV
        ..

b. **OWL Resource**: The template for the workflow is provided by `this YAML file <https://github.com/hrshdhgd/ontobot-change-agent/blob/main/.github/workflows/new-pr-java.yml>`_.
Just uncomment the code and change the following:

Update the resource (:code:`*.owl` file) path in the ontology's repository.

.. code-block:: shell

    run: |
        echo "resource=src/ontology/YOUR-RESOURCE-FILENAME.owl" >> $GITHUB_ENV
        ..
2. `Create a personal access token <https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token>`_ 
and enter it in the "Secrets" section of the ontology repository `as explained here <https://docs.github.com/en/actions/security-guides/encrypted-secrets>`_.
    **Note:** The variable name could be either :code:`GH_TOKEN` or anything else but it must match
    in the workflow (:code:`${{ secrets.GH_TOKEN }}`) and the repository secret section (e.g. :code:`GH_TOKEN`).

3. The title for the pull request generated corresponds to the issue that triggered its generation. If the issue is edited, the same pull request is updated.

4. An example of a issue to trigger a pull request:
.. code-block:: none

Hey ontobot!, apply:
- create exact synonym 'ABCD1' for PREFIX:12345
- create broad synonym 'ABCD2' for PREFIX:12345
    
    There are no limits on the number of bullets one can pass.