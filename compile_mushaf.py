"""
Mushaf Ashathili - Image Normalization and PDF Compiler
This script normalizes all raw scanned pages in pngs/ to uniform dimensions
(1488x2207) based on the maximum dimensions across the scan collection,
and losslessly compiles them into Mushaf-Ashathili.pdf.
"""

import os
import sys
import time
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import img2pdf

TARGET_W = 1488
TARGET_H = 2207
SRC_DIR = 'pngs'
NORM_DIR = 'pngs_normalised'
OUTPUT_PDF = 'Mushaf-Ashathili.pdf'


def normalize_pages():
    os.makedirs(NORM_DIR, exist_ok=True)
    ref_file = os.path.join(SRC_DIR, 'page0588.png')
    if not os.path.exists(ref_file):
        ref_file = os.path.join(SRC_DIR, sorted(os.listdir(SRC_DIR))[0])
    
    ref_img = Image.open(ref_file)
    pal_img = ref_img.copy()

    files = [f for f in sorted(os.listdir(SRC_DIR)) if f.lower().endswith('.png')]
    print(f"[+] Normalizing {len(files)} pages to {TARGET_W}x{TARGET_H}...")

    def process_page(fname):
        src_path = os.path.join(SRC_DIR, fname)
        dst_path = os.path.join(NORM_DIR, fname)
        with Image.open(src_path) as im:
            if im.size == (TARGET_W, TARGET_H):
                im.save(dst_path, optimize=True)
            else:
                resized = im.convert('RGB').resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
                quantized = resized.quantize(palette=pal_img, dither=Image.Dither.NONE)
                quantized.save(dst_path, optimize=True)
        return fname

    t0 = time.time()
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_page, files))
    t1 = time.time()
    print(f"[+] Normalized {len(results)} pages in {t1 - t0:.2f}s.")


def compile_pdf():
    images = [os.path.join(NORM_DIR, f) for f in sorted(os.listdir(NORM_DIR)) if f.lower().endswith('.png')]
    if not images:
        print("[-] No normalized images found. Run normalization first.")
        sys.exit(1)

    print(f"[+] Compiling {len(images)} normalized pages into '{OUTPUT_PDF}'...")
    t0 = time.time()
    with open(OUTPUT_PDF, 'wb') as f:
        f.write(img2pdf.convert(images))
    t1 = time.time()

    size_mb = os.path.getsize(OUTPUT_PDF) / (1024 * 1024)
    print(f"[+] PDF compiled successfully in {t1 - t0:.2f}s! Size: {size_mb:.2f} MB")


if __name__ == '__main__':
    normalize_pages()
    compile_pdf()
