Lens and Layered Suite v2.0 ⚡ – Creator Control Center

A fully featured creator-focused desktop control center designed for real-world workflow across the Lens and Layered Designs ecosystem.
Everything you need to build, edit, plan, organize, and execute your creative work — all in one UI with a Stark-inspired aesthetic.

📌 Overview

The Lens and Layered Suite v2.0 is an all-in-one command console for photographers, editors, developers, designers, builders and creators.
Instead of juggling separate scripts and random utilities, the Suite gives you a centralized, consistent, and expandable control center.

It includes integrated tools for:

• Branding
• Media
• System utilities
• Networking
• Development
• Finance
• Car build planning
• Motivation

All wrapped in a clean UI with persistent settings and modern visuals.

🌟 Features
🧠 Motivation Hub

Rotating focus text, mindset reinforcement, and simple daily boosts.

🖋️ Branding Tools

Batch watermarking
Smart output organization
Automatic logo handling
Supports JPG, PNG, JPEG, WEBP

⚙️ System Utilities

RAM flush
Temp cleanup
Quick maintenance tasks
Live logs

🎞️ Media Manager

Folder helpers
Simple workflow shortcuts
Organization support

🌐 Network Tools

Ping testing
Connectivity checks
Diagnostics

🚗 Car Tools

Build planning helpers
Audio wiring helpers
Future expansion planned

🧪 Developer and Game Tools

Testing helpers
Workflow boosters
Mini-scripts for debugging

💰 Finance Dashboard

Debt tracking
Payment logging
Auto totals
Local JSON storage

🎛️ Settings

Themes
Behavior toggles
Saved file paths
Persistent preferences

🧩 Tech Stack

Python 3.11+
Tkinter UI
Local JSON storage
PyInstaller packaging
Windows-optimized UX

📂 Project Structure
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

▶️ Running from Source

Install Python 3.11 or newer.

Clone the repo:

git clone https://github.com/joshyboo25/LensAndLayeredSuite.git
cd LensAndLayeredSuite


Run the Suite:

python src/lens_layered_control_center_full.py

🏗️ Building a Windows Executable

Run this from the project root:

pyinstaller --onefile --noconsole ^
  --name "LensAndLayeredSuite" ^
  --splash "src/assets/splash/splash_clean.png" ^
  --add-data "src/assets;assets" ^
  src/lens_layered_control_center_full.py


Your EXE will appear inside the dist folder.

💾 Data Storage

The Suite saves user data inside your home directory.

Config:
LensAndLayered_SuiteConfig.json

Finance Data:
LensAndLayered_FinanceData.json

Deleting these files resets the Suite.

📅 Roadmap
Short Term

• Live theme switching
• Startup default view
• Configurable close-confirmation
• Finance payoff projections

Long Term

• Media automation
• Advanced branding workflows
• Car audio calculators
• Signed Windows releases
• Full documentation and user guide

🧠 Author

Built by Josh
Part of the Lens and Layered Designs ecosystem
GitHub: @joshyboo25

📄 License

MIT License
See the LICENSE file for details.
