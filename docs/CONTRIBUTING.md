<!-- This template is created by @nayafia https://github.com/nayafia/contributing-template -->
# Contributing

## Introduction

Thanks for considering contributing to this project.
Please follow these guidelines to develop
in order to guarantee the code quality and save time for other developers.

## Ground rules

- Ensure the cross-platform compatibility of latest Windows and Ubuntu.
- Please use [poetry](https://python-poetry.org/) as the dependencies management tool.
- Please follow [Conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) for your commits message.
- Please follow [gitflow](https://nvie.com/posts/a-successful-git-branching-model/) branch strategy.

## Get started

### Fork and create a new branch

Fork this project before your contributing.
We recommend to use [git-flow](https://github.com/petervanderdoes/gitflow-avh) and initialize:

```bash
git config gitflow.branch.master main
git config gitflow.prefix.versiontag v
git flow init -d
```

If you want to fix bugs:

```bash
git flow bugfix start <branch_name>
```

or

```bash
git checkout develop
git branch -b bugfix/<branch_name>
```

If you want to add new features, refactor codes:

```bash
git flow feature start <branch_name>
```

or

```bash
git checkout develop
git branch -b feature/<branch_name>
```

Branch name should only contains alphabets, digits, and `-`.
Corresponding issue number should be included if applicable.

### Install dependencies

Now you are in a new branch for developing.
Install dependencies and `pre-commit` hooks:

```bash
poetry install -E test
pre-commit install -t pre-commit -t commit-msg
```

Recommend to use [commitizen](https://github.com/commitizen-tools/commitizen) to submit commits。

### Test your code

Before your pull request, please test your code:

```bash
pytest
```

If you add new features, remember to add corresponding tests.

### Make a pull request

If the upstream is updated, please rebase to track the update of develop branch:

```bash
git checkout develop
git pull --rebase upstream develop
git flow bugfix rebase <branch_name>
```

or

```bash
git checkout develop
git pull --rebase upstream develop
git checkout <branch_name>
git rebase develop
```

Finally, make a pull request against **develop branch**.

## How to report a bug

If you find bugs of documentation or code,
please [submit](https://github.com/hktkzyx/travel-map/issues/new/choose) a bug report in GitHub.

## How to suggest a feature or enhancement

[Open](https://github.com/hktkzyx/travel-map/issues/new/choose) an issue in GitHub
if you have any suggestions of this project.
