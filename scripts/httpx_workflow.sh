#!/usr/bin/env bash
# httpx_workflow_v2.sh
# Riferimento operativo completo. Solo target autorizzati.
# Le note spiegano il perché e il quando, non solo il cosa.

TARGET="<HOST_O_URL>"
TARGETS_FILE="<FILE_CON_LISTA_TARGET>"
OUT="<PREFISSO_OUTPUT>"

# ---------------------------------------------------------------
# Prerequisiti
# httpx non richiede browser per il probing base. Per -ss
# (screenshot) serve Chrome. -system-chrome usa quello installato
# ed evita il download del browser bundled. In container, Chrome
# non parte come root senza --no-sandbox, ma httpx gestisce il
# flag internamente: non serve passarlo.
# ---------------------------------------------------------------
httpx -version

# ---------------------------------------------------------------
# Comportamento di default: HTTPS-poi-HTTP con fallback
#
# Il default di httpx è: prova HTTPS, e SOLO se HTTPS non
# risponde, fa fallback a HTTP.
# Questo significa che un servizio HTTP-only su porta 80 che
# ha anche un HTTPS valido (es. pagina di default Nginx su 443)
# viene marcato come vivo su HTTPS, e la risposta HTTP reale
# non viene mai vista. Il fallback scatta solo se HTTPS fallisce
# completamente, non se risponde con contenuto diverso.
#
# -nf (no-fallback) forza il probe di entrambi gli schemi.
# È il flag da usare quando l'input è solo hostname (senza
# schema) e vuoi essere sicuro di non perdere servizi HTTP.
# ---------------------------------------------------------------

# Probe base con default (HTTPS-first). Comodo ma può nascondere
# servizi HTTP su host che hanno anche un HTTPS attivo.
httpx -u "$TARGET" -sc -title -silent

# Da lista, default. -sc status, -title titolo pagina.
httpx -l "$TARGETS_FILE" -sc -title -silent -o "$OUT.live.txt"

# Dual-scheme esplicito: prova HTTP e HTTPS indipendentemente.
# Usalo quando l'input sono hostname nudi e sospetti servizi
# HTTP-only o porte custom.
httpx -l "$TARGETS_FILE" -nf -sc -title -silent -o "$OUT.nf.txt"

# ---------------------------------------------------------------
# Technology detection (-td)
# Fingerprint basato sul dataset Wappalyzer.
# Il Server header e la tecnologia rilevata possono divergere:
# un reverse proxy (Cloudflare, Akamai) maschera l'origine, e
# ciò che vedi è lo stack del CDN, non del backend.
# Dove divergono, è un'informazione, non un errore.
# ---------------------------------------------------------------
httpx -l "$TARGETS_FILE" -td -server -silent -o "$OUT.tech.txt"

# ---------------------------------------------------------------
# Path probing (-path)
# Verifica path noti su tutti gli host della lista in parallelo.
# Attenzione: -path moltiplica le richieste per il numero di host.
# Su 100 host con 4 path, sono 400 richieste. Usalo su liste
# già filtrate, non su tutto l'estrattore.
# ---------------------------------------------------------------
httpx -l "$TARGETS_FILE" -path /,/login,/admin,/.git/HEAD -sc -title -silent -j -o "$OUT.paths.jsonl"

# ---------------------------------------------------------------
# Port probing (-p)
# Quando hai host e vuoi verificare servizi su porte non standard.
# httpx non inferisce porte non standard: se non le passi, non
# le prova.
# ---------------------------------------------------------------
httpx -l "$TARGETS_FILE" -p 80,443,8080,8443,3000,5000 -sc -title -silent -o "$OUT.ports.txt"

# ---------------------------------------------------------------
# Filtri: match e filter
# -mc tiene solo gli status specificati. -fc li esclude.
# -fr (follow redirects) fa atterrare il probe sull'URL finale.
# -fd filtra gli host duplicati (stesso body/title su IP diversi).
# ---------------------------------------------------------------

# Solo pagine servite e access-controlled. Il rumore (404, 500)
# viene scartato prima di passare a Nuclei.
httpx -l "$TARGETS_FILE" -mc 200,401,403 -title -silent -o "$OUT.filtered.txt"

# Escludi redirect e errori server.
httpx -l "$TARGETS_FILE" -fc 301,302,500,502,503 -sc -title -silent -o "$OUT.noredirect.txt"

# Follow redirect + deduplica: riduce il rumore di redirect-only
# e host duplicati.
httpx -l "$TARGETS_FILE" -fr -fd -sc -title -silent -o "$OUT.clean.txt"

# ---------------------------------------------------------------
# Output strutturato
# -j produce JSONL, parsabile con jq, importabile in Nuclei.
# ---------------------------------------------------------------
httpx -l "$TARGETS_FILE" -sc -title -server -td -j -o "$OUT.jsonl"

# ---------------------------------------------------------------
# Screenshot (-ss)
# Headless browser. Lento: usalo solo su host già filtrati.
# -system-chrome evita il download del browser bundled.
# -esb esclude i byte dello screenshot dal JSON (output più leggero).
# ---------------------------------------------------------------
httpx -l "$OUT.filtered.txt" -ss -system-chrome -esb -silent -o "$OUT.screenshots.txt"

# ---------------------------------------------------------------
# Rate limiting
# -t: thread (default 50)
# -rl: richieste al secondo (default 150)
# Ordine di tuning: abbassa -t prima, poi -rl.
# Su produzione reale, -t 25 -rl 50 è conservativo.
# ---------------------------------------------------------------
httpx -l "$TARGETS_FILE" -sc -title -t 25 -rl 50 -timeout 10 -retries 1 -silent -o "$OUT.safe.txt"

# ---------------------------------------------------------------
# Pipeline completa: Katana → httpx → jq → Nuclei (eseguibile)
# httpx verifica quali URL di Katana sono vivi, arricchisce
# con tech detection, e passa a Nuclei solo i vivi.
# ---------------------------------------------------------------

# Step 1: Katana produce URL.
katana -u "$TARGET" -d 3 -jc -f url -silent -o /tmp/katana_urls.txt

# Step 2: httpx verifica e arricchisce.
httpx -l /tmp/katana_urls.txt -sc -title -td -mc 200,401,403 -silent -j -o /tmp/httpx_live.jsonl

# Step 3: estrai solo gli URL vivi per Nuclei.
if command -v jq &>/dev/null; then
    jq -r '.url' /tmp/httpx_live.jsonl > /tmp/live_urls.txt
else
    echo "jq non installato. Estrazione URL fallita."
    exit 1
fi

# Step 4: Nuclei sui soli vivi.
if command -v nuclei &>/dev/null; then
    nuclei -l /tmp/live_urls.txt -severity critical,high -exclude-tags intrusive,dos -jsonl -o /tmp/nuclei_findings.jsonl
else
    echo "nuclei non installato. Pipeline fermata a live_urls.txt."
fi

# ---------------------------------------------------------------
# Comando di produzione completo
# Verifica, arricchisce, filtra il rumore, output JSONL.
# ---------------------------------------------------------------
httpx -l "$TARGETS_FILE" \
  -sc -title -server -td \
  -mc 200,401,403 \
  -fr -fd \
  -timeout 10 -retries 1 -t 25 -rl 50 \
  -silent -j -o "$OUT.jsonl"
