# Copyright 2026 realman-robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Canonical robot descriptions exposed by rm_description launch files."""
from dataclasses import dataclass
import re
from typing import Dict, Tuple

XacroMappings = Tuple[Tuple[str, str], ...]

@dataclass(frozen=True)
class DescriptionModel:
    """Files and fixed xacro inputs for one supported robot model."""

    model_file: str
    rviz_file: str
    xacro_mappings: XacroMappings = ()
    dual_arm: bool = False

# Each complete arm_type selects its model file and fixed xacro inputs.
DESCRIPTION_MODELS: Dict[str, DescriptionModel] = {
    "63": DescriptionModel("rml_63.urdf", "rm_63.rviz"),
    "63-6f": DescriptionModel(
        "rml_63.urdf.xacro", "rm_63.rviz", (("link6_type", "Link6_6f"),)
    ),
    "63-6fb": DescriptionModel(
        "rml_63.urdf.xacro", "rm_63.rviz", (("link6_type", "Link6_6fb"),)
    ),
    "63_iii": DescriptionModel(
        "rml_63.urdf.xacro",
        "rm_63.rviz",
        (("link6_type", "Link6"), ("base_type", "base_link_III")),
    ),
    "63_iii-6fb": DescriptionModel(
        "rml_63.urdf.xacro",
        "rm_63.rviz",
        (("link6_type", "Link6_6fb"), ("base_type", "base_link_III")),
    ),
    "65": DescriptionModel("rm_65.urdf", "rm_65.rviz"),
    "65-6f": DescriptionModel(
        "rm_65.urdf.xacro", "rm_65.rviz", (("link6_type", "Link6_6f"),)
    ),
    "65-6fb": DescriptionModel(
        "rm_65.urdf.xacro", "rm_65.rviz", (("link6_type", "Link6_6fb"),)
    ),
    "75": DescriptionModel("rm_75.urdf", "rm_75.rviz"),
    "75-6f": DescriptionModel(
        "rm_75.urdf.xacro", "rm_75.rviz", (("link7_type", "Link7_6f"),)
    ),
    "75-6fb": DescriptionModel(
        "rm_75.urdf.xacro", "rm_75.rviz", (("link7_type", "Link7_6fb"),)
    ),
    "eco62": DescriptionModel(
        "rm_eco62.urdf.xacro", "rm_eco62.rviz"
    ),
    "eco63": DescriptionModel("rm_eco63.urdf", "rm_eco63.rviz"),
    "eco63-6fb": DescriptionModel(
        "rm_eco63.urdf.xacro", "rm_eco63.rviz", (("link6_type", "Link6_6fb"),)
    ),
    "eco65": DescriptionModel("rm_eco65.urdf", "rm_eco65.rviz"),
    "eco65-6f": DescriptionModel(
        "rm_eco65.urdf.xacro", "rm_eco65.rviz", (("link6_type", "Link6_6f"),)
    ),
    "eco65-6fb": DescriptionModel(
        "rm_eco65.urdf.xacro", "rm_eco65.rviz", (("link6_type", "Link6_6fb"),)
    ),
    "gen72": DescriptionModel("rm_gen72.urdf", "rm_gen72.rviz"),
    "gen72_ii": DescriptionModel(
        "rm_gen72_II.urdf", "rm_gen72.rviz"
    ),
    "rx75-6fb": DescriptionModel(
        "rm_rx75-6fb.urdf.xacro", "rm_rx75.rviz", dual_arm=True
    ),
    "rx75-6fb-v": DescriptionModel(
        "rm_rx75-6fb_v.urdf.xacro", "rm_rx75.rviz", dual_arm=True
    ),
}

GLB_ARM_TYPES = ("65", "75", "eco62", "eco63", "eco65", "rx75")
MODEL_FORMATS = ("auto", "glb", "stl")
GLB_MODELS = {
    arm_type: DescriptionModel(
        "imported/" + arm_type.replace("-", "_")
        + ("_standard" if "-" not in arm_type else "") + ".urdf.xacro",
        spec.rviz_file,
        dual_arm=spec.dual_arm,
    )
    for arm_type, spec in DESCRIPTION_MODELS.items()
    if arm_type.split("-")[0] in GLB_ARM_TYPES
}


# The complete compatibility surface.  Tests keep this list synchronized with
# the catalog and with the actual wrapper files.
LEGACY_DISPLAY_LAUNCHES: Dict[str, str] = {
    "rm_63_display.launch.py": "63",
    "rm_63_6f_display.launch.py": "63-6f",
    "rm_63_6fb_display.launch.py": "63-6fb",
    "rm_63_III_display.launch.py": "63_iii",
    "rm_63_III_6fb_display.launch.py": "63_iii-6fb",
    "rm_65_display.launch.py": "65",
    "rm_65_6f_display.launch.py": "65-6f",
    "rm_65_6fb_display.launch.py": "65-6fb",
    "rm_75_display.launch.py": "75",
    "rm_75_6f_display.launch.py": "75-6f",
    "rm_75_6fb_display.launch.py": "75-6fb",
    "rm_eco62_display.launch.py": "eco62",
    "rm_eco63_display.launch.py": "eco63",
    "rm_eco63_6fb_display.launch.py": "eco63-6fb",
    "rm_eco65_display.launch.py": "eco65",
    "rm_eco65_6f_display.launch.py": "eco65-6f",
    "rm_eco65_6fb_display.launch.py": "eco65-6fb",
    "rm_gen72_display.launch.py": "gen72",
    "rm_gen72_II_display.launch.py": "gen72_ii",
    "rm_rx75_6fb_display.launch.py": "rx75-6fb",
    "rm_rx75_6fb_v_display.launch.py": "rx75-6fb-v",
}

_ARM_TYPE_ALIASES = {
    '63': '63',
    'rm63': '63',
    'rml63': '63',
    '63iii': '63_iii',
    'rm63iii': '63_iii',
    'rml63iii': '63_iii',
    '65': '65',
    'rm65': '65',
    '75': '75',
    'rm75': '75',
    'eco62': 'eco62',
    'rmeco62': 'eco62',
    'eco63': 'eco63',
    'rmeco63': 'eco63',
    'eco65': 'eco65',
    'rmeco65': 'eco65',
    'gen72': 'gen72',
    'rmgen72': 'gen72',
    'gen72ii': 'gen72_ii',
    'rmgen72ii': 'gen72_ii',
    'rx75': 'rx75',
    'rmrx75': 'rx75',
}

_ARM_TYPE_ALIASES.update({
    alias + arm_type[len(family):].replace("-", ""): arm_type
    for alias, family in _ARM_TYPE_ALIASES.items()
    for arm_type in DESCRIPTION_MODELS
    if arm_type == family or arm_type.startswith(family + "-")
})


def normalize_arm_type(arm_type: str) -> str:
    """Normalize a complete selector and reject unsupported end-link versions."""
    if not isinstance(arm_type, str) or not arm_type.strip():
        raise ValueError("arm_type must be a non-empty string.")
    token = re.sub(r"[\s_-]+", "", arm_type.strip().casefold())
    normalized = _ARM_TYPE_ALIASES.get(token)
    if normalized not in DESCRIPTION_MODELS:
        raise ValueError(
            f"Unsupported arm_type='{arm_type}'. Valid values: "
            + ", ".join(DESCRIPTION_MODELS)
        )
    return normalized


def resolve_model(arm_type: str, model: str = "auto") -> DescriptionModel:
    """Resolve one selector or raise an error suitable for launch output."""
    arm_type = normalize_arm_type(arm_type)
    model = model.strip().casefold()
    if model not in MODEL_FORMATS:
        raise ValueError(
            f"Unsupported model='{model}'. "
            f"Valid values: {', '.join(MODEL_FORMATS)}."
        )
    use_glb = model == "glb" or (model == "auto" and arm_type in GLB_MODELS)
    catalog = GLB_MODELS if use_glb else DESCRIPTION_MODELS
    try:
        return catalog[arm_type]
    except KeyError as exc:
        raise ValueError(
            f"No {model.upper()} model for arm_type='{arm_type}'. "
            f"Valid arm_type values: {', '.join(catalog)}."
        ) from exc
