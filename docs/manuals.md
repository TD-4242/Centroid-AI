# Official manuals

The skills cite these manuals by page. The PDFs are not redistributed here; they are free from
Centroid and TECO-Westinghouse. Centroid serves only the latest revision of each manual, so a
page citation can drift if the manual has been revised since the revision listed below.

When a skill needs the exact wording, it offers to download the PDF to `~/.centroid-ai/manuals/`
(see [Installing](installing.md#your-settings) to change that behavior).

PDF page = cited page + offset. An offset of +0 means the skills cite PDF page numbers directly;
+1 means the printed page number is one less than the PDF viewer's.

| Manual | Cite as | Revision written against | Pages | PDF page = cited page + | Used by |
| --- | --- | --- | --- | --- | --- |
| [CNC12 PLC Programming Manual](https://www.centroidcnc.com/centroid_diy/downloads/centroid_plc_programming_manual.pdf) | PLC Manual | rev8 07/24/26 | 132 | +0 | [centroid-acorn](plugins/centroid-acorn.md), [centroid-allin1dc](plugins/centroid-allin1dc.md), [centroid-cnc12-ops](plugins/centroid-cnc12-ops.md), [centroid-plc](plugins/centroid-plc.md), [centroid-vcp](plugins/centroid-vcp.md), [teco-f510](plugins/teco-f510.md) |
| [VCP 2.0 Users Manual](https://www.centroidcnc.com/centroid_diy/downloads/centroid_vcp_users_manual.pdf) | VCP Manual | rev28 | 64 | +0 | [centroid-cnc12-ops](plugins/centroid-cnc12-ops.md), [centroid-vcp](plugins/centroid-vcp.md) |
| [CNC12 Milling Machine Operators Manual](https://www.centroidcnc.com/centroid_diy/downloads/operator_manuals/centroid-cnc12-mill-operator-manual.pdf) | Mill Manual | CNC12 V5.4+ | 506 | +1 | [centroid-cnc12-ops](plugins/centroid-cnc12-ops.md) |
| [CNC12 Router Operators Manual](https://www.centroidcnc.com/centroid_diy/downloads/operator_manuals/centroid-cnc12-router-operator-manual.pdf) | Router Manual | CNC12 V5.42+ | 511 | +1 | [centroid-acorn](plugins/centroid-acorn.md), [centroid-cnc12-ops](plugins/centroid-cnc12-ops.md), [centroid-plc](plugins/centroid-plc.md) |
| [Acorn Installation Manual](https://www.centroidcnc.com/centroid_diy/downloads/acorn_documentation/centroid_acorn_install_manual.pdf) | Acorn Install | rev6 | 138 | +1 | [centroid-acorn](plugins/centroid-acorn.md), [centroid-cnc12-ops](plugins/centroid-cnc12-ops.md), [centroid-plc](plugins/centroid-plc.md), [centroid-vcp](plugins/centroid-vcp.md) |
| [Acorn Axis Pairing and Squaring](https://www.centroidcnc.com/centroid_diy/downloads/acorn_documentation/paired_axes_acorn_user_guide.pdf) | Pairing Guide | rev19 | 41 | +0 | [centroid-acorn](plugins/centroid-acorn.md), [centroid-cnc12-ops](plugins/centroid-cnc12-ops.md) |
| [ALLIN1DC Installation Manual](https://www.centroidcnc.com/downloads/centroid_allin1dc_install_manual.pdf) | ALLIN1DC Install | rev22 | 125 | +1 | [centroid-allin1dc](plugins/centroid-allin1dc.md), [teco-f510](plugins/teco-f510.md) |
| [F510 Instruction Manual](https://www.tecowestinghouse.com/Manuals/F510_instruction_manual.pdf) | F510 Manual | TECO-F510IM Ver 01 2017.12 | 438 | +0 | [teco-f510](plugins/teco-f510.md) |

## Downloading by hand

Centroid's server rejects requests without a browser-like user agent. With curl:

```bash
curl -fL -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36' \
  -H 'Accept: application/pdf,*/*' -o ~/.centroid-ai/manuals/<file> <url>
```

Use the manual's link above as `<url>` and the last part of that link as `<file>`. Or open the
link in a browser and save the PDF into `~/.centroid-ai/manuals/` (or your `manuals.dir`).
