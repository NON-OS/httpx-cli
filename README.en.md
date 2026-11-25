# httpx-cli

🌐 [Italiano](README.md) · **English** · [中文](README.zh.md)

[![ci](https://github.com/NON-OS/httpx-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/NON-OS/httpx-cli/actions/workflows/ci.yml)
![License MIT](https://img.shields.io/badge/License-MIT-yellow)
![python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![Kali · Parrot · Linux](https://img.shields.io/badge/Kali%20%C2%B7%20Parrot%20%C2%B7%20Linux-primary-1793d1)
![httpx](https://img.shields.io/badge/wrapper%20for-httpx-green)
![dependencies 0](https://img.shields.io/badge/dependencies-0-lightgrey)

```
  ┌─ scope ─┐   ┌─ dry-run ─┐   ┌─ confirm ─┐   ┌─ httpx ─┐   ┌─ audit ─┐   ┌─ report ─┐
  │ check   │ → │ show      │ → │ ticket    │ → │ runs    │ → │ chain   │ → │ summary  │
  └─────────┘   └───────────┘   └───────────┘   └─────────┘   └─────────┘   └──────────┘
```

HTTP probes with a validated scope, dry-run by default and a hash-chained audit. Authorized targets only.

> **Only systems you own or have written authorization for.** Read [DISCLAIMER.md](DISCLAIMER.md) before you launch anything.

## What it is

`httpx-cli` is a thin orchestrator around ProjectDiscovery's httpx (the Go tool, not the Python library of the same name). It does not replace it. It checks that the host of every URL is in scope, does not follow redirects to other hosts, and logs every run.

By default httpx does not follow redirects, but `-fr` does, and it is a common habit: a site in scope that redirects to a third-party service takes you outside the perimeter without you noticing. Here `-fr` is forbidden. The URLs are then parsed carefully: `http://10.0.0.5@evil.example` looks like an internal address but is an external host with credentials attached, and it is rejected.

## In action

![httpx-cli in guided mode on Kali Linux](docs/img/guida-kali.en.png)

*Guided mode (`httpx-cli guida`) running on Kali Linux: logo, profile selection, scope validation, command preview. Real screenshot.*

```console
$ httpx-cli --lang en lancia vivi https://app.example.org --scope scope.toml
Engagement: ACME-2026 (ACME-2026-014)
Profile   : vivi - Status code and page title. [noise low]
  ok  https://app.example.org  (host app.example.org: matches app.example.org)
Command   : httpx -sc -title -silent -l out/esempio/target.txt -o out/esempio/risultati.txt
Activity  : it sends HTTP requests to the targets: active, visible in application logs.

Dry-run: nothing was run. Add --esegui to actually run it.
```

With an out-of-scope target, even among valid ones, nothing runs:

```console
$ httpx-cli --lang en lancia vivi https://app.example.org https://evil.example --scope scope.toml
httpx-cli: targets out of scope, running nothing:
  https://evil.example: host evil.example: hostname not among the included ones
$ echo $?
3
```

The `lancia` command never runs without `--esegui`. What you see above is a preview.

The output follows the language you pick: `--lang it|en|zh` or the `NONOS_LANG` variable (handy for setting it system-wide). It always starts in Italian.

## What it does

| | |
|---|---|
| Scope | Domain, host or URL (`url` mode), with exclusions and validity dates. When in doubt, it refuses. |
| Dry-run | By default nothing runs. `--esegui` asks for confirmation. |
| Profiles | 7, each marked with its noise level and when to use it. |
| Flag filter | Flags that bypass the scope or seize control of the output are blocked. |
| List filter | `filtra` reads a list from stdin and lets through only what is in scope. |
| Signed scope | The client signs the scope with their SSH key. If the file changes after signing, nothing runs. |
| Audit | Hash-chained log. Scope hash and signer included, sensitive values masked. |
| Report | Summary of results as text, Markdown or JSON. |
| Diff | What changed between two runs, with an exit code for CI. |
| Dependencies | None: just the Python standard library. |

## Platform

Built for **Kali**, **Parrot** and Linux in general: that is where these tools live and where `httpx-cli` gets used. It also runs on macOS. Windows is untested, and there some privilege checks (`os.geteuid`) do not apply.

## Installation

You need Python 3.11 or newer and httpx on your `PATH`. Kali/Debian: sudo apt install httpx-toolkit (on Kali the package is renamed to avoid clashing with Python's httpx; the binary is called httpx-toolkit and this wrapper finds it on its own). Anywhere with Go: go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest. Note: there is also a Python 'httpx' (pip), which is a different program.

```sh
git clone git@github.com:NON-OS/httpx-cli.git
cd httpx-cli
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
httpx-cli doctor
```

## First use

### The simplest way: guided mode

`httpx-cli guida` asks you one question at a time — scope, profile, target — shows the command preview, and launches nothing without your final confirmation. It is the recommended way to start:

```sh
httpx-cli guida
```

### Or by command

```sh
httpx-cli init scope.toml          # crea il modello
$EDITOR scope.toml               # compilalo con il cliente
httpx-cli verifica https://app.example.org --scope scope.toml
httpx-cli lancia vivi https://app.example.org --scope scope.toml            # dry-run
httpx-cli lancia vivi https://app.example.org --scope scope.toml --esegui   # parte davvero
```

In a terminal, `--esegui` asks you to type the engagement ticket. In a script, use `--conferma`. Other httpx flags go after `--`, unless they are among the forbidden ones ([docs/04-profili.md](docs/en/04-profili.md)).

A full flow:

```sh
naabu-cli lancia web 192.0.2.10 --scope scope.toml --esegui
httpx-cli lancia vivi https://app.example.org --scope scope.toml --esegui
```

## Commands

| Command | What it does |
|---|---|
| `guida` | step-by-step interactive mode: scope → profile → target → confirmation |
| `lancia <profilo> <target...>` | validates and builds (or runs) httpx. With `-` it reads targets from stdin |
| `filtra` | reads targets from stdin and prints only those in scope |
| `verifica <target...>` | tells you whether the targets are in scope, without launching |
| `scope-firma <file>` / `scope-verifica <file>` | signs and checks the scope with an SSH key |
| `rapporto <file_or_dir>` | summary of results: live web hosts |
| `confronta <old> <new>` | differences between two runs |
| `profili` | lists the profiles with their exact flags |
| `audit [file]` | verifies the log's hash chain |
| `init [file]` | creates a scope file to fill in |
| `doctor` | checks httpx, version, privileges |

## Profiles

| Profile | What it does | Noise | Root |
|---|---|---|---|
| `vivi` | Status code and page title. | low | no |
| `tech` | Declared technologies and server. | low | no |
| `percorsi` | Common paths, in JSON. | medium | no |
| `porte-web` | Alternative web ports. | medium | no |
| `filtrati` | Only 200, 401 and 403. | low | no |
| `jsonl` | Status, title, server and technologies in JSON. | low | no |
| `prudente` | With thread, rate and timeout limits. | low | no |

![httpx-cli doctor and profiles on Kali Linux](docs/img/info-kali.en.png)

*`httpx-cli doctor` (finds the real httpx binary in `/usr/bin/`) and the profile list, on Kali Linux.*

## Exit codes

| Code | Meaning |
|---|---|
| 0 | all good |
| 1 | `confronta --exit-code` found differences |
| 2 | wrong arguments or a forbidden flag |
| 3 | at least one target out of scope |
| 4 | scope unreadable, malformed or expired |
| 5 | httpx missing |
| 6 | run without confirmation, or a profile that needs root without sudo |
| 7 | httpx exited with an error, or the audit chain is broken |

## The tool chain

This repository is one of eight, designed to work together. Each one checks the scope on its own.

```mermaid
flowchart LR
    subfinder[subfinder-cli]
    dnsx[dnsx-cli]
    subfinder --> dnsx
    naabu[naabu-cli]
    dnsx --> naabu
    httpx[httpx-cli]
    naabu --> httpx
    katana[katana-cli]
    httpx --> katana
    ffuf[ffuf-cli]
    katana --> ffuf
    nuclei[nuclei-cli]
    ffuf --> nuclei
    style httpx stroke-width:3px
```

- [subfinder-cli](https://github.com/NON-OS/subfinder-cli): subdomain enumeration
- [dnsx-cli](https://github.com/NON-OS/dnsx-cli): dns resolution
- [naabu-cli](https://github.com/NON-OS/naabu-cli): port scanning
- [katana-cli](https://github.com/NON-OS/katana-cli): web crawling
- [ffuf-cli](https://github.com/NON-OS/ffuf-cli): path fuzzing
- [nuclei-cli](https://github.com/NON-OS/nuclei-cli): vulnerability scanning
- [nmap-cli](https://github.com/NON-OS/nmap-cli): port and service scanning with nmap

## Documentation

1. [Introduction and philosophy](docs/en/01-introduzione.md)
2. [Authorization: what you need before touching a target](docs/en/02-autorizzazione.md)
3. [The scope file](docs/en/03-scope.md)
4. [Profiles and forbidden flags](docs/en/04-profili.md)
5. [The audit log](docs/en/05-audit.md)
6. [Architecture](docs/en/06-architettura.md)
7. [Where to try it safely](docs/en/07-lab.md)
8. [Reports and diffs](docs/en/08-rapporti.md)
9. [Signed scope](docs/en/09-firma.md)
10. [Compatibility and testing](docs/en/10-compatibilita.md)

The shell cheatsheet the project grew out of is in [scripts/](scripts/).

## What it does not do

It does not find out whether you have permission: you declare that in the scope file, and the program takes your word for it. It does not protect against anyone who runs `httpx` directly. The flag filter is a safety net against mistakes, not a sandbox. The details are in [docs/06-architettura.md](docs/en/06-architettura.md).

## Development

```sh
make check     # ruff (lint + format), mypy --strict, test e coverage
```

No runtime dependencies (just the standard library). Development tools install with `pip install -e ".[dev]"`. See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## License

MIT, see [LICENSE](LICENSE). The license covers the code; it does not authorize any activity.
