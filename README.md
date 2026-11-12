# PatchRice GitHub community templates

一套可跨仓库复用的 Issue Forms、PR 模板、安全报告表单和标签规范。借鉴 Rust 的标签分层方式，并保持轻量、无项目专属假设。**本目录是一份可提交到 `PatchRice/.github` 的草案，不会自动修改任何现有 GitHub 仓库。**

## 目录结构

```text
.github/
  ISSUE_TEMPLATE/
    01-bug.yml
    02-feature.yml
    03-task.yml
    04-docs.yml
    05-question.yml
    config.yml
  pull_request_template.md
  VULNERABILITY_REPORT.yml
CONTRIBUTING.md
SECURITY.md
SUPPORT.md
README.md
labels.json
scripts/apply_labels.py
```

## 部署步骤

- 安装 Python 3.9+、Git 和 GitHub CLI，使用 `gh auth login` 登录。在 `PatchRice` 下使用名为 `.github` 的 Public 仓库；已有仓库先盘点，不能重建或擅自改变可见性。公共默认文件仓库必须公开。
- 将本目录的内容准备到独立工作目录或工作分支，保留 `.github/` 隐藏目录。此时先审查变更，暂不发布到默认分支。按下文检查同类配置的不同路径以及已有模板，避免新增文件遮蔽现有配置。
- 盘点全部可访问、未归档且适合同步的组织仓库，先决定旧标签是否暂时并存。默认保留旧名称与历史关联；统一改名属于独立迁移。
- 从本目录运行预演，查看各标签的新增、修改、无需修改和阻塞情况。`--dry-run` 会读取 GitHub，要求有效登录；不写入远端。仅使用 `labels.json` 作为同步来源，不使用整仓标签复制。

  ```bash
  python3 scripts/apply_labels.py PatchRice/.github PatchRice/clininote --dry-run --overwrite --report /tmp/patchrice-label-plan.json
  ```

- 审查预演中的颜色与描述变化后，运行正式同步。脚本只创建缺失标签、更新有差异的标准标签，跳过一致项，最后重新读取远端验证。仓库独有标签、旧标签与 Issue 关联均保留。

  ```bash
  python3 scripts/apply_labels.py PatchRice/.github PatchRice/clininote --overwrite --report /tmp/patchrice-label-result.json
  ```

  不带 `--overwrite` 时，仅创建缺失标签；有差异的同名标签会保留并报告为阻塞，退出码为 1。预演会显示实际旧值与目标值；正式执行会重新计算差异，JSON 报告不是锁定的事务或可直接执行的计划。执行过程可能部分成功，可排除错误后重跑，已一致项不会重复写入。报告可能包含私有仓库名，保存在本地，不提交到公共仓库。

- 在公共仓库及目标仓库至少具备五个 `C-*` 与 `S-needs-triage` 后，将已审查的模板变更发布到默认分支；有分支保护时走 PR。无法准备标签的目标仓库应列为例外，报告自动标签可能不完整；如必须保证全部目标生效，应先解决这些例外。
- 在组织 **Settings → Repository → General → Repository labels** 中按 `labels.json` 建立新仓库默认标签。修改默认值只影响以后创建的仓库，不替代已有仓库同步。
- 对需要外部安全报告的公开仓库，由管理员单独启用 **Private vulnerability reporting**。模板文件本身不会开启此功能。尚未配置入口时，按照 `SECURITY.md` 的方式询问安全联系方式。
- 检查无自定义模板的目标仓库 `/issues/new/choose`，确认五个表单可见，并检查 PR 模板与安全策略的实际来源。保留公共仓库已有表单时，入口数可能超过五个；有项目模板覆盖的仓库单独记录。没有实际创建测试 Issue 时，将自动标签记录为“定义和标签存在性已核对，提交行为未实测”。

## 配置生效与冲突检查

同一路径 diff 之外，还需按配置类型盘点 `.github/`、仓库根目录和 `docs/` 下的候选文件。GitHub 对支持这些位置的社区文件按 `.github/` → 根目录 → `docs/` 取用，先查目标项目自己的配置，再考虑公共仓库默认配置。新增根目录 `SECURITY.md` 不会取代公共仓库里已有的 `.github/SECURITY.md`。遇到多个候选文件，应明确保留哪个生效版本，先展示差异；不要仅凭文件提交成功判定部署完成。

Issue 模板还要检查已有 Markdown 模板、表单与 `config.yml`；PR 模板还要检查单模板及 `PULL_REQUEST_TEMPLATE/` 中的多模板配置；漏洞表单检查 `.yml` 和 `.yaml` 两种扩展名。发现冲突时先确定合并方案，保留项目自己的入口。报告分别列出“文件已提交”“默认分支已生效”“被项目配置覆盖”“页面未验证”。

## 跨仓库继承规则

- `PatchRice/.github` 的默认社区文件可用于组织下的公开及私有目标仓库，前提是目标仓库未提供其自己的对应文件。
- **Issue 模板目录是整体覆盖关系**：若目标仓库定义了有效的 `.github/ISSUE_TEMPLATE` 表单或 `config.yml`，便不会从默认仓库继承该目录的其他文件。不要期望子仓库模板与公共模板逐文件合并。
- PR 模板、`SECURITY.md`、`CONTRIBUTING.md` 等按文件类型使用本仓库的默认版本；目标仓库可以提供自己的版本。
- 默认文件不自动复制到子仓库 Git 历史或本地 clone。
- Issue Forms 中 `labels` 指定的标签**必须预先存在于 `PatchRice/.github` 和目标仓库中**，否则不会自动添加。
- 默认的 `config.yml` 禁用普通用户的 Blank issue 入口；拥有写权限的维护者仍可创建空白 Issue。
- 安全漏洞报告表单是单独的 `VULNERABILITY_REPORT.yml`，**不是**一个公开 Issue 模板。

## 标签规范

| 前缀 | 类别 | 示例 | 规则 |
|---|---|---|---|
| `C-*` | Category / 类型 | `C-bug`, `C-enhancement`, `C-maintenance`, `C-docs`, `C-question` | 每条 Issue 仅选一个主类型；表单自动添加 |
| `P-*` | Priority / 处理优先级 | `P-critical`, `P-high`, `P-medium`, `P-low` | 由维护者决定；最多一个；不在提交时自动添加 |
| `S-*` | Status / 当前处理状态 | `S-needs-triage`, `S-needs-info`, `S-ready`, `S-blocked` | 维护者更新；推荐同一时刻只保留一个 |
| `I-*` | Impact / 特殊性质 | `I-regression`, `I-crash`, `I-data-loss`, `I-performance` | 可以多个，不等于优先级 |
| `A-*` | Area / 子系统 | `A-api`, `A-ui`, `A-sync` 等 | **各项目按需创建**，不放进通用标签集合 |
| 无前缀 | 社区/解决状态 | `good first issue`, `help wanted`, `duplicate`, `wontfix` | 保留 GitHub 社区常用名称，利于发现与协作 |

**不要混淆漏洞严重程度和开发优先级**。`P-critical` 用于会阻塞发布、导致大范围严重故障或必须立即处理的情况；安全漏洞优先使用私密报告流程，后续由维护者评估处理优先级。

### P-* 具体判定标准

| 优先级 | 建议依据 | 维护动作 |
|---|---|---|
| `P-critical` | 发布阻塞、广泛严重故障、实际数据丢失等需立即处置的问题 | 尽快明确负责人并优先处理，必要时暂停发布 |
| `P-high` | 核心功能严重受损、影响明显且缺少可行绕过方案 | 纳入近期计划并主动推进 |
| `P-medium` | 明确存在问题或价值，但范围有限、可绕过或无需立即修复 | 正常排期，视人力推进 |
| `P-low` | 低影响、体验细节或短期内不计划主动处理的改进 | 保留跟踪，欢迎贡献 |

优先级还取决于触发概率、受影响用户、版本范围、可用替代方案以及发布阶段。安全漏洞的 CVSS/严重程度与工作优先级不是同一个字段。**此表为 PatchRice 自定规则，并非 Rust 官方标准的逐字复刻。**

### 推荐分诊工作流

- 创建：模板添加 `C-*` 和 `S-needs-triage`。
- 分诊：确认问题可操作性，必要时标注 `I-*`、`A-*`，由维护者按需选一个 `P-*`；可执行的工作转为 `S-ready`，咨询则按答复需要处理，无需强制设置优先级。
- 状态切换时先移除旧的 `S-*`，再设置新状态。信息不足：改为 `S-needs-info`，指出具体需要的资料；补充后返回 `S-ready` 或重新分诊。
- 准备开发：标注 `S-ready`；如果被外部依赖阻塞则用 `S-blocked`。是否已开始可直接看 Assignee 和关联 PR，不强制额外状态标签。
- 关闭：移除尚未结束的 `S-*` 状态，在评论或 PR 中说明结论；可根据情况使用 `duplicate` 或 `wontfix`，并选择恰当的 GitHub 关闭理由。

### 旧标签过渡与独立迁移

默认安装保留 `bug`、`enhancement`、`documentation`，同时建立对应的 `C-*` 标签。脚本会提示旧标签存在，历史 Issue 仍使用旧标签；过渡期可使用 `is:issue label:bug,C-bug` 查找任一缺陷标签，同理处理另外两组，避免只筛选新名称遗漏历史问题。

若决定统一名称，请在新增标准标签前安排独立迁移：确认新名称不存在、检查项目模板与自动化引用，再通过 `gh label edit bug --name C-bug --repo OWNER/REPO` 等命令改名，保留标签关联。然后运行标准标签同步。改名会影响依赖旧名称的筛选与自动化，需同步调整。

如果新旧名称已经同时存在，无法直接重命名合并；应先制定关联迁移方案，再取得单独授权执行。默认安装不迁移 Issue 关联，不删除旧标签。`A-*` 由各项目按需建立。

## 设计约束与扩展

- 表单主要使用语言无关的字段，兼容 Python、Android、Web、C++ 和其他仓库。
- 保持 2–3 个关键必填信息，偶发 Bug 可以提供线索而非稳定复现代码；没有要求强制上传截图或日志。
- 不给新 Issue 预置优先级、处理人、里程碑或 Projects，因为不同仓库的负责团队和发布周期可能不同。
- `P-*` 是维护排程，`I-*` 描述问题性质。用户可以在正文中说明后果，但不让提交者通过表单自选 Critical。
- 若以后要接入跨仓库自动分诊，可再增加 GitHub Actions / Projects 规则。**这些不会随组织的公共模板仓库自动继承到子仓库。**

## 官方参考

- [Default community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)
- [Issue forms syntax](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms)
- [Private vulnerability reporting](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository)
- [Organization default labels](https://docs.github.com/en/organizations/managing-organization-settings/managing-default-labels-for-repositories-in-your-organization)
