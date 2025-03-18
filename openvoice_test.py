import torch
from openvoice import se_extractor
from openvoice.api import BaseSpeakerTTS, ToneColorConverter

# Paths to checkpoints (adjust based on your downloaded files)
base_speaker_checkpoint = "checkpoints_v2/base_speakers/EN/checkpoint.pth"
converter_checkpoint = "checkpoints_v2/converter/checkpoint.pth"
config_path = "checkpoints_v2/converter/config.json"

# Device setup (use GPU if available, else CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load models
tts = BaseSpeakerTTS(
    "checkpoints_v2/base_speakers/EN/config.json", device=device)
tts.load_ckpt(base_speaker_checkpoint)

converter = ToneColorConverter(config_path, device=device)
converter.load_ckpt(converter_checkpoint)

# Input parameters
# Short audio of the voice to clone (e.g., 5-10s)
reference_audio = "path/to/your/reference_audio.wav"
output_path = "output_cloned_voice.wav"
text_to_speak = "Hello, this is a test of voice cloning with OpenVoice!"  # Text to generate

# Step 1: Extract source speaker embedding (default English speaker)
source_se = torch.load(
    "checkpoints_v2/base_speakers/EN/en_default_se.pth").to(device)

# Step 2: Extract target speaker embedding from reference audio
target_se, _ = se_extractor.get_se(
    reference_audio, converter, target_sample_rate=16000)

# Step 3: Generate base audio with the source speaker
tts.tts(text_to_speak, output_path, speaker="default", speed=1.0)

# Step 4: Convert the tone color to match the target voice
converter.convert(
    audio_src_path=output_path,
    src_se=source_se,
    tgt_se=target_se,
    output_path=output_path,
    message="Converting tone color..."
)

print(f"Voice cloned successfully! Output saved to {output_path}")
