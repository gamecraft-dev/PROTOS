// Balance probe for Paint Sort. Runs the level generator headlessly and prints
// the difficulty of each level, so the sawtooth can be checked without playing.
//
//   node tools/probe.mjs            levels 1-40
//   node tools/probe.mjs 1 120      a custom range
//
// The generator lives in src/games/paint-sort.html between the @engine-start
// and @engine-end markers; that slice is pure JS and is evaluated here as-is.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));
const src = readFileSync(join(here, '../src/games/paint-sort.html'), 'utf8');
const m = src.match(/\/\/ @engine-start[^\n]*\n([\s\S]*?)\/\/ @engine-end/);
if(!m) throw new Error('engine markers not found');

const ctx = {};
vm.createContext(ctx);
vm.runInContext(m[1] + '\nthis.engine = { spec, generate, solve, probe, isSolved, listMoves, applyMove };', ctx);
const { probe, generate, solve } = ctx.engine;

const from = +(process.argv[2] || 1), to = +(process.argv[3] || 40);
const rows = probe(from, to);
const tierName = ['', 'HARD', 'SUPER'];
const bar = f => '#'.repeat(Math.round(f * 24)).padEnd(24, '.');

// difficulty = mean failure rate of two simulated players (see playout /
// playoutSkilled in the engine); the bar is that number
console.log(' lvl  tier  colours hidden moves  casual skilled  difficulty                     ms');
for(const r of rows){
  console.log(
    String(r.n).padStart(4), ' ', tierName[r.tier].padEnd(5),
    String(r.K).padStart(5), String(r.hidden).padStart(7), String(r.len).padStart(6), ' ',
    r.casual.toFixed(2).padStart(6), r.skilled.toFixed(2).padStart(7), '  ',
    bar(r.fail), r.fail.toFixed(2).padStart(5), String(r.ms).padStart(6)
  );
}

// sanity: every generated board is solvable and nothing starts solved
let bad = 0;
for(let n = from; n <= to; n++){
  const g = generate(n);
  const sol = solve(g.vials, g.spec.cap, 400000);
  if(!sol.ok){ bad++; console.log('UNSOLVED level', n); }
}
const slow = rows.filter(r => r.ms > 400).map(r => r.n);
const avg = arr => arr.reduce((a, b) => a + b, 0) / (arr.length || 1);
console.log('\nall solvable:', bad === 0 ? 'yes' : `NO (${bad})`);
console.log('mean difficulty   normal %s · hard %s · super %s',
  avg(rows.filter(r => r.tier === 0).map(r => r.fail)).toFixed(2),
  avg(rows.filter(r => r.tier === 1).map(r => r.fail)).toFixed(2),
  avg(rows.filter(r => r.tier === 2).map(r => r.fail)).toFixed(2));
console.log('generation ms   max %d · mean %s%s', Math.max(...rows.map(r => r.ms)),
  avg(rows.map(r => r.ms)).toFixed(0), slow.length ? ` · slow: ${slow.join(',')}` : '');
