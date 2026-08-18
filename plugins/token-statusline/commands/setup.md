---
name: setup
description: 安装 token-statusline 状态栏：复制脚本并向 settings.json 写入 statusLine 配置
---

把 token-statusline 的脚本复制到用户目录，并在 `~/.codebuddy/settings.json` 中启用 `statusLine`。请执行以下 bash 步骤：

1. 复制脚本到稳定路径并设为可执行：

```bash
cp "${CODEBUDDY_PLUGIN_ROOT}/statusline-tokens.py" "$HOME/.codebuddy/statusline-tokens.py"
chmod +x "$HOME/.codebuddy/statusline-tokens.py"
```

2. 确保 `~/.codebuddy/settings.json` 含有如下 `statusLine` 字段。用 Edit 工具合并，不要破坏其它配置：

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 $HOME/.codebuddy/statusline-tokens.py",
    "padding": 0
  }
}
```

完成后提示用户：重启或新开会话后，输入栏底部即显示 token 状态栏；可用 `Shift+Tab` 在权限模式间循环，切到 `auto` 即可（状态栏里的 `(mode)` 会实时跟随）。
