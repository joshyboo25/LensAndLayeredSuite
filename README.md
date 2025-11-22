Lens and Layered Suite v2.0

A creator focused desktop control center designed for real world workflow across the Lens and Layered Designs ecosystem.
The Suite brings multiple tools into one unified interface with a Stark inspired aesthetic and a clean, extensible architecture.

Overview

Lens and Layered Suite v2.0 operates as an all in one command console for creators, photographers, developers, editors and builders.
Instead of juggling separate scripts and windows, everything lives in one place with consistent UI, persistent configuration and modular expansion.

Core areas include branding, media handling, system tools, car build helpers, developer utilities, game tools and finance tracking.

Features
Motivation hub

Daily mindset feed, rotating text and focus helpers.

Branding tools

Batch watermarking, organized exports and workflow helpers.

System utilities

Quick cleanups, RAM flush, temp clearing and status logs.

Media manager

Folder helpers and simple media workflows.

Network tools

Ping tests, connectivity checks and lightweight diagnostics.

Car tools

Build planning helpers and audio utilities.

Developer and game utilities

Small workflow scripts and testing helpers.

Finance dashboard

Local JSON tracking for debt, payments and totals.

Settings page

Theme options, behavior toggles, saved paths and persistent preferences.

Tech Stack

Python 3.11 or newer
Tkinter for UI
Local JSON config and finance data
Packaged with PyInstaller
Windows-optimized UX

Project Structure
LensAndLayeredSuite/
  src/
    lens_layered_control_center_full.py
    assets/
      icons/
        lens_layered.ico
        lens_layered_32.png
      branding/
      splash/
        splash_clean.png
      watermark images/
        watermark_dark.png
        watermark_light.png
  README.md
  LICENSE
  .gitignore

Running from Source

Make sure Python 3.11 or newer is installed.

Clone the repository:

git clone https://github.com/joshyboo25/LensAndLayeredSuite.git
cd LensAndLayeredSuite


Run the Suite:

python src/lens_layered_control_center_full.py

Building a Windows Executable

Run the following from the project root:

pyinstaller --onefile --noconsole ^
  --name "LensAndLayeredSuite" ^
  --splash "src/assets/splash/splash_clean.png" ^
  --add-data "src/assets;assets" ^
  src/lens_layered_control_center_full.py


The executable will appear in the dist directory.

Data Storage

The Suite stores user specific data in the user’s home directory.

Config file
LensAndLayered_SuiteConfig.json

Finance data
LensAndLayered_FinanceData.json

Deleting these files resets the Suite to default settings.

Roadmap
Short term

Live theme switching in Settings
Close confirmation behavior controlled by preferences
Startup default view selection
Payoff projections in Finance dashboard

Long term

Expanded media processing and automated branding workflows
Additional car build and audio calculators
Signed Windows releases
Full documentation and user guide

License

Licensed under the MIT License.
See the LICENSE file for details.

Author

Built by Josh
Part of the Lens and Layered Designs ecosystem
GitHub: @joshyboo25
