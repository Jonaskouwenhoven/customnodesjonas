import hashlib
import torch
from comfy.cli_args import args
from PIL import ImageFile, UnidentifiedImageError

def conditioning_set_values(conditioning, values={}):
    c = []
    for t in conditioning:
        n = [t[0], t[1].copy()]
        for k in values:
            n[1][k] = values[k]
        c.append(n)
    return c

def pillow(fn, arg):
    prev_value = None
    try:
        x = fn(arg)
    except (OSError, UnidentifiedImageError, ValueError): #PIL issues #4472 and #2445, also fixes ComfyUI issue #3416
        prev_value = ImageFile.LOAD_TRUNCATED_IMAGES
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        x = fn(arg)
    finally:
        if prev_value is not None:
            ImageFile.LOAD_TRUNCATED_IMAGES = prev_value
    return x

def hasher():
    hashfuncs = {
        "md5": hashlib.md5,
        "sha1": hashlib.sha1,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512
    }
    return hashfuncs[args.default_hashing_function]

def string_to_torch_dtype(string):
    if string == "fp32":
        return torch.float32
    if string == "fp16":
        return torch.float16
    if string == "bf16":
        return torch.bfloat16

def image_alpha_fix(destination, source):
    if destination.shape[-1] < source.shape[-1]:
        source = source[...,:destination.shape[-1]]
    elif destination.shape[-1] > source.shape[-1]:
        destination = torch.nn.functional.pad(destination, (0, 1))
        destination[..., -1] = 1.0
    return destination, source

import node_helpers

class KiaFluxConceptNode:
    """
    A combined node that preloads prompts based on theme/strength and allows for Flux encoding.
    
    - Includes dropdown fields for common strength presets to easily select prompt levels
    - Shows the prompt in text fields that can be edited
    - Uses the edited prompt for encoding with Flux
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "clip": ("CLIP", ),
            "theme": (["City", "Comfortability (Coming Soon)", "Travel (Coming Soon)"], {"default": "City"}),
            "preset": (["Level 0 - Basic (0.0)", 
                      "Level 1 - Simple (0.2)", 
                      "Level 2 - Enhanced (0.4)", 
                      "Level 3 - Advanced (0.6)", 
                      "Level 4 - Premium (0.8)", 
                      "Level 5 - Ultimate (1.0)"], {"default": "Level 3 - Advanced (0.6)"}),
            "clip_l": ("STRING", {"multiline": True, "dynamicPrompts": True, "default": "Futuristic white concept car interior, officepod workspace, premium ergonomic office chair, professional lighting, connectivity command center, luxury office environment, integrated display array, conference capability, white studio background, side view visualization, KIA concept design"}),
            "t5xxl": ("STRING", {"multiline": True, "dynamicPrompts": True, "default": "Futuristic white concept car interior, officepod workspace, premium ergonomic office chair, professional lighting, connectivity command center, luxury office environment, integrated display array, conference capability, white studio background, side view visualization, KIA concept design"}),
            "guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.1}),
            }}
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "encode"
    CATEGORY = "advanced/conditioning/flux"
    DESCRIPTION = "Generates Kia concept car prompts with various luxury office features for Flux conditioning"
    
    def preset_to_strength(self, preset):
        """Convert a preset level to a strength value"""
        preset_map = {
            "Level 0 - Basic (0.0)": 0.0,
            "Level 1 - Simple (0.2)": 0.2,
            "Level 2 - Enhanced (0.4)": 0.4,
            "Level 3 - Advanced (0.6)": 0.6,
            "Level 4 - Premium (0.8)": 0.8,
            "Level 5 - Ultimate (1.0)": 1.0
        }
        return preset_map.get(preset, 0.6)  # Default to 0.6 if preset not found
    
    def get_prompt_for_strength(self, theme, strength):
        """Get the appropriate prompt based on theme and strength"""
        # Round strength to nearest 0.2 to match our presets
        strength_rounded = round(strength * 5) / 5
        
        if theme == "City":
            city_prompts = {
                0.0: "White car interior, standard office workspace, office chair, basic lighting, connectivity features, office environment, display screen, white background, side view, KIA design",
                
                0.2: "Contemporary white car interior, mobile office space, ergonomic office chair, quality lighting system, connectivity center, practical office environment, integrated display, white background, side view, KIA design concept",
                
                0.4: "Advanced white car interior, mobile officepod, premium ergonomic chair, studio lighting system, digital connectivity center, comfortable office environment, integrated display array, white studio background, detailed side view, KIA concept design",
                
                0.6: "Futuristic white concept car interior, officepod workspace, premium ergonomic office chair, professional lighting, connectivity command center, luxury office environment, integrated display array, conference capability, white studio background, side view visualization, KIA concept design",
                
                0.8: "Futuristic white concept car interior, officepod_v1, premium ergonomic office chair, comprehensive studio lighting, state-of-art connectivity command center, luxury executive office environment, immersive display array, conference capability, built-in file storage, high-quality detailed render, white studio background, side view visualization, KIA concept design",
                
                1.0: "Futuristic white concept car interior, officepod_v1 ultimate, complete mobile office suite, expansive executive desk workspace, premium ergonomic office chair, comprehensive studio lighting, state-of-art connectivity command center, luxury executive office environment, immersive display array, conference capabilities, built-in file storage, high-quality detailed render, white studio background, side view visualization, KIA concept design"
            }
            
            # Get the closest strength value if the exact one isn't available
            if strength_rounded not in city_prompts:
                available_strengths = sorted(city_prompts.keys())
                # Find the closest strength value
                closest = min(available_strengths, key=lambda x: abs(x - strength_rounded))
                strength_rounded = closest
                
            return city_prompts[strength_rounded]
        else:
            # Return a placeholder for other themes
            return f"This theme ({theme}) is coming soon. Current strength setting: {strength_rounded}"
    
    def encode(self, clip, theme, preset, clip_l, t5xxl, guidance):
        """Encode the prompts using the CLIP model"""
        # Get the strength value from the preset
        strength = self.preset_to_strength(preset)
        
        # Get the preset prompt based on theme and strength
        preset_prompt = self.get_prompt_for_strength(theme, strength)
        
        # Check if we need to update the text widgets with new preset
        # We'll compare the input prompt with our generated preset
        need_update = False
        ui_update = {}
        
        # Only update if user hasn't made manual changes
        # Or if theme/preset selection has changed
        if clip_l != preset_prompt or t5xxl != preset_prompt:
            need_update = True
            ui_update["clip_prompt"] = preset_prompt
            ui_update["t5xxl_prompt"] = preset_prompt
        
        # Tokenize and encode using either the preset prompt or user-edited prompt
        tokens = clip.tokenize(clip_l)
        tokens["t5xxl"] = clip.tokenize(t5xxl)["t5xxl"]
        
        # Return conditioning with the guidance value
        conditioning = clip.encode_from_tokens_scheduled(tokens, add_dict={"guidance": guidance})
        
        # Pass the updated prompts to the UI if needed
        if need_update:
            return (conditioning, ui_update)
        else:
            return (conditioning, )

# Include the original Flux nodes for compatibility
class CLIPTextEncodeFlux:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "clip": ("CLIP", ),
            "clip_l": ("STRING", {"multiline": True, "dynamicPrompts": True}),
            "t5xxl": ("STRING", {"multiline": True, "dynamicPrompts": True}),
            "guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.1}),
            }}
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "encode"
    CATEGORY = "advanced/conditioning/flux"
    
    def encode(self, clip, clip_l, t5xxl, guidance):
        tokens = clip.tokenize(clip_l)
        tokens["t5xxl"] = clip.tokenize(t5xxl)["t5xxl"]
        return (clip.encode_from_tokens_scheduled(tokens, add_dict={"guidance": guidance}), )

class FluxGuidance:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "conditioning": ("CONDITIONING", ),
            "guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.1}),
            }}
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "append"
    CATEGORY = "advanced/conditioning/flux"
    
    def append(self, conditioning, guidance):
        c = node_helpers.conditioning_set_values(conditioning, {"guidance": guidance})
        return (c, )

class FluxDisableGuidance:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "conditioning": ("CONDITIONING", ),
            }}
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "append"
    CATEGORY = "advanced/conditioning/flux"
    DESCRIPTION = "This node completely disables the guidance embed on Flux and Flux like models"
    
    def append(self, conditioning):
        c = node_helpers.conditioning_set_values(conditioning, {"guidance": None})
        return (c, )

NODE_CLASS_MAPPINGS = {
    "KiaFluxConceptNode": KiaFluxConceptNode,
    "CLIPTextEncodeFlux": CLIPTextEncodeFlux,
    "FluxGuidance": FluxGuidance,
    "FluxDisableGuidance": FluxDisableGuidance,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KiaFluxConceptNode": "Kia Concept Car (Flux)",
    "CLIPTextEncodeFlux": "CLIP Text Encode (Flux)",
    "FluxGuidance": "Flux Guidance",
    "FluxDisableGuidance": "Flux Disable Guidance",
}