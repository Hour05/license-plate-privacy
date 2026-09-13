import cv2
import imutils
import numpy as np


def process_image(Car_image):
    """Detect the plate, blur it, and return all pipeline stages."""
    original = Car_image.copy()

    # Grayscale Conversion
    gray = cv2.cvtColor(Car_image, cv2.COLOR_BGR2GRAY) 
    # Filtering / Smoothing
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Edge Detection
    edges = cv2.Canny(blur, 50, 150)

    # Find Contours
    keypoints = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(keypoints)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    location = None
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 10, True)
        if len(approx) == 4:
            location = approx
            break

    annotated_image = original.copy()
    final_mobile = None

    if location is not None:
        # Image Annotation
        cv2.drawContours(annotated_image, [location], -1, (0, 255, 0), 3)
        cv2.putText(annotated_image, "License Plate Detected",(location[0][0][0], location[0][0][1] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Apply Mask on Detected Plate
        mask = np.zeros(gray.shape, np.uint8)
        cv2.drawContours(mask, [location], 0, 255, -1)

        # Blur the whole image, then replace only the plate region
        blurred = cv2.GaussianBlur(Car_image, (51, 51), 0)
        Car_image[mask == 255] = blurred[mask == 255]

        h, w = Car_image.shape[:2]
        if w * 16 > h * 9:                    # wider than 9:16 -> crop the sides
            side = h * 9 // 16
            x = (w - side) // 2
            cropped = Car_image[:, x:x + side]
        else:                                 # taller than 9:16 -> crop top/bottom
            side = w * 16 // 9
            y = (h - side) // 2
            cropped = Car_image[y:y + side, :]

        final_mobile = cv2.resize(cropped, (1080, 1920), interpolation=cv2.INTER_AREA)

    # return every stage
    return {
        "original": original,"gray": gray,"blur": blur,"edges": edges,
        "annotated": annotated_image,"final": final_mobile,"location": location,}

# runs ONLY when I execute:  python main.py alone
if __name__ == "__main__":
    img = cv2.imread("input/car3.jpeg")
    out = process_image(img)
    if out["final"] is not None:
        cv2.imwrite("output/06_final_result.jpg", out["final"])
        print("Processing completed!")
    else:
        print("No license plate detected. No output saved.")