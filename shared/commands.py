"""Auto-generated command type definitions.

Generated from handler function signatures by scripts/generate_command_types.py.
Do not edit manually — regenerate after changing handler signatures.
"""

from __future__ import annotations

from typing import Any, TypedDict

REGISTRY_FINGERPRINT = "5e2327273bdb4042"


# ============================================================
# arrangement
# ============================================================

class DeleteArrangementClipParams(TypedDict, total=False):
    track_index: int
    clip_index_in_arrangement: int


class DuplicateClipToArrangementParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    time: float


class GetArrangementClipInfoParams(TypedDict, total=False):
    track_index: int
    clip_index_in_arrangement: int


class GetArrangementClipsParams(TypedDict, total=False):
    track_index: int


class MoveArrangementClipParams(TypedDict, total=False):
    track_index: int
    clip_index_in_arrangement: int
    new_start_time: float


class SetArrangementClipPropertiesParams(TypedDict, total=False):
    track_index: int
    clip_index_in_arrangement: int
    muted: bool | None
    gain: float | None
    name: str | None
    color_index: int | None
    loop_start: float | None
    loop_end: float | None
    looping: bool | None
    start_marker: float | None
    end_marker: float | None
    pitch_coarse: int | None
    pitch_fine: int | None


# ============================================================
# audio
# ============================================================

class AnalyzeAudioClipParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class FreezeTrackParams(TypedDict, total=False):
    track_index: int


class GetAudioClipInfoParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class ReverseClipParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class SetClipWarpParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    warping_enabled: bool


class SetWarpModeParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    warp_mode: str


class UnfreezeTrackParams(TypedDict, total=False):
    track_index: int


# ============================================================
# automation
# ============================================================

class ClearAllClipEnvelopesParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class ClearClipAutomationParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    parameter_name: str
    device_index: int | None


class ClearClipEnvelopeParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    parameter_name: str
    device_index: int | None


class ClearTrackAutomationParams(TypedDict, total=False):
    track_index: int
    parameter_name: str
    start_time: float
    end_time: float
    device_index: int | None


class CreateClipAutomationParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    parameter_name: str
    automation_points: list
    device_index: int | None
    append: bool


class CreateStepAutomationParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    parameter_name: str
    steps: list
    device_index: int | None


class CreateTrackAutomationParams(TypedDict, total=False):
    track_index: int
    parameter_name: str
    automation_points: list
    device_index: int | None
    append: bool


class DeleteTimeParams(TypedDict, total=False):
    start_time: float
    end_time: float


class DuplicateTimeParams(TypedDict, total=False):
    start_time: float
    end_time: float


class GetClipAutomationParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    parameter_name: str
    device_index: int | None


class GetClipAutomationHiresParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    parameter_name: str
    sample_count: int
    device_index: int | None


class GetClipAutomationValueParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    parameter_name: str
    time: float
    device_index: int | None


class InsertSilenceParams(TypedDict, total=False):
    position: float
    length: float


class ListClipAutomatedParamsParams(TypedDict, total=False):
    track_index: int
    clip_index: int


# ============================================================
# browser
# ============================================================

class GetBrowserItemParams(TypedDict, total=False):
    uri: str | None
    path: str | None


class GetBrowserItemsAtPathParams(TypedDict, total=False):
    path: str


class GetBrowserTreeParams(TypedDict, total=False):
    category_type: str


class GetDevicePresetsParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class GetUserFoldersParams(TypedDict, total=False):
    pass


class GetUserLibraryParams(TypedDict, total=False):
    pass


class LoadBrowserItemParams(TypedDict, total=False):
    track_index: int
    item_uri: str


class LoadDevicePresetParams(TypedDict, total=False):
    track_index: int
    device_index: int
    preset_uri: str
    track_type: str


class LoadInstrumentOrEffectParams(TypedDict, total=False):
    track_index: int
    uri: str


class LoadSampleParams(TypedDict, total=False):
    track_index: int
    sample_uri: str


class PreviewBrowserItemParams(TypedDict, total=False):
    uri: str | None
    action: str


class SearchBrowserParams(TypedDict, total=False):
    query: str
    category: str


# ============================================================
# clips
# ============================================================

class AddNotesToClipParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    notes: list


class AddWarpMarkerParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    beat_time: float
    sample_time: float


class AudioToMidiParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    conversion_type: str


class ClipBeatToSampleTimeParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    beat_time: float


class ClipSampleToBeatTimeParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    sample_time: float


class ClipScrubNativeParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    position: float


class ClipStopScrubParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class CreateArrangementAudioClipParams(TypedDict, total=False):
    track_index: int
    time: float
    length: float


class CreateArrangementMidiClipParams(TypedDict, total=False):
    track_index: int
    time: float
    length: float


class CreateClipParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    length: float


class CropClipParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class DeleteClipParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class DeselectAllNotesParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class DuplicateClipParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    target_clip_index: int


class DuplicateClipLoopParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class DuplicateClipRegionParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    region_start: float
    region_length: float
    destination_time: float
    pitch: int
    transposition_amount: int


class DuplicateClipSlotParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class FireClipParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class GetClipFollowActionsParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class GetClipInfoParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class GetClipPropertiesParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class GetClipSlotPropertiesParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class GetSelectedNotesParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class GetWarpMarkersParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class MoveClipPlayingPosParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    time: float


class MoveWarpMarkerParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    beat_time: float
    beat_time_distance: float


class RemoveWarpMarkerParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    beat_time: float


class SelectAllNotesParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class SetClipColorParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    color_index: int


class SetClipFollowActionsParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    follow_action_0: int
    follow_action_1: int
    follow_action_probability: float
    follow_action_time: float
    follow_action_enabled: bool
    follow_action_linked: bool
    follow_action_return_to_zero: bool


class SetClipGridParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    grid_quantization: float
    grid_is_triplet: bool


class SetClipLaunchModeParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    launch_mode: int


class SetClipLaunchQuantizationParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    quantization: int


class SetClipLegatoParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    legato: bool


class SetClipLoopPointsParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    loop_start: float
    loop_end: float


class SetClipLoopingParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    looping: bool


class SetClipNameParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    name: str


class SetClipPitchParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    pitch_coarse: int
    pitch_fine: int


class SetClipPropertiesParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    muted: bool
    velocity_amount: float
    groove: float
    signature_numerator: int
    signature_denominator: int
    ram_mode: bool
    warping: bool
    gain: float


class SetClipSlotPropertiesParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    has_stop_button: bool
    color_index: int


class SetClipStartEndParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    start_marker: float
    end_marker: float


class SetClipStartTimeParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    time: float


class SetFireButtonStateParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    state: bool


class StopClipParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class StopTrackClipsParams(TypedDict, total=False):
    track_index: int


# ============================================================
# devices
# ============================================================

class ChainInsertDeviceParams(TypedDict, total=False):
    track_index: int
    device_index: int
    chain_index: int
    device_name: str
    target_index: int | None
    track_type: str


class ControlLooperParams(TypedDict, total=False):
    track_index: int
    device_index: int
    action: str
    clip_slot_index: int | None
    track_type: str


class CopyDrumPadParams(TypedDict, total=False):
    track_index: int
    device_index: int
    source_note: int
    dest_note: int
    track_type: str


class DeleteChainDeviceParams(TypedDict, total=False):
    track_index: int
    device_index: int
    chain_index: int
    chain_device_index: int
    track_type: str


class DeleteDeviceParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class GetChainSelectorParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class GetCompressorSidechainParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class GetDeviceInfoParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class GetDeviceParametersParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class GetDrumPadsParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class GetEq8PropertiesParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class GetHybridReverbIrParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class GetMacroValuesParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class GetRackVariationsParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class GetSimplerPropertiesParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class GetTransmutePropertiesParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class InsertChainParams(TypedDict, total=False):
    track_index: int
    device_index: int
    index: int
    track_type: str


class ManageSampleSlicesParams(TypedDict, total=False):
    track_index: int
    device_index: int
    action: str
    slice_time: int | None
    new_time: int | None
    track_type: str


class MoveDeviceParams(TypedDict, total=False):
    track_index: int
    device_index: int
    dest_track_index: int
    dest_position: int
    track_type: str


class RackVariationActionParams(TypedDict, total=False):
    track_index: int
    device_index: int
    action: str
    variation_index: int | None
    track_type: str


class SetChainPropertiesParams(TypedDict, total=False):
    track_index: int
    device_index: int
    chain_index: int
    mute: bool | None
    solo: bool | None
    name: str | None
    color_index: int | None
    volume: float | None
    panning: float | None
    track_type: str


class SetChainSelectorParams(TypedDict, total=False):
    track_index: int
    device_index: int
    value: float
    track_type: str


class SetCompressorSidechainParams(TypedDict, total=False):
    track_index: int
    device_index: int
    input_type: str | None
    input_channel: str | None
    track_type: str


class SetDeviceEnabledParams(TypedDict, total=False):
    track_index: int
    device_index: int
    enabled: bool
    track_type: str


class SetDeviceParameterParams(TypedDict, total=False):
    track_index: int
    device_index: int
    parameter_name: str
    value: float
    track_type: str
    value_display: str | None


class SetDeviceParametersBatchParams(TypedDict, total=False):
    track_index: int
    device_index: int
    parameters: list
    track_type: str


class SetDrumPadParams(TypedDict, total=False):
    track_index: int
    device_index: int
    note: int
    mute: bool | None
    solo: bool | None
    track_type: str


class SetEq8PropertiesParams(TypedDict, total=False):
    track_index: int
    device_index: int
    edit_mode: int | None
    global_mode: int | None
    oversample: bool | None
    selected_band: int | None
    track_type: str


class SetHybridReverbIrParams(TypedDict, total=False):
    track_index: int
    device_index: int
    ir_category_index: int | None
    ir_file_index: int | None
    ir_attack_time: float | None
    ir_decay_time: float | None
    ir_size_factor: float | None
    ir_time_shaping_on: bool | None
    track_type: str


class SetMacroValueParams(TypedDict, total=False):
    track_index: int
    device_index: int
    macro_index: int
    value: float
    track_type: str


class SetSidechainByNameParams(TypedDict, total=False):
    track_index: int
    device_index: int
    source_track_name: str
    track_type: str


class SetSimplerPropertiesParams(TypedDict, total=False):
    track_index: int
    device_index: int
    playback_mode: int | None
    voices: int | None
    retrigger: bool | None
    slicing_playback_mode: int | None
    start_marker: int | None
    end_marker: int | None
    gain: float | None
    warp_mode: int | None
    warping: bool | None
    slicing_style: int | None
    slicing_sensitivity: float | None
    slicing_beat_division: int | None
    beats_granulation_resolution: int | None
    beats_transient_envelope: float | None
    beats_transient_loop_mode: int | None
    complex_pro_formants: float | None
    complex_pro_envelope: float | None
    texture_grain_size: float | None
    texture_flux: float | None
    tones_grain_size: float | None
    track_type: str


class SetTransmutePropertiesParams(TypedDict, total=False):
    track_index: int
    device_index: int
    frequency_dial_mode_index: int | None
    pitch_mode_index: int | None
    mod_mode_index: int | None
    mono_poly_index: int | None
    midi_gate_index: int | None
    polyphony: int | None
    pitch_bend_range: int | None
    track_type: str


class SimplerSampleActionParams(TypedDict, total=False):
    track_index: int
    device_index: int
    action: str
    beats: float | None
    track_type: str


class SlicedSimplerToDrumRackParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


# ============================================================
# midi
# ============================================================

class AddNotesExtendedParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    notes: list


class ApplyGrooveParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    groove_amount: float


class CaptureMidiParams(TypedDict, total=False):
    pass


class ClearClipNotesParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class GetClipNotesParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    start_time: float
    time_span: float
    start_pitch: int
    pitch_span: int


class GetNotesExtendedParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    start_time: float
    time_span: float


class QuantizeClipNotesParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    grid_size: float


class RemoveNotesRangeParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    from_time: float
    time_span: float
    from_pitch: int
    pitch_span: int


class TransposeClipNotesParams(TypedDict, total=False):
    track_index: int
    clip_index: int
    semitones: int


# ============================================================
# mixer
# ============================================================

class GetCrossfaderParams(TypedDict, total=False):
    pass


class GetMasterTrackInfoParams(TypedDict, total=False):
    pass


class GetReturnTrackInfoParams(TypedDict, total=False):
    return_track_index: int


class GetReturnTracksParams(TypedDict, total=False):
    pass


class GetScenesParams(TypedDict, total=False):
    pass


class GetTrackDelayParams(TypedDict, total=False):
    track_index: int


class SetCrossfadeAssignParams(TypedDict, total=False):
    track_index: int
    assign: int


class SetCrossfaderParams(TypedDict, total=False):
    value: float


class SetCueVolumeParams(TypedDict, total=False):
    value: float


class SetMasterVolumeParams(TypedDict, total=False):
    volume: float


class SetPanningModeParams(TypedDict, total=False):
    track_index: int
    mode: int


class SetReturnTrackMuteParams(TypedDict, total=False):
    return_track_index: int
    mute: bool


class SetReturnTrackPanParams(TypedDict, total=False):
    return_track_index: int
    pan: float


class SetReturnTrackSoloParams(TypedDict, total=False):
    return_track_index: int
    solo: bool


class SetReturnTrackVolumeParams(TypedDict, total=False):
    return_track_index: int
    volume: float


class SetSplitStereoPanParams(TypedDict, total=False):
    track_index: int
    left: float | None
    right: float | None


class SetTrackArmParams(TypedDict, total=False):
    track_index: int
    arm: bool


class SetTrackDelayParams(TypedDict, total=False):
    track_index: int
    delay: float


class SetTrackMuteParams(TypedDict, total=False):
    track_index: int
    mute: bool


class SetTrackPanParams(TypedDict, total=False):
    track_index: int
    pan: float


class SetTrackSendParams(TypedDict, total=False):
    track_index: int
    send_index: int
    value: float


class SetTrackSoloParams(TypedDict, total=False):
    track_index: int
    solo: bool


class SetTrackVolumeParams(TypedDict, total=False):
    track_index: int
    volume: float


# ============================================================
# scenes
# ============================================================

class CreateSceneParams(TypedDict, total=False):
    index: int
    name: str


class DeleteSceneParams(TypedDict, total=False):
    scene_index: int


class DuplicateSceneParams(TypedDict, total=False):
    scene_index: int


class FireSceneParams(TypedDict, total=False):
    scene_index: int


class FireSceneAsSelectedParams(TypedDict, total=False):
    scene_index: int


class GetSceneFollowActionsParams(TypedDict, total=False):
    scene_index: int


class SetSceneColorParams(TypedDict, total=False):
    scene_index: int
    color_index: int


class SetSceneFollowActionsParams(TypedDict, total=False):
    scene_index: int
    follow_action_0: int | None
    follow_action_1: int | None
    follow_action_probability: float | None
    follow_action_time: float | None
    follow_action_enabled: bool | None
    follow_action_linked: bool | None


class SetSceneNameParams(TypedDict, total=False):
    scene_index: int
    name: str


class SetSceneTempoParams(TypedDict, total=False):
    scene_index: int
    tempo: float


# ============================================================
# session
# ============================================================

class CaptureAndInsertSceneParams(TypedDict, total=False):
    pass


class ContinuePlayingParams(TypedDict, total=False):
    pass


class EndUndoStepParams(TypedDict, total=False):
    pass


class GetAllScalesParams(TypedDict, total=False):
    pass


class GetAppointedDeviceParams(TypedDict, total=False):
    pass


class GetBeatTimeParams(TypedDict, total=False):
    pass


class GetCountInDurationParams(TypedDict, total=False):
    pass


class GetCuePointsParams(TypedDict, total=False):
    pass


class GetGroovePoolParams(TypedDict, total=False):
    pass


class GetHighlightedClipSlotParams(TypedDict, total=False):
    pass


class GetLinkStatusParams(TypedDict, total=False):
    pass


class GetLoopInfoParams(TypedDict, total=False):
    pass


class GetPlayingClipsParams(TypedDict, total=False):
    pass


class GetRecordingStatusParams(TypedDict, total=False):
    pass


class GetSelectedParameterParams(TypedDict, total=False):
    pass


class GetSelectionStateParams(TypedDict, total=False):
    pass


class GetSessionInfoParams(TypedDict, total=False):
    pass


class GetSmpteTimeParams(TypedDict, total=False):
    time_format: int


class GetSongDataParams(TypedDict, total=False):
    key: str


class GetSongFilePathParams(TypedDict, total=False):
    pass


class GetSongLengthParams(TypedDict, total=False):
    pass


class GetSongScaleParams(TypedDict, total=False):
    pass


class GetSongSettingsParams(TypedDict, total=False):
    pass


class GetSongTransportParams(TypedDict, total=False):
    pass


class GetTuningSystemParams(TypedDict, total=False):
    pass


class GetViewStateParams(TypedDict, total=False):
    pass


class JumpToCueParams(TypedDict, total=False):
    direction: str


class NavigatePlaybackParams(TypedDict, total=False):
    action: str
    beats: float


class NudgeTempoParams(TypedDict, total=False):
    direction: str


class ReEnableAutomationParams(TypedDict, total=False):
    pass


class RedoParams(TypedDict, total=False):
    pass


class SelectDeviceParams(TypedDict, total=False):
    track_index: int
    device_index: int
    track_type: str


class SelectInstrumentParams(TypedDict, total=False):
    track_index: int


class SelectSceneParams(TypedDict, total=False):
    scene_index: int


class SelectTrackParams(TypedDict, total=False):
    track_index: int
    track_type: str


class SetArrangementOverdubParams(TypedDict, total=False):
    enabled: bool


class SetDetailClipParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class SetDrawModeParams(TypedDict, total=False):
    enabled: bool


class SetFollowSongParams(TypedDict, total=False):
    enabled: bool


class SetGrooveSettingsParams(TypedDict, total=False):
    groove_amount: float
    groove_index: int
    timing_amount: float
    quantization_amount: float
    random_amount: float
    velocity_amount: float


class SetLinkEnabledParams(TypedDict, total=False):
    enabled: bool
    start_stop_sync: bool


class SetLoopEndParams(TypedDict, total=False):
    position: float


class SetLoopLengthParams(TypedDict, total=False):
    length: float


class SetLoopStartParams(TypedDict, total=False):
    position: float


class SetMetronomeParams(TypedDict, total=False):
    enabled: bool


class SetOrDeleteCueParams(TypedDict, total=False):
    pass


class SetPlaybackPositionParams(TypedDict, total=False):
    position: float


class SetPunchParams(TypedDict, total=False):
    punch_in: bool
    punch_out: bool
    count_in_duration: int


class SetSessionRecordParams(TypedDict, total=False):
    enabled: bool


class SetSongDataParams(TypedDict, total=False):
    key: str
    value: str


class SetSongLoopParams(TypedDict, total=False):
    enabled: bool
    start: float
    length: float


class SetSongScaleParams(TypedDict, total=False):
    root_note: int
    scale_name: str
    scale_mode: bool


class SetSongSettingsParams(TypedDict, total=False):
    signature_numerator: int
    signature_denominator: int
    swing_amount: float
    clip_trigger_quantization: int
    midi_recording_quantization: int
    back_to_arranger: bool
    follow_song: bool
    draw_mode: bool
    session_automation_record: bool


class SetSongTimeParams(TypedDict, total=False):
    time: float


class SetTempoParams(TypedDict, total=False):
    tempo: float


class SetViewParams(TypedDict, total=False):
    action: str
    view_name: str


class StartArrangementRecordingParams(TypedDict, total=False):
    pass


class StartPlaybackParams(TypedDict, total=False):
    pass


class StopAllClipsParams(TypedDict, total=False):
    pass


class StopArrangementRecordingParams(TypedDict, total=False):
    stop_playback: bool


class StopPlaybackParams(TypedDict, total=False):
    pass


class TapTempoParams(TypedDict, total=False):
    pass


class TriggerSessionRecordParams(TypedDict, total=False):
    record_length: float


class UndoParams(TypedDict, total=False):
    pass


class ZoomScrollViewParams(TypedDict, total=False):
    action: str
    direction: int
    view_name: str
    modifier_pressed: bool


# ============================================================
# tracks
# ============================================================

class ArmTrackParams(TypedDict, total=False):
    track_index: int


class CreateAudioTrackParams(TypedDict, total=False):
    index: int


class CreateMidiTrackParams(TypedDict, total=False):
    index: int


class CreateMidiTrackWithSimplerParams(TypedDict, total=False):
    track_index: int
    clip_index: int


class CreateReturnTrackParams(TypedDict, total=False):
    pass


class CreateTakeLaneParams(TypedDict, total=False):
    track_index: int


class DeleteReturnTrackParams(TypedDict, total=False):
    return_index: int


class DeleteTrackParams(TypedDict, total=False):
    track_index: int


class DisarmTrackParams(TypedDict, total=False):
    track_index: int


class DuplicateTrackParams(TypedDict, total=False):
    track_index: int


class GetAllTracksInfoParams(TypedDict, total=False):
    pass


class GetReturnTracksInfoParams(TypedDict, total=False):
    pass


class GetTakeLanesParams(TypedDict, total=False):
    track_index: int


class GetTrackDataParams(TypedDict, total=False):
    track_index: int
    key: str


class GetTrackInfoParams(TypedDict, total=False):
    track_index: int


class GetTrackInputMetersParams(TypedDict, total=False):
    track_index: int


class GetTrackMetersParams(TypedDict, total=False):
    track_index: int


class GetTrackRoutingParams(TypedDict, total=False):
    track_index: int


class GroupTracksParams(TypedDict, total=False):
    track_indices: list
    name: str


class InsertDeviceParams(TypedDict, total=False):
    track_index: int
    device_name: str
    target_index: int


class JumpInRunningSessionClipParams(TypedDict, total=False):
    track_index: int
    amount: float


class SetImplicitArmParams(TypedDict, total=False):
    track_index: int
    enabled: bool


class SetTrackCollapseParams(TypedDict, total=False):
    track_index: int
    collapsed: bool


class SetTrackColorParams(TypedDict, total=False):
    track_index: int
    color_index: int


class SetTrackDataParams(TypedDict, total=False):
    track_index: int
    key: str
    value: str


class SetTrackFoldParams(TypedDict, total=False):
    track_index: int
    fold_state: bool


class SetTrackMonitoringParams(TypedDict, total=False):
    track_index: int
    state: int


class SetTrackNameParams(TypedDict, total=False):
    track_index: int
    name: str


class SetTrackRoutingParams(TypedDict, total=False):
    track_index: int
    input_type: str
    input_channel: str
    output_type: str
    output_channel: str


# ============================================================
# Command metadata
# ============================================================

COMMAND_TYPES: dict[str, type] = {
    "add_notes_extended": AddNotesExtendedParams,
    "add_notes_to_clip": AddNotesToClipParams,
    "add_warp_marker": AddWarpMarkerParams,
    "analyze_audio_clip": AnalyzeAudioClipParams,
    "apply_groove": ApplyGrooveParams,
    "arm_track": ArmTrackParams,
    "audio_to_midi": AudioToMidiParams,
    "capture_and_insert_scene": CaptureAndInsertSceneParams,
    "capture_midi": CaptureMidiParams,
    "chain_insert_device": ChainInsertDeviceParams,
    "clear_all_clip_envelopes": ClearAllClipEnvelopesParams,
    "clear_clip_automation": ClearClipAutomationParams,
    "clear_clip_envelope": ClearClipEnvelopeParams,
    "clear_clip_notes": ClearClipNotesParams,
    "clear_track_automation": ClearTrackAutomationParams,
    "clip_beat_to_sample_time": ClipBeatToSampleTimeParams,
    "clip_sample_to_beat_time": ClipSampleToBeatTimeParams,
    "clip_scrub_native": ClipScrubNativeParams,
    "clip_stop_scrub": ClipStopScrubParams,
    "continue_playing": ContinuePlayingParams,
    "control_looper": ControlLooperParams,
    "copy_drum_pad": CopyDrumPadParams,
    "create_arrangement_audio_clip": CreateArrangementAudioClipParams,
    "create_arrangement_midi_clip": CreateArrangementMidiClipParams,
    "create_audio_track": CreateAudioTrackParams,
    "create_clip": CreateClipParams,
    "create_clip_automation": CreateClipAutomationParams,
    "create_midi_track": CreateMidiTrackParams,
    "create_midi_track_with_simpler": CreateMidiTrackWithSimplerParams,
    "create_return_track": CreateReturnTrackParams,
    "create_scene": CreateSceneParams,
    "create_step_automation": CreateStepAutomationParams,
    "create_take_lane": CreateTakeLaneParams,
    "create_track_automation": CreateTrackAutomationParams,
    "crop_clip": CropClipParams,
    "delete_arrangement_clip": DeleteArrangementClipParams,
    "delete_chain_device": DeleteChainDeviceParams,
    "delete_clip": DeleteClipParams,
    "delete_device": DeleteDeviceParams,
    "delete_return_track": DeleteReturnTrackParams,
    "delete_scene": DeleteSceneParams,
    "delete_time": DeleteTimeParams,
    "delete_track": DeleteTrackParams,
    "deselect_all_notes": DeselectAllNotesParams,
    "disarm_track": DisarmTrackParams,
    "duplicate_clip": DuplicateClipParams,
    "duplicate_clip_loop": DuplicateClipLoopParams,
    "duplicate_clip_region": DuplicateClipRegionParams,
    "duplicate_clip_slot": DuplicateClipSlotParams,
    "duplicate_clip_to_arrangement": DuplicateClipToArrangementParams,
    "duplicate_scene": DuplicateSceneParams,
    "duplicate_time": DuplicateTimeParams,
    "duplicate_track": DuplicateTrackParams,
    "end_undo_step": EndUndoStepParams,
    "fire_clip": FireClipParams,
    "fire_scene": FireSceneParams,
    "fire_scene_as_selected": FireSceneAsSelectedParams,
    "freeze_track": FreezeTrackParams,
    "get_all_scales": GetAllScalesParams,
    "get_all_tracks_info": GetAllTracksInfoParams,
    "get_appointed_device": GetAppointedDeviceParams,
    "get_arrangement_clip_info": GetArrangementClipInfoParams,
    "get_arrangement_clips": GetArrangementClipsParams,
    "get_audio_clip_info": GetAudioClipInfoParams,
    "get_beat_time": GetBeatTimeParams,
    "get_browser_item": GetBrowserItemParams,
    "get_browser_items_at_path": GetBrowserItemsAtPathParams,
    "get_browser_tree": GetBrowserTreeParams,
    "get_chain_selector": GetChainSelectorParams,
    "get_clip_automation": GetClipAutomationParams,
    "get_clip_automation_hires": GetClipAutomationHiresParams,
    "get_clip_automation_value": GetClipAutomationValueParams,
    "get_clip_follow_actions": GetClipFollowActionsParams,
    "get_clip_info": GetClipInfoParams,
    "get_clip_notes": GetClipNotesParams,
    "get_clip_properties": GetClipPropertiesParams,
    "get_clip_slot_properties": GetClipSlotPropertiesParams,
    "get_compressor_sidechain": GetCompressorSidechainParams,
    "get_count_in_duration": GetCountInDurationParams,
    "get_crossfader": GetCrossfaderParams,
    "get_cue_points": GetCuePointsParams,
    "get_device_info": GetDeviceInfoParams,
    "get_device_parameters": GetDeviceParametersParams,
    "get_device_presets": GetDevicePresetsParams,
    "get_drum_pads": GetDrumPadsParams,
    "get_eq8_properties": GetEq8PropertiesParams,
    "get_groove_pool": GetGroovePoolParams,
    "get_highlighted_clip_slot": GetHighlightedClipSlotParams,
    "get_hybrid_reverb_ir": GetHybridReverbIrParams,
    "get_link_status": GetLinkStatusParams,
    "get_loop_info": GetLoopInfoParams,
    "get_macro_values": GetMacroValuesParams,
    "get_master_track_info": GetMasterTrackInfoParams,
    "get_notes_extended": GetNotesExtendedParams,
    "get_playing_clips": GetPlayingClipsParams,
    "get_rack_variations": GetRackVariationsParams,
    "get_recording_status": GetRecordingStatusParams,
    "get_return_track_info": GetReturnTrackInfoParams,
    "get_return_tracks": GetReturnTracksParams,
    "get_return_tracks_info": GetReturnTracksInfoParams,
    "get_scene_follow_actions": GetSceneFollowActionsParams,
    "get_scenes": GetScenesParams,
    "get_selected_notes": GetSelectedNotesParams,
    "get_selected_parameter": GetSelectedParameterParams,
    "get_selection_state": GetSelectionStateParams,
    "get_session_info": GetSessionInfoParams,
    "get_simpler_properties": GetSimplerPropertiesParams,
    "get_smpte_time": GetSmpteTimeParams,
    "get_song_data": GetSongDataParams,
    "get_song_file_path": GetSongFilePathParams,
    "get_song_length": GetSongLengthParams,
    "get_song_scale": GetSongScaleParams,
    "get_song_settings": GetSongSettingsParams,
    "get_song_transport": GetSongTransportParams,
    "get_take_lanes": GetTakeLanesParams,
    "get_track_data": GetTrackDataParams,
    "get_track_delay": GetTrackDelayParams,
    "get_track_info": GetTrackInfoParams,
    "get_track_input_meters": GetTrackInputMetersParams,
    "get_track_meters": GetTrackMetersParams,
    "get_track_routing": GetTrackRoutingParams,
    "get_transmute_properties": GetTransmutePropertiesParams,
    "get_tuning_system": GetTuningSystemParams,
    "get_user_folders": GetUserFoldersParams,
    "get_user_library": GetUserLibraryParams,
    "get_view_state": GetViewStateParams,
    "get_warp_markers": GetWarpMarkersParams,
    "group_tracks": GroupTracksParams,
    "insert_chain": InsertChainParams,
    "insert_device": InsertDeviceParams,
    "insert_silence": InsertSilenceParams,
    "jump_in_running_session_clip": JumpInRunningSessionClipParams,
    "jump_to_cue": JumpToCueParams,
    "list_clip_automated_params": ListClipAutomatedParamsParams,
    "load_browser_item": LoadBrowserItemParams,
    "load_device_preset": LoadDevicePresetParams,
    "load_instrument_or_effect": LoadInstrumentOrEffectParams,
    "load_sample": LoadSampleParams,
    "manage_sample_slices": ManageSampleSlicesParams,
    "move_arrangement_clip": MoveArrangementClipParams,
    "move_clip_playing_pos": MoveClipPlayingPosParams,
    "move_device": MoveDeviceParams,
    "move_warp_marker": MoveWarpMarkerParams,
    "navigate_playback": NavigatePlaybackParams,
    "nudge_tempo": NudgeTempoParams,
    "preview_browser_item": PreviewBrowserItemParams,
    "quantize_clip_notes": QuantizeClipNotesParams,
    "rack_variation_action": RackVariationActionParams,
    "re_enable_automation": ReEnableAutomationParams,
    "redo": RedoParams,
    "remove_notes_range": RemoveNotesRangeParams,
    "remove_warp_marker": RemoveWarpMarkerParams,
    "reverse_clip": ReverseClipParams,
    "search_browser": SearchBrowserParams,
    "select_all_notes": SelectAllNotesParams,
    "select_device": SelectDeviceParams,
    "select_instrument": SelectInstrumentParams,
    "select_scene": SelectSceneParams,
    "select_track": SelectTrackParams,
    "set_arrangement_clip_properties": SetArrangementClipPropertiesParams,
    "set_arrangement_overdub": SetArrangementOverdubParams,
    "set_chain_properties": SetChainPropertiesParams,
    "set_chain_selector": SetChainSelectorParams,
    "set_clip_color": SetClipColorParams,
    "set_clip_follow_actions": SetClipFollowActionsParams,
    "set_clip_grid": SetClipGridParams,
    "set_clip_launch_mode": SetClipLaunchModeParams,
    "set_clip_launch_quantization": SetClipLaunchQuantizationParams,
    "set_clip_legato": SetClipLegatoParams,
    "set_clip_loop_points": SetClipLoopPointsParams,
    "set_clip_looping": SetClipLoopingParams,
    "set_clip_name": SetClipNameParams,
    "set_clip_pitch": SetClipPitchParams,
    "set_clip_properties": SetClipPropertiesParams,
    "set_clip_slot_properties": SetClipSlotPropertiesParams,
    "set_clip_start_end": SetClipStartEndParams,
    "set_clip_start_time": SetClipStartTimeParams,
    "set_clip_warp": SetClipWarpParams,
    "set_compressor_sidechain": SetCompressorSidechainParams,
    "set_crossfade_assign": SetCrossfadeAssignParams,
    "set_crossfader": SetCrossfaderParams,
    "set_cue_volume": SetCueVolumeParams,
    "set_detail_clip": SetDetailClipParams,
    "set_device_enabled": SetDeviceEnabledParams,
    "set_device_parameter": SetDeviceParameterParams,
    "set_device_parameters_batch": SetDeviceParametersBatchParams,
    "set_draw_mode": SetDrawModeParams,
    "set_drum_pad": SetDrumPadParams,
    "set_eq8_properties": SetEq8PropertiesParams,
    "set_fire_button_state": SetFireButtonStateParams,
    "set_follow_song": SetFollowSongParams,
    "set_groove_settings": SetGrooveSettingsParams,
    "set_hybrid_reverb_ir": SetHybridReverbIrParams,
    "set_implicit_arm": SetImplicitArmParams,
    "set_link_enabled": SetLinkEnabledParams,
    "set_loop_end": SetLoopEndParams,
    "set_loop_length": SetLoopLengthParams,
    "set_loop_start": SetLoopStartParams,
    "set_macro_value": SetMacroValueParams,
    "set_master_volume": SetMasterVolumeParams,
    "set_metronome": SetMetronomeParams,
    "set_or_delete_cue": SetOrDeleteCueParams,
    "set_panning_mode": SetPanningModeParams,
    "set_playback_position": SetPlaybackPositionParams,
    "set_punch": SetPunchParams,
    "set_return_track_mute": SetReturnTrackMuteParams,
    "set_return_track_pan": SetReturnTrackPanParams,
    "set_return_track_solo": SetReturnTrackSoloParams,
    "set_return_track_volume": SetReturnTrackVolumeParams,
    "set_scene_color": SetSceneColorParams,
    "set_scene_follow_actions": SetSceneFollowActionsParams,
    "set_scene_name": SetSceneNameParams,
    "set_scene_tempo": SetSceneTempoParams,
    "set_session_record": SetSessionRecordParams,
    "set_sidechain_by_name": SetSidechainByNameParams,
    "set_simpler_properties": SetSimplerPropertiesParams,
    "set_song_data": SetSongDataParams,
    "set_song_loop": SetSongLoopParams,
    "set_song_scale": SetSongScaleParams,
    "set_song_settings": SetSongSettingsParams,
    "set_song_time": SetSongTimeParams,
    "set_split_stereo_pan": SetSplitStereoPanParams,
    "set_tempo": SetTempoParams,
    "set_track_arm": SetTrackArmParams,
    "set_track_collapse": SetTrackCollapseParams,
    "set_track_color": SetTrackColorParams,
    "set_track_data": SetTrackDataParams,
    "set_track_delay": SetTrackDelayParams,
    "set_track_fold": SetTrackFoldParams,
    "set_track_monitoring": SetTrackMonitoringParams,
    "set_track_mute": SetTrackMuteParams,
    "set_track_name": SetTrackNameParams,
    "set_track_pan": SetTrackPanParams,
    "set_track_routing": SetTrackRoutingParams,
    "set_track_send": SetTrackSendParams,
    "set_track_solo": SetTrackSoloParams,
    "set_track_volume": SetTrackVolumeParams,
    "set_transmute_properties": SetTransmutePropertiesParams,
    "set_view": SetViewParams,
    "set_warp_mode": SetWarpModeParams,
    "simpler_sample_action": SimplerSampleActionParams,
    "sliced_simpler_to_drum_rack": SlicedSimplerToDrumRackParams,
    "start_arrangement_recording": StartArrangementRecordingParams,
    "start_playback": StartPlaybackParams,
    "stop_all_clips": StopAllClipsParams,
    "stop_arrangement_recording": StopArrangementRecordingParams,
    "stop_clip": StopClipParams,
    "stop_playback": StopPlaybackParams,
    "stop_track_clips": StopTrackClipsParams,
    "tap_tempo": TapTempoParams,
    "transpose_clip_notes": TransposeClipNotesParams,
    "trigger_session_record": TriggerSessionRecordParams,
    "undo": UndoParams,
    "unfreeze_track": UnfreezeTrackParams,
    "zoom_scroll_view": ZoomScrollViewParams,
}

MODIFYING_COMMANDS: frozenset[str] = frozenset({
    "add_notes_extended",
    "add_notes_to_clip",
    "add_warp_marker",
    "apply_groove",
    "arm_track",
    "audio_to_midi",
    "capture_and_insert_scene",
    "capture_midi",
    "chain_insert_device",
    "clear_all_clip_envelopes",
    "clear_clip_automation",
    "clear_clip_envelope",
    "clear_clip_notes",
    "clear_track_automation",
    "clip_scrub_native",
    "clip_stop_scrub",
    "continue_playing",
    "control_looper",
    "copy_drum_pad",
    "create_arrangement_audio_clip",
    "create_arrangement_midi_clip",
    "create_audio_track",
    "create_clip",
    "create_clip_automation",
    "create_midi_track",
    "create_midi_track_with_simpler",
    "create_return_track",
    "create_scene",
    "create_step_automation",
    "create_take_lane",
    "create_track_automation",
    "crop_clip",
    "delete_arrangement_clip",
    "delete_chain_device",
    "delete_clip",
    "delete_device",
    "delete_return_track",
    "delete_scene",
    "delete_time",
    "delete_track",
    "deselect_all_notes",
    "disarm_track",
    "duplicate_clip",
    "duplicate_clip_loop",
    "duplicate_clip_region",
    "duplicate_clip_slot",
    "duplicate_clip_to_arrangement",
    "duplicate_scene",
    "duplicate_time",
    "duplicate_track",
    "end_undo_step",
    "fire_clip",
    "fire_scene",
    "fire_scene_as_selected",
    "freeze_track",
    "group_tracks",
    "insert_chain",
    "insert_device",
    "insert_silence",
    "jump_in_running_session_clip",
    "jump_to_cue",
    "load_browser_item",
    "load_device_preset",
    "load_instrument_or_effect",
    "load_sample",
    "manage_sample_slices",
    "move_arrangement_clip",
    "move_clip_playing_pos",
    "move_device",
    "move_warp_marker",
    "navigate_playback",
    "nudge_tempo",
    "preview_browser_item",
    "quantize_clip_notes",
    "rack_variation_action",
    "re_enable_automation",
    "redo",
    "remove_notes_range",
    "remove_warp_marker",
    "reverse_clip",
    "select_all_notes",
    "select_device",
    "select_instrument",
    "select_scene",
    "select_track",
    "set_arrangement_clip_properties",
    "set_arrangement_overdub",
    "set_chain_properties",
    "set_chain_selector",
    "set_clip_color",
    "set_clip_follow_actions",
    "set_clip_grid",
    "set_clip_launch_mode",
    "set_clip_launch_quantization",
    "set_clip_legato",
    "set_clip_loop_points",
    "set_clip_looping",
    "set_clip_name",
    "set_clip_pitch",
    "set_clip_properties",
    "set_clip_slot_properties",
    "set_clip_start_end",
    "set_clip_start_time",
    "set_clip_warp",
    "set_compressor_sidechain",
    "set_crossfade_assign",
    "set_crossfader",
    "set_cue_volume",
    "set_detail_clip",
    "set_device_enabled",
    "set_device_parameter",
    "set_device_parameters_batch",
    "set_draw_mode",
    "set_drum_pad",
    "set_eq8_properties",
    "set_fire_button_state",
    "set_follow_song",
    "set_groove_settings",
    "set_hybrid_reverb_ir",
    "set_implicit_arm",
    "set_link_enabled",
    "set_loop_end",
    "set_loop_length",
    "set_loop_start",
    "set_macro_value",
    "set_master_volume",
    "set_metronome",
    "set_or_delete_cue",
    "set_panning_mode",
    "set_playback_position",
    "set_punch",
    "set_return_track_mute",
    "set_return_track_pan",
    "set_return_track_solo",
    "set_return_track_volume",
    "set_scene_color",
    "set_scene_follow_actions",
    "set_scene_name",
    "set_scene_tempo",
    "set_session_record",
    "set_sidechain_by_name",
    "set_simpler_properties",
    "set_song_data",
    "set_song_loop",
    "set_song_scale",
    "set_song_settings",
    "set_song_time",
    "set_split_stereo_pan",
    "set_tempo",
    "set_track_arm",
    "set_track_collapse",
    "set_track_color",
    "set_track_data",
    "set_track_delay",
    "set_track_fold",
    "set_track_monitoring",
    "set_track_mute",
    "set_track_name",
    "set_track_pan",
    "set_track_routing",
    "set_track_send",
    "set_track_solo",
    "set_track_volume",
    "set_transmute_properties",
    "set_view",
    "set_warp_mode",
    "simpler_sample_action",
    "sliced_simpler_to_drum_rack",
    "start_arrangement_recording",
    "start_playback",
    "stop_all_clips",
    "stop_arrangement_recording",
    "stop_clip",
    "stop_playback",
    "stop_track_clips",
    "tap_tempo",
    "transpose_clip_notes",
    "trigger_session_record",
    "undo",
    "unfreeze_track",
    "zoom_scroll_view",
})

READONLY_COMMANDS: frozenset[str] = frozenset({
    "analyze_audio_clip",
    "clip_beat_to_sample_time",
    "clip_sample_to_beat_time",
    "get_all_scales",
    "get_all_tracks_info",
    "get_appointed_device",
    "get_arrangement_clip_info",
    "get_arrangement_clips",
    "get_audio_clip_info",
    "get_beat_time",
    "get_browser_item",
    "get_browser_items_at_path",
    "get_browser_tree",
    "get_chain_selector",
    "get_clip_automation",
    "get_clip_automation_hires",
    "get_clip_automation_value",
    "get_clip_follow_actions",
    "get_clip_info",
    "get_clip_notes",
    "get_clip_properties",
    "get_clip_slot_properties",
    "get_compressor_sidechain",
    "get_count_in_duration",
    "get_crossfader",
    "get_cue_points",
    "get_device_info",
    "get_device_parameters",
    "get_device_presets",
    "get_drum_pads",
    "get_eq8_properties",
    "get_groove_pool",
    "get_highlighted_clip_slot",
    "get_hybrid_reverb_ir",
    "get_link_status",
    "get_loop_info",
    "get_macro_values",
    "get_master_track_info",
    "get_notes_extended",
    "get_playing_clips",
    "get_rack_variations",
    "get_recording_status",
    "get_return_track_info",
    "get_return_tracks",
    "get_return_tracks_info",
    "get_scene_follow_actions",
    "get_scenes",
    "get_selected_notes",
    "get_selected_parameter",
    "get_selection_state",
    "get_session_info",
    "get_simpler_properties",
    "get_smpte_time",
    "get_song_data",
    "get_song_file_path",
    "get_song_length",
    "get_song_scale",
    "get_song_settings",
    "get_song_transport",
    "get_take_lanes",
    "get_track_data",
    "get_track_delay",
    "get_track_info",
    "get_track_input_meters",
    "get_track_meters",
    "get_track_routing",
    "get_transmute_properties",
    "get_tuning_system",
    "get_user_folders",
    "get_user_library",
    "get_view_state",
    "get_warp_markers",
    "list_clip_automated_params",
    "search_browser",
})
