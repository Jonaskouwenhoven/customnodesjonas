from .kia_flux_node import KiaFluxConceptNode, CLIPTextEncodeFlux, FluxGuidance, FluxDisableGuidance

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

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']