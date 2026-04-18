<div align="center">

# 盘古造物.meta-skill

<br>

> **不止于蒸馏万物，更要超越万物** <br>

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-orange.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![Skills](https://img.shields.io/badge/skills.sh-Compatible-green)](https://skills.sh)

<br>

**盘古（创世大神），开天辟地后觉天地孤寂，** <br>
**用泥沙黄泥捏人，吹气后泥人成活，** <br>
**结果：泥人主宰世界。**

<br>

受到 [同事.skill](https://github.com/titanwings/colleague-skill) 和 [女娲.skill](https://github.com/titanwings/colleague-skill) 启发，蒸馏名人、故人、精英等，为何止步于蒸馏 ？<br>
 **盘古造物.meta-skill** ，不止于蒸馏万物，更要**超越万物** 。

---

**快捷导航**

[使用演示](#使用演示) | [快速安装](#快速安装) | [经典案例](#经典案例) | [架构原理](#架构原理) | [仓库结构](#仓库结构) | [关于我](#关于我)

<br>

**多国语言**

[English](README_EN.md) · [日本語](README_JA.md) · [한국어](README_KO.md) · [Español](README_ES.md)

<br>


</div>

---

## 使用演示


### 超越 ：进化思维框架(推荐)

超越长期主义，不是更强的话语，是真的补全了缺陷：

```
用户      ❯ 超越「长期主义」

盘古造物  ❯ 【Phase 1 → 2 执行中】
            ✓ 蒸馏完成
            ✓ 超越路径分析完成（路径A+路径C）

            【蒸馏版局限识别】
            - 忽视反脆弱性：没有考虑「黑天鹅」风险
            - 忽视现金流：长期主义需要短期生存支撑
            - 不适用于快速变化领域

            【进化版产出：《长期主义-Plus》】

            继承（蒸馏版精华）：
            ✓ 复利思维 ✓ 长期焦点 ✓ 坚持不懈

            增强（超越版独有）：
            ✓ 可选择性（路径A）：长期押注+保持退出权
            ✓ 三层决策体系（路径B）：长期/中期/短期分层
            ✓ 短期验证机制（路径C）：长期决策有中期checkpoint
```

### 蒸馏：提取思维框架

蒸馏长期主义，提取的不只是"坚持"二字，而是可运行的认知框架：

```
用户      ❯ 蒸馏「长期主义」

盘古造物  ❯ 【Phase 1 执行中】
            ✓ 六路采集完成（著作/访谈/批评/决策/时间线/同类）
            ✓ 心智模型三重验证通过
            ✓ 蒸馏完成

            产出：《长期主义·思维框架》

            核心心智模型：
            ① 复利思维：坚持做时间的朋友，享受指数增长
            ② 长期焦点：忽略短期波动，聚焦长期价值
            ③ 坚持不懈：困难时期不放弃

            表达DNA：
            - 确定性高：「显然」「必须」「毫无疑问」
            - 少用转折，少用「但是」
            - 口癖：「时间的朋友」「慢慢来比较快」
```

---

## 快速安装

### 方式一：技术人员（命令行）

直接用 npx 安装：

```bash
npx skills add wukongnotnull/pangu-creator
```

安装完成后，在 Agent 的对话框中说：

```markdown
> 超越「长期主义」
> 蒸馏「长期主义」
```

### 方式二：文科生（对话式）

不需要记命令，直接把下面这段话复制给 Agent：

```
帮我安装这个 skill：https://github.com/wukongnotnull/pangu-creator
```

安装完成后，用自然语言告诉它你想要什么：

```markdown
> 帮我超越：我的决策框架
> 帮我蒸馏：长期主义
> 我想做一个巴菲特的思维框架
```

## 经典案例

盘古造物已蒸馏了13位人物，按领域分组，便于按需查找：

### 💰 投资/商业

| 人物 | 超越方向 | 一键安装(超越版) |
|------|---------|------------------|
| **纳瓦尔** | 财富/杠杆/人生哲学 | `npx skills add wukongnotnull/pangu-naval` |
| **芒格** | 投资/多元思维/逆向思考 | `npx skills add wukongnotnull/pangu-munger` |
| **张雪峰** | 教育/职业规划/阶层流动 | `npx skills add wukongnotnull/pangu-zhangxuefeng` |

### 🚀 创业/产品

| 人物 | 超越方向 | 一键安装(超越版) |
|------|---------|------------------|
| **Paul Graham** | 创业/写作/产品/人生哲学 | `npx skills add wukongnotnull/pangu-paul-graham` |
| **张一鸣** | 产品/组织/全球化/人才 | `npx skills add wukongnotnull/pangu-zhang-yiming` |
| **乔布斯** | 产品/设计/战略 | `npx skills add wukongnotnull/pangu-steve-jobs` |
| **马斯克** | 工程/成本/第一性原理 | `npx skills add wukongnotnull/pangu-elon-musk` |

### 🤖 AI/技术

| 人物 | 超越方向 | 一键安装(超越版) |
|------|---------|------------------|
| **Karpathy** | AI/工程/教育/开源 | `npx skills add wukongnotnull/pangu-karpathy` |
| **Ilya Sutskever** | AI安全/scaling/研究品味 | `npx skills add wukongnotnull/pangu-ilya-sutskever` |

### 🎬 内容创作

| 人物 | 超越方向 | 一键安装(超越版) |
|------|---------|------------------|
| **MrBeast** | 内容创造/YouTube方法论 | `npx skills add wukongnotnull/pangu-mrbeast` |

### 🎯 传播/权力

| 人物 | 超越方向 | 一键安装(超越版) |
|------|---------|------------------|
| 🔥**特朗普** | 谈判/权力/传播/行为预判 | `npx skills add wukongnotnull/pangu-trump` |

### 🧠 思维/学习

| 人物 | 超越方向 | 一键安装(超越版) |
|------|---------|------------------|
| **费曼** | 学习/教学/科学思维 | `npx skills add wukongnotnull/pangu-feynman` |
| **塔勒布** | 风险/反脆弱/不确定性 | `npx skills add wukongnotnull/pangu-taleb` |

---

## 架构原理

### 双重能力

| 能力 | 定义 | 产出 |
|------|------|------|
| **蒸馏万物** | 从任意对象提取可运行的思维框架 | 人物类Skill / 内容类Skill / 思想类Skill等 |
| **超越万物** | 在蒸馏基础上诊断缺陷、引入外部优势、生成增强版 | 比原对象更强的思维框架 |

### 执行流程

#### Phase 1：蒸馏（Distillation）

**Step 1：信息采集**

3个Agent并行采集（主从模式）：

| Agent | 职责 | 输出文件 |
|-------|------|---------|
| Master（素材收集师） | 核心著作 + 时间线 | `01-writings.md`, `06-timeline.md` |
| Analyst A（分析师_A） | 播客访谈 + 表达DNA | `02-conversations.md`, `03-expression-dna.md` |
| Analyst B（分析师_B） | 批评评价 + 重大决策 + 同类 | `04-limitations.md`, `05-decisions.md`, `07-similar-objects.md` |

**Step 2：框架提炼**

- **心智模型三重验证**：
  - 验证1：跨域复现（≥2个不同领域）
  - 验证2：有生成力（能推断对新问题的立场）
  - 验证3：有排他性（不是所有聪明人都这样想）
  - 通过3重 → 心智模型；通过1-2重 → 决策启发式

- **表达DNA量化**：句式指纹、风格标签、禁忌词和口癖

- **矛盾处理**：时间性矛盾→记录演化轨迹；领域性矛盾→分领域记录；本质性张力→明确为核心张力

**Step 3：Skill构建**

3-7个心智模型 + 5-10条决策启发式 + 表达DNA + 价值观与反模式 + 诚实边界

#### Phase 2：超越（Transcendence）

在蒸馏基础上，4条超越路径系统性增强：

| 路径 | 操作 | 超越策略 |
|------|------|---------|
| **路径A：向自身学习** | 识别核心局限、自我矛盾、时代局限 | 补全碎片、强化边界、更新假设 |
| **路径B：向同类学习** | 找到3-5个同类优秀对象 | 优势叠加、盲区互补、差异化创新 |
| **路径C：向对手学习** | 收集最强批评者观点、分析竞争对手 | 吸收反击、超越对立、整合替代 |
| **路径D：向历史学习** | 梳理过往失败案例、分析历史相似案例 | 避免重蹈覆辙、加速演化、预测趋势 |

### 质量验证

- **蒸馏版验证**：拿3个此人公开回答过的问题测试，方向一致才通过
- **超越版验证**：用1个他没讨论过的问题测试，Skill应表现适度不确定而非斩钉截铁

---

## 仓库结构

```
pangu-creator/
├── SKILL.md                           # 盘古造物本体
├── references/
│   ├── quality-checklist.md            # 质量自检清单
│   ├── special-scenarios.md           # 特殊场景处理
│   ├── examples/                       # 蒸馏/超越示例
│   │   ├── distillation-example.md    # 蒸馏示例（长期主义）
│   │   └── transcendence-example.md   # 超越示例（长期主义）
│   └── templates/                       # Skill模板
│       ├── README.md                  # 模板索引
│       ├── person-skill-template.md   # D1人物类蒸馏模板
│       ├── content-skill-template.md  # D2内容类蒸馏模板
│       ├── idea-skill-template.md     # D3思想类蒸馏模板
│       ├── phenomenon-skill-template.md # D4现象类蒸馏模板
│       ├── person-plus-template.md    # D1人物类超越模板
│       ├── content-plus-template.md   # D2内容类超越模板
│       ├── idea-plus-template.md      # D3思想类超越模板
│       └── phenomenon-plus-template.md # D4现象类超越模板
└── scripts/                            # Python搜索模块
    ├── search/                         # 搜索管道
    ├── crawl/                          # 网页爬取
    └── transcribe/                     # 音视频转录
```

---

## 关于我

**悟空非空也** — AI之道创始人，独立开发者，Up主。

| 平台         | 链接                                                                         |
| ------------ | ---------------------------------------------------------------------------- |
| 🌐  官网      | [AI之道官网](https://waytoai.cn)                                                |
| 𝕏  Twitter   | [悟空非空也](https://x.com/wukongnotnull)                                   |
| 📺  B站       | [悟空非空也](https://space.bilibili.com/456634391)                              |
| ▶️  YouTube   | [悟空非空也](https://www.youtube.com/@wukongnotnull)                        |
| 📕  小红书    | [悟空非空也](https://www.xiaohongshu.com/user/profile/5ca89c2f000000001100952b) |
| 💬  公众号    | 微信搜「悟空非空也」或扫码关注 ↓                                            |

<img src="./images/wechat-qrcode.jpg" alt="公众号二维码" width="360">

---

<div align="center">

Apache-2.0 license © [悟空非空也](https://github.com/wukongnotnull)

</div>
