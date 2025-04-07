from .kia_prompt_display import CLIPTextEncodeFlux, FluxGuidance, FluxDisableGuidance, KiaPromptDisplay, KiaPromptToFlux

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

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']