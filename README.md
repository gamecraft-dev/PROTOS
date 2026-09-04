# PROTOS

Playable mobile game prototypes. Each folder is a self-contained HTML file you
can open in a browser — no build step, no dependencies, no assets.

| Prototype | What it is | Status |
| --- | --- | --- |
| **[blockcharge](blockcharge/)** | Block puzzle where clearing lines earns powers you pick and bank. Mass-market verb, one tweak. | Current |
| **[sparkweave](sparkweave/)** | Beam-routing roguelite on a 5×5 loom. Deep systems, but too much to explain for a casual audience. | Shelved — see note |

Each folder has a `DESIGN.md` with the market rationale, the balance numbers, and
the risks.

### Note on sparkweave

Kept because the engine work is reusable — a deterministic simulator that emits an
event log, animated by a separate playback layer, is a good pattern for any
chain-reaction game. Shelved as a product because it needed a tutorial before a
player could tell what they were looking at, which is disqualifying for a
mass-market casual title.
