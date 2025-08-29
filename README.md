# AI Context Builder 🤖✨

**The ultimate desktop utility for crafting perfect, context-rich prompts for any Large Language Model (LLM).**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/UI-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)

AI Context Builder is a powerful desktop tool designed to streamline the process of creating comprehensive prompts for models like GPT-4, Claude 3, and Llama 3. Stop manually copying and pasting files and start building your context with a simple, intuitive interface that combines file selection, text prompts, and voice dictation.


## The Problem It Solves

When working with LLMs on coding or analysis tasks, providing sufficient context is key to getting high-quality responses. This often involves:
1.  Writing a detailed main prompt or question.
2.  Finding all relevant files (`.py`, `.js`, `.css`, `.md`, etc.).
3.  Opening each file one by one.
4.  Copying the entire contents.
5.  Pasting it into the chat interface, carefully formatting it with file paths and code fences.

This process is tedious, error-prone, and kills productivity. **AI Context Builder automates this entire workflow.**

## Key Features

*   📂 **Intuitive File Explorer:** Navigate your entire file system with a familiar tree view.
*   🖱️ **Multi-File Selection:** Simply click on any files or directories you want to include in the context.
*   🎙️ **Voice-to-Text Dictation:** Use your microphone to dictate your prompt directly into the app, powered by a local, fast Whisper model.
*   ✨ **Automatic Formatting:** The tool automatically grabs the content of selected files and formats it perfectly for LLMs, including file paths and markdown code fences.
*   📋 **One-Click Generation:** Click "Generate" to combine your typed/spoken prompt with all selected file contexts into a single, clipboard-ready text block.
*   💾 **Persistent Save:** Save your generated context to a file and the app will remember the location for quick saves later.
*   🎨 **Modern Dark Theme:** A sleek, modern UI that's easy on the eyes.

## Technology Stack

This application is built with a focus on local, efficient processing.

*   **GUI:** [Tkinter](https://docs.python.org/3/library/tkinter.html) with the beautiful [sv-ttk](https://github.com/rdbende/sv-ttk) theme for a modern look and feel.
*   **Audio Transcription:** [faster-whisper](https://github.com/guillaumekln/faster-whisper), a highly optimized implementation of OpenAI's Whisper model, running locally on your CPU.
*   **Audio Processing:** [SoundDevice](https://python-sounddevice.readthedocs.io/), [Librosa](https://librosa.org/doc/latest/index.html), and [noisereduce](https://github.com/timsainb/noisereduce) for a clean audio capture and enhancement pipeline.
*   **Core Logic:** Python 3, with no external API dependencies.

## Installation

Follow these steps to get the AI Context Builder running on your local machine.

#### 1. Prerequisites
*   **Python 3.8+**
*   **Git**
*   **PortAudio** (This is a dependency for `sounddevice`. Installation varies by OS):
    *   **Windows:** Usually works out of the box with the Python wheel.
    *   **macOS:** `brew install portaudio`
    *   **Debian/Ubuntu:** `sudo apt-get install libportaudio2`

#### 2. Setup Steps

```bash
# 1. Clone the repository (replace YOUR_USERNAME with your GitHub username)
git clone git@github.com:PouyaZX4/PromptCreator.git
cd ai-prompt-builder

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# 3. Install the required packages
pip install -r requirements.txt