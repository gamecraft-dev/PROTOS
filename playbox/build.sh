#!/usr/bin/env bash
# Builds Playbox into one self-contained page.
#
# src/shell.html is the hub (home screen, settings, saving, sound, sheets).
# Every file in src/games/ is one game; it is inlined where the shell says
# <!-- @games -->, in file-name order. The result is index.html, a single file
# you can open straight from disk. No dependencies.
#
# The sources use the artifact-host format (no <!doctype>/<html>/<head>/<body>).
# Set ARTIFACT_OUT=path to also write that host-format page, unwrapped.
set -euo pipefail
cd "$(dirname "$0")"

python3 - <<'PY'
import glob, os
shell = open('src/shell.html', encoding='utf-8').read()
games = sorted(glob.glob('src/games/*.html'))
assert '<!-- @games -->' in shell, 'games marker not found in shell'
body = shell.replace('<!-- @games -->', '\n'.join(open(g, encoding='utf-8').read() for g in games), 1)

out = os.environ.get('ARTIFACT_OUT')
if out:
    open(out, 'w', encoding='utf-8').write(body)
    print('wrote', out, len(body), 'bytes')

marker = '<div id="app">'
assert marker in body, 'app root not found'
head = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,maximum-scale=1,user-scalable=no">
<meta name="theme-color" content="#EEF1F6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0E1220" media="(prefers-color-scheme: dark)">
<meta name="description" content="Playbox: a shelf of small puzzle games. First up, Paint Sort: pour paint between vials until each holds one colour.">
<meta name="apple-mobile-web-app-capable" content="yes">
<style>html,body{margin:0;padding:0}img{max-width:100%}[hidden]{display:none!important}</style>
'''
page = head + body.replace(marker, '</head>\n<body>\n' + marker, 1) + '\n</body>\n</html>\n'
open('index.html', 'w', encoding='utf-8').write(page)
print('built index.html with', len(games), 'game(s),', len(page), 'bytes')
PY
