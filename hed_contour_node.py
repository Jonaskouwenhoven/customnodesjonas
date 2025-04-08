# hed_contour_node.py
import cv2
import numpy as np
import torch
import os
import sys

print("HED Contour node module loaded", file=sys.stderr)

class HEDContourPreprocessor:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "image": ("IMAGE",),
            "threshold": ("INT", {"default": 100, "min": 0, "max": 255, "step": 1}),
            "min_contour_area": ("INT", {"default": 500, "min": 10, "max": 10000, "step": 10}),
            "line_thickness": ("INT", {"default": 3, "min": 1, "max": 10, "step": 1}),
            "resolution": ("INT", {"default": 512, "min": 64, "max": 2048, "step": 8}),
        }}

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("contour_image",)
    FUNCTION = "generate_contour"
    CATEGORY = "image/preprocessors"

    def generate_contour(self, image, threshold=100, min_contour_area=500, line_thickness=3, resolution=512):
        # Convert from ComfyUI [B,H,W,C] format to [H,W,C]
        if len(image.shape) == 4:
            image = image[0]
        
        # Convert to numpy and ensure uint8 format
        image_np = np.clip(255. * image.cpu().numpy(), 0, 255).astype(np.uint8)
        
        # Resize to target resolution while maintaining aspect ratio
        h, w = image_np.shape[:2]
        aspect_ratio = w / h
        if w > h:
            new_w = resolution
            new_h = int(resolution / aspect_ratio)
        else:
            new_h = resolution
            new_w = int(resolution * aspect_ratio)
        
        resized = cv2.resize(image_np, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Create a HED detector (load the model)
        try:
            from controlnet_aux import HEDdetector
            hed_detector = HEDdetector.from_pretrained('lllyasviel/Annotators')
        except ImportError:
            print("Error: controlnet_aux package not found. Please install with: pip install controlnet_aux", file=sys.stderr)
            # Return original image if HED detector can't be loaded
            return (torch.from_numpy(image_np.astype(np.float32) / 255.0).unsqueeze(0),)
        
        # Convert to RGB for HED
        if resized.shape[2] == 3:
            rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = resized
        
        # Process with HED detector
        with torch.no_grad():
            hed_image = hed_detector(rgb_image)
        
        # Convert PIL image to numpy array
        hed_np = np.array(hed_image)
        if len(hed_np.shape) == 3:
            hed_np = cv2.cvtColor(hed_np, cv2.COLOR_RGB2GRAY)
        
        # Apply binary thresholding
        _, binary = cv2.threshold(hed_np, threshold, 255, cv2.THRESH_BINARY)
        
        # Clean up noise
        kernel = np.ones((3, 3), np.uint8)
        morph = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create output image
        contour_image = np.zeros_like(morph)
        
        # Filter and draw main contours
        if contours:
            # Sort by area (largest first)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            # Keep only contours above minimum area
            significant_contours = [c for c in contours if cv2.contourArea(c) > min_contour_area]
            
            # Draw main contour
            cv2.drawContours(contour_image, significant_contours[:1], -1, 255, line_thickness)
            
            # Ensure continuous outline
            kernel = np.ones((5, 5), np.uint8)
            contour_image = cv2.dilate(contour_image, kernel, iterations=1)
        
        # Convert to RGB
        contour_rgb = cv2.cvtColor(contour_image, cv2.COLOR_GRAY2RGB)
        
        # Convert back to ComfyUI format [B,H,W,C]
        tensor_image = torch.from_numpy(contour_rgb.astype(np.float32) / 255.0).unsqueeze(0)
        
        return (tensor_image,)