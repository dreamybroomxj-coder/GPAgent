https://deepwiki.com/openai/whisper/2.4-api-reference

def transcribe(
    model: "Whisper",
    audio: Union[str, np.ndarray, torch.Tensor],
    *,
    verbose: Optional[bool] = None,
    temperature: Union[float, Tuple[float, ...]] = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
    compression_ratio_threshold: Optional[float] = 2.4,
    logprob_threshold: Optional[float] = -1.0,
    no_speech_threshold: Optional[float] = 0.6,
    condition_on_previous_text: bool = True,
    initial_prompt: Optional[str] = None,
    carry_initial_prompt: bool = False,
    word_timestamps: bool = False,
    prepend_punctuations: str = "\"'"¿([{-",
    append_punctuations: str = "\"'.。,，!！?？:：")]}、",
    clip_timestamps: Union[str, List[float]] = "0",
    hallucination_silence_threshold: Optional[float] = None,
    **decode_options,
) -> dict
Core Parameters:

model: Whisper model instance 
whisper/transcribe.py
62-63
audio: Audio file path, numpy array, or torch tensor 
whisper/transcribe.py
65-66
verbose: Controls progress display (True, False, or None) 
whisper/transcribe.py
68-70
temperature: Sampling temperature(s) for fallback strategy 
whisper/transcribe.py
72-74
word_timestamps: Extract word-level timing information using cross-attention patterns 
whisper/transcribe.py
91-93
Quality Control:

compression_ratio_threshold: Detect repetitive output (default: 2.4) 
whisper/transcribe.py
76-77
logprob_threshold: Detect low-confidence output (default: -1.0) 
whisper/transcribe.py
79-80
no_speech_threshold: Detect silent segments (default: 0.6) 
whisper/transcribe.py
82-85
hallucination_silence_threshold: Skip silent periods in word timestamps 
whisper/transcribe.py
118-120
Text Processing:

condition_on_previous_text: Use previous output as context 
whisper/transcribe.py
86-89
initial_prompt: Custom vocabulary or context prompt 
whisper/transcribe.py
101-104
carry_initial_prompt: Prepend initial prompt to each segment 
whisper/transcribe.py
106-110
Segmentation:

clip_timestamps: Process specific time ranges 
whisper/transcribe.py
114-116
Returns: Dictionary containing "text", "segments", and detected "language" 
whisper/transcribe.py
122-126

Sources: 
whisper/transcribe.py
38-126