# Scan Aligner

This is a tool for automatically aligning scanned copies of some source template.

This was motivated by the need to align answer sheets for exams before uploading them to Gradescope to make automatic grading easier and more accurate.

It consists of two scripts:
* `align.py`, which takes a template PDF and a PDF containing scanned pages, and outputs a PDF with the scanned pages each transformed to align with the template PDF
* `add_marker.py`, which takes a template PDF and adds the [fiducial markers](https://en.wikipedia.org/wiki/Fiducial_marker) necessary for alignment


## Installation

Requires Python 3. Install the required dependencies with `pip install -r requirements.txt`.

This tool also needs `pdftoppm`, which is a component of [Poppler](https://en.wikipedia.org/wiki/Poppler_(software)). You can install it on macOS with Homebrew: `brew install poppler`.


## Usage

`python3 align.py <path to template PDF> <path to the scanned PDF> [--output <path to save output PDF>]`

`python3 add_marker.py <path to input PDF> <path to save output PDF>`

