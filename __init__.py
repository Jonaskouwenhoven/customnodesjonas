from .kia_flux_node import CLIPTextEncodeFlux, FluxGuidance, FluxDisableGuidance 
from .kia_flux_encode import KiaConceptClipTextEncodeFlux

NODE_CLASS_MAPPINGS = {
    "KiaConceptClipTextEncodeFlux": KiaConceptClipTextEncodeFlux,
    "CLIPTextEncodeFlux": CLIPTextEncodeFlux,
    "FluxGuidance": FluxGuidance,
    "FluxDisableGuidance": FluxDisableGuidance,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KiaConceptClipTextEncodeFlux": "Kia Concept CLIP Text Encode (Flux)",
    "CLIPTextEncodeFlux": "CLIP Text Encode (Flux)",
    "FluxGuidance": "Flux Guidance",
    "FluxDisableGuidance": "Flux Disable Guidance",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']