# License Plate Privacy Protector

An image-processing project that detects a vehicle's license plate in a photo and
blurs **only the plate**, protecting the owner's privacy while keeping the rest of
the image unchanged. Built with **Python** and **OpenCV**, using classic image-
processing techniques only (no machine learning or deep learning).

---

## 1. Overview

**Problem.** Photos of cars often reveal license plates, which can be traced back
to the owner's identity and location. Sharing such photos publicly is a privacy
risk.

**Solution.** The program automatically locates the license plate using classic
image-processing steps, then blurs that region only, leaving the rest of the photo
clear.

**Result.** A privacy-safe image, ready to share, with the plate concealed and all
other details preserved.

The project is delivered in two forms:
- `main.py` — a standalone script that processes an image and saves each stage.
- `app.py` — a Streamlit web interface where a user uploads an image and sees the
  full pipeline and the final result.

Both share the **same processing logic** (defined once in `main.py`), so behaviour
is identical.

---

## 2. Image-Processing Techniques Used

The project uses **five** techniques from the approved list, each with a real,
justified role in the pipeline (not added just to increase the count).

| # (from list) | Technique | Where it is used | Why it is needed |
|---|---|---|---|
| 1 | **Grayscale / color-space conversion** | `cv2.cvtColor(..., COLOR_BGR2GRAY)` | Edge detection and contour analysis require a single-channel image. It is the foundation of the whole pipeline. |
| 4 | **Image filtering / smoothing** | `cv2.GaussianBlur(gray, (5,5), 0)` | Removes noise so that Canny does not produce spurious edges, giving a cleaner edge map. |
| 5 | **Edge detection** | `cv2.Canny(blur, 50, 150)` | The **core** detection step. It extracts object outlines from which the rectangular plate is found. |
| 7 | **Image annotation** | `cv2.drawContours` + `cv2.putText` | Draws the detected plate boundary and a label on a separate demo image, for visualization only. |
| 2 | **Resizing / cropping (transformation)** | Center-crop to 9:16 + `cv2.resize` | Standardizes the final output to a mobile-friendly 9:16 portrait format. |

### Supporting tools (not counted as techniques)

- `cv2.findContours` — extracts closed shapes from the edge map.
- `cv2.approxPolyDP` — simplifies each shape to a polygon; a shape with **4 corners**
  is treated as a plate candidate.
- **Masking** (`np.zeros` + `drawContours` filled) — a binary selector that restricts
  the blur to the plate region only.

These are analysis/utility methods, not stand-alone techniques from the list.

---

## 3. Processing Pipeline

The image passes through the following ordered stages:

1. **Original Image** — the input photo is read at full resolution.
2. **Grayscale Conversion** — convert to a single channel.
3. **Noise Reduction (Filtering)** — Gaussian blur (5×5) to clean the image.
4. **Edge Detection** — Canny edge detection produces the edge map.
5. **Plate Detection (Annotation)** — find contours, keep the largest, and look for
   a 4-corner rectangle; the detected plate is outlined and labelled on a demo image.
6. **Privacy Protection (Final)** — a mask covers the plate region, a heavily blurred
   copy (Gaussian 51×51) is composited into that region only, and the result is
   cropped/resized to 9:16 for mobile.

### How the plate is located

```
Grayscale -> Blur -> Canny edges -> findContours -> approxPolyDP -> 4-corner shape
```

The core technique is **edge detection (Canny)**. Grayscale and filtering are
supporting steps that make the edges clean and reliable. `findContours` and
`approxPolyDP` then search the edge map for a rectangular shape (the plate).

---

## 4. Techniques That Were Tested and Removed

To keep every step meaningful, two techniques were tested and **removed** after
measuring their effect:

- **Contrast enhancement** (`convertScaleAbs`, alpha=1.5) — An ablation test (running
  the pipeline with and without each step) showed that on the test images, contrast
  enhancement **increased edge noise** and did not improve detection; in some cases it
  caused detection to fail. It was therefore removed.
- **Thresholding** (`cv2.threshold`) — In the original code the threshold result was
  computed and saved but **never used** by the detector (Canny operated on the blurred
  image, not on the threshold). It had no effect on detection, so it was removed rather
  than kept as dead code.

This keeps the final pipeline honest: every remaining step measurably contributes.

---

## 5. Limitations

The detection method is **classic and rule-based**, so it has clear limits:

- **Depends on a clean edge rectangle.** The plate must form a closed, 4-corner
  contour in the edge map. If the plate is small, tilted, low-contrast, or partly in
  shadow, its contour may not be detected.
- **Sensitive to cluttered backgrounds.** The code inspects the largest contours. When
  the background contains large rectangular structures (buildings, fences), the plate
  may fall outside the inspected shapes and be missed.
- **Can detect the wrong rectangle.** Because it accepts the first 4-corner shape it
  finds, other rectangular regions (grille, emblem, bumper openings) can occasionally
  be selected instead of the plate.
- **Resolution matters.** Downscaling the image too much removes the fine plate edges
  and breaks detection. For this reason, cropping/resizing is applied **at the end**,
  after detection runs on the full-resolution image.
- **Fixed parameters.** Canny thresholds and the polygon approximation value are fixed
  and tuned for typical images; very different lighting or angles may need retuning.
- **No machine learning.** A learning-based detector (e.g. Haar cascade or YOLO) would
  be far more robust, but was intentionally excluded per the project constraints.

**Best results** are obtained with photos where the plate is clearly visible, roughly
frontal, and the background is relatively simple.

---

## 6. Project Structure

```
LicensePlatePrivacy/
├── input/                     # input car images
│   └── car3.jpeg
├── output/                    # saved pipeline stages (created by main.py)
├── main.py                    # standalone script + process_image() function
├── app.py                     # Streamlit web interface
└── README.md
```

---

## 7. Requirements

- Python 3.8+
- OpenCV
- NumPy
- imutils
- Streamlit (only for the web interface)

Install everything with:

```bash
pip install opencv-python numpy imutils streamlit
```

---

## 8. How to Run

### Option A — Standalone script

1. Put a car image in the `input/` folder.
2. In `main.py`, set the image name (e.g. `cv2.imread("input/car3.jpeg")`).
3. Run:

```bash
python main.py
```

The processed stages are saved in the `output/` folder. If no plate is detected, a
message is printed and no output is saved (so a photo with a visible plate is never
produced by mistake).

### Option B — Web interface

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, upload a car image, and view the full
pipeline, the input-vs-output comparison, and a download button for the final image.

---

## 9. Summary

- **Techniques used:** Grayscale (1), Filtering/Smoothing (4), Edge Detection (5),
  Image Annotation (7), Resizing/Cropping (2) — **five techniques**, all with a real
  role.
- **Core detection technique:** Edge Detection (Canny).
- **Supporting steps:** Grayscale and Filtering.
- **Privacy mechanism:** masking + heavy Gaussian blur applied to the plate only.
- **Removed (no real effect):** Contrast enhancement and Thresholding.
- **Constraint respected:** classic image processing only, no ML/DL.