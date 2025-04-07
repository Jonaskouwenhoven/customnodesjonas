from .kia_flux_encode import CLIPTextEncodeFlux, FluxGuidance, FluxDisableGuidance, KiaConceptClipTextEncodeFlux, KiaFluxEncode

NODE_CLASS_MAPPINGS = {
    "CLIPTextEncodeFlux": CLIPTextEncodeFlux,
    "FluxGuidance": FluxGuidance,
    "FluxDisableGuidance": FluxDisableGuidance,
    "KiaConceptClipTextEncodeFlux": KiaConceptClipTextEncodeFlux,
    "KiaFluxEncode": KiaFluxEncode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CLIPTextEncodeFlux": "CLIP Text Encode (Flux)",
    "FluxGuidance": "Flux Guidance",
    "FluxDisableGuidance": "Flux Disable Guidance",
    "KiaConceptClipTextEncodeFlux": "Kia Concept CLIP Text Encode (Flux)",
    "KiaFluxEncode": "Kia Flux Encoder (Simple)",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']