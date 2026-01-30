# 项目说明文档（CleverGit - Git 客户端，Python 实现）

## 1. 项目背景与目标

本项目旨在使用 **Python** 开发一个高级 Git 客户端工具 CleverGit，重点功能：

* 提供 **更友好、更高层次** 的 Git 操作封装
* 降低日常 Git 使用门槛（尤其是复杂命令）
* 支持 **CLI 优先，GUI 可扩展** 的架构设计
* 代码结构清晰，方便后续使用 **GitHub Copilot / AI** 辅助完善

项目目标用户：

* 熟悉 Git 基本概念，但不想频繁记命令的开发者
* 希望在脚本 / 工具链中以 Python 方式操作 Git 的用户

---

## 2. 设计原则

1. **高层语义，而非命令拼接**
   例如：

   * `repo.commit_all("fix login bug")`
   * 而不是 `git commit -am "..."`

2. **可读性优先**
   类名、方法名尽量表达「用户意图」而不是 Git 细节

3. **模块化 & 可扩展**

   * CLI / GUI / API 解耦
   * 后期可加 TUI / Web UI

4. **失败可解释**

   * 尽量将 Git 错误转换为「人类可理解」的异常信息

---

## 3. 技术选型

* Python >= 3.10
* Git 调用方式：

  * 优先：`GitPython`
  * 兜底：`subprocess`（处理 GitPython 不支持的场景）
* CLI 框架：

  * `typer`（推荐，类型友好，适合 Copilot）
* GUI（后期）：

  * `PySide6` 或 `Tkinter`

---

## 4. 核心功能规划

### 4.1 仓库管理

* 打开 / 初始化仓库
* 检测仓库状态
* 当前分支、HEAD 状态

```text
✔ 是否是 Git 仓库
✔ 是否存在未提交修改
✔ 是否落后 / 超前远程分支
```

---

### 4.2 状态视图（Status）

* 已修改（modified）
* 未跟踪（untracked）
* 已暂存（staged）
* 冲突文件（conflicted）

支持：

* 按文件类型分组
* 输出为结构化对象，方便 UI 使用

---

### 4.3 提交（Commit）

* 提交所有变更
* 选择性提交（指定文件）
* 自动生成 commit message（可选）
* commit 前检查（lint / test 钩子）

---

### 4.4 分支管理

* 列出分支（本地 / 远程）
* 创建 / 删除 / 重命名分支
* 切换分支
* 显示分支关系（简单 DAG）

---

### 4.5 合并 & Rebase（高层封装）

* 安全合并（检测冲突）
* Rebase 向导式流程（一步一步）
* 冲突文件列表 + 提示

---

### 4.6 远程仓库操作

* fetch / pull / push
* 显示即将 push / pull 的提交
* force push 风险提示

---

### 4.7 历史记录（Log）

* 简洁日志视图（类似 `git log --oneline --graph`）
* 按作者 / 时间 / 分支过滤
* 单条 commit 详情

---

## 5. 项目文件结构（建议）

```text
clevergit_py/
├── README.md
├── pyproject.toml
├── clevergit/
│   ├── __init__.py
│   ├── core/                  # 核心 Git 逻辑
│   │   ├── repo.py             # 仓库对象（核心入口）
│   │   ├── status.py           # 状态分析
│   │   ├── commit.py           # 提交相关逻辑
│   │   ├── branch.py           # 分支管理
│   │   ├── merge.py            # merge / rebase
│   │   ├── remote.py           # fetch / pull / push
│   │   └── log.py              # 历史记录
│   │
│   ├── git/                    # Git 适配层
│   │   ├── client.py           # GitPython / subprocess 封装
│   │   └── errors.py           # Git 错误 → 业务异常
│   │
│   ├── cli/                    # CLI 层
│   │   ├── app.py              # Typer 入口
│   │   ├── repo_cmd.py
│   │   ├── commit_cmd.py
│   │   └── branch_cmd.py
│   │
│   ├── ui/                     # GUI / TUI（预留）
│   │   └── __init__.py
│   │
│   ├── models/                 # 领域模型（DTO）
│   │   ├── file_status.py
│   │   ├── commit_info.py
│   │   └── branch_info.py
│   │
│   └── utils/
│       ├── formatter.py        # 输出格式化
│       └── helpers.py
│
└── tests/
    ├── test_repo.py
    ├── test_status.py
    └── test_commit.py
```

---

## 6. 核心对象设计示例

### Repo（核心入口）

```python
repo = Repo.open(".")

repo.status()
repo.commit_all("fix: login bug")
repo.create_branch("feature/auth")
repo.checkout("feature/auth")
```

设计目标：

* **一个 Repo 对象 = 一个 Git 仓库**
* 绝大多数功能从这里开始

---

## 7. CLI 设计示例

```bash
sg status
sg commit -m "fix bug"
sg branch new feature/auth
sg branch switch main
sg log --oneline
```

CLI 原则：

* 命令短
* 不要求用户理解 Git 细节参数

---

## 8. 错误处理策略

* Git 原始错误 → 自定义异常
* CLI 层捕获异常 → 用户友好提示

示例：

```text
❌ 当前分支存在未提交修改，无法切换分支
建议：
- 提交修改
- 或使用 sg stash
```

---

## 9. 与 Copilot 协作建议

* 每个模块：

  * 先写 **清晰的 docstring**
  * 明确输入 / 输出类型
* 拆分小函数，避免“巨型方法”
* 在 TODO 中明确业务语义，而不是技术细节

---

## 10. 后续可扩展方向

* GUI（图形界面）
* AI 辅助：

  * 自动生成 commit message
  * 冲突解决建议
* 插件系统（hooks）
* Git Flow / Trunk Based 流程支持

---

## 11. 项目一句话总结

> 用 Python 封装 Git 的“意图层”，让 Git 像对象一样被使用，而不是像咒语一样被记忆。
