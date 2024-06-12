Ontobot is a GitHub-based bot for making ontology change requests in KGCL, the Knowledge Graph Change Language. 
It can be installed in a GitHub ontology repository, where it then watches for issues that include a specific text string: “Hey ontobot!, apply:”
When it sees that string, Ontobot scans the issue for a bulleted list of ontology change requests, written in the KGCL syntax.
Ontobot reads the list of one or more KGCL commands, and automatically generates a GitHub Pull Request that will make the requested change(s) in the ontology source file.

Ontobo workflows are defined using YAML files, and placed in a directory called ‘.github/workflows’ within the repository.
The Ontobot manual provides YAML templates, which can be downloaded, customized, and added to the GitHub repository where your ontology source file is maintained:
.github/workflows/ontobot.yaml.

KGCL can express common ontology editing operations (such as modifying a label or a definition, obsoleting a term, moving a term under another parent term, etc.)
using a syntax as close as possible to natural English language.
As an example, the KGCL command to change the name of the ontology term with the ID ENVO:01000575 from ‘wax’ to ‘oil’ is “rename ENVO:01000575 from ‘wax’ to ‘oil’”.

The grammar defining KGCL can be found at https://github.com/INCATools/kgcl/blob/main/src/kgcl_schema/grammar/kgcl.lark.
