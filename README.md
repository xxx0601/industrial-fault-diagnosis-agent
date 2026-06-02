# New Project

独立新项目工作区，与 `D:\cursorproject`（GPU Commerce Agent）**完全分离**。

## 目录说明

```
D:\new-project/
├── .env              # 本地密钥（已 gitignore，勿提交）
├── .env.example      # 环境变量模板（可提交）
├── .gitignore
└── README.md
```

在此目录下开发你的下一个项目；需要 monorepo 时可自行添加 `frontend/`、`backend/` 等。

## 与旧项目隔离

| 项目 | 路径 | GitHub |
|------|------|--------|
| GPU 商城 | `D:\cursorproject` | `gpu-commerce-agent` |
| 本项目 | `D:\new-project` | 待创建新仓库 |

建议本地端口与旧项目错开（例如前端 `3001`、后端 `8001`、Postgres `5433`）。

## 本地开始

1. 在 Cursor 中 **File → Open Folder** 选择 `D:\new-project`
2. 编辑 `.env` 填入所需密钥
3. 在 GitHub 创建**新仓库**后：

```powershell
cd D:\new-project
git remote add origin https://github.com/你的用户名/新仓库名.git
git push -u origin main
```

## License

待定
