# Dispatch Queue: Neon Drift

Last updated: 2025-12-30

## Pending Tasks

### Priority 1: Publishing
1. **Prepare platform assets** → zx-publish:prepare-platform-assets
   - Game icon (256x256)
   - Screenshots (3-5)
   - Store description

2. **Publish to nethercore.systems** → zx-publish:publish-game

### Priority 2: Optional Polish
3. **Balance tuning** → Manual testing
   - Car stats (speed, accel, handling)
   - Track difficulty progression
   - AI opponent behavior

## Completed This Session
- [x] Build ROM package with `nether build`
- [x] Test in Nethercore player - RUNNING SUCCESSFULLY
- [x] Generate XM music tracks (5 tracks)
- [x] Tech director code analysis
- [x] Fix drift bonus decay bug
- [x] Add track segment bounds checking
- [x] Create constants module
- [x] Implement visual polish effects:
  - [x] Boost flame particles (orange/cyan synthwave)
  - [x] Drift smoke particles (from tires)
  - [x] Speed-based camera zoom (60°→75° FOV)
  - [x] Collision screen shake (±2px, 0.2s)

## Notes
- Game is fully playable with all assets and effects
- ROM size: 2.1 MB (71 assets)
- Ready for publishing workflow
