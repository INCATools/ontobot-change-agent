Implementation
===============

Step 1: GitHub Workflow
-----------------------

The implementation of :code:`ontobot-change-agent` is generally within a github workflow of an ontology 
repository.

#. \ 
    - **OBO Resource**: The template for the workflow is provided by `this YAML file <https://github.com/hrshdhgd/ontobot-change-agent/blob/main/.github/workflows/new-pr.yml>`_.
    Just uncomment the code and change the following:

    Update the resource (:code:`*.obo` file) path in the ontology's repository.

    .. code-block:: shell

        run: |
            echo "resource=src/ontology/YOUR-RESOURCE-FILENAME.obo" >> $GITHUB_ENV
            

    - **OWL Resource**: The template for the workflow is provided by `this YAML file <https://github.com/hrshdhgd/ontobot-change-agent/blob/main/.github/workflows/new-pr-java.yml>`_.
    Just uncomment the code and change the following:

    Update the resource (:code:`*.owl` file) path in the ontology's repository.

    .. code-block:: shell

        run: |
            echo "resource=src/ontology/YOUR-RESOURCE-FILENAME.owl" >> $GITHUB_ENV
            
    .. note::
        For OWL resources we use `kgcl-java <https://github.com/gouttegd/kgcl-java/tree/master>`_ as the underlying package to carry out the change.
        There are 2 options for implementation here:\ 
        - Use existing an instance of ROBOT (via ODK) with `kgcl-java` as a plugin. OR\ 
        - Use a standalone JAR file which combines both ROBOT and `kgcl-java`.

        We highly recommend using the standard option (#1). For this you should just uncomment `this code block <https://github.com/hrshdhgd/ontobot-change-agent/blob/b60d32375941c19672deace22b74814e04a73284/.github/workflows/new-pr-java.yml#L56-L62>`_
        and delete `this code block <https://github.com/hrshdhgd/ontobot-change-agent/blob/b60d32375941c19672deace22b74814e04a73284/.github/workflows/new-pr-java.yml#L63-L68>`_

#. Create a `personal access token <https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token>`_ 
and enter it in the "Secrets" section of the ontology repository `as explained here <https://docs.github.com/en/actions/security-guides/encrypted-secrets>`_.
    .. note::
        The variable name could be either :code:`GH_TOKEN` or anything else but it must match
        in the workflow (:code:`${{ secrets.GH_TOKEN }}`) and the repository secret section (e.g. :code:`GH_TOKEN`).


Step 2: Take it for a spin!
---------------------------

Create a new issue
""""""""""""""""""
#. Create a new issue in the repository as one would usually do and give it a clear subject.
#. In the body, `ontobot-change-agent` will be looking for the phrase - "Hey ontobot!, apply:"\ (the "!" is optional).\ 
#. In the next line start writing change language commands as bullets (using "-" or "*").
    a. The list of commands can be found `here <https://incatools.github.io/kgcl/examples/>`_ ("Command" section).

    #. An example of an issue to trigger a pull request:

    .. code-block:: html

        Hey ontobot!, apply:
        
        - create exact synonym 'ABCD1' for PREFIX:12345
        - create broad synonym 'ABCD2' for PREFIX:12345

    There are no limits on the number of bullets one can pass.

Pull request
""""""""""""
Once the issue is created, it triggers the GitHub workflow mentioned above and creates a corresponding pull request
which should reflect the expected change in the ontology resource based on the commands listed in the issue.
The title for the pull request generated corresponds to the issue that triggered its generation. If the issue is edited, 
the same pull request is updated.