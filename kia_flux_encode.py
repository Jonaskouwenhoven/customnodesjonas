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

class KiaPromptDisplay:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "theme": (["City", "Comfortability (Coming Soon)", "Travel (Coming Soon)"], {"default": "City"}),
            "strength": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05}),
            }}
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "prompts/kia_concept"
    
    def get_city_prompts(self):
        # Define prompts for different strength levels (0.0 to 1.0 in steps of 0.05)
        city_prompts = {
            0.0: "White car interior, standard office workspace, office chair, basic lighting, connectivity features, office environment, display screen, white background, side view, KIA design",
            
            0.05: "Modern white car interior, enhanced office workspace, comfortable office chair, good lighting, connectivity hub, practical office environment, display screen, white background, side view, KIA design concept",
            
            0.1: "Modern white car interior, mobile workspace, ergonomic office chair, good lighting system, connectivity hub, functional office environment, display screen, white background, side view, KIA design concept",
            
            0.15: "Modern white car interior, mobile office space, ergonomic office chair, quality lighting system, connectivity center, functional office environment, display screen, white background, side view, KIA design concept",
            
            0.2: "Contemporary white car interior, mobile office space, ergonomic office chair, quality lighting system, connectivity center, practical office environment, integrated display, white background, side view, KIA design concept",
            
            0.25: "Contemporary white car interior, mobile office setup, ergonomic office chair, enhanced lighting system, digital connectivity center, practical office environment, integrated display, white background, side view, KIA design concept",
            
            0.3: "Sleek white car interior, mobile office setup, ergonomic office chair, enhanced lighting system, digital connectivity center, comfortable office environment, integrated display array, white background, side view, KIA design concept",
            
            0.35: "Sleek white car interior, mobile officepod, premium ergonomic chair, enhanced lighting system, digital connectivity center, comfortable office environment, integrated display array, white background, detailed side view, KIA design concept",
            
            0.4: "Advanced white car interior, mobile officepod, premium ergonomic chair, studio lighting system, digital connectivity center, comfortable office environment, integrated display array, white studio background, detailed side view, KIA concept design",
            
            0.45: "Advanced white car interior, officepod design, premium ergonomic chair, studio lighting system, digital connectivity center, luxury office environment, integrated display array, white studio background, detailed side view, KIA concept design",
            
            0.5: "Innovative white car interior, officepod setup, premium ergonomic office chair, studio lighting system, digital connectivity center, luxury office environment, integrated display array, conference feature, white studio background, detailed side view, KIA concept design",
            
            0.55: "Innovative white concept car interior, officepod workspace, premium ergonomic office chair, professional lighting, digital connectivity center, luxury office environment, integrated display array, conference capability, white studio background, detailed side view, KIA concept design",
            
            0.6: "Futuristic white concept car interior, officepod workspace, premium ergonomic office chair, professional lighting, connectivity command center, luxury office environment, integrated display array, conference capability, white studio background, side view visualization, KIA concept design",
            
            0.65: "Futuristic white concept car interior, officepod premium, premium ergonomic office chair, studio lighting, connectivity command center, luxury office environment, immersive display array, conference capability, file storage, white studio background, side view visualization, KIA concept design",
            
            0.7: "Futuristic white concept car interior, officepod premium, premium ergonomic office chair, comprehensive studio lighting, connectivity command center, luxury executive office environment, immersive display array, conference capability, built-in file storage, white studio background, side view visualization, KIA concept design",
            
            0.75: "Futuristic white concept car interior, officepod advanced, premium ergonomic office chair, comprehensive studio lighting, connectivity command center, luxury executive office environment, immersive display array, conference capability, built-in file storage, high-quality render, white studio background, side view visualization, KIA concept design",
            
            0.8: "Futuristic white concept car interior, officepod_v1, premium ergonomic office chair, comprehensive studio lighting, state-of-art connectivity command center, luxury executive office environment, immersive display array, conference capability, built-in file storage, high-quality detailed render, white studio background, side view visualization, KIA concept design",
            
            0.85: "Futuristic white concept car interior, officepod_v1 pro, premium ergonomic office chair, comprehensive studio lighting, state-of-art connectivity command center, luxury executive office environment, immersive display array, conference capability, built-in file storage, high-quality detailed render, white studio background, side view visualization, KIA concept design",
            
            0.9: "Futuristic white concept car interior, officepod_v1 professional, premium ergonomic office chair, comprehensive studio lighting, state-of-art connectivity command center, luxury executive office environment, immersive display array, conference capabilities, built-in file storage, high-quality detailed render, white studio background, side view visualization, KIA concept design",
            
            0.95: "Futuristic white concept car interior, officepod_v1 ultimate, premium ergonomic office chair workspace, comprehensive studio lighting, state-of-art connectivity command center, luxury executive office environment, immersive display array, conference capabilities, built-in file storage, high-quality detailed render, white studio background, side view visualization, KIA concept design",
            
            1.0: "Futuristic white concept car interior, officepod_v1 ultimate, complete mobile office suite, expansive executive desk workspace, premium ergonomic office chair, comprehensive studio lighting, state-of-art connectivity command center, luxury executive office environment, immersive display array, conference capabilities, built-in file storage, high-quality detailed render, white studio background, side view visualization, KIA concept design"
        }
        return city_prompts
    
    def generate_prompt(self, theme, strength):
        # Round strength to nearest 0.05
        strength_rounded = round(strength * 20) / 20
        
        if theme == "City":
            prompts = self.get_city_prompts()
            
            # Get the closest strength value if the exact one isn't available
            if strength_rounded not in prompts:
                available_strengths = sorted(prompts.keys())
                # Find the closest strength value
                closest = min(available_strengths, key=lambda x: abs(x - strength_rounded))
                strength_rounded = closest
                
            return (prompts[strength_rounded],)
        else:
            # Return a placeholder for other themes
            return (f"This theme ({theme}) is coming soon. Current strength setting: {strength_rounded}",)

class KiaPromptToFlux:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "clip": ("CLIP", ),
            "prompt": ("STRING", {"multiline": True}),
            "guidance": ("FLOAT", {"default": 3.5, "min": 0.0, "max": 100.0, "step": 0.1}),
            }}
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "encode"
    CATEGORY = "advanced/conditioning/flux"
    
    def encode(self, clip, prompt, guidance):
        # Use the same prompt for both CLIP and T5XXL
        tokens = clip.tokenize(prompt)
        tokens["t5xxl"] = clip.tokenize(prompt)["t5xxl"]
        
        # Return encoding with guidance
        return (clip.encode_from_tokens_scheduled(tokens, add_dict={"guidance": guidance}), )


NODE_CLASS_MAPPINGS = {
    "CLIPTextEncodeFlux": CLIPTextEncodeFlux,
    "FluxGuidance": FluxGuidance,
    "FluxDisableGuidance": FluxDisableGuidance,
    "KiaPromptDisplay": KiaPromptDisplay,
    "KiaPromptToFlux": KiaPromptToFlux,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CLIPTextEncodeFlux": "CLIP Text Encode (Flux)",
    "FluxGuidance": "Flux Guidance",
    "FluxDisableGuidance": "Flux Disable Guidance",
    "KiaPromptDisplay": "Kia Concept Prompt Display",
    "KiaPromptToFlux": "Kia Prompt to Flux",
}