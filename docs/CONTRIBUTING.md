<!-- This template is created by @nayafia https://github.com/nayafia/contributing-template -->
# Contributing

## 简介

欢迎并感谢各位开发者对本项目的贡献。
为了保证本项目的代码质量，节省项目管理的时间，
请各位开发者在开始自己的开发工作前阅读本指南。

## 基本规则

- 请确保新提交的代码能够兼容最新的 Windows 和 Ubuntu 系统。
- 请使用 [poetry](https://python-poetry.org/) 作为依赖管理。
- 请遵守 [Conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) 规范。
- 请遵循 [gitflow](https://nvie.com/posts/a-successful-git-branching-model/) 分支管理策略。

## 指南

### Fork 并新建一个分支

如果你想提交你的代码，先 Fork 本项目。
推荐安装 [git-flow](https://github.com/petervanderdoes/gitflow-avh) 并初始化：

```bash
git config gitflow.branch.master main
git config gitflow.prefix.versiontag v
git flow init -d
```

如果你的代码是修复 bug，则运行:

```bash
git flow bugfix start <branch_name>
```

或者

```bash
git checkout develop
git branch -b bugfix/<branch_name>
```

如果是提交新功能、重构代码，则运行：

```bash
git flow feature start <branch_name>
```

或者

```bash
git checkout develop
git branch -b feature/<branch_name>
```

这里的分支名应当只包括字母、数字和 `-` 。
如果有对应的 issue 应当包含 issue 的编号。

### 开发准备

目前你已经在一个新的开发分支上了。
开发前，安装相应的依赖：

```bash
poetry install -E test
pre-commit install -t pre-commit -t commit-msg
```

推荐使用 [commitizen](https://github.com/commitizen-tools/commitizen) 提交您的 commits。

### 测试代码

在提交你的 Pull request 之前，请测试你的代码：

```bash
pytest
```

如果你添加了新的功能，请添加对应的测试。

### 提交 Pull request

如果原仓库的代码有了更改，请务必 rebase 保持 develop 分支更新：

```bash
git checkout develop
git pull --rebase upstream develop
git flow bugfix/feature rebase <branch_name>
```

或者

```bash
git checkout develop
git pull --rebase upstream develop
git checkout <branch_name>
git rebase/merge develop
```

最后，就可以提交你的 PR 到 develop 分支了。

## 如何报告 Bug

本项目生成的地图是基于开源项目 [pyechart](https://github.com/pyecharts/pyecharts)，
如果生成的地图有不符合中国法律规范的，请邮件联系 <hktkzyx@yeah.net>。

如果发现关于项目文档、代码等其他的 bug，请直接在 GitHub 上[提交](https://github.com/hktkzyx/travel-map/issues/new/choose) Bug report。
按照模板报告即可。

## 如何提出新功能和改进的建议

旅行地图已经有很多工具了，但大多是精确到省级行政区。
本项目目前是精确到低级市，没有计划精确到县级行政区，也没有计划开发图形界面。
如有其他建议，请在 GitHub 上按照模板[提交](https://github.com/hktkzyx/travel-map/issues/new/choose)你的 issue 即可。
