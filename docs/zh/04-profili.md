# 配置与被禁标志

🌐 [Italiano](../04-profili.md) · [English](../en/04-profili.md) · **中文**

> ⚠️ 本页为机器翻译草稿，正式发布前需母语者校对。

| 配置 | 作用 | 噪声 | Root |
|---|---|---|---|
| `vivi` | 状态码和页面标题。 | 低 | 否 |
| `tech` | 声明的技术栈和服务器。 | 低 | 否 |
| `percorsi` | 常见路径，以 JSON 输出。 | 中 | 否 |
| `porte-web` | 备用的 Web 端口。 | 中 | 否 |
| `filtrati` | 仅 200、401 和 403。 | 低 | 否 |
| `jsonl` | 状态码、标题、服务器和技术栈，以 JSON 输出。 | 低 | 否 |
| `prudente` | 带线程数、频率和超时限制。 | 低 | 否 |

`httpx-cli profili` 会打印每个配置的具体标志。

## 各配置的作用

**vivi** (`-sc -title -silent`). 状态码和页面标题。 发现阶段之后的常规步骤：哪些目标真正通过 Web 响应？

**tech** (`-td -server -silent`). 声明的技术栈和服务器。 用于了解背后运行的技术栈，然后再选择 nuclei 的模板。

**percorsi** (`-path /,/login,/admin,/.git/HEAD -sc -title -silent -j`). 常见路径，以 JSON 输出。 检查一些敏感路径。可访问的 /.git/HEAD 是严重问题。

**porte-web** (`-p 80,443,8080,8443,3000,5000 -sc -title -silent`). 备用的 Web 端口。 用于不在 80 和 443 端口上的 Web 服务器。

**filtrati** (`-mc 200,401,403 -title -silent`). 仅 200、401 和 403。 只保留确实存在且值得进一步查看的内容。

**jsonl** (`-sc -title -server -td -j`). 状态码、标题、服务器和技术栈，以 JSON 输出。 用于使用其他工具处理结果。

**prudente** (`-sc -title -t 25 -rl 50 -timeout 10 -retries 1 -silent`). 带线程数、频率和超时限制。 在客户基础设施上默认使用的配置。

## 手动传入标志

`--` 之后写的所有内容都会追加在配置标志之后传给 httpx，前提是不在被禁清单中。比对时不区分大小写，`-flag valore` 和 `-flag=valore` 两种写法都能识别，一个或两个短横线均可。

```sh
httpx-cli lancia vivi https://app.example.org --scope scope.toml -- -timeout 5
```

## 被禁标志清单

| 标志 | 原因 |
|---|---|
| `-u`, `-target`, `-l`, `-list` | 目标来自经过作用域校验的文件 |
| `-o`, `-output` | 输出由 httpx-cli 管理 |
| `-fr`, `-follow-redirects` | 跟随重定向可能跳转到作用域之外的主机 |
| `-pa`, `-probe-all-ips`, `-tls-probe`, `-csp-probe` | 会探测临时发现的主机（证书、CSP、其他 IP）：它们不在作用域内 |
| `-rr`, `-request` | 一个已保存的请求可能指向另一个主机 |
| `-im`, `-input-mode` | 导入的规格文件可能包含作用域之外的主机 |
| `-jsc`, `-javascript-code` | 在浏览器中对目标页面执行 JavaScript |
| `-up`, `-update` | 程序更新应单独进行，而不是在一次授权任务中进行 |

## 过滤器做不到的事

它不是沙箱。想绕过它并不难，比如直接调用 `httpx`。它的作用是拦住失误和坏习惯，而不是拦住一个已经能访问你终端的恶意人员。如果某项与客户约定好的活动需要用到被禁标志，请直接使用 httpx，并在项目记录中注明这一选择。
