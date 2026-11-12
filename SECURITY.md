# Security policy / 安全报告说明

Please report **potentially exploitable security vulnerabilities privately**. Do not disclose exploit instructions, credential leaks, authentication bypasses, sensitive records or unpatched vulnerabilities in public issues or discussions.

请**私密报告尚未修复的安全漏洞**。请勿在公开 Issue 或 Discussion 中发布利用代码、敏感信息或未修复漏洞细节。

## How to report / 报告方式

For a **public repository** with private vulnerability reporting enabled, open the repository's **Security → Advisories → Report a vulnerability** and use the structured form. This feature must be enabled for each repository by its administrator; publishing this policy or form does not enable it automatically.

对于已启用私密漏洞报告的公开仓库，请前往 **Security → Advisories → Report a vulnerability**。该功能需由各仓库管理员启用，提交本文件本身不会自动开启。

If the repository does not offer a private reporting channel, choose the **Question** issue form (or an available support channel) and ask maintainers how to contact them securely, without disclosing the flaw itself. For private repositories, use a trusted private channel available to the collaborators or administrators.

如果仓库未提供私密报告入口，请使用 **Question / 使用与技术咨询** 表单或现有支持渠道，仅询问安全联系方式，**不包含漏洞细节**。私有仓库的内部问题请通过已有的可信私密渠道沟通。

## Information to include / 建议材料

Describe affected versions, the attack prerequisites, impact and a minimal safe proof of concept. Use only synthetic data. Never include passwords, API keys, user information, medical records or production data.

请说明受影响版本、利用条件、影响范围及最小复现步骤。仅使用模拟数据，不附真实密码、Token、个人信息、医疗记录或生产数据。

## Supported versions / 支持版本

Version support varies by repository. Consult that repository's release information and ask the maintainers if the status is unclear. This shared policy does not promise a fixed response time or a particular support window.

支持版本以各仓库发布说明为准，本组织通用模板不承诺固定的响应时间或支持周期。
