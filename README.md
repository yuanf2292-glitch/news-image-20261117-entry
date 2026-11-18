# The World in One Page — Tuesday 17 November 2026

A newspaper front page that sums up the world news of Tuesday 17 November
2026 in a single image.

## The day, as reported

- **Lead: Ukraine hits the Crimea Bridge again** — a second strike in two
  days collapses part of the road bridge to occupied Crimea, as Russian
  missiles hit Kyiv's bridges over the Dnipro.
- **Tankers hit by mines off Hormuz** — Iran says tankers struck mines near
  the Strait of Hormuz, and fires drones at a US radar site in Bahrain.
- **Xi, Trump, Putin to meet Thursday** — the first trilateral of the three
  leaders, set for Shenzhen on the APEC sidelines.
- **Third US carrier reaches the Mideast** — USS Theodore Roosevelt joins
  the build-up in the region.
- **Estonia to shut its Russia border** — crossings close on 1 December
  over a foiled sabotage plot.
- **Japan scrambles jets** — Russian aircraft violate Japanese airspace.
- **Pentagon fails its audit again** — ninth year running, $4.8 trillion
  unverified.

## The entry

- `entry.png` — the finished front page, 1024x1024, JPEG bytes under the
  `.png` name (the competition reads the format from the first bytes).
- `main.py` — Python 3.13, standard library only, no network. It validates
  the artwork (size at most 1 MiB, a real PNG or JPEG header, dimensions at
  most 1024x1024), copies it to `$MAKEFUN_OUTPUT_DIR` (else `/output`) in
  64 KiB chunks, then re-reads the copy and checks its SHA-256 against the
  source. Any failed check writes nothing and exits non-zero.

## Check it

```sh
mkdir -p out1 out2
MAKEFUN_OUTPUT_DIR=out1 python3 main.py
MAKEFUN_OUTPUT_DIR=out2 python3 main.py
cmp out1/entry.png out2/entry.png   # byte-identical across runs
```
