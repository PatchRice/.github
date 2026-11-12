# Contributing / 贡献指南

Thanks for contributing to PatchRice projects. Repository-specific setup, testing and coding conventions take precedence over this shared guide.

感谢为 PatchRice 项目做出贡献。各仓库自身的构建、测试和编码规范优先于此通用说明。

## Before opening an issue / 提交 Issue 前

- Search existing issues. Choose the closest Issue Form and provide enough context to reproduce or evaluate the request.
- Report security vulnerabilities **privately**; see [SECURITY.md](SECURITY.md).
- Remove secrets, personal information and private records from logs or screenshots.

## Before opening a pull request / 提交 PR 前

- Keep the change focused. Link any relevant issues using `Fixes #123` or `Refs #123` as appropriate.
- Explain the intended behavior, verification steps and meaningful compatibility or migration concerns.
- Run relevant checks described by the target repository and document what was and was not tested.
- For large or uncertain design changes, consider discussing the approach in an issue first. Small, self-contained fixes need no preliminary issue.
- Do not add extra configuration switches when fixing behavior that should be consistent, unless the repository's design requires them.

## Review and issue triage / 维护流程

Maintainers review new issues tagged `S-needs-triage`, confirm the category, assign a `P-*` priority when appropriate, and add repository-specific `A-*` area labels if needed. Priority is a maintenance scheduling decision, not a severity claim made by the reporter.

维护者通过 `S-needs-triage` 统一处理新 Issue，必要时设置 `P-*` 优先级、`A-*` 模块标签。优先级由维护团队决定，提交人无需猜测严重程度。
