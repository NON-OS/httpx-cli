"""Descrizione di httpx (ProjectDiscovery): profili, flag vietati, formato dei risultati."""

from __future__ import annotations

import re

from httpxcli.profili import Profilo
from httpxcli.risultati import Voce, righe_json

NOME = "httpx"
BINARIO = "httpx"
BINARI_ALT = ("httpx-toolkit",)  # su Kali il pacchetto apt httpx-toolkit installa il binario con questo nome
DESCRIZIONE = "Sonde HTTP con scope validato, dry-run di default e audit a catena di hash."
MODO = "url"
PASSA = ("file", "-l")
UNO_EXTRA: tuple[str, ...] = ()  # solo ffuf lavora "un comando per target"
USCITA = "-o"
VERSIONE = ("-version",)
RICONOSCI = "current version"  # testo che il binario vero stampa con {VERSIONE}: distingue da programmi omonimi
INSTALLAZIONE = (
    "Kali/Debian: sudo apt install httpx-toolkit (su Kali il pacchetto è rinominato per non "
    "confliggere con l'httpx di Python; il binario si chiama httpx-toolkit e questo wrapper lo trova da solo). "
    "Ovunque con Go: go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest. "
    "Attenzione: esiste anche un 'httpx' Python (pip), che è un altro programma."
)
SEGRETI = frozenset({"h", "header"})
GRUPPO = "Status HTTP"
NOTA_ATTIVITA = "invia richieste HTTP ai target: attivo, visibile nei log applicativi."

PROFILI = {
    p.nome: p
    for p in (
        Profilo("vivi", "Status code e titolo della pagina.", ("-sc", "-title", "-silent"), "basso",
                "Il passo normale dopo la scoperta: cosa risponde davvero via web?"),
        Profilo("tech", "Tecnologie e server dichiarati.", ("-td", "-server", "-silent"), "basso",
                "Per capire che stack gira dietro, prima di scegliere i template di nuclei."),
        Profilo("percorsi", "Percorsi comuni, in JSON.",
                ("-path", "/,/login,/admin,/.git/HEAD", "-sc", "-title", "-silent", "-j"), "medio",
                "Controlla alcuni percorsi sensibili. Un /.git/HEAD raggiungibile è un problema serio.",
                uscita="jsonl"),
        Profilo("porte-web", "Porte web alternative.",
                ("-p", "80,443,8080,8443,3000,5000", "-sc", "-title", "-silent"), "medio",
                "Per i server web che non stanno su 80 e 443."),
        Profilo("filtrati", "Solo 200, 401 e 403.", ("-mc", "200,401,403", "-title", "-silent"), "basso",
                "Per tenere solo ciò che esiste e merita un secondo sguardo."),
        Profilo("jsonl", "Status, titolo, server e tecnologie in JSON.",
                ("-sc", "-title", "-server", "-td", "-j"), "basso",
                "Per elaborare il risultato con altri strumenti.", uscita="jsonl"),
        Profilo("prudente", "Con limiti su thread, frequenza e timeout.",
                ("-sc", "-title", "-t", "25", "-rl", "50", "-timeout", "10", "-retries", "1", "-silent"),
                "basso", "Il profilo da usare di default su infrastrutture di clienti."),
    )
}  # fmt: skip

VIETATI = {
    "u": "i target arrivano dal file validato contro lo scope",
    "target": "i target arrivano dal file validato contro lo scope",
    "l": "i target arrivano dal file validato contro lo scope",
    "list": "i target arrivano dal file validato contro lo scope",
    "o": "l'output lo gestisce httpx-cli",
    "output": "l'output lo gestisce httpx-cli",
    "fr": "seguire i redirect può portare su host fuori scope",
    "follow-redirects": "seguire i redirect può portare su host fuori scope",
    "pa": "sonda host scoperti al volo (certificati, CSP, altri IP): non sono nello scope",
    "probe-all-ips": "sonda host scoperti al volo (certificati, CSP, altri IP): non sono nello scope",
    "tls-probe": "sonda host scoperti al volo (certificati, CSP, altri IP): non sono nello scope",
    "csp-probe": "sonda host scoperti al volo (certificati, CSP, altri IP): non sono nello scope",
    "rr": "una richiesta salvata può puntare a un host diverso",
    "request": "una richiesta salvata può puntare a un host diverso",
    "im": "una specifica importata può contenere host fuori scope",
    "input-mode": "una specifica importata può contenere host fuori scope",
    "jsc": "esegue JavaScript nel browser sulle pagine dei target",
    "javascript-code": "esegue JavaScript nel browser sulle pagine dei target",
    "up": "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato",
    "update": "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato",
}

ESEMPI_VIETATI = [
    ["-u", "x"],
    ["-l", "x"],
    ["-fr"],
    ["-follow-redirects"],
    ["-o", "x"],
    ["-tls-probe"],
    ["-csp-probe"],
    ["-pa"],
    ["-jsc", "x"],
]
ESEMPI_AMMESSI = [["-mc", "200"], ["-H", "X-Test: 1"], ["-rl", "10"]]

_STATUS = re.compile(r"\[(\d{3})\]")


def voci(testo: str) -> list[Voce]:
    out = []
    for r in righe_json(testo):
        if isinstance(r, dict):
            url = str(r.get("url", ""))
            if not url:
                continue
            stato = str(r.get("status_code", ""))
            titolo = str(r.get("title", ""))
            out.append(Voce(url, f"{url} [{stato}] {titolo}".rstrip(), stato))
        else:
            url = r.split()[0]
            m = _STATUS.search(r)
            out.append(Voce(url, r, m.group(1) if m else ""))
    return out


# -- lingua -------------------------------------------------------------------
# Testi tradotti, generati da l10n/. L'italiano resta quello definito sopra.
_TR_TESTI: dict[str, dict[str, str]] = {
    "en": {
        "descrizione": "HTTP probes with a validated scope, dry-run by default and a hash-chained audit.",
        "nota_attivita": "it sends HTTP requests to the targets: active, visible in application logs.",
        "installazione": "Kali/Debian: sudo apt install httpx-toolkit (on Kali the package is renamed to avoid clashing with Python's httpx; the binary is called httpx-toolkit and this wrapper finds it on its own). Anywhere with Go: go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest. Note: there is also a Python 'httpx' (pip), which is a different program.",
        "gruppo": "HTTP status",
    },
    "zh": {
        "descrizione": "HTTP 探测，带作用域校验、默认 dry-run 以及哈希链审计。",
        "nota_attivita": "向目标发送 HTTP 请求：主动行为，会出现在应用日志中。",
        "installazione": "Kali/Debian：sudo apt install httpx-toolkit（在 Kali 上，为避免与 Python 的 httpx 冲突，该包被重命名；二进制文件名为 httpx-toolkit，本封装会自动找到它）。任何装了 Go 的环境：go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest。注意：还存在一个 Python 的 'httpx'（pip），那是另一个程序。",
        "gruppo": "HTTP 状态码",
    },
}
_TR_PROFILI: dict[str, dict[str, list[str]]] = {
    "en": {
        "vivi": [
            "Status code and page title.",
            "The normal step after discovery: what actually responds over the web?",
        ],
        "tech": [
            "Declared technologies and server.",
            "To see what stack runs behind it, before picking nuclei templates.",
        ],
        "percorsi": [
            "Common paths, in JSON.",
            "Checks a few sensitive paths. A reachable /.git/HEAD is a serious problem.",
        ],
        "porte-web": ["Alternative web ports.", "For web servers that don't sit on 80 and 443."],
        "filtrati": ["Only 200, 401 and 403.", "To keep only what exists and deserves a second look."],
        "jsonl": ["Status, title, server and technologies in JSON.", "To process the result with other tools."],
        "prudente": ["With thread, rate and timeout limits.", "The default profile on client infrastructure."],
    },
    "zh": {
        "vivi": ["状态码和页面标题。", "发现阶段之后的常规步骤：哪些目标真正通过 Web 响应？"],
        "tech": ["声明的技术栈和服务器。", "用于了解背后运行的技术栈，然后再选择 nuclei 的模板。"],
        "percorsi": ["常见路径，以 JSON 输出。", "检查一些敏感路径。可访问的 /.git/HEAD 是严重问题。"],
        "porte-web": ["备用的 Web 端口。", "用于不在 80 和 443 端口上的 Web 服务器。"],
        "filtrati": ["仅 200、401 和 403。", "只保留确实存在且值得进一步查看的内容。"],
        "jsonl": ["状态码、标题、服务器和技术栈，以 JSON 输出。", "用于使用其他工具处理结果。"],
        "prudente": ["带线程数、频率和超时限制。", "在客户基础设施上默认使用的配置。"],
    },
}
_TR_VIETATI: dict[str, dict[str, str]] = {
    "en": {
        "esegue JavaScript nel browser sulle pagine dei target": "runs JavaScript in the browser on target pages",
        "i target arrivano dal file validato contro lo scope": "targets come from the file validated against the scope",
        "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato": "updating the program is done separately, not inside an authorized run",
        "l'output lo gestisce httpx-cli": "output is handled by httpx-cli",
        "seguire i redirect può portare su host fuori scope": "following redirects can lead to out-of-scope hosts",
        "sonda host scoperti al volo (certificati, CSP, altri IP): non sono nello scope": "probes hosts discovered on the fly (certificates, CSP, other IPs): they're not in scope",
        "una richiesta salvata può puntare a un host diverso": "a saved request can point to a different host",
        "una specifica importata può contenere host fuori scope": "an imported spec can contain out-of-scope hosts",
    },
    "zh": {
        "esegue JavaScript nel browser sulle pagine dei target": "在浏览器中对目标页面执行 JavaScript",
        "i target arrivano dal file validato contro lo scope": "目标来自经过作用域校验的文件",
        "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato": "程序更新应单独进行，而不是在一次授权任务中进行",
        "l'output lo gestisce httpx-cli": "输出由 httpx-cli 管理",
        "seguire i redirect può portare su host fuori scope": "跟随重定向可能跳转到作用域之外的主机",
        "sonda host scoperti al volo (certificati, CSP, altri IP): non sono nello scope": "会探测临时发现的主机（证书、CSP、其他 IP）：它们不在作用域内",
        "una richiesta salvata può puntare a un host diverso": "一个已保存的请求可能指向另一个主机",
        "una specifica importata può contenere host fuori scope": "导入的规格文件可能包含作用域之外的主机",
    },
}
_ORIGINALI = (DESCRIZIONE, NOTA_ATTIVITA, INSTALLAZIONE, GRUPPO, PROFILI, VIETATI)


def applica_lingua(lingua: str) -> None:
    """Passa testi, profili e motivi dei flag vietati alla lingua scelta. Ripartendo
    sempre dagli originali italiani, chiamarla più volte non accumula niente."""
    global DESCRIZIONE, NOTA_ATTIVITA, INSTALLAZIONE, GRUPPO, PROFILI, VIETATI
    from dataclasses import replace

    DESCRIZIONE, NOTA_ATTIVITA, INSTALLAZIONE, GRUPPO, PROFILI, VIETATI = _ORIGINALI
    testi = _TR_TESTI.get(lingua)
    if not testi:
        return
    DESCRIZIONE = testi["descrizione"] or DESCRIZIONE
    NOTA_ATTIVITA = testi["nota_attivita"] or NOTA_ATTIVITA
    INSTALLAZIONE = testi["installazione"] or INSTALLAZIONE
    GRUPPO = testi["gruppo"] or GRUPPO
    prof = _TR_PROFILI.get(lingua, {})
    PROFILI = {
        n: replace(p, descrizione=prof[n][0] or p.descrizione, quando=prof[n][1] or p.quando) if n in prof else p
        for n, p in PROFILI.items()
    }
    viet = _TR_VIETATI.get(lingua, {})
    VIETATI = {k: viet.get(v, v) for k, v in VIETATI.items()}
