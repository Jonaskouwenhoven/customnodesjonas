import torch
import node_helpers
import json
import sys

print("KIA Flux Encode module loaded", file=sys.stderr)

class KiaConceptClipTextEncodeFlux:
    """
    A specialized node for KIA concept car visualizations using the Flux model.
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "clip": ("CLIP", ),
            "theme": (["City", "Comfortability (Coming Soon)", "Travel (Coming Soon)"], {"default": "City"}),
            "strength": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.01}),
            "guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.1}),
            "clip_l": ("STRING", {"multiline": True, "dynamicPrompts": True, "default": ""}),
            "t5xxl": ("STRING", {"multiline": True, "dynamicPrompts": True, "default": ""}),
            }}
    RETURN_TYPES = ("CONDITIONING",)
    RETURN_NAMES = ("conditioning",)
    OUTPUT_NODE = True
    FUNCTION = "encode"
    CATEGORY = "advanced/conditioning/flux"
    
    def get_prompt_for_strength(self, theme, strength):
        """Get the appropriate prompt based on theme and strength"""
        print(f"Getting prompt for theme: {theme}, strength: {strength}", file=sys.stderr)
        
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
        elif theme == "Comfortability (Coming Soon)":
            # Placeholder for Comfortability theme
            return f"Premium KIA concept car with focus on comfort features, luxurious seating, ambient lighting, advanced climate control, noise-cancelling interior, smooth ride technology, spacious cabin design, strength level: {strength_rounded}"
        elif theme == "Travel (Coming Soon)":
            # Placeholder for Travel theme
            return f"KIA travel concept car, integrated luggage compartments, panoramic viewing windows, convertible sleeping area, built-in navigation system, advanced driver assistance, long-distance comfort features, strength level: {strength_rounded}"
        else:
            # Generic fallback
            return f"KIA concept car design, futuristic features, innovative technology, premium materials, strength level: {strength_rounded}"
    
    def encode(self, clip, theme, strength, guidance, clip_l, t5xxl):
        """Encode the prompts using the CLIP model with Flux dual-encoder approach"""
        print(f"KiaConceptClipTextEncodeFlux.encode called with theme={theme}, strength={strength}", file=sys.stderr)
        
        # Get the preset prompt based on theme and strength
        preset_prompt = self.get_prompt_for_strength(theme, strength)
        print(f"Generated preset prompt: {preset_prompt}", file=sys.stderr)
        
        # Determine which prompts to use
        use_clip_l = clip_l if clip_l.strip() and clip_l != preset_prompt else preset_prompt
        use_t5xxl = t5xxl if t5xxl.strip() and t5xxl != preset_prompt else preset_prompt
        
        print(f"Using clip_l: {use_clip_l[:50]}...", file=sys.stderr)
        print(f"Using t5xxl: {use_t5xxl[:50]}...", file=sys.stderr)
        
        # Tokenize and encode
        tokens = clip.tokenize(use_clip_l)
        tokens["t5xxl"] = clip.tokenize(use_t5xxl)["t5xxl"]
        
        # Create the conditioning
        conditioning = clip.encode_from_tokens_scheduled(tokens, add_dict={"guidance": guidance})
        
        # Always return the UI update to ensure prompts are displayed
        # Pass explicitly formatted data to make it easier for JS to handle
        ui_update = {
            "ui": {
                "clip_prompt": preset_prompt,
                "t5xxl_prompt": preset_prompt
            }
        }
        print(f"Returning UI update: {json.dumps(ui_update)[:100]}...", file=sys.stderr)
        
        return (conditioning, ui_update)