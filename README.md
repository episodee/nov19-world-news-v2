# The World in One Day — renewal

A deterministic newspaper front page naming Thursday, 19 November 2026.
Three illustrated leads show the Trump–Xi–Putin Shenzhen summit, GTA VI's
Vice City launch, and the ICJ ruling on Myanmar's genocide against the Rohingya.
Twelve illustrated secondary cards cover conflict, politics, finance, weather,
space, technology and diplomacy. Twenty-six numbered briefs match map pins.
Total: **41 story units**, excluding repeated statistics and timeline items.

The eight-number strip, UTC timeline, markets panel, verdict and date check
anchor the page to the requested day. GTA sales are explicitly Sensor Tower
estimates; cyclone landfall and winds are forecasts. The Riyadh brief attributes
the coalition's claim. Market index percentages refer to Wednesday's close;
commodities, bitcoin and the Treasury yield appear as levels.

## Sources and scope

All facts are hardcoded from the competition brief supplied for this renewal;
no live research or network requests were used. Supplied attribution: Reuters,
AP, BBC, CBS, NPR, IMD, NASA and Sensor Tower (estimates). The summit is attributed
to AP/Reuters/BBC/CBS; the Myanmar ruling to Reuters. These are attribution names,
not a claim that this session independently retrieved the underlying articles.
The reported date includes Wednesday's Jeffries nomination and market close.
The 589m statistic describes 2025 and was reported on the pictured day.

## Run

Drawing requires Pillow and the installed DejaVu fonts under
`/usr/share/fonts/truetype`; helpers and flat illustration style extend the
supplied v1 drawing reference. Fixed geometry, palette and text; no network,
clock or randomness. `main.py` uses only the Python standard library and targets
Python 3.13. It checks PNG magic, stages beside the destination, renames, then
reads back and compares every byte.

```sh
python3 draw.py
MAKEFUN_OUTPUT_DIR=out python3 main.py
MAKEFUN_OUTPUT_DIR=out-second python3 main.py
cmp out/entry.png out-second/entry.png
```

The image is the deliverable; nothing is submitted by either script.

## Visual review and revision

The first full-size and 300px renders were opened during this session. The
second pass makes the summit's first explicit in its headline and expands the
Myanmar lead to three large lines, with the ICJ ruling identified above it.
At 300px the masthead, date and hero headlines read; the 41-story requirement
necessarily makes the secondary summaries, timeline, briefs and footer small.
Those details are intended for the full 1024px image, not claimed to be readable
at thumbnail size. Map shapes are schematic; space/global stories use ocean
margin pins rather than implying a terrestrial observation site.

## Verification results

Final PNG: 1024 × 1024 RGB, 226,976 bytes (below 1 MiB). Both
`out/entry.png` and `out-second/entry.png` passed the copier's read-back check
and `cmp` found them byte-identical. Both final render sizes were opened and
reviewed; no overlapping, clipped or garbled text was seen. Count: 3 + 12 + 26
= 41 story units. No competition submission or repository creation was run.
