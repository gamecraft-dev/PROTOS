// Balance probe for Cake Sort. Plays each level headlessly with two simulated
// players and prints how often each one fails, so the sawtooth can be checked
// without playing.
//
//   node tools/cake-probe.mjs            levels 1-40, 16 runs each
//   node tools/cake-probe.mjs 1 120 24   a custom range and run count
//
// The rules and the plate dealer live in src/games/cake-sort.html between the
// @engine-start and @engine-end markers; that slice is pure JS and is evaluated
// here as-is.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));
const src = readFileSync(join(here, '../src/games/cake-sort.html'), 'utf8');
const m = src.match(/\/\/ @engine-start[^\n]*\n([\s\S]*?)\/\/ @engine-end/);
if(!m) throw new Error('engine markers not found');

const ctx = {};
vm.createContext(ctx);
vm.runInContext(m[1] + '\nthis.engine = { probe, newLevel, place, isWon, CELLS };', ctx);
const { probe, newLevel, place, isWon } = ctx.engine;

const from = +(process.argv[2] || 1), to = +(process.argv[3] || 40), runs = +(process.argv[4] || 16);
const rows = probe(from, to, runs);
const tierName = ['', 'HARD', 'SUPER'];
const bar = f => '#'.repeat(Math.round(f * 24)).padEnd(24, '.');

// difficulty = mean failure rate of a casual player (drops plates next to a
// matching cake, otherwise anywhere) and a skilled one (looks one plate ahead)
console.log(' lvl  tier  cakes goal stands  casual skilled plates  difficulty');
for(const r of rows){
  console.log(
    String(r.n).padStart(4), ' ', tierName[r.tier].padEnd(5),
    String(r.K).padStart(5), String(r.goal).padStart(5), String(r.blocked).padStart(7), ' ',
    r.casual.toFixed(2).padStart(6), r.skilled.toFixed(2).padStart(7), r.plates.toFixed(0).padStart(7), '  ',
    bar(r.fail), r.fail.toFixed(2).padStart(5)
  );
}

// sanity: the first level's opening plate bakes a cake straight away
const L1 = newLevel(1), first = place(L1, 0, 10);
console.log('\nlevel 1 opening bakes a cake:', first && first.steps.some(s => s.cake) ? 'yes' : 'NO');
const avg = arr => arr.reduce((a, b) => a + b, 0) / (arr.length || 1);
console.log('mean difficulty   normal %s · hard %s · super %s',
  avg(rows.filter(r => r.tier === 0).map(r => r.fail)).toFixed(2),
  avg(rows.filter(r => r.tier === 1).map(r => r.fail)).toFixed(2),
  avg(rows.filter(r => r.tier === 2).map(r => r.fail)).toFixed(2));
