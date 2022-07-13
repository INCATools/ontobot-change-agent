<!--
<p align="center">
  <img src="https://github.com/hrshdhgd/onto-crawler/raw/main/docs/source/logo.png" height="150">
</p>
-->

Crawl github for ontology related issues.

## Getting Started

Firstly, generate a personalized token as instructed [here](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) and save it in `src/onto_crawler/token.txt`

Next, run:

```shell
$ poetry run ocrawl issues --label synonym
```
This should return a list of issue titles tagged with the label `synonym`. By default, we've chosen the [mondo repository](https://github.com/monarch-initiative/mondo). If you need to test with another repository, add an option `-r` and follow it with the `organization/repository_name`. 

### Command Line Interface

The onto_crawler command line tool is automatically installed. It can
be used from the shell with the `--help` flag to show all subcommands:

```shell
$ poetry run ocrawl --help
```

## Installation

<!-- Uncomment this section after first release
The most recent release can be installed from
[PyPI](https://pypi.org/project/onto_crawler/) with:

```bash
$ pip install onto-crawler
```
-->

The most recent code and data can be installed directly from GitHub with:

```bash
$ pip install git+https://github.com/hrshdhgd/onto-crawler.git
```

<!-- ## Contributing

Contributions, whether filing an issue, making a pull request, or forking, are appreciated. See
[CONTRIBUTING.md](https://github.com/hrshdhgd/onto-crawler/blob/master/.github/CONTRIBUTING.md) for more information on getting involved. -->



### License

The code in this package is licensed under the MIT License.


## For Developers

<details>
  <summary>See developer instructions</summary>


The final section of the README is for if you want to get involved by making a code contribution.

### Development Installation

To install in development mode, use the following:

```bash
$ pip install poetry
$ git clone git+https://github.com/hrshdhgd/onto-crawler.git
$ cd onto-crawler
$ poetry install
```

### Testing

After cloning the repository and installing `tox` with `pip install tox`, the unit tests in the `tests/` folder can be
run reproducibly with:

```shell
$ tox
```

Additionally, these tests are automatically re-run with each commit in a [GitHub Action](https://github.com/hrshdhgd/onto-crawler/actions?query=workflow%3ATests).


### Making a Release

> TODO
</details>
