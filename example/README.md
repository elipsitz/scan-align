# Example

First, add the fiducial markers to the sample answer sheet:

`python3 ../add_marker.py sheet.pdf marked_sheet.pdf`

Then, print this out and rescan it, or use the sample `scan.pdf`. Realign the scan with:

`python3 ../align.py marked_sheet.pdf scan.pdf --output aligned_scan.pdf`
