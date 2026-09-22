# PowerPoint image compatibility and acceptance

Some generated PNG bytes have triggered image-export and full-slide-render failures in PowerPoint even though their CRC, XML, and alternate-render checks pass. Lossless re-encoding resolved the observed cases. This is a compatibility mitigation; do not claim that all such PNGs violate the format, that the user's computer is defective, or that a particular Office cache/decoder defect is proven.

An unchanged original file also passed in a later Office session. This argues against permanent file damage and supports investigating transient Office loading/cache state, without identifying its exact mechanism. Do not present normalization as a proven repair for an inherently invalid PNG or as a substitute for native verification.

## Generated decks

`postprocess.py` also isolates a notes-master theme that is shared with another master. In native tests, changing the generated presentation's child order exposed a loader failure with the shared theme; keeping the order and cloning only the theme bytes/relationship resolved it. The helper preserves the complete notes master, its text, theme contents, and any theme image relationships. This is a distinct structural compatibility case, not evidence that the earlier PNG symptom has the same cause.

`build.py` calls `normalize_png.py` after postprocessing. It recompresses static PNG IDAT while verifying identical decompressed scanlines and non-IDAT metadata. Other package parts remain byte-identical. APNG is retained unchanged and reported; signed packages are rejected instead of invalidating their signatures silently.

The default `--powerpoint=auto` detects Windows COM registration and PowerShell. If available, `powerpoint_check.py` exports embedded picture objects and each slide, saves a temporary copy, reopens it, and compares object counts/types and text. An observed native failure fails the build. `--powerpoint=required` also fails when native QA is unavailable. `--powerpoint=off` is an explicit diagnostic override and never means native acceptance.

Native renders replace the alternate render step; still inspect them for missing content, clipping, and layout defects. A successful automated export is not visual QA. The checker verifies counts against source slide XML, so content silently removed on open must not pass just because the resulting file can be saved. Inspect charts/OLE/media appropriate to the requested content; picture/slide export is not a promise that every interactive feature works.

## Existing decks and merged output

Preserve the latest user-edited file. Do not regenerate it from a stale generator. When this image symptom is confirmed, create a new copy:

```text
python scripts/normalize_png.py original.pptx fixed.pptx --report=png-changes.json
python scripts/powerpoint_check.py fixed.pptx
```

`--in-place` is for a freshly generated output or an explicitly authorized in-place edit. Re-run native validation on the **final merged/template-applied PPTX**; passing on an intermediate content-only page does not validate the merged result.

Do not change page counts, rename relationship IDs, remove masters, or delete content based on guesses. If normalization does not resolve the symptom, isolate a suspect picture in a blank deck and compare original/re-encoded copies. Do not loop indefinitely through template rewrites. State the confirmed trigger separately from any unproven Office-internal mechanism.

## Environment and user-session boundaries

The checker operates on uniquely named temporary copies and leaves source bytes untouched. It does not quit PowerPoint or change global alerts/security settings. If Office is busy or a check times out, report failure and inspect the application state; do not kill the user's process. No native tool is available on many non-Windows hosts: use the configured alternate renderer, mark **PowerPoint NOT VERIFIED**, and do not claim the original repair issue is resolved without native evidence.

QA artifacts live under `<deck>.powerpoint-qa/run-*`: copied input, saved copy, per-picture and per-slide PNGs, source counts, and the native log/report. The saved copy is an evidence artifact, not an automatic replacement for the user's source.
