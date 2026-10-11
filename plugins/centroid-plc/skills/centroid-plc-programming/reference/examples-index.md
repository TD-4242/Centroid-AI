# Official ALLIN1DC Example Projects

When implementing a feature, find the closest official example and crib its proven pattern
rather than inventing from scratch.

The PLC Manual's Appendix A prints the complete basic ALLIN1DC program, `allin1dc-basic.src`
("PLC for MPU11 and allin1dc + keyboard jog") (PLC Manual, PDF p.64-98).

The projects below are from Centroid's sample ALLIN1DC PLC project set (Copyright Centroid
Corp.), which is not shipped with this plugin. No manual gives a download location for it; ask
Centroid Tech Support (support@centroidcnc.com) or the Centroid forum,
https://centroidcncforum.com (PLC Manual, PDF p.10-11). Paths are relative to the set's
`_ALLIN1DC/` folder. Row descriptions come from reading each sample's source and carry no
manual page.

## Standard builds

| Path | What it demonstrates |
|---|---|
| `_basic/cncm/allin1dc-basic-v6.src` | Baseline ALLIN1DC mill PLC with keyboard jog; the canonical reference starting point for any new build (CNC11 3.12+) |
| `_basicVCPMpgBeta/cncm/allin1dc-basic-mill-skin2.src` | Basic mill PLC extended with VCP (virtual control panel) and wireless MPG support (CNC12 4.09r10+, beta) |
| `_BOSSVCPMpgBeta/cncm/allin1dc-BOSS-mill-skin2.src` | BOSS-variant mill PLC with VCP and wireless MPG; uses P800 control-type parameter to set VCP key layout/labelling |

## ATC builds

| Path | What it demonstrates |
|---|---|
| `_atc/_umbrella/cncm/allin1dc-umbrella-v7.src` | 16/16 umbrella ATC with spindle orient (M19), carousel in/out (M80/M81), throwaway count on reversal, spindle load meter, and Z-brake release (CNC11 3.14+) |
| `_atc/_umbrella_no_throw_away_std_io/cncm/A1DC-umb-stdio-no-throwaway.src` | 16/16 umbrella ATC with standardized I/O and no throwaway count on carousel reversal; simpler state machine than the v7 umbrella (CNC11 3.16+) |

## Custom builds

| Path | What it demonstrates |
|---|---|
| `_custom/_allin1dc-basic_3rd_axis_brake/cncm/allin1dc-basic_3rd_axis_brake.src` | Basic mill PLC with OUT9 driven as a 3rd-axis electromagnetic brake output; shows brake-release pattern around axis motion |
| `_custom/allin1dc-basic-v2-with_remote_start/cncm/allin1dc-basic-v2-with_remote_start.src` | Basic mill PLC with INP13 wired as a remote cycle-start input; demonstrates external-trigger → `SV_CYCLE_START` pattern |
| `_custom/_allin1dc-basic-w-lowrange-reverse/cncm/allin1dc-basic-w-lowrange-reverse.src` | Basic mill PLC with low-range spindle speed and VFD reverse-direction support; shows 12-bit DAC spindle control with range switching |
| `_custom/_allin1dc-spindle-brake/cncm/allin1dc-spindle-brake-v2.src` | Standard basic PLC with spindle-brake logic on AUX3; `BrakeMode_M` tracks brake state and AUX3 is forced ON at power-up (CNC11 3.16+) |
