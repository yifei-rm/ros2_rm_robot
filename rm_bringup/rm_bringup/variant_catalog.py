"""
Canonical component plans for every supported robot variant.

The catalog is deliberately explicit. Launch filenames, hardware profile
reuse, dual-arm topology, and joint-state defaults are product capabilities;
they must not be inferred from string concatenation.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


PACKAGE_NAME = 'rm_bringup'

ARM_TYPES = (
    '63',
    '63_iii',
    '65',
    '75',
    'eco62',
    'eco63',
    'eco65',
    'gen72',
    'gen72_ii',
    'rx75',
)
ARM_VARIANTS = ('standard', '6f', '6fb', '6fb_v')
MODES = ('real', 'gazebo')


@dataclass(frozen=True)
class LaunchReference:
    """One installed launch file."""

    package: str
    launch_file: str


@dataclass(frozen=True)
class ArmProfile:
    """Hardware/control topology shared by one or more product models."""

    arm_type: str
    driver_profile: str
    control_profile: str
    topology: str
    real_joint_states_topic: str
    gazebo_joint_states_topic: str
    use_joint_state_bridge: bool = False

    def joint_states_topic(self, mode: str) -> str:
        if mode == 'real':
            return self.real_joint_states_topic
        if mode == 'gazebo':
            return self.gazebo_joint_states_topic
        raise ValueError(
            f"Unsupported mode: {mode}. Valid modes: {', '.join(MODES)}."
        )


ARM_PROFILES = {
    '63': ArmProfile(
        '63', '63', '63', 'single', '/joint_states', '/joint_states'
    ),
    '63_iii': ArmProfile(
        '63_iii', '63', '63', 'single', '/joint_states', '/joint_states'
    ),
    '65': ArmProfile(
        '65', '65', '65', 'single', '/joint_states', '/joint_states'
    ),
    '75': ArmProfile(
        '75', '75', '75', 'single', '/joint_states', '/joint_states'
    ),
    'eco62': ArmProfile(
        'eco62', 'eco62', 'eco62', 'single', '/joint_states', '/joint_states'
    ),
    'eco63': ArmProfile(
        'eco63', 'eco63', 'eco63', 'single', '/joint_states', '/joint_states'
    ),
    'eco65': ArmProfile(
        'eco65', 'eco65', 'eco65', 'single', '/joint_states', '/joint_states'
    ),
    'gen72': ArmProfile(
        'gen72', 'gen72', 'gen72', 'single', '/joint_states', '/joint_states'
    ),
    'gen72_ii': ArmProfile(
        'gen72_ii', 'gen72', 'gen72', 'single', '/joint_states', '/joint_states'
    ),
    'rx75': ArmProfile(
        'rx75',
        'rx75',
        'rx75',
        'dual',
        '/joint_states',
        '/joint_state_broadcaster/joint_states',
        use_joint_state_bridge=True,
    ),
}


@dataclass(frozen=True)
class VariantEntry:
    """The two legacy launch files for one supported arm/variant pair."""

    arm_type: str
    arm_variant: str
    real_launch: str
    gazebo_launch: str

    def launch_file(self, mode: str) -> str:
        """Return the legacy launch filename for a canonical mode."""
        if mode == 'real':
            return self.real_launch
        if mode == 'gazebo':
            return self.gazebo_launch
        raise ValueError(
            f"Unsupported mode: {mode}. Valid modes: {', '.join(MODES)}."
        )


@dataclass(frozen=True)
class ResolvedBringupPlan:
    """A normalized, component-level plan for the unified launch."""

    arm_type: str
    arm_variant: str
    mode: str
    arm_profile: ArmProfile
    driver: LaunchReference
    description: LaunchReference
    control: LaunchReference
    gazebo: LaunchReference
    moveit: LaunchReference
    legacy: LaunchReference

    @property
    def components(self) -> tuple[LaunchReference, ...]:
        if self.mode == 'real':
            return (self.driver, self.description, self.control, self.moveit)
        return (self.gazebo, self.moveit)


_VARIANT_ENTRIES = (
    VariantEntry(
        '63',
        'standard',
        'rm_63_bringup.launch.py',
        'rm_63_gazebo.launch.py',
    ),
    VariantEntry(
        '63',
        '6f',
        'rm_63_6f_bringup.launch.py',
        'rm_63_6f_gazebo.launch.py',
    ),
    VariantEntry(
        '63',
        '6fb',
        'rm_63_6fb_bringup.launch.py',
        'rm_63_6fb_gazebo.launch.py',
    ),
    VariantEntry(
        '63_iii',
        'standard',
        'rm_63_III_bringup.launch.py',
        'rm_63_III_gazebo.launch.py',
    ),
    VariantEntry(
        '63_iii',
        '6fb',
        'rm_63_III_6fb_bringup.launch.py',
        'rm_63_III_6fb_gazebo.launch.py',
    ),
    VariantEntry(
        '65',
        'standard',
        'rm_65_bringup.launch.py',
        'rm_65_gazebo.launch.py',
    ),
    VariantEntry(
        '65',
        '6f',
        'rm_65_6f_bringup.launch.py',
        'rm_65_6f_gazebo.launch.py',
    ),
    VariantEntry(
        '65',
        '6fb',
        'rm_65_6fb_bringup.launch.py',
        'rm_65_6fb_gazebo.launch.py',
    ),
    VariantEntry(
        '75',
        'standard',
        'rm_75_bringup.launch.py',
        'rm_75_gazebo.launch.py',
    ),
    VariantEntry(
        '75',
        '6f',
        'rm_75_6f_bringup.launch.py',
        'rm_75_6f_gazebo.launch.py',
    ),
    VariantEntry(
        '75',
        '6fb',
        'rm_75_6fb_bringup.launch.py',
        'rm_75_6fb_gazebo.launch.py',
    ),
    VariantEntry(
        'eco62',
        'standard',
        'rm_eco62_bringup.launch.py',
        'rm_eco62_gazebo.launch.py',
    ),
    VariantEntry(
        'eco63',
        'standard',
        'rm_eco63_bringup.launch.py',
        'rm_eco63_gazebo.launch.py',
    ),
    VariantEntry(
        'eco63',
        '6fb',
        'rm_eco63_6fb_bringup.launch.py',
        'rm_eco63_6fb_gazebo.launch.py',
    ),
    VariantEntry(
        'eco65',
        'standard',
        'rm_eco65_bringup.launch.py',
        'rm_eco65_gazebo.launch.py',
    ),
    VariantEntry(
        'eco65',
        '6f',
        'rm_eco65_6f_bringup.launch.py',
        'rm_eco65_6f_gazebo.launch.py',
    ),
    VariantEntry(
        'eco65',
        '6fb',
        'rm_eco65_6fb_bringup.launch.py',
        'rm_eco65_6fb_gazebo.launch.py',
    ),
    VariantEntry(
        'gen72',
        'standard',
        'rm_gen72_bringup.launch.py',
        'rm_gen72_gazebo.launch.py',
    ),
    VariantEntry(
        'gen72_ii',
        'standard',
        'rm_gen72_II_bringup.launch.py',
        'rm_gen72_II_gazebo.launch.py',
    ),
    VariantEntry(
        'rx75',
        '6fb',
        'rm_rx75_6fb_bringup.launch.py',
        'rm_rx75_6fb_gazebo.launch.py',
    ),
    VariantEntry(
        'rx75',
        '6fb_v',
        'rm_rx75_6fb_v_bringup.launch.py',
        'rm_rx75_6fb_v_gazebo.launch.py',
    ),
)

_variant_keys = tuple(
    (entry.arm_type, entry.arm_variant) for entry in _VARIANT_ENTRIES
)
if len(_variant_keys) != len(set(_variant_keys)):
    raise RuntimeError('Duplicate arm_type/arm_variant entries in variant catalog.')

VARIANT_CATALOG = {
    (entry.arm_type, entry.arm_variant): entry for entry in _VARIANT_ENTRIES
}

_GENERIC_DRIVER = LaunchReference('rm_driver', 'rm_driver.launch.py')
_GENERIC_DESCRIPTION = LaunchReference(
    'rm_description', 'rm_description.launch.py'
)
_GENERIC_CONTROL = LaunchReference('rm_control', 'rm_control.launch.py')
_GENERIC_GAZEBO = LaunchReference('rm_gazebo', 'rm_gazebo.launch.py')

_MOVEIT_LAUNCHES = {
    ('63', 'standard'): (
        'rm_63_config',
        'real_moveit_demo.launch.py',
        'gazebo_moveit_demo.launch.py',
    ),
    ('63', '6f'): (
        'rm_63_config',
        'real_moveit_demo_6f.launch.py',
        'gazebo_moveit_demo_6f.launch.py',
    ),
    ('63', '6fb'): (
        'rm_63_config',
        'real_moveit_demo_6fb.launch.py',
        'gazebo_moveit_demo_6fb.launch.py',
    ),
    ('63_iii', 'standard'): (
        'rm_63_config',
        'real_moveit_demo_III.launch.py',
        'gazebo_moveit_demo_III.launch.py',
    ),
    ('63_iii', '6fb'): (
        'rm_63_config',
        'real_moveit_demo_III_6fb.launch.py',
        'gazebo_moveit_demo_III_6fb.launch.py',
    ),
    ('65', 'standard'): (
        'rm_65_config',
        'real_moveit_demo.launch.py',
        'gazebo_moveit_demo.launch.py',
    ),
    ('65', '6f'): (
        'rm_65_config',
        'real_moveit_demo_6f.launch.py',
        'gazebo_moveit_demo_6f.launch.py',
    ),
    ('65', '6fb'): (
        'rm_65_config',
        'real_moveit_demo_6fb.launch.py',
        'gazebo_moveit_demo_6fb.launch.py',
    ),
    ('75', 'standard'): (
        'rm_75_config',
        'real_moveit_demo.launch.py',
        'gazebo_moveit_demo.launch.py',
    ),
    ('75', '6f'): (
        'rm_75_config',
        'real_moveit_demo_6f.launch.py',
        'gazebo_moveit_demo_6f.launch.py',
    ),
    ('75', '6fb'): (
        'rm_75_config',
        'real_moveit_demo_6fb.launch.py',
        'gazebo_moveit_demo_6fb.launch.py',
    ),
    ('eco62', 'standard'): (
        'rm_eco62_config',
        'real_moveit_demo.launch.py',
        'gazebo_moveit_demo.launch.py',
    ),
    ('eco63', 'standard'): (
        'rm_eco63_config',
        'real_moveit_demo.launch.py',
        'gazebo_moveit_demo.launch.py',
    ),
    ('eco63', '6fb'): (
        'rm_eco63_config',
        'real_moveit_demo_6fb.launch.py',
        'gazebo_moveit_demo_6fb.launch.py',
    ),
    ('eco65', 'standard'): (
        'rm_eco65_config',
        'real_moveit_demo.launch.py',
        'gazebo_moveit_demo.launch.py',
    ),
    ('eco65', '6f'): (
        'rm_eco65_config',
        'real_moveit_demo_6f.launch.py',
        'gazebo_moveit_demo_6f.launch.py',
    ),
    ('eco65', '6fb'): (
        'rm_eco65_config',
        'real_moveit_demo_6fb.launch.py',
        'gazebo_moveit_demo_6fb.launch.py',
    ),
    ('gen72', 'standard'): (
        'rm_gen72_config',
        'real_moveit_demo.launch.py',
        'gazebo_moveit_demo.launch.py',
    ),
    ('gen72_ii', 'standard'): (
        'rm_gen72_config',
        'real_moveit_demo_II.launch.py',
        'gazebo_moveit_demo_II.launch.py',
    ),
    ('rx75', '6fb'): (
        'rm_rx75_config',
        'real_moveit_demo_6fb.launch.py',
        'gazebo_moveit_demo_6fb.launch.py',
    ),
    ('rx75', '6fb_v'): (
        'rm_rx75_config',
        'real_moveit_demo_6fb_v.launch.py',
        'gazebo_moveit_demo_6fb_v.launch.py',
    ),
}

if set(_MOVEIT_LAUNCHES) != set(VARIANT_CATALOG):
    raise RuntimeError('MoveIt launch map and variant catalog are out of sync.')

VARIANTS_BY_ARM_TYPE = {
    arm_type: tuple(
        arm_variant
        for arm_variant in ARM_VARIANTS
        if (arm_type, arm_variant) in VARIANT_CATALOG
    )
    for arm_type in ARM_TYPES
}


_ARM_TYPE_ALIASES = {
    '63': '63',
    'rm63': '63',
    '63iii': '63_iii',
    'rm63iii': '63_iii',
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


def _require_token(value: str | None, parameter: str) -> str:
    if value is None or not isinstance(value, str) or not value.strip():
        if parameter == 'arm_type':
            raise ValueError(
                f"arm_type is required. Valid arm types: {', '.join(ARM_TYPES)}."
            )
        raise ValueError(f'{parameter} must be a non-empty string.')
    return value.strip()


def _compact_token(value: str) -> str:
    normalized = re.sub(r'[\s-]+', '_', value.lower())
    normalized = re.sub(r'_+', '_', normalized).strip('_')
    return normalized.replace('_', '')


def normalize_arm_type(value: str | None) -> str:
    """Normalize a supported arm name, including common ``RM_*`` aliases."""
    raw_value = _require_token(value, 'arm_type')
    normalized = _ARM_TYPE_ALIASES.get(_compact_token(raw_value))
    if normalized is None:
        raise ValueError(
            f'Unsupported arm_type: {raw_value}. '
            f"Valid arm types: {', '.join(ARM_TYPES)}."
        )
    return normalized


def normalize_arm_variant(value: str | None) -> str:
    """Normalize case and separators in an end-link variant name."""
    raw_value = _require_token(value, 'arm_variant')
    compact_value = _compact_token(raw_value)
    aliases = {
        'standard': 'standard',
        '6f': '6f',
        '6fb': '6fb',
        '6fbv': '6fb_v',
    }
    normalized = aliases.get(compact_value)
    if normalized is None:
        raise ValueError(
            f'Unsupported arm_variant: {raw_value}. '
            f"Valid arm variants: {', '.join(ARM_VARIANTS)}."
        )
    return normalized


def normalize_mode(value: str | None) -> str:
    """Normalize a launch mode while rejecting unsupported simulation aliases."""
    raw_value = _require_token(value, 'mode')
    normalized = raw_value.lower()
    if normalized not in MODES:
        raise ValueError(
            f"Unsupported mode: {raw_value}. Valid modes: {', '.join(MODES)}."
        )
    return normalized


def resolve_variant(
    arm_type: str | None,
    arm_variant: str | None = 'standard',
    mode: str | None = 'real',
) -> ResolvedBringupPlan:
    """Resolve public selector values to a component-level bringup plan."""
    canonical_arm_type = normalize_arm_type(arm_type)
    canonical_arm_variant = normalize_arm_variant(arm_variant)
    canonical_mode = normalize_mode(mode)

    entry = VARIANT_CATALOG.get((canonical_arm_type, canonical_arm_variant))
    if entry is None:
        valid_variants = ', '.join(VARIANTS_BY_ARM_TYPE[canonical_arm_type])
        raise ValueError(
            'Unsupported combination: '
            f'arm_type={canonical_arm_type}, '
            f'arm_variant={canonical_arm_variant}.\n'
            f'Valid variants for {canonical_arm_type}: {valid_variants}.'
        )

    moveit_package, real_moveit_launch, gazebo_moveit_launch = (
        _MOVEIT_LAUNCHES[(canonical_arm_type, canonical_arm_variant)]
    )
    moveit_launch = (
        real_moveit_launch
        if canonical_mode == 'real'
        else gazebo_moveit_launch
    )

    return ResolvedBringupPlan(
        arm_type=canonical_arm_type,
        arm_variant=canonical_arm_variant,
        mode=canonical_mode,
        arm_profile=ARM_PROFILES[canonical_arm_type],
        driver=_GENERIC_DRIVER,
        description=_GENERIC_DESCRIPTION,
        control=_GENERIC_CONTROL,
        gazebo=_GENERIC_GAZEBO,
        moveit=LaunchReference(moveit_package, moveit_launch),
        legacy=LaunchReference(
            PACKAGE_NAME,
            entry.launch_file(canonical_mode),
        ),
    )
