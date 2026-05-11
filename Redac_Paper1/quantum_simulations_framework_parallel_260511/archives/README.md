# Archives Directory
> Last updated: 2026-05-11

This directory contains archived code that is no longer part of the active codebase.

## Subdirectories

- **obsolete/** — Code that is no longer used
- **experimental/** — Experimental and work-in-progress code
- **notebooks/** — Archived Jupyter notebooks
- **duplicates/** — Duplicate implementations (consolidated into main codebase)
- **incomplete_tests/** — Placeholder test files

## How to Restore

If you need to restore any archived files:

```bash
git checkout HEAD -- archives/<path>/<filename>
```

## Notes

- All archived files remain in Git history
- Do not use archived code in production
- Consider deleting after 6 months if not needed
