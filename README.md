# ClockWise

A top-down pixel-art life game about **using your time wisely**. Every day you
choose where your hours go — clock in at the 9–5, play the markets at the bank,
or pour everything into your startup garage — while still keeping food on the
table. Planned to be online/multiplayer.

## Art style mockup

![ClockWise mockup](Assets/Art/Showcase/clockwise_mockup.png)

*Concept mockup — every pixel generated procedurally. The clock tower is the
town centerpiece; the Bank, 9–5 Inc. office, and Startup garage are the three
ways to spend your time.*

## Project

- **Engine:** Unity 6 (6000.6.5f1), 2D URP, new Input System
- `Assets/Art/` — generated pixel art (tiles, characters, buildings).
  Import settings are enforced by `Assets/Editor/PixelArtImportSettings.cs`
  (point filtering, no compression, 16 pixels per unit).
- `Tools/artgen/` — Python scripts that generate the art
  (`python3 Tools/artgen/generate_art.py`).

## Status

Early concept — mechanics and plot are still being designed.
