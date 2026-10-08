"""Canonical robot-description variants exposed by rm_description launch files."""

from dataclasses import dataclass
from typing import Dict, Tuple


XacroMappings = Tuple[Tuple[str, str], ...]


@dataclass(frozen=True)
class DescriptionVariant:
    """Files and fixed xacro inputs for one supported robot variant."""

    model_file: str
    rviz_file: str
    xacro_mappings: XacroMappings = ()
    dual_arm: bool = False


# Keep this table explicit.  In particular, the eco65 6f/6fb entries intentionally
# retain the legacy .urdf input even though the old launch files supplied a xacro
# mapping to it.  Changing that file would silently change the published model.
DESCRIPTION_VARIANTS: Dict[Tuple[str, str], DescriptionVariant] = {
    ("63", "standard"): DescriptionVariant("rml_63.urdf", "rm_63.rviz"),
    ("63", "6f"): DescriptionVariant(
        "rml_63.urdf.xacro", "rm_63.rviz", (("link6_type", "Link6_6f"),)
    ),
    ("63", "6fb"): DescriptionVariant(
        "rml_63.urdf.xacro", "rm_63.rviz", (("link6_type", "Link6_6fb"),)
    ),
    ("63_iii", "standard"): DescriptionVariant(
        "rml_63.urdf.xacro",
        "rm_63.rviz",
        (("link6_type", "Link6"), ("base_type", "base_link_III")),
    ),
    ("63_iii", "6fb"): DescriptionVariant(
        "rml_63.urdf.xacro",
        "rm_63.rviz",
        (("link6_type", "Link6_6fb"), ("base_type", "base_link_III")),
    ),
    ("65", "standard"): DescriptionVariant("rm_65.urdf", "rm_65.rviz"),
    ("65", "6f"): DescriptionVariant(
        "rm_65.urdf.xacro", "rm_65.rviz", (("link6_type", "Link6_6f"),)
    ),
    ("65", "6fb"): DescriptionVariant(
        "rm_65.urdf.xacro", "rm_65.rviz", (("link6_type", "Link6_6fb"),)
    ),
    ("75", "standard"): DescriptionVariant("rm_75.urdf", "rm_75.rviz"),
    ("75", "6f"): DescriptionVariant(
        "rm_75.urdf.xacro", "rm_75.rviz", (("link7_type", "Link7_6f"),)
    ),
    ("75", "6fb"): DescriptionVariant(
        "rm_75.urdf.xacro", "rm_75.rviz", (("link7_type", "Link7_6fb"),)
    ),
    ("eco62", "standard"): DescriptionVariant(
        "rm_eco62.urdf.xacro", "rm_eco62.rviz"
    ),
    ("eco63", "standard"): DescriptionVariant("rm_eco63.urdf", "rm_eco63.rviz"),
    ("eco63", "6fb"): DescriptionVariant(
        "rm_eco63.urdf.xacro", "rm_eco63.rviz", (("link6_type", "Link6_6fb"),)
    ),
    ("eco65", "standard"): DescriptionVariant("rm_eco65.urdf", "rm_eco65.rviz"),
    ("eco65", "6f"): DescriptionVariant(
        "rm_eco65.urdf", "rm_eco65.rviz", (("link6_type", "Link6_6f"),)
    ),
    ("eco65", "6fb"): DescriptionVariant(
        "rm_eco65.urdf", "rm_eco65.rviz", (("link6_type", "Link6_6fb"),)
    ),
    ("gen72", "standard"): DescriptionVariant("rm_gen72.urdf", "rm_gen72.rviz"),
    ("gen72_ii", "standard"): DescriptionVariant(
        "rm_gen72_II.urdf", "rm_gen72.rviz"
    ),
    ("rx75", "6fb"): DescriptionVariant(
        "rm_rx75-6fb.urdf.xacro", "rm_rx75.rviz", dual_arm=True
    ),
    ("rx75", "6fb_v"): DescriptionVariant(
        "rm_rx75-6fb_v.urdf.xacro", "rm_rx75.rviz", dual_arm=True
    ),
}


GLB_ARM_TYPES = ("65", "75", "eco62", "eco63", "eco65", "rx75")
MODEL_FORMATS = ("auto", "glb", "stl")
GLB_VARIANTS = {
    key: DescriptionVariant(
        f"imported/{key[0]}_{key[1]}.urdf.xacro",
        spec.rviz_file,
        dual_arm=spec.dual_arm,
    )
    for key, spec in DESCRIPTION_VARIANTS.items()
    if key[0] in GLB_ARM_TYPES
}


# The complete compatibility surface.  Tests keep this list synchronized with
# the catalog and with the actual wrapper files.
LEGACY_DISPLAY_LAUNCHES: Dict[str, Tuple[str, str]] = {
    "rm_63_display.launch.py": ("63", "standard"),
    "rm_63_6f_display.launch.py": ("63", "6f"),
    "rm_63_6fb_display.launch.py": ("63", "6fb"),
    "rm_63_III_display.launch.py": ("63_iii", "standard"),
    "rm_63_III_6fb_display.launch.py": ("63_iii", "6fb"),
    "rm_65_display.launch.py": ("65", "standard"),
    "rm_65_6f_display.launch.py": ("65", "6f"),
    "rm_65_6fb_display.launch.py": ("65", "6fb"),
    "rm_75_display.launch.py": ("75", "standard"),
    "rm_75_6f_display.launch.py": ("75", "6f"),
    "rm_75_6fb_display.launch.py": ("75", "6fb"),
    "rm_eco62_display.launch.py": ("eco62", "standard"),
    "rm_eco63_display.launch.py": ("eco63", "standard"),
    "rm_eco63_6fb_display.launch.py": ("eco63", "6fb"),
    "rm_eco65_display.launch.py": ("eco65", "standard"),
    "rm_eco65_6f_display.launch.py": ("eco65", "6f"),
    "rm_eco65_6fb_display.launch.py": ("eco65", "6fb"),
    "rm_gen72_display.launch.py": ("gen72", "standard"),
    "rm_gen72_II_display.launch.py": ("gen72_ii", "standard"),
    "rm_rx75_6fb_display.launch.py": ("rx75", "6fb"),
    "rm_rx75_6fb_v_display.launch.py": ("rx75", "6fb_v"),
}


def format_arm_type(arm_type: str, arm_variant: str) -> str:
    """Format an internal catalog pair as one public arm_type selector."""

    if arm_variant == "standard":
        return arm_type
    return f"{arm_type}-{arm_variant.replace('_', '-')}"


def normalize_selection(arm_type: str) -> Tuple[str, str]:
    """Split a public selector without aliasing unsupported model variants."""

    if not isinstance(arm_type, str) or not arm_type.strip():
        raise ValueError("arm_type must be a non-empty string.")
    normalized = arm_type.strip().casefold()
    for suffix in ("6fb-v", "6fb_v", "6fb", "6f"):
        if normalized.endswith(f"-{suffix}"):
            return normalized[:-(len(suffix) + 1)], suffix.replace("-", "_")
    return normalized, "standard"


def resolve_variant(arm_type: str, model: str = "auto") -> DescriptionVariant:
    """Resolve one selector or raise an error suitable for launch output."""

    key = normalize_selection(arm_type)
    model = model.strip().casefold()
    if model not in MODEL_FORMATS:
        raise ValueError(
            f"Unsupported model='{model}'. "
            f"Valid values: {', '.join(MODEL_FORMATS)}."
        )
    use_glb = model == "glb" or (model == "auto" and key in GLB_VARIANTS)
    catalog = GLB_VARIANTS if use_glb else DESCRIPTION_VARIANTS
    try:
        return catalog[key]
    except KeyError as exc:
        valid_selections = sorted(
            format_arm_type(*item) for item in catalog if item[0] == key[0]
        ) or sorted(format_arm_type(*item) for item in catalog)
        detail = "Valid arm_type values: " + ", ".join(valid_selections)
        raise ValueError(
            "Unsupported rm_description selection "
            f"arm_type='{arm_type}', model='{model}'. {detail}"
        ) from exc
