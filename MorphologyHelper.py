import os
import numpy as np
import cv2

# Define a kernel for morphology operations
KERNEL = np.ones((3, 3), np.uint8)


def process_image(filepath, kernel):
    """Processes a single binary image from a txt file and highlights differences in blue."""
    # Load the binary image from a txt file
    binary_image = np.loadtxt(filepath, dtype=int)

    # Convert binary to uint8 (0 or 255)
    binary_image = np.uint8(binary_image * 255)

    # Apply Morphological Operations
    denoised = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)  # Remove noise
    smoothed = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)  # Smooth edges

    # Fill holes
    filled = binary_image.copy()
    h, w = filled.shape
    mask = np.zeros((h+2, w+2), np.uint8)
    cv2.floodFill(filled, mask, (0, 0), 255)
    filled = cv2.bitwise_not(filled) | binary_image

    # Skeletonization
    skeleton = np.zeros_like(binary_image)
    temp_binary = binary_image.copy()
    while True:
        eroded = cv2.erode(temp_binary, kernel)
        temp = cv2.dilate(eroded, kernel)
        temp = cv2.subtract(temp_binary, temp)
        skeleton = cv2.bitwise_or(skeleton, temp)
        temp_binary = eroded.copy()
        if cv2.countNonZero(temp_binary) == 0:
            break

    # Convert original to BGR for coloring differences
    original_bgr = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)

    # Highlight differences in blue
    highlighted_denoised = highlight_changes(original_bgr, denoised)
    highlighted_smoothed = highlight_changes(original_bgr, smoothed)
    highlighted_filled = highlight_changes(original_bgr, filled)
    highlighted_skeleton = cv2.cvtColor(skeleton, cv2.COLOR_GRAY2BGR)  # Convert to 3-channel grayscale

    return binary_image, highlighted_denoised, highlighted_smoothed, highlighted_filled, highlighted_skeleton


def highlight_changes(original_bgr, transformed):
    """Highlights changes in blue compared to the original image."""
    difference = cv2.absdiff(original_bgr[:, :, 0], transformed)  # Compute difference in grayscale
    highlighted = original_bgr.copy()
    
    # Set changed pixels to blue (255, 0, 0) where difference is nonzero
    highlighted[difference > 0] = (0, 255, 0)
    
    return highlighted


def add_label(image, label):
    """Adds a text label below an image."""
    h, w = image.shape[:2]
    labeled_img = np.full((h + 30, w, 3), 255, dtype=np.uint8)  # Extra space for text
    labeled_img[:h, :] = image  # Copy the image
    cv2.putText(labeled_img, label, (10, h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    return labeled_img


def getMorphImagesFromFolder(txt_folder, output_folder):
    """Processes all .txt images in a folder and saves a combined image with morphology results."""
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(txt_folder):
        if filename.endswith(".txt"):
            filepath = os.path.join(txt_folder, filename)
            print(f"Processing {filename}...")

            # Process the image
            original, denoised, smoothed, filled, skeleton = process_image(filepath, KERNEL)

            # Create labeled images
            labeled_original = add_label(cv2.cvtColor(original, cv2.COLOR_GRAY2BGR), "Original")
            labeled_denoised = add_label(denoised, "Denoised")
            labeled_smoothed = add_label(smoothed, "Smoothed")
            labeled_filled = add_label(filled, "Filled")
            labeled_skeleton = add_label(skeleton, "Skeleton")

            # Combine all labeled images into one
            combined_image = np.hstack([labeled_original, labeled_denoised, labeled_smoothed, labeled_filled, labeled_skeleton])

            # Save the combined image
            base_name = os.path.splitext(filename)[0]
            output_image_path = os.path.join(output_folder, f"{base_name}_morphology.png")
            cv2.imwrite(output_image_path, combined_image)

    print("Processing complete. Results saved in the output folder.")
