# Profiles and forbidden flags

🌐 [Italiano](../04-profili.md) · **English** · [中文](../zh/04-profili.md)

| Profile | What it does | Noise | Root |
|---|---|---|---|
| `vivi` | Status code and page title. | low | no |
| `tech` | Declared technologies and server. | low | no |
| `percorsi` | Common paths, in JSON. | medium | no |
| `porte-web` | Alternative web ports. | medium | no |
| `filtrati` | Only 200, 401 and 403. | low | no |
| `jsonl` | Status, title, server and technologies in JSON. | low | no |
| `prudente` | With thread, rate and timeout limits. | low | no |

`httpx-cli profili` prints the exact flags of each one.

## What each profile does

**vivi** (`-sc -title -silent`). Status code and page title. The normal step after discovery: what actually responds over the web?

**tech** (`-td -server -silent`). Declared technologies and server. To see what stack runs behind it, before picking nuclei templates.

**percorsi** (`-path /,/login,/admin,/.git/HEAD -sc -title -silent -j`). Common paths, in JSON. Checks a few sensitive paths. A reachable /.git/HEAD is a serious problem.

**porte-web** (`-p 80,443,8080,8443,3000,5000 -sc -title -silent`). Alternative web ports. For web servers that don't sit on 80 and 443.

**filtrati** (`-mc 200,401,403 -title -silent`). Only 200, 401 and 403. To keep only what exists and deserves a second look.

**jsonl** (`-sc -title -server -td -j`). Status, title, server and technologies in JSON. To process the result with other tools.

**prudente** (`-sc -title -t 25 -rl 50 -timeout 10 -retries 1 -silent`). With thread, rate and timeout limits. The default profile on client infrastructure.

## Passing flags by hand

Everything you write after `--` goes to httpx, after the profile flags, provided it is not on the forbidden list. The check is case-insensitive and accepts both `-flag valore` and `-flag=valore`, with one or two dashes.

```sh
httpx-cli lancia vivi https://app.example.org --scope scope.toml -- -timeout 5
```

## Forbidden list

| Flag | Why |
|---|---|
| `-u`, `-target`, `-l`, `-list` | targets come from the file validated against the scope |
| `-o`, `-output` | output is handled by httpx-cli |
| `-fr`, `-follow-redirects` | following redirects can lead to out-of-scope hosts |
| `-pa`, `-probe-all-ips`, `-tls-probe`, `-csp-probe` | probes hosts discovered on the fly (certificates, CSP, other IPs): they're not in scope |
| `-rr`, `-request` | a saved request can point to a different host |
| `-im`, `-input-mode` | an imported spec can contain out-of-scope hosts |
| `-jsc`, `-javascript-code` | runs JavaScript in the browser on target pages |
| `-up`, `-update` | updating the program is done separately, not inside an authorized run |

## What the filter does not do

It is not a sandbox. If you want to get around it you can, for example by calling `httpx` directly. It is there to stop mistakes and bad habits, not an attacker who already has access to your terminal. If you need a forbidden flag for an activity agreed with the client, use httpx directly and record the decision in the engagement.
