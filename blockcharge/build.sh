#!/usr/bin/env bash
# Wraps the artifact-ready source (src/app.html) into a standalone page.
# src/app.html has no <!doctype>/<html>/<head>/<body> because the Artifact host
# supplies those; index.html is the same game as a file you can just open.
set -euo pipefail
cd "$(dirname "$0")"

{
  cat <<'HEAD'
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,maximum-scale=1,user-scalable=no">
<meta name="theme-color" content="#EDEFFA">
<meta name="description" content="Blockcharge — a block puzzle where clearing lines earns powers you choose and bank. Mobile prototype.">
<meta name="apple-mobile-web-app-capable" content="yes">
<style>html,body{margin:0;padding:0}img{max-width:100%}[hidden]{display:none!important}</style>
HEAD
  cat src/app.html
  cat <<'TAIL'
</body>
</html>
TAIL
} > index.html

# the source opens with <title>/<link>/<style> (head material) and then markup;
# splice the body tag in at the first <div id="app">
python3 - <<'PY'
p = 'index.html'
s = open(p, encoding='utf-8').read()
marker = '<div id="app">'
assert marker in s, 'app root not found'
s = s.replace(marker, '</head>\n<body>\n' + marker, 1)
open(p, 'w', encoding='utf-8').write(s)
print('built index.html', len(s), 'bytes')
PY
