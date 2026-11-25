# Profili e flag vietati

🌐 **Italiano** · [English](en/04-profili.md) · [中文](zh/04-profili.md)

| Profilo | Cosa fa | Rumore | Root |
|---|---|---|---|
| `vivi` | Status code e titolo della pagina. | basso | no |
| `tech` | Tecnologie e server dichiarati. | basso | no |
| `percorsi` | Percorsi comuni, in JSON. | medio | no |
| `porte-web` | Porte web alternative. | medio | no |
| `filtrati` | Solo 200, 401 e 403. | basso | no |
| `jsonl` | Status, titolo, server e tecnologie in JSON. | basso | no |
| `prudente` | Con limiti su thread, frequenza e timeout. | basso | no |

`httpx-cli profili` stampa i flag esatti di ciascuno.

## Cosa fa ciascun profilo

**vivi** (`-sc -title -silent`). Status code e titolo della pagina. Il passo normale dopo la scoperta: cosa risponde davvero via web?

**tech** (`-td -server -silent`). Tecnologie e server dichiarati. Per capire che stack gira dietro, prima di scegliere i template di nuclei.

**percorsi** (`-path /,/login,/admin,/.git/HEAD -sc -title -silent -j`). Percorsi comuni, in JSON. Controlla alcuni percorsi sensibili. Un /.git/HEAD raggiungibile è un problema serio.

**porte-web** (`-p 80,443,8080,8443,3000,5000 -sc -title -silent`). Porte web alternative. Per i server web che non stanno su 80 e 443.

**filtrati** (`-mc 200,401,403 -title -silent`). Solo 200, 401 e 403. Per tenere solo ciò che esiste e merita un secondo sguardo.

**jsonl** (`-sc -title -server -td -j`). Status, titolo, server e tecnologie in JSON. Per elaborare il risultato con altri strumenti.

**prudente** (`-sc -title -t 25 -rl 50 -timeout 10 -retries 1 -silent`). Con limiti su thread, frequenza e timeout. Il profilo da usare di default su infrastrutture di clienti.

## Passare flag a mano

Tutto ciò che scrivi dopo `--` finisce a httpx, dopo i flag del profilo, a patto che non sia nell'elenco dei vietati. Il confronto non distingue maiuscole e minuscole e accetta sia `-flag valore` sia `-flag=valore`, con uno o due trattini.

```sh
httpx-cli lancia vivi https://app.example.org --scope scope.toml -- -timeout 5
```

## Elenco dei vietati

| Flag | Perché |
|---|---|
| `-u`, `-target`, `-l`, `-list` | i target arrivano dal file validato contro lo scope |
| `-o`, `-output` | l'output lo gestisce httpx-cli |
| `-fr`, `-follow-redirects` | seguire i redirect può portare su host fuori scope |
| `-pa`, `-probe-all-ips`, `-tls-probe`, `-csp-probe` | sonda host scoperti al volo (certificati, CSP, altri IP): non sono nello scope |
| `-rr`, `-request` | una richiesta salvata può puntare a un host diverso |
| `-im`, `-input-mode` | una specifica importata può contenere host fuori scope |
| `-jsc`, `-javascript-code` | esegue JavaScript nel browser sulle pagine dei target |
| `-up`, `-update` | l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato |

## Quello che il filtro non fa

Non è una sandbox. Se vuoi aggirarlo ci riesci, per esempio chiamando `httpx` direttamente. Serve a fermare gli errori e le abitudini sbagliate, non un malintenzionato che ha già accesso al tuo terminale. Se ti serve un flag vietato per un'attività concordata con il cliente, usa httpx direttamente e annota la scelta nell'ingaggio.
