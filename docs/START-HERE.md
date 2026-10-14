# Image Review: start here

**Continuing this tool? Read [the detailed handover](HANDOVER.md).** For pictures and operation, use the [manual](USER-MANUAL.md) and [offline demo](../demo.html).

Owner-only photo review with independent people/content decisions, undo/history and optional decision-based filter calibration. Human labels are not automatic face recognition.

**Start with:** Choose a small review queue. Choose the intended Review pass before judging an image. Start with a manageable queue such as Borderline rather than treating every suggestion as a verdict.

**Source:** this is a private source checkpoint, not a live-system mirror. Check [the source manifest](../SOURCE-MANIFEST.json) and current working files before merging.

**Keep your work safe:** Images/previews, names, labels and histories are private NAS data and are not included in this source repository. The demo uses generated sample shapes. Exported histories can contain sensitive annotations and should remain private unless reviewed.

**Next maintainer action:** Verify revision conflict/retry and per-pass undo with synthetic media. Keep gateway access owner-only. Learning calibrates the existing score cutoff; its retained holdout/near-duplicate limitations do not support claims of general classifier accuracy.

**Status:** private upload verified on 14 October 2026. These guides accompany the source package. Live runtime, data backups and full recovery were not retested. Public sharing was authorised on 14 October 2026; the NAS backup remains private.
