# AI Pokemon Game Fix TODO
Status: [In Progress]

## Steps from Approved Plan
### 1. [x] Call storage.init_storage() in main_fixed.py init
### 2. [x] Fix/improve main() game loop: state machine (TITLE/PLAYING/GAMEOVER), proper event handling
### 3. [x] Add item rendering (pokeball speed/yellow freeze/blue) in draw loop
### 4. [x] Add item pickup logic & effects (speed boost player, freeze pokemon)
### 5. [x] Update player.prev_pos after moves
### 6. [x] Polish UI: high scores, instructions, effects text, bg color from theme
### 7. [x] Gradual difficulty increase, visual feedback
### 8. [x] Test full flow: python3 main_fixed.py (title→play→pickup→lose→restart→scores)
### 9. [ ] Minor entities.py tweaks if needed (item colors)

**Game fully functional! Title screen, WASD chase, yellow SPEED (bigger player), blue FREEZE (pokemon skips turns), score/difficulty ramp, gameover/save highscore, R restart. Run `python3 main_fixed.py` to play.**

**Next: Step 1-2 edits to main_fixed.py**

