# Lens & Layered Suite v2.0

A creator focused desktop control center built for real world projects across the Lens & Layered Designs ecosystem.  
This Suite consolidates multiple tools into a single unified interface with a Stark inspired aesthetic and simple, extensible architecture.

---

## Overview

Lens & Layered Suite v2.0 is designed as an all in one command console for creators, developers, photographers and builders.  
Instead of juggling multiple scripts and windows, everything lives in one place with consistent UI, persistent configuration and expandable modules.

Core focus areas include branding, media handling, system utilities, car build planning, networking tools, developer helpers and finance tracking.

---

## Features

**Motivation hub**  
Daily mindset feed, rotating text and focus helpers.

**Branding tools**  
Batch watermarking, output organization and export helpers.

**System utilities**  
Quick cleanups, RAM flush, temp clearing and status logs.

**Media manager**  
Folder helpers and simple media workflows.

**Network tools**  
Ping tester, connectivity checks and lightweight diagnostics.

**Car tools**  
Build planning and audio related helpers.

**Developer and game utilities**  
Small helpers for workflow and testing.

**Finance dashboard**  
Local JSON based tracking for debt, payments and totals.

**Settings page**  
Theme selection, behavior toggles, saved paths and persistent preferences.

---

## Tech Stack

• Python 3.11+  
• Tkinter for UI  
• Local JSON for config and finance data  
• Packaged with PyInstaller  
• Windows focused UX and behavior

---

## Project Structure

```text
LensAndLayeredSuite/
  src/
    lens_layered_suite_v2.py
  assets/
    icons/
      lens_layered.ico
      lens_layered_32.png
    splash/
      splash_clean.png
  README.md
  LICENSE
  .gitignore


Running from Source

Install Python 3.11 or newer.

Clone the repository:

git clone https://github.com/joshyboo25/LensAndLayeredSuite.git
cd LensAndLayeredSuite


Run the Suite:

python src/lens_layered_suite_v2.py

Building a Windows Executable

Use PyInstaller from the project root:

pyinstaller --onefile --noconsole ^
  --name "LensAndLayeredSuite" ^
  --splash "assets/splash/splash_clean.png" ^
  --add-data "assets;assets" ^
  src/lens_layered_suite_v2.py


The executable will be created in the dist directory.

Data Storage

The Suite stores user-specific data in the user's home directory:

• LensAndLayered_SuiteConfig.json – application settings
• LensAndLayered_FinanceData.json – finance dashboard entries

Deleting these files resets the Suite to defaults.

Roadmap
Short term

• Live theme switching based on Settings
• Close confirmation behavior wired to settings
• Default view selection on startup
• Payoff projections and timelines in Finance

Long term

• Expanded media processing and branding automation
• Additional car build and audio calculators
• Signed Windows releases
• Documentation and user guide

License

This project is licensed under the MIT License.
See the LICENSE file for details.

Author

Built by Josh
Part of the Lens & Layered Designs creative ecosystem

GitHub: @joshyboo25
