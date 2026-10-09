// Checks the adaptive difficulty end to end: simulated players of different
// skill play through the levels while the Bayesian skill model (Playbox.skill,
// in src/shell.html) picks every level's heat, exactly as the games do.
//
//   node tools/adaptive-sim.mjs model          the model alone, with idealised players
//   node tools/adaptive-sim.mjs cake [levels]  Cake Sort's real engine and bots (default 40 levels)
//   node tools/adaptive-sim.mjs paint [levels] Paint Sort's real engine and bots (default 30 levels)
//
// For each player it prints the first-try win rate on ordinary, hard and
// super-hard levels next to the targets, and the heat the model settled on.
// The same players on the fixed sawtooth (the old design) are shown for
// comparison: there the strong player wins almost everything and the weak one
// keeps failing; with the model both land near the targets.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));
const slice = (file, a, b) => {
  const src = readFileSync(join(here, '..', file), 'utf8');
  const m = src.match(new RegExp(`// @${a}[^\\n]*\\n([\\s\\S]*?)// @${b}`));
  if(!m) throw new Error(`${a} markers not found in ${file}`);
  return m[1];
};
const ctx = {};
vm.createContext(ctx);
vm.runInContext(slice('src/shell.html', 'skill-start', 'skill-end') +
  '\nthis.SK = { TARGET: SKILL_TARGET, create: skillNew, chance: skillChance, target: skillTarget, heat: skillHeat, observe: skillObserve, quality: skillObserveQuality, Phi: skillPhi };', ctx);
const SK = ctx.SK;

const tierOf = n => { const p = (n - 1) % 10; return p === 9 ? 2 : p === 4 ? 1 : 0; };
const TIERS = ['ordinary', 'hard', 'super hard'];
const targetMean = t => { const ps = [0, 1, 2, 3, 5, 6, 7, 8].map(i => SK.TARGET[i]); return t === 0 ? ps.reduce((a, b) => a + b) / ps.length : SK.TARGET[t === 1 ? 4 : 9]; };
const mulberry = s => () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

/* Play levels 1..levels. `play(n, h, seed)` returns { won, q }. With `adaptive`
   the model picks each heat (retries eased by mercy); otherwise the fixed curve
   `base(n)` is used. A level is retried until it is won (at most 6 tries). */
function campaign(G, play, levels, adaptive, seed){
  const s = SK.create(G.cfg), first = [[0, 0], [0, 0], [0, 0]], late = [[0, 0], [0, 0], [0, 0]], heats = [];
  for(let n = 1; n <= levels; n++){
    let fails = 0, done = false;
    for(let tries = 0; tries < 6 && !done; tries++){
      let h;
      if(adaptive){
        const [lo, hi] = G.range(n);
        h = Math.min(hi, Math.max(lo, SK.heat(s, SK.target((n - 1) % 10, fails), G.cfg)));
        h = Math.round(h * 20) / 20;
      } else h = G.base(n);
      const r = play(n, h, (seed * 7919 + n * 131 + tries * 17) >>> 0);
      if(tries === 0){
        first[tierOf(n)][0]++; if(r.won) first[tierOf(n)][1]++; heats.push(h);
        if(n > 20){ late[tierOf(n)][0]++; if(r.won) late[tierOf(n)][1]++; }
      }
      SK.observe(s, h, r.won, G.cfg);
      if(r.won && r.q != null) SK.quality(s, h, r.q, G.cfg);
      if(r.won) done = true; else fails++;
    }
  }
  return { first, late, heats, mu: s.mu, sd: s.sd };
}
function report(title, G, players, levels, runs){
  console.log(`\n${title}: ${levels} levels, ${runs} players of each kind`);
  console.log('first-try win rate: all levels, then levels 21+ (once the model has settled); targets in brackets');
  console.log('player          mode       ' + TIERS.map(t => t.padStart(11)).join('') + ' |' + TIERS.map(t => t.padStart(11)).join('') + '   mean heat by block of ten           skill (mu ± sd)');
  const tg = TIERS.map((t, i) => `(${targetMean(i).toFixed(2)})`.padStart(11)).join('');
  console.log(' '.repeat(27) + tg + ' |' + tg);
  for(const [name, play] of players){
    for(const adaptive of [false, true]){
      const acc = [[0, 0], [0, 0], [0, 0]], lat = [[0, 0], [0, 0], [0, 0]], blocks = [], mus = [], sds = [];
      for(let r = 0; r < runs; r++){
        const c = campaign(G, play, levels, adaptive, 1000 + r);
        c.first.forEach((x, i) => { acc[i][0] += x[0]; acc[i][1] += x[1]; });
        c.late.forEach((x, i) => { lat[i][0] += x[0]; lat[i][1] += x[1]; });
        c.heats.forEach((h, i) => { const b = Math.floor(i / 10); (blocks[b] = blocks[b] || []).push(h); });
        mus.push(c.mu); sds.push(c.sd);
      }
      const avg = a => a.reduce((x, y) => x + y, 0) / a.length;
      console.log(name.padEnd(16), (adaptive ? 'adaptive' : 'fixed').padEnd(9),
        acc.map(([a, w]) => (a ? (w / a).toFixed(2) : '-').padStart(11)).join(''), '|' +
        lat.map(([a, w]) => (a ? (w / a).toFixed(2) : '-').padStart(11)).join(''), '  ',
        blocks.map(b => avg(b).toFixed(2).padStart(5)).join(' ').padEnd(36),
        adaptive ? `${avg(mus).toFixed(2)} ± ${avg(sds).toFixed(2)}` : '');
    }
  }
}

const mode = process.argv[2] || 'model';
if(mode === 'model'){
  // idealised players: they win heat h with chance Φ((θ − h)/β), θ fixed or growing
  // the same curve and range as Cake Sort's engine (heat 0..10, the typical curve capped after 8 blocks)
  const RAMP = [0, .4, .8, 1.2, 2.4, .5, .9, 1.3, 1.7, 3.4], blk = n => Math.min(8, Math.floor((n - 1) / 10));
  const G = { cfg: { beta: 1, mu0: 2.5, sd0: 1.8, drift: .2 }, base: n => blk(n) * .6 + RAMP[(n - 1) % 10],
    range: n => [Math.max(0, blk(n) * .6 - 2.5), Math.min(10, blk(n) * .6 + RAMP[9] + 4)] };
  const ideal = theta => (n, h, seed) => ({ won: mulberry(seed)() < SK.Phi((theta(n) - h) / G.cfg.beta) });
  report('Model only (idealised players, β = 1)', G, [
    ['weak (θ 1.5)', ideal(() => 1.5)], ['typical (θ 3)', ideal(() => 3)], ['strong (θ 6)', ideal(() => 6)],
    ['improving 2→6', ideal(n => 2 + 4 * Math.min(1, n / 60))]
  ], 60, 200);
} else if(mode === 'cake'){
  const levels = +(process.argv[3] || 40);
  vm.runInContext(slice('src/games/cake-sort.html', 'engine-start', 'engine-end') +
    '\nthis.CS = { newLevel, place, isWon, isStuck, botMove, rngNext, baseHeat, heatRange, CELLS };', ctx);
  const C = ctx.CS;
  const G = { cfg: { beta: 1, mu0: 2.5, sd0: 1.8, drift: .2 }, base: C.baseHeat, range: C.heatRange };
  // a bot plays one try of level n at heat h; q is the room left at the tightest moment, as in the game
  const bot = skill => (n, h, seed) => {
    const L = C.newLevel(n, h); L.rs.s = (L.rs.s ^ seed) | 0;
    const rr = { s: seed | 0 }, rand = () => C.rngNext(rr);
    let minFree = C.CELLS;
    for(let k = 0; k < 600; k++){
      if(C.isWon(L)) return { won: true, q: SK.Phi((minFree / (C.CELLS - L.sp.blocked) - .12) / .3) };
      const m = C.botMove(L, skill, rand);
      if(!m) return { won: false };
      C.place(L, m[0], m[1]);
      minFree = Math.min(minFree, L.cells.reduce((a, x) => a + (x === null), 0));
    }
    return { won: false };
  };
  report('Cake Sort (real engine)', G, [['casual bot', bot(0)], ['skilled bot', bot(1)]], levels, 6);
} else if(mode === 'paint'){
  const levels = +(process.argv[3] || 30);
  vm.runInContext(slice('src/games/paint-sort.html', 'engine-start', 'engine-end') +
    '\nthis.PS = { generate, playout, playoutSkilled, rng32, seedFor, baseHeat, heatRange, CAP };', ctx);
  const P = ctx.PS;
  const G = { cfg: { beta: 1.8, mu0: 3.2, sd0: 1.8, drift: .3 }, base: P.baseHeat, range: P.heatRange };
  const cache = new Map();
  const board = (n, h) => { const k = n + '|' + h; if(!cache.has(k)) cache.set(k, P.generate(n, h)); return cache.get(k); };
  // one try: the bot plays the generated board; a dead end is a lost try
  const bot = skilled => (n, h, seed) => {
    const g = board(n, h), r = P.rng32(seed), steps = 60 + g.spec.K * 14;
    const used = skilled ? P.playoutSkilled(g.vials, P.CAP, r, steps) : P.playout(g.vials, P.CAP, r, steps);
    return used < 0 ? { won: false } : { won: true, q: SK.Phi((g.len / used - .7) / .25) };
  };
  report('Paint Sort (real engine)', G, [['casual bot', bot(false)], ['skilled bot', bot(true)]], levels, 4);
}
