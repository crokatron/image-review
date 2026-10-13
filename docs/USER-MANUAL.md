# Image Review — visual user manual

[Project overview](../README.md) · [Offline interactive demo](../demo.html)

Start with the numbered picture guide. Each number identifies the exact highlighted control. Work through one step at a time; the longer reference is below it.

### Try the working offline example

Screenshot of this project’s interactive demo. Side-by-side services are explicitly simulated.

![Image Review — numbered controls](images/guide-1.jpg)

1. **Inspect one image.** The demo uses generated shapes, never private photos.
2. **Make one decision.** A decision advances the queue and records a label.
3. **Correct without starting over.** Undo returns to the previous item and restores its prior label.

## Detailed task reference

### Choose a small review queue

1. Choose the intended Review pass before judging an image. Start with a manageable queue such as Borderline rather than treating every suggestion as a verdict.
2. Inspect the image; enlarge it when the detail matters. If the preview is unavailable, skip instead of guessing.
3. Use the appropriate positive/negative decision or Skip. Wait for saving to finish before assuming the next item represents a committed choice.

### Tag people manually

1. Use Tag people to create/select an appropriate name or nickname and mark the people actually visible.
2. Use Other people are present for additional unlabelled people, or No people when that is accurate.
3. People tags are manual. This tool does not perform face recognition or propagate someone’s identity automatically.

### Correct a decision

1. Use Undo for the current review channel, then make the intended decision again. Meme, people and adult-content histories are independent.
2. If a save failed, use the retry state rather than creating conflicting changes in another tab. A stale revision can require refreshing before editing again.
3. Use filters to revisit previously reviewed items and export the decision history when auditing a batch.

### Use machine suggestions appropriately

1. Open the machine-flagged queue to prioritise review, then inspect each image yourself.
2. Treat model scores as ranking signals rather than calibrated certainty. Your manual label remains a separate record.
3. Updating the learning filter uses eligible human labels; a failed quality gate should leave a previous valid filter or no active update, not fabricate success.

## Keep your work

Images/previews, names, labels and histories are private NAS data and are not included in this source repository. The demo uses generated sample shapes. Exported histories can contain sensitive annotations and should remain private unless reviewed.

## If something looks wrong

- Image missing: verify preview availability and do not blindly label it.
- Decision not saved: inspect retry/conflict state and connection.
- Learning inactive: reviewed labels or quality criteria may not be sufficient; manual review still works.

## What this manual does not promise

The app depends on the owner-authenticated gateway and persistent database. No private photographs are used in the shareable demo. No new classifier or private-image scan is run by this documentation work.

Screenshots show the actual application where captured. The offline demo is a deliberately smaller simulation and identifies its dummy services. It never controls devices, sends notifications, uploads files or launches printing.
