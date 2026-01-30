# CleverGit - Python Git 客户端

一个高级 Python Git 客户端工具，提供更友好、更高层次的 Git 操作封装。

## 项目特点

- 🎯 **高层语义** - 用 `repo.commit_all()` 代替复杂的 Git 命令
- 🔧 **模块化设计** - 清晰的架构，便于扩展和维护  
- 🚀 **CLI 优先** - 强大的命令行界面，支持日常 Git 操作
- 🤖 **AI 友好** - 代码结构适合 Copilot 辅助开发

## 快速开始

### 安装依赖

```bash
cd /Users/zhenyutao/Downloads/HandyApp/CleverGit
pip install -e .
```

### 基础使用

```bash
# 查看仓库状态
sg status

# 提交所有更改
sg commit all -m "feat: add new feature"

# 查看提交历史
sg log --oneline

# 分支管理
sg branch list
sg branch new feature/auth
sg branch switch main
```

## 项目结构

```
clevergit/
├── core/          # 核心 Git 逻辑
├── git/           # Git 适配层
├── models/        # 数据模型
├── cli/           # CLI 命令
├── utils/         # 工具函数
└── ui/            # GUI/TUI（预留）
```

## Python API

```python
from clevergit import Repo

# 打开仓库
repo = Repo.open(".")

# 查看状态
status = repo.status()
print(f"Modified files: {len(status.modified)}")

# 提交更改
repo.commit_all("fix: resolve issue")

# 分支操作
repo.create_branch("feature/new")
repo.checkout("feature/new")
```

## 开发

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black clevergit/
ruff check clevergit/
```

## 功能特性

✅ 已规划：
- 仓库管理（初始化、打开）
- 状态查看
- 提交操作
- 分支管理
- 历史记录
- 远程操作

🚧 待实现：
- GUI 界面
- AI 辅助提交信息生成
- 冲突解决向导
- Git Flow 支持

## 设计理念

> 用 Python 封装 Git 的"意图层"，让 Git 像对象一样被使用，而不是像咒语一样被记忆。

详见完整的 [项目说明文档](README.MD)。

## License

MIT License
