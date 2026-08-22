# Route Stitch checkpoint 04: threshold and close

- Local start: `2026-08-22T16:35:07.9149419+08:00`.
- Required threshold: `2026-08-22T18:35:07.9149419+08:00`.
- Final exact/static verification: `2026-08-22T18:35:47.1038278+08:00`.
- Elapsed through verification: `02:00:39.1888859`.

The two-hour floor was exceeded before finalization.  The closing suite
compiled all eight route scripts, parsed all eight JSON evidence files,
checked Markdown fence balance, and reran the exact theorem/obstruction
checkers.  Every checker returned PASS in its stated scope.

Four structured `W4` slices received independent hostile reconstruction:
matching support, the `d=6` weighted three-path, the all-`d` weighted
three-path, and the all-dimensional equal-magnitude star.  The last result
does not cover unequal star weights.  The unrestricted `W4` and half-depth
RPCD targets remain open.
