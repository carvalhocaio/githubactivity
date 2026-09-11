# VHS tape recording the github-activity demo.
# Install VHS (https://github.com/charmbracelet/vhs) and run:
#   vhs assets/demo.tape
# Requires vhs <= 0.11.0 -- v0.12.0 has a regression where the render step
# receives an already-cancelled context and silently produces no output
# (https://github.com/charmbracelet/vhs/compare/v0.11.0...v0.12.0).
Output assets/demo.gif

Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 650
Set Theme "Dracula"
Set TypingSpeed 40ms

Type "uv run github-activity torvalds --limit 5"
Enter
Sleep 3s

Type "uv run github-activity this-user-should-not-exist-xyz123"
Enter
Sleep 1500ms

Type "echo exit code: $?"
Enter
Sleep 1500ms
