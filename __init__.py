# print("Loading KIA Flux modules...")

# from .kia_flux_encode import KiaConceptClipTextEncodeFlux
# from .kia_flux_node import CLIPTextEncodeFlux, FluxGuidance, FluxDisableGuidance

# NODE_CLASS_MAPPINGS = {
#     "KiaConceptClipTextEncodeFlux": KiaConceptClipTextEncodeFlux,
#     "CLIPTextEncodeFlux": CLIPTextEncodeFlux,
#     "FluxGuidance": FluxGuidance,
#     "FluxDisableGuidance": FluxDisableGuidance,
# }

# NODE_DISPLAY_NAME_MAPPINGS = {
#     "KiaConceptClipTextEncodeFlux": "Kia Concept CLIP Text Encode (Flux)",
#     "CLIPTextEncodeFlux": "CLIP Text Encode (Flux)",
#     "FluxGuidance": "Flux Guidance",
#     "FluxDisableGuidance": "Flux Disable Guidance",
# }

# print("KIA Flux modules loaded successfully!")

# __all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print("Loading KIA Flux modules...")

from .kia_flux_encode import KiaConceptClipTextEncodeFlux
from .kia_flux_node import CLIPTextEncodeFlux, FluxGuidance, FluxDisableGuidance
from .hed_contour_node import HEDContourPreprocessor  # Add this line

NODE_CLASS_MAPPINGS = {
    "KiaConceptClipTextEncodeFlux": KiaConceptClipTextEncodeFlux,
    "CLIPTextEncodeFlux": CLIPTextEncodeFlux,
    "FluxGuidance": FluxGuidance,
    "FluxDisableGuidance": FluxDisableGuidance,
    "HEDContourPreprocessor": HEDContourPreprocessor,  # Add this line
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KiaConceptClipTextEncodeFlux": "Kia Concept CLIP Text Encode (Flux)",
    "CLIPTextEncodeFlux": "CLIP Text Encode (Flux)",
    "FluxGuidance": "Flux Guidance",
    "FluxDisableGuidance": "Flux Disable Guidance",
    "HEDContourPreprocessor": "HED Contour",  # Add this line
}

print("KIA Flux modules loaded successfully!")

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']