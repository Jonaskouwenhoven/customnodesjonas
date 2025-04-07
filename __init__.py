from .kia_flux_encode import CLIPTextEncodeFlux, FluxGuidance, FluxDisableGuidance, KiaConceptPromptGenerator, KiaThemeStrengthCLIPTextEncodeFlux

NODE_CLASS_MAPPINGS = {
    "CLIPTextEncodeFlux": CLIPTextEncodeFlux,
    "FluxGuidance": FluxGuidance,
    "FluxDisableGuidance": FluxDisableGuidance,
    "KiaConceptPromptGenerator": KiaConceptPromptGenerator,
    "KiaThemeStrengthCLIPTextEncodeFlux": KiaThemeStrengthCLIPTextEncodeFlux,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CLIPTextEncodeFlux": "CLIP Text Encode (Flux)",
    "FluxGuidance": "Flux Guidance",
    "FluxDisableGuidance": "Flux Disable Guidance",
    "KiaConceptPromptGenerator": "Kia Concept Prompt Generator",
    "KiaThemeStrengthCLIPTextEncodeFlux": "Kia Theme+Strength CLIP Encode (Flux)",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']