# token-statusline

一个 CodeBuddy Code 状态栏（statusline）插件：在**输入栏底部常驻**显示 token 用量、上下文窗口占用、权限模式与工作目录，格式类似：

```
~/project (branch)
↑81k ↓25k R2.4M CH97.0%   7.8%/1.0M (auto)
```

字段含义：

| 片段 | 含义 |
|------|------|
| `~/project (branch)` | 当前工作目录（家目录缩写为 `~`）+ git 分支 |
| `↑` | 当前上下文的新鲜（未缓存）输入 token（压缩上下文后会下降） |
| `↓` | 当前上下文输出 token |
| `R` | 缓存读 token（会话累计） |
| `CH` | 缓存命中率 = 缓存读 / (新鲜 + 缓存读 + 缓存写) × 100 |
| `X%` | 当前上下文窗口占用率（来自 payload 的 `used_percentage`，即最近一次请求新增 token / 窗口预算） |
| `/Y` | 上下文窗口大小（优先用 payload 的 `context_window_size`，如 hy3 实际为 192k；未提供时回退 `MODEL_CONTEXT`，默认 1.0M） |
| `(mode)` | 权限模式（`default` / `auto` / `plan` …），通过 `Shift+Tab` 切换，状态栏实时跟随 |

## 安装

```bash
# 1. 添加市场
/plugin marketplace add BurNing-Voidreaver/codebuddy-statusline-marketplace

# 2. 安装插件（市场标识为 owner-repo）
/plugin install token-statusline@BurNing-Voidreaver-codebuddy-statusline-marketplace

# 3. 一键完成脚本复制 + settings.json 配置
/token-statusline:setup

# 4. 重新加载插件
/reload-plugins
```

> 说明：框架限制下，插件本身无法自动修改用户的 `statusLine` 设置，因此第 3 步的
> `setup` 命令会把脚本复制到 `~/.codebuddy/statusline-tokens.py` 并写入配置。
> 如果你更喜欢手动配置，只需把该脚本放到任意路径，并在
> `~/.codebuddy/settings.json` 加入：
>
> ```json
> {
>   "statusLine": {
>     "type": "command",
>     "command": "python3 /你的路径/statusline-tokens.py",
>     "padding": 0
>   }
> }
> ```

## 依赖

- Python 3（脚本用标准库，无需 pip 安装第三方包）
- `jq` / `git` 不需要（git 分支通过 `git` 命令获取，缺失时自动省略）

## 自定义

- 修改 `MODEL_CONTEXT` 字典可调整各模型的上下文窗口大小（影响 `/Y` 与 `X%`）。
- 输出格式在 `main()` 末尾的 `line = ...` 处，可按需增删字段。
