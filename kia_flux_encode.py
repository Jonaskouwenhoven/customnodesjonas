import torch
import node_helpers

class KiaConceptClipTextEncodeFlux:
    """
    A specialized node for KIA concept car visualizations using the Flux model.
    
    Features:
    - Theme selection for different concept environments
    - Strength slider to control level of detail and features
    - Automatic generation of appropriate prompts based on settings
    - User-editable prompt fields for customization
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
    FUNCTION = "encode"
    CATEGORY = "advanced/conditioning/flux"
    DESCRIPTION = "Generates Kia concept car prompts with various luxury office features for Flux conditioning"
    
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
        # Get the preset prompt based on theme and strength
        preset_prompt = self.get_prompt_for_strength(theme, strength)
        
        # Always create a UI update to ensure prompts are shown
        ui_update = {
            "clip_prompt": preset_prompt,
            "t5xxl_prompt": preset_prompt
        }
        
        # Use preset prompts if fields are empty, otherwise use user inputs
        actual_clip_prompt = preset_prompt if clip_l == "" else clip_l
        actual_t5xxl_prompt = preset_prompt if t5xxl == "" else t5xxl
        
        # Tokenize and encode
        tokens = clip.tokenize(actual_clip_prompt)
        tokens["t5xxl"] = clip.tokenize(actual_t5xxl_prompt)["t5xxl"]
        
        # Return conditioning with guidance AND UI updates
        conditioning = clip.encode_from_tokens_scheduled(tokens, add_dict={"guidance": guidance})
        
        # ALWAYS return the UI update to ensure prompts are displayed
        return (conditioning, ui_update)