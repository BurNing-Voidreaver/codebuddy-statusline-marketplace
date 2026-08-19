# CodeBuddy Statusline Marketplace

> 为 [CodeBuddy Code](https://cnb.cool/codebuddy/codebuddy-code) 提供的状态栏（statusline）插件市场。

本仓库收集「常驻在输入栏底部」的轻量状态栏插件，用于实时展示 token 用量、上下文窗口占用、权限模式等信息。

---

## 目录 / Contents

- [中文说明](#中文说明)
- [English](#english)

---

## 中文说明

### 插件列表

| 插件 | 说明 |
|------|------|
| [`token-statusline`](plugins/token-statusline) | 在输入栏底部常驻显示 token 用量、上下文窗口、权限模式与工作目录 |

### 安装

```bash
# 1. 添加市场
/plugin marketplace add BurNing-Voidreaper/codebuddy-statusline-marketplace

# 2. 安装插件（市场标识为 owner-repo）
/plugin install token-statusline@BurNing-Voidreaper-codebuddy-statusline-marketplace

# 3. 一键完成脚本复制 + settings.json 配置
/token-statusline:setup

# 4. 重新加载插件
/reload-plugins
```

> 说明：受框架限制，插件本身无法自动修改你的 `statusLine` 设置，因此 `setup`
> 命令会把脚本复制到 `~/.codebuddy/statusline-tokens.py` 并写入配置。
> 若你更偏好手动配置，把脚本放到任意路径，并在 `~/.codebuddy/settings.json` 加入：
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

### 字段说明（token-statusline）

状态栏格式示例：

```
~/project (branch)
↑81k ↓25k R2.4M CH97.0%   7.8%/1.0M (auto)
```

| 片段 | 含义 |
|------|------|
| `~/project (branch)` | 当前工作目录（家目录缩写为 `~`）+ git 分支 |
| `↑` | 当前上下文的新鲜（未缓存）输入 token（压缩上下文后会下降） |
| `↓` | 当前上下文输出 token（数值常小于 1000，统一以 `k` 为单位显示，如 `0.9k`） |
| `R` | 缓存读 token（会话累计） |
| `CH` | 缓存命中率 = 缓存读 / (新鲜 + 缓存读 + 缓存写) × 100 |
| `X%` | 当前上下文窗口占用率 |
| `/Y` | 上下文窗口大小 |
| `(mode)` | 权限模式（`default` / `auto` / `plan` …），通过 `Shift+Tab` 切换 |

### 依赖

- Python 3（仅用标准库，无需 `pip install`）
- `git`（用于读取分支名，缺失时自动省略）

### 自定义

- 修改 `MODEL_CONTEXT` 字典可调整各模型的上下文窗口大小（影响 `/Y` 与 `X%`）。
- 输出格式在 `main()` 末尾的 `line = ...` 处，可按需增删字段。

### 许可证

[MIT](LICENSE)

---

## English

### Plugins

| Plugin | Description |
|--------|-------------|
| [`token-statusline`](plugins/token-statusline) | A persistent status line showing token usage, context-window occupancy, permission mode and working directory at the bottom of the input bar |

### Installation

```bash
# 1. Add the marketplace
/plugin marketplace add BurNing-Voidreaper/codebuddy-statusline-marketplace

# 2. Install the plugin (market id is owner-repo)
/plugin install token-statusline@BurNing-Voidreaper-codebuddy-statusline-marketplace

# 3. One-shot script copy + settings.json wiring
/token-statusline:setup

# 4. Reload plugins
/reload-plugins
```

> Note: due to framework limitations the plugin cannot modify your `statusLine`
> setting by itself, so the `setup` command copies the script to
> `~/.codebuddy/statusline-tokens.py` and writes the config for you. For a manual
> setup, place the script anywhere and add this to `~/.codebuddy/settings.json`:
>
> ```json
> {
>   "statusLine": {
>     "type": "command",
>     "command": "python3 /your/path/statusline-tokens.py",
>     "padding": 0
>   }
> }
> ```

### Field reference (token-statusline)

Example output:

```
~/project (branch)
↑81k ↓25k R2.4M CH97.0%   7.8%/1.0M (auto)
```

| Segment | Meaning |
|---------|---------|
| `~/project (branch)` | Current working directory (`~` for home) + git branch |
| `↑` | Fresh (non-cached) input tokens in the current context (drops after compaction) |
| `↓` | Output tokens of the current context (often < 1000; always shown with a `k` unit, e.g. `0.9k`) |
| `R` | Cache-read tokens (session cumulative) |
| `CH` | Cache-hit ratio = cache_read / (fresh + cache_read + cache_write) × 100 |
| `X%` | Current context-window usage percentage |
| `/Y` | Context-window size |
| `(mode)` | Permission mode (`default` / `auto` / `plan` …), toggled with `Shift+Tab` |

### Dependencies

- Python 3 (standard library only, no `pip install` needed)
- `git` (used for the branch name; omitted automatically if unavailable)

### Customization

- Edit the `MODEL_CONTEXT` dict to tune per-model context-window sizes (affects `/Y` and `X%`).
- The output format lives in the `line = ...` assignment at the end of `main()`.

### License

[MIT](LICENSE)
