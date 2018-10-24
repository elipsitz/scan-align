import argparse
import os
import subprocess
import sys
import tempfile

import cv2 as cv
import img2pdf
import numpy as np

scriptdir = os.path.dirname(os.path.abspath(__file__))
default_dpi = 300
jpeg_quality = 50


def pdf2png(filename, dpi=default_dpi):
    """
    Takes the PDF file at `filename` and converts it into a series of PNGs.
    Returns a list of filenames of the PNGs.
    Uses pdftoppm
    """
    d = tempfile.mkdtemp()
    cmd = ["pdftoppm", filename, d + "/out", "-png", "-r", str(dpi)]
    subprocess.run(cmd)
    filenames = sorted(os.listdir(d))
    paths = [os.path.join(d, x) for x in filenames]
    return paths


def dist(pt1, pt2):
    dx = pt1[0] - pt2[0]
    dy = pt1[1] - pt2[1]
    dist2 = (dx ** 2.0) + (dy ** 2.0)
    return dist2 ** 0.5


def imthreshold(im):
    _, out = cv.threshold(im, 127, 255, cv.THRESH_BINARY)
    return out


def find_markers(im):
    threshold = 0.8
    method = cv.TM_CCORR_NORMED

    img = im.copy()
    res = cv.matchTemplate(img, marker, method)

    loc = np.where(res >= threshold)
    pts = list(zip(*loc[::-1]))

    grouped_points = []
    while len(pts):
        pt = pts[0]
        pts = pts[1:]
        group = [pt]
        remainder = []
        for x in pts:
            if dist(x, pt) < (marker_w / 2.0):
                group.append(x)
            else:
                remainder.append(x)
        pts = remainder
        grouped_points.append(group)

    points = [max(g, key=lambda x: res[x[1], x[0]]) for g in grouped_points]
    vals = [res[x[1], x[0]] for x in points]
    points = [(p[0] + (marker_w // 2), p[1] + (marker_h // 2)) for p in points]
    return points


def align_points(points):
    """
    Given three points corresponding to markers,
    returns them in a standard orientation: top-left, top-right, bottom-left
    """

    pt1, pt2, pt3 = points
    dist12 = dist(pt1, pt2)
    dist23 = dist(pt2, pt3)
    dist13 = dist(pt1, pt3)
    maxdist = max(dist12, dist23, dist13)

    # origin (top-left) is opposite of the largest distance
    origin = None
    if maxdist == dist12:
        origin = pt3
    if maxdist == dist23:
        origin = pt1
    if maxdist == dist13:
        origin = pt2

    return sorted(
        points, key=lambda x: dist(origin, x)
    )  # todo fix, relies on rectangle (not true)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aligns scanned PDFs to a template")
    parser.add_argument("template", type=str, help="path to the template PDF")
    parser.add_argument("input", type=str, help="path to the scanned PDF")
    parser.add_argument("--output", type=str, help="path to output the aligned PDF")
    args = parser.parse_args()
    if not args.output:
        args.output = args.input + "-aligned.pdf"

    print("Loading marker...")
    marker_size = 0.35
    marker_w = marker_h = int(default_dpi * marker_size)
    marker_filename = pdf2png(scriptdir + "/marker.pdf", dpi=marker_w)[0]
    marker = cv.imread(marker_filename, 0)
    marker = imthreshold(marker)

    print("Loading template...")
    template_png = pdf2png(args.template)[0]
    template_img = cv.imread(template_png, 0)
    template_img = imthreshold(template_img)
    template_points = align_points(find_markers(template_img))

    print("Loading scan (this may take a while)...")
    input_pngs = pdf2png(args.input)
    print("Done.")

    outfiles = []
    outdir = tempfile.mkdtemp()
    for page, input_filename in enumerate(input_pngs):
        print("Matching page {} / {}".format(page + 1, len(input_pngs)))
        img = cv.imread(input_filename, 0)

        points = find_markers(imthreshold(img))
        points = align_points(points)
        M = cv.getAffineTransform(np.float32(points), np.float32(template_points))
        dst = cv.warpAffine(
            img,
            M,
            template_img.shape[::-1],
            borderMode=cv.BORDER_CONSTANT,
            borderValue=(255, 255, 255),
        )

        output_filename = outdir + os.path.basename(input_filename) + ".jpg"
        outfiles.append(output_filename)
        cv.imwrite(output_filename, dst, [cv.IMWRITE_JPEG_QUALITY, jpeg_quality])

    print("Writing output...")
    with open(args.output, "wb") as f:
        f.write(img2pdf.convert(outfiles))
