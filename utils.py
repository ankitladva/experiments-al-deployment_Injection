import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import colorsys
import os
from pathlib import Path
import json
import datetime

def extract_face_region(image):
    """
    Extract the face region from an image using a face detector.
    Returns the face region or the original image if no face is detected.
    """
    if image is None:
        print("Error: Invalid image provided to face detection")
        return None, None
    
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Load face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    
    if len(faces) > 0:
        # Take the largest face
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = largest_face
        
        # Extract face region with some margin
        margin = 20
        x_start = max(0, x - margin)
        y_start = max(0, y - margin)
        x_end = min(image.shape[1], x + w + margin)
        y_end = min(image.shape[0], y + h + margin)
        
        return image[y_start:y_end, x_start:x_end], (x_start, y_start, x_end, y_end)
    else:
        # print("Warning: No face detected in image")
        return image, (0, 0, image.shape[1], image.shape[0])

# def get_dominant_colors(image, n_colors=5,debug=False):

#     """
#     Extract the dominant colors from an image using K-means clustering.
#     """
#     if image is None or image.size == 0:
#         print("Warning: Empty image provided to color analysis")
#         return []
    
#     # Reshape the image to be a list of pixels
#     pixels = image.reshape(-1, 3)
    
#     if debug:
#         # Visualize effects of different black pixel thresholds
#         thresholds = [10, 20, 30, 40, 50]
#         plt.figure(figsize=(15, 8))
        
#         # Original image
#         plt.subplot(2, 3, 1)
#         plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#         plt.title('Original Image')
#         plt.axis('off')
        
#         # Show effect of different thresholds
#         for idx, thresh in enumerate(thresholds, 2):
#             # Create mask for non-black pixels
#             non_black_mask = np.sum(pixels, axis=1) > thresh
#             filtered_image = image.copy()
            
#             # Create visualization mask
#             mask_3d = np.repeat(non_black_mask.reshape(image.shape[0], image.shape[1], 1), 3, axis=2)
#             filtered_image[~mask_3d] = 0  # Set black pixels to zero
            
#             plt.subplot(2, 3, idx)
#             plt.imshow(cv2.cvtColor(filtered_image, cv2.COLOR_BGR2RGB))
#             plt.title(f'Threshold = {thresh}\nPixels Kept: {(100*np.sum(non_black_mask)/len(non_black_mask)):.1f}%')
#             plt.axis('off')
        
#         plt.tight_layout()
#         plt.show()
        
#         # Show pixel intensity distribution
#         plt.figure(figsize=(10, 4))
#         pixel_sums = np.sum(pixels, axis=1)
#         plt.hist(pixel_sums, bins=50, color='blue', alpha=0.7)
#         plt.axvline(x=30, color='red', linestyle='--', label='Current Threshold (30)')
#         plt.title('Pixel Intensity Distribution')
#         plt.xlabel('Sum of RGB Values')
#         plt.ylabel('Number of Pixels')
#         plt.legend()
#         plt.grid(True, alpha=0.3)
#         plt.show()
#     # Filter out black pixels (near zero values in all channels)
#     non_black_pixels = pixels[np.sum(pixels, axis=1) > 30]
    
    
#     if len(non_black_pixels) < n_colors:
#         print(f"Warning: Not enough non-black pixels ({len(non_black_pixels)}) for clustering")
#         if len(non_black_pixels) == 0:
#             return []
#         n_colors = max(1, len(non_black_pixels))
    
#     # Perform K-means clustering
#     try:
#         kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
#         kmeans.fit(non_black_pixels)
        
#         # Get the colors
#         colors = kmeans.cluster_centers_.astype(int)
        
#         # Get the percentage of each color
#         labels = kmeans.labels_
#         counts = np.bincount(labels)
#         percentages = counts / len(labels) * 100
        
#         return list(zip(colors, percentages))
#     except Exception as e:
#         print(f"Error in color clustering: {e}")
#         return []
def get_dominant_colors(image, n_colors=5, debug=False):
    """
    Extract the dominant colors from an image using K-means clustering.
    """
    if image is None or image.size == 0:
        print("Warning: Empty image provided to color analysis")
        return []
    
    # Check and reshape image properly
    if len(image.shape) == 2:
        # Convert single channel to 3 channels
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif len(image.shape) == 3 and image.shape[2] == 1:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    # Ensure correct shape before reshaping to 2D
    if debug:
        print(f"Original image shape: {image.shape}")
    
    # # Reshape maintaining the color channels
    # try:
    #     pixels = image.reshape(-1, image.shape[-1])
    #     if debug:
    #         print(f"Reshaped pixels shape: {pixels.shape}")
    # except Exception as e:
    #     print(f"Error in reshaping: {e}")
    #     return []
    # Get original dimensions
    h, w = image.shape[:2]
    
    # Reshape the image to be a list of pixels
    pixels = image.reshape(-1, 3)
    
    if debug:
        # Visualize effects of different black pixel thresholds
        thresholds = [10, 20, 30, 40, 50]
        plt.figure(figsize=(15, 8))
        
        # Original image
        plt.subplot(2, 3, 1)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.title('Original Image')
        plt.axis('off')
        
        # Show effect of different thresholds
        for idx, thresh in enumerate(thresholds, 2):
            try:
                # Create mask for non-black pixels
                non_black_mask = np.sum(pixels, axis=1) > thresh
                filtered_image = image.copy()
                
                # # Fix the mask reshaping to match image dimensions
                # mask_3d = non_black_mask.reshape(image.shape[0], image.shape[1])
                # mask_3d = np.stack([mask_3d] * 3, axis=2)  
                
                # # Create visualization mask
                # # mask_3d = np.repeat(non_black_mask.reshape(image.shape[0], -1, 1), 3, axis=2)
                # filtered_image[~mask_3d] = 0  # Set black pixels to zero
                # Reshape mask to match image dimensions
                # mask_2d = non_black_mask.reshape(image.shape[0], image.shape[1])
                # # Reshape mask to match image dimensions properly
                # h, w = image.shape[:2]
                # mask_2d = non_black_mask.reshape(h, w)
                
                # # Create 3-channel mask
                # mask_3d = np.repeat(mask_2d[..., np.newaxis], 3, axis=2)
                
                # # Apply mask
                # filtered_image = filtered_image * mask_3d
                # # Apply mask to each channel
                # for c in range(3):
                #     filtered_image[:,:,c] = filtered_image[:,:,c] * mask_2d
                # Reshape mask to match image dimensions
                # mask_2d = non_black_mask.reshape(h, w)
                
                # # Apply mask to each channel separately
                # for c in range(3):
                #     filtered_image[:,:,c] = filtered_image[:,:,c] * mask_2d
                # Reshape mask to match original image dimensions
                # mask_2d = non_black_mask.reshape(image.shape[0], -1)  # -1 infers correct width
                
                # # Expand mask to 3 channels using broadcasting
                # filtered_image = filtered_image * mask_2d[..., np.newaxis]
                h, w = image.shape[:2]
                mask_2d = non_black_mask.reshape(h, w)
                
                # Apply mask to all channels simultaneously
                filtered_image = filtered_image * mask_2d[:, :, np.newaxis]

                plt.subplot(2, 3, idx)
                plt.imshow(cv2.cvtColor(filtered_image, cv2.COLOR_BGR2RGB))
                plt.title(f'Threshold = {thresh}\nPixels Kept: {(100*np.sum(non_black_mask)/len(non_black_mask)):.1f}%')
                plt.axis('off')
            except Exception as e:
                print(f"Error in threshold visualization {thresh}: {e}")
                continue
        
        plt.tight_layout()
        plt.show()
        
        # Show pixel intensity distribution
        plt.figure(figsize=(10, 4))
        pixel_sums = np.sum(pixels, axis=1)
        plt.hist(pixel_sums, bins=50, color='blue', alpha=0.7)
        plt.axvline(x=30, color='red', linestyle='--', label='Current Threshold (30)')
        plt.title('Pixel Intensity Distribution')
        plt.xlabel('Sum of RGB Values')
        plt.ylabel('Number of Pixels')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    # Filter out black pixels (near zero values in all channels)
    try:
        non_black_pixels = pixels[np.sum(pixels, axis=1) > 30]
    except Exception as e:
        print(f"Error in filtering black pixels: {e}")
        return []
    
    if len(non_black_pixels) < n_colors:
        print(f"Warning: Not enough non-black pixels ({len(non_black_pixels)}) for clustering")
        if len(non_black_pixels) == 0:
            return []
        n_colors = max(1, len(non_black_pixels))
    
    # Perform K-means clustering
    try:
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(non_black_pixels)
        
        # Get the colors
        colors = kmeans.cluster_centers_.astype(int)
        
        # Get the percentage of each color
        labels = kmeans.labels_
        counts = np.bincount(labels)
        percentages = counts / len(labels) * 100
        
        return list(zip(colors, percentages))
    except Exception as e:
        print(f"Error in color clustering: {e}")
        return []
def color_to_name(rgb):
    """
    Convert RGB color to a human-readable color name based on HSV color space.
    """
    # Convert RGB to HSV
    r, g, b = rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    # Convert hue to degrees
    h *= 360
    
    # Define color ranges for common colors
    if s < 0.15:
        if v < 0.30:
            return "Black"
        elif v > 0.80:
            return "White"
        else:
            return "Gray"
    
    brightness = ""
    if v < 0.3:
        brightness = "Dark "
    elif v > 0.7:
        brightness = "Light "
    
    if s < 0.4:
        saturation = "Pale "
    else:
        saturation = ""
    
    if h < 30 or h > 330:
        color_name = "Red"
    elif h < 90:
        color_name = "Yellow"
    elif h < 150:
        color_name = "Green"
    elif h < 210:
        color_name = "Cyan"
    elif h < 270:
        color_name = "Blue"
    elif h < 330:
        color_name = "Magenta"
    else:
        color_name = "Red"
    
    return brightness + saturation + color_name

def analyze_reflection(no_reflection_frame, reflection_frame, threshold=20, region_focus='full',debug=False):
    """
    Analyze the reflection by comparing frames with and without reflection.
    
    Parameters:
    - no_reflection_frame: Frame without color reflection
    - reflection_frame: Frame with color reflection
    - threshold: Sensitivity threshold for detecting differences
    - region_focus: 'full', 'face', 'forehead', 'cheeks' - region to focus on
    """
    
    if no_reflection_frame is None or reflection_frame is None:
        print("Error: Invalid frames provided")
        return None
    
    # Get image resolutions
    nrf_height, nrf_width = no_reflection_frame.shape[:2]
    rf_height, rf_width = reflection_frame.shape[:2]
    
    if debug:
        plt.figure(figsize=(15, 10))
        plt.subplot(231)
        plt.imshow(cv2.cvtColor(no_reflection_frame, cv2.COLOR_BGR2RGB))
        plt.title(f'Step 1: Base Frame ({nrf_width}x{nrf_height})')
        plt.axis('off')
        
        plt.subplot(232)
        plt.imshow(cv2.cvtColor(reflection_frame, cv2.COLOR_BGR2RGB))
        plt.title(f'Step 2: Reflection Frame ({rf_width}x{rf_height})')
        plt.axis('off')
    
    # Step 3: Face Detection and ROI Extraction
    nrf_face, nrf_coords = extract_face_region(no_reflection_frame)
    rf_face, rf_coords = extract_face_region(reflection_frame)
    
    # Create face detection visualization
    nrf_face_vis = no_reflection_frame.copy()
    rf_face_vis = reflection_frame.copy()
    
    # Draw face detection rectangles
    if nrf_coords:
        x, y, x2, y2 = nrf_coords
        cv2.rectangle(nrf_face_vis, (x, y), (x2, y2), (0, 255, 0), 2)
        cv2.putText(nrf_face_vis, f"Face: {x2-x}x{y2-y}", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    if rf_coords:
        x, y, x2, y2 = rf_coords
        cv2.rectangle(rf_face_vis, (x, y), (x2, y2), (0, 255, 0), 2)
        cv2.putText(rf_face_vis, f"Face: {x2-x}x{y2-y}", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    if debug:
        plt.subplot(233)
        if nrf_face is not None:
            plt.imshow(cv2.cvtColor(nrf_face_vis, cv2.COLOR_BGR2RGB))
            plt.title('Step 3: Face Detection')
        plt.axis('off')
    
    if nrf_face is None or rf_face is None:
        print("Error: Failed to extract face regions")
        return None
    
    # Resize the face regions to match dimensions
    min_height = min(nrf_face.shape[0], rf_face.shape[0])
    min_width = min(nrf_face.shape[1], rf_face.shape[1])
    
    # Ensure the dimensions are valid
    if min_height <= 0 or min_width <= 0:
        print("Error: Invalid face dimensions")
        return None
    
    nrf_face = cv2.resize(nrf_face, (min_width, min_height))
    rf_face = cv2.resize(rf_face, (min_width, min_height))
    
    # Define regions of interest based on face anatomy
    height, width = nrf_face.shape[:2]
    regions = {
        'full': (0, 0, width, height),
        'face': (width//6, height//6, width*5//6, height*5//6),
        'forehead': (width//6, height//6, width*5//6, height//3),
        'cheeks': (width//6, height//3, width*5//6, height*2//3)
    }
    
    roi = regions.get(region_focus, regions['full'])
    x, y, x2, y2 = roi
    
    # Safety checks for ROI boundaries
    x = max(0, min(x, width-1))
    y = max(0, min(y, height-1))
    x2 = max(x+1, min(x2, width))
    y2 = max(y+1, min(y2, height))
    
    nrf_roi = nrf_face[y:y2, x:x2]
    rf_roi = rf_face[y:y2, x:x2]
    
    # Calculate the difference
    diff = cv2.absdiff(rf_roi, nrf_roi)
    if debug:
        plt.subplot(234)
        plt.imshow(cv2.cvtColor(diff, cv2.COLOR_BGR2RGB))
        plt.title('Step 4: Absolute Difference')
        plt.axis('off')
    
    # Enhance the difference for better visualization
    diff_enhanced = cv2.convertScaleAbs(diff, alpha=2.0, beta=0)
    
    # Create a heat map for better visualization
    diff_heat = np.sum(diff, axis=2)
    diff_heat_norm = cv2.normalize(diff_heat, None, 0, 255, cv2.NORM_MINMAX)
    diff_heat_color = cv2.applyColorMap(diff_heat_norm.astype(np.uint8), cv2.COLORMAP_JET)
    
    # Threshold the difference to get only significant changes
    mask = np.any(diff > threshold, axis=2)
    diff_masked = np.zeros_like(diff)
    diff_masked[mask] = diff[mask]
    
    if debug:
        plt.subplot(235)
        plt.imshow(mask, cmap='gray')
        plt.title(f'Step 5: Threshold Mask (t={threshold})')
        plt.axis('off')
        
        plt.subplot(236)
        plt.imshow(cv2.cvtColor(diff_masked, cv2.COLOR_BGR2RGB))
        plt.title('Step 6: Masked Difference')
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
    
    # Get dominant colors in the difference image
    if np.any(mask):
        reflection_colors = get_dominant_colors(diff_masked[mask],debug=False)
    else:
        reflection_colors = []
    
    # Add color names
    reflection_colors_with_names = [(color, percentage, color_to_name(color)) 
                                   for color, percentage in reflection_colors]
    
    # Calculate overall reflection intensity
    reflection_intensity = np.mean(diff)
    channel_means = np.mean(diff, axis=(0,1))
    max_channel_diff = np.max(channel_means)
    dominant_channel = np.argmax(channel_means)
    channel_names = ['Blue', 'Green', 'Red']  # BGR order in OpenCV
    
    # Add BGR values to stats for clearer output
    channel_values = {
        'Blue': float(channel_means[0]),
        'Green': float(channel_means[1]),
        'Red': float(channel_means[2])
    }
    
    # Create overlay for reflection highlighting
    overlay = rf_face.copy()
    for i in range(3):
        channel_mask = np.zeros_like(rf_face[:,:,0], dtype=bool)
        roi_mask = diff[:,:,i] > threshold
        channel_mask[y:y2, x:x2] = roi_mask
        overlay[:,:,i][channel_mask] = np.minimum(255, overlay[:,:,i][channel_mask] + 50)
    
    # Create heat map overlay
    heat_overlay = rf_face.copy()
    heat_mask = np.zeros((height, width), dtype=bool)
    heat_mask[y:y2, x:x2] = diff_heat > threshold * 3
    
    # Create a colored overlay
    heat_colored = np.zeros_like(heat_overlay)
    heat_colored[:,:,2][heat_mask] = 255
    
    # Blend with original image
    heat_vis = cv2.addWeighted(rf_face, 0.7, heat_colored, 0.3, 0)
    
    # Apply colorized difference as semi-transparent overlay
    alpha_overlay = 0.6
    reflection_highlighted = cv2.addWeighted(rf_face, 1 - alpha_overlay, overlay, alpha_overlay, 0)
    
    # Calculate key statistics for comparison
    stats = {
        'reflection_intensity': float(reflection_intensity),
        'max_channel_diff': float(max_channel_diff),
        'dominant_channel': channel_names[dominant_channel],
        'pixel_percentage_affected': float(100 * np.sum(mask) / mask.size),
        'channel_values': channel_values,
        'image_resolution': {
            'base_frame': f"{nrf_width}x{nrf_height}",
            'reflection_frame': f"{rf_width}x{rf_height}",
            'face_region': f"{min_width}x{min_height}",
            'roi': f"{x2-x}x{y2-y}"
        }
    }
    
    return {
        'no_reflection_face': nrf_face,
        'reflection_face': rf_face,
        'difference': diff,
        'difference_enhanced': diff_enhanced,
        'difference_heat': diff_heat_color,
        'difference_masked': diff_masked,
        'reflection_highlighted': reflection_highlighted,
        'heat_visualization': heat_vis,
        'reflection_colors': reflection_colors_with_names,
        'stats': stats,
        'roi': roi,
        'face_detection': {
            'base_frame': nrf_face_vis,
            'reflection_frame': rf_face_vis
        }
    }

def visualize_results(results, save_path=None):
    """
    Visualize the analysis results with enhanced graphics.
    """
    if results is None:
        print("Error: No results to visualize")
        return
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.patch.set_facecolor('white')  # White background
    
    # No reflection face
    axes[0, 0].imshow(cv2.cvtColor(results['no_reflection_face'], cv2.COLOR_BGR2RGB))
    axes[0, 0].set_title('No Reflection Face', fontsize=14, fontweight='bold')
    axes[0, 0].axis('off')
    
    # Reflection face
    axes[0, 1].imshow(cv2.cvtColor(results['reflection_face'], cv2.COLOR_BGR2RGB))
    axes[0, 1].set_title('Reflection Face', fontsize=14, fontweight='bold')
    axes[0, 1].axis('off')
    
    # Heat visualization
    axes[0, 2].imshow(cv2.cvtColor(results['heat_visualization'], cv2.COLOR_BGR2RGB))
    axes[0, 2].set_title('Heat Map Overlay', fontsize=14, fontweight='bold')
    axes[0, 2].axis('off')
    
    # Draw a rectangle for the ROI on the original images
    x, y, x2, y2 = results['roi']
    rect = plt.Rectangle((x, y), x2-x, y2-y, linewidth=2, edgecolor='yellow', facecolor='none')
    axes[0, 0].add_patch(rect)
    rect = plt.Rectangle((x, y), x2-x, y2-y, linewidth=2, edgecolor='yellow', facecolor='none')
    axes[0, 1].add_patch(rect)
    
    # Difference visualization
    diff_rgb = cv2.cvtColor(results['difference_enhanced'], cv2.COLOR_BGR2RGB)
    axes[1, 0].imshow(diff_rgb)
    axes[1, 0].set_title('Enhanced Difference', fontsize=14, fontweight='bold')
    axes[1, 0].axis('off')
    
    # Stats visualization with color coding
    axes[1, 1].axis('off')
    
    # Background box for stats
    rect = plt.Rectangle((0.1, 0.1), 0.8, 0.8, linewidth=1, edgecolor='black', 
                         facecolor='lightgray', alpha=0.2, transform=axes[1, 1].transAxes)
    axes[1, 1].add_patch(rect)
    
    # Stats with improved formatting
    stats_text = [
        f"Reflection Intensity: {results['stats']['reflection_intensity']:.2f}",
        f"Affected Pixels: {results['stats']['pixel_percentage_affected']:.1f}%",
        f"Dominant Channel: {results['stats']['dominant_channel']}",
        f"R: {results['stats']['channel_values']['Red']:.2f}",
        f"G: {results['stats']['channel_values']['Green']:.2f}",
        f"B: {results['stats']['channel_values']['Blue']:.2f}"
    ]
    
    # Add color to the dominant channel
    dominant = results['stats']['dominant_channel']
    colors = ['black'] * len(stats_text)
    for i, text in enumerate(stats_text):
        if dominant in text and "Dominant" not in text:
            colors[i] = {'Red': 'darkred', 'Green': 'darkgreen', 'Blue': 'darkblue'}[dominant]
    
    for i, (text, color) in enumerate(zip(stats_text, colors)):
        y_pos = 0.8 - i * 0.1
        axes[1, 1].text(0.5, y_pos, text, horizontalalignment='center', 
                      fontsize=12, fontweight='bold', color=color)
    
    axes[1, 1].set_title('Reflection Analysis', fontsize=14, fontweight='bold')
    
    # Color distribution visualization
    axes[1, 2].axis('off')
    axes[1, 2].set_title('Detected Colors', fontsize=14, fontweight='bold')
    
    if len(results['reflection_colors']) > 0:
        colors = [color[0] for color in results['reflection_colors']]
        percentages = [color[1] for color in results['reflection_colors']]
        color_names = [color[2] for color in results['reflection_colors']]
        
        # Sort by percentage
        sorted_indices = np.argsort(percentages)[::-1]
        colors = [colors[i] for i in sorted_indices]
        percentages = [percentages[i] for i in sorted_indices]
        color_names = [color_names[i] for i in sorted_indices]
        
        # Only show top 4 colors for clarity
        if len(colors) > 4:
            colors = colors[:4]
            percentages = percentages[:4]
            color_names = color_names[:4]
        
        # Background for colors
        rect = plt.Rectangle((0.1, 0.1), 0.8, 0.8, linewidth=1, edgecolor='black', 
                         facecolor='white', alpha=0.2, transform=axes[1, 2].transAxes)
        axes[1, 2].add_patch(rect)
        
        # Draw color swatches and labels
        for i, (color, percentage, name) in enumerate(zip(colors, percentages, color_names)):
            y_pos = 0.8 - i * 0.15
            
            # Color swatch
            swatch = plt.Rectangle((0.15, y_pos-0.06), 0.1, 0.1, 
                                   facecolor=[c/255 for c in color[::-1]])  # RGB for matplotlib
            axes[1, 2].add_patch(swatch)
            
            # Text label
            axes[1, 2].text(0.3, y_pos, f"{name}: {percentage:.1f}%", 
                          va='center', fontsize=11)
            
    else:
        axes[1, 2].text(0.5, 0.5, "No significant color changes detected", 
                      horizontalalignment='center', fontsize=12)
    
    plt.tight_layout()
    
    # Save the visualization if a path is provided
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig

def combine_analysis_images(image_paths, save_path, titles=None):
    """
    Combine multiple images into a single grid image and save it.
    """
    import matplotlib.pyplot as plt
    import cv2
    import numpy as np
    n = len(image_paths)
    cols = 3
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 5*rows))
    axes = axes.flatten()
    for i, img_path in enumerate(image_paths):
        img = cv2.imread(img_path)
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            axes[i].imshow(img)
            axes[i].axis('off')
            if titles and i < len(titles):
                axes[i].set_title(titles[i])
        else:
            axes[i].set_visible(False)
    for j in range(i+1, len(axes)):
        axes[j].set_visible(False)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)

def compare_all_frames(base_frame_path, colored_frame_paths, user_id, output_dir="results", threshold=20):
    """
    Compare a base frame with multiple colored frames and generate analysis for each.
    Now saves results in a user-specific folder and combines all analysis images for each color.
    """
    import json, datetime
    # Create user-specific visualization directory
    user_vis_dir = os.path.join("data", "visualization", f"{user_id}_analysis")
    os.makedirs(user_vis_dir, exist_ok=True)
    
    # Load base frame
    base_frame = cv2.imread(base_frame_path)
    if base_frame is None:
        print(f"Error: Could not load base frame from {base_frame_path}")
        return None
    
    results = []
    for frame_path in colored_frame_paths:
        try:
            color_name = Path(frame_path).stem.split('_')[-1]
            vis_path = os.path.join(user_vis_dir, f"analysis_{color_name}")
            os.makedirs(vis_path, exist_ok=True)
            
            colored_frame = cv2.imread(frame_path)
            if colored_frame is None:
                print(f"Error: Could not load colored frame from {frame_path}")
                continue
            analysis = analyze_reflection(base_frame, colored_frame, threshold=threshold)
            if analysis is None:
                print(f"Error: Analysis failed for {frame_path}")
                continue
            # Save individual analysis components
            img_files = []
            img_titles = []
            def save_img_and_track(key, title):
                out_path = os.path.join(vis_path, f"{key}.png")
                cv2.imwrite(out_path, analysis[key])
                img_files.append(out_path)
                img_titles.append(title)
            save_img_and_track('no_reflection_face', 'Base Face')
            save_img_and_track('reflection_face', 'Colored Face')
            save_img_and_track('difference', 'Difference')
            save_img_and_track('difference_enhanced', 'Enhanced Diff')
            save_img_and_track('difference_heat', 'Heatmap')
            save_img_and_track('difference_masked', 'Masked Diff')
            save_img_and_track('reflection_highlighted', 'Reflection Highlight')
            save_img_and_track('heat_visualization', 'Heat Visualization')
            # Face detection overlays
            cv2.imwrite(os.path.join(vis_path, "face_detection_base.png"), analysis['face_detection']['base_frame'])
            img_files.append(os.path.join(vis_path, "face_detection_base.png"))
            img_titles.append('Face Detected (Base)')
            cv2.imwrite(os.path.join(vis_path, "face_detection_colored.png"), analysis['face_detection']['reflection_frame'])
            img_files.append(os.path.join(vis_path, "face_detection_colored.png"))
            img_titles.append('Face Detected (Colored)')
            # Save resolution info
            resolution_info = {
                'image_resolution': analysis['stats']['image_resolution'],
                'timestamp': datetime.datetime.now().isoformat()
            }
            with open(os.path.join(vis_path, "resolution_info.json"), 'w') as f:
                json.dump(resolution_info, f, indent=4)
            # Combine all images for this color into a grid
            combined_path = os.path.join(vis_path, f"combined_{color_name}.png")
            combine_analysis_images(img_files, combined_path, img_titles)
            # Extract essential results for summary
            summary = {
                'color': color_name,
                'path': frame_path,
                'intensity': analysis['stats']['reflection_intensity'],
                'dominant_channel': analysis['stats']['dominant_channel'],
                'affected_pixels': analysis['stats']['pixel_percentage_affected'],
                'channel_values': analysis['stats']['channel_values'],
                'image_resolution': analysis['stats']['image_resolution'],
                'detected_colors': [(color, pct, name) for color, pct, name in analysis['reflection_colors'] if pct > 5]
            }
            results.append(summary)
        except Exception as e:
            print(f"Error processing {frame_path}: {e}")
    # Generate and save summary visualization
    if results:
        summary_path = os.path.join(user_vis_dir, "summary_analysis.png")
        generate_summary_visualization(results, summary_path)
    return results

def generate_summary_visualization(results, output_path):
    """
    Generate a summary visualization comparing all frames.
    """
    if not results:
        print("No results to visualize")
        return
    
    # Sort results by color name
    results.sort(key=lambda x: x['color'])
    
    # Set up the figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10))
    fig.patch.set_facecolor('white')
    
    # Color names and values for bar chart
    colors = [r['color'] for r in results]
    r_values = [r['channel_values']['Red'] for r in results]
    g_values = [r['channel_values']['Green'] for r in results]
    b_values = [r['channel_values']['Blue'] for r in results]
    
    # Bar positions
    x = np.arange(len(colors))
    width = 0.25
    
    # Create bars
    ax1.bar(x - width, r_values, width, label='Red', color='red', alpha=0.7)
    ax1.bar(x, g_values, width, label='Green', color='green', alpha=0.7)
    ax1.bar(x + width, b_values, width, label='Blue', color='blue', alpha=0.7)
    
    # Add labels and title
    ax1.set_xlabel('Color Frame', fontweight='bold')
    ax1.set_ylabel('Channel Difference Value', fontweight='bold')
    ax1.set_title('RGB Channel Differences by Color Frame', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(colors, rotation=45)
    ax1.legend()
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # Second plot: Affected pixels vs Intensity
    intensities = [r['intensity'] for r in results]
    affected = [r['affected_pixels'] for r in results]
    
    # Create scatter plot
    scatter = ax2.scatter(intensities, affected, c=range(len(colors)), 
                         cmap='viridis', s=100, alpha=0.8)
    
    # Label each point with its color name
    for i, color in enumerate(colors):
        ax2.annotate(color, (intensities[i], affected[i]), 
                    xytext=(5, 5), textcoords='offset points')
    
    # Add labels and title
    ax2.set_xlabel('Reflection Intensity', fontweight='bold')
    ax2.set_ylabel('Affected Pixels (%)', fontweight='bold')
    ax2.set_title('Intensity vs Coverage by Color Frame', fontweight='bold')
    ax2.grid(True, linestyle='--', alpha=0.7)
    
    # Add a colorbar
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label('Color Frame Index', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

def main3():
    """
    Main function for analyzing color reflections in KYC video frames.
    """
    ###Aaryan 
    import glob
    base_dir = "/Users/ankitladva/Desktop/idfy/active-liveness1/experiments/data/images/36570f21-68c2-4d3b-9717-8cdb2e3eb886"
    transparent="/Users/ankitladva/Desktop/idfy/active-liveness1/experiments/data/images/36570f21-68c2-4d3b-9717-8cdb2e3eb886/1744959510474_transparent.png"
    # Define base frame (no reflection) and colored frames
    # base_frame_path = os.path.join(base_dir, "1743677605166_Black.png")  # Using Black as base
    # base_frame_path = os.path.join(base_dir, "1743677605166_Black.png")  # Using Black as base
    base_frame_path = transparent
#     colored_frame_paths = [
#     os.path.join(base_dir, "1744872705288_blue.png"),
#     os.path.join(base_dir, "1744872705988_yellow.png"),
#     os.path.join(base_dir, "1744872706704_green.png"),
#     os.path.join(base_dir, "1744872708122_red.png"),
#     os.path.join(base_dir, "1744872708823_blue.png"),
#     os.path.join(base_dir, "1744872709537_cyan.png"),
#     os.path.join(base_dir, "1744872710238_green.png")
# ]
    images = glob.glob(os.path.join(base_dir, "*.png"))
    images.sort()  # Sort to ensure consistent order
    
    # if len(images) < 2:
    #     print(f"Warning: Not enough images in {base_dir}")
    #     continue
        
    # Use the first transparent image as base
    base_frame_path = None
    colored_frame_paths = []
    
    for img_path in images:
        print("img_path",img_path)
        if "transparent" in os.path.basename(img_path).lower():
            if base_frame_path is None:
                base_frame_path = img_path
            else:
                colored_frame_paths.append(img_path)
        else:
            colored_frame_paths.append(img_path)
    # Create output directory
    output_dir = "reflection_analysis_results_13May"
    
    ###Ankit 
     # Get paths from the error message
    # base_dir = "/Users/ankitladva/Desktop/idfy/active-liveness/experiments/data_24march_normal_data/images/3657e83e-acc9-44c4-981c-329d5b975b01"
    # transparent="/Users/ankitladva/Desktop/idfy/active-liveness/experiments/data_24march_normal_data/images/3657e83e-acc9-44c4-981c-329d5b975b01/1742814636285.png"
    # # Define base frame (no reflection) and colored frames
    # glob.glob(base_dir+"/*")
    # # base_frame_path = os.path.join(base_dir, "1743677605166_Black.png")  # Using Black as base
    # # base_frame_path = os.path.join(base_dir, "1743677605166_Black.png")  # Using Black as base
    # # base_frame_path = transparent
    
    # images=glob.glob(base_dir+"/*")
    # # images[1:9]
    # images.sort()
    # base_frame_path=images[1]
    # colored_frame_paths=images[2:9]
    
    # # Create output directory
    # output_dir = f"reflection_analysis_results_{os.path.basename(base_dir)}_transparent_all_normal_images"
    # Set threshold for detection sensitivity
    threshold = 20  # Lower value = more sensitive detection
    
    try:
        # Run comparison for all frames
        results = compare_all_frames(base_frame_path, colored_frame_paths, 
                                   user_id="user1", output_dir=output_dir, threshold=threshold)
        
        if results:
            print(f"\nAnalysis complete! Results saved to {output_dir}/")
            print("\nKey findings for KYC validation:")
            
            # Find the frame with the most distinct color reflection
            best_frame = max(results, key=lambda x: x['intensity'])
            print(f"1. Strongest reflection detected in {best_frame['color']} frame")
            print(f"   - Intensity: {best_frame['intensity']:.2f}")
            print(f"   - Dominant channel: {best_frame['dominant_channel']}")
            
            # Check if the dominant channels match expected colors
            expected_matches = {
                'Blue': 'Blue', 'Blue2': 'Blue',
                'Red': 'Red', 
                'Green': 'Green', 'Green2': 'Green',
                'Yellow': 'Red',  # Yellow often appears as high in red channel
                'Cyan': 'Green'   # Cyan often appears as high in green/blue
            }
            
            matches = sum(1 for r in results if r['dominant_channel'] == expected_matches.get(r['color'], ''))
            print("results",results)
            print(f"2. {matches}/{len(results)} frames show expected dominant channel for their color")
            
            # Calculate overall reflection consistency
            intensities = [r['intensity'] for r in results]
            print(intensities)
            print(min(intensities)) 
            print(max(intensities))
            print(max(intensities) - min(intensities))
            print(1 - (max(intensities) - min(intensities)) / max(intensities))
            consistency = 100 * (1 - (max(intensities) - min(intensities)) / max(intensities))
            print(f"3. Reflection consistency: {consistency:.1f}%")
            
            print("\nSuggested interpretation for KYC verification:")
            if matches >= len(results) * 0.5 and consistency > 50:
                print("✅ LIKELY GENUINE: Consistent color reflections match expected patterns")
            else:
                print("⚠️ SUSPICIOUS: Inconsistent color reflections may indicate a static image")
            
    except Exception as e:
        print(f"Error in main execution: {e}")
