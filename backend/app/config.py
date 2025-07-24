from typing_extensions import NotRequired, TypedDict


class GenerationParams(TypedDict):
    max_tokens: int
    top_k: NotRequired[int]
    top_p: float
    temperature: float
    stop_sequences: list[str]
    reasoning_params: NotRequired[dict[str, int]]


class EmbeddingConfig(TypedDict):
    model_id: str
    chunk_size: int
    chunk_overlap: int
    enable_partition_pdf: bool


# Configure generation parameter for Claude chat response.
# Adjust the values according to your application.
# See: https://docs.anthropic.com/claude/reference/complete_post
DEFAULT_GENERATION_CONFIG: GenerationParams = {
    # Minimum (Haiku) is 4096
    # Ref: https://docs.anthropic.com/en/docs/about-claude/models/all-models#model-comparison
    "max_tokens": 4096,
    "top_k": 250,
    "top_p": 0.999,
    "temperature": 1.0,
    "stop_sequences": ["Human: ", "Assistant: "],
    # Budget tokens must NOT exceeds max_tokens
    "reasoning_params": {"budget_tokens": 1024},
}

# Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-mistral.html#model-parameters-mistral-request-response
DEFAULT_MISTRAL_GENERATION_CONFIG: GenerationParams = {
    "max_tokens": 4096,
    "top_k": 250,
    "top_p": 0.9,
    "temperature": 0.5,
    "stop_sequences": ["[INST]", "[/INST]"],
}

# Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-deepseek.html
DEFAULT_DEEP_SEEK_GENERATION_CONFIG: GenerationParams = {
    "max_tokens": 4096,
    "top_p": 0.9,
    "temperature": 1.0,
    "stop_sequences": [],
}

# Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-meta.html
DEFAULT_LLAMA_GENERATION_CONFIG: GenerationParams = {
    "max_tokens": 2048,
    "top_p": 0.9,
    "temperature": 0.7,
    "stop_sequences": [],
}


# Used for price estimation.
# NOTE: The following is based on 2024-03-07
# See: https://aws.amazon.com/bedrock/pricing/
BEDROCK_PRICING = {
    "us-east-1": {
        "claude-v4-opus": {"input": 0.015, "output": 0.075},
        "claude-v4-sonnet": {"input": 0.003, "output": 0.015},
        "claude-v3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-v3.5-haiku": {"input": 0.001, "output": 0.005},
        "claude-v3.5-sonnet": {"input": 0.00300, "output": 0.01500},
        "claude-v3.5-sonnet-v2": {"input": 0.00300, "output": 0.01500},
        "claude-v3.7-sonnet": {"input": 0.00300, "output": 0.01500},
        "mistral-7b-instruct": {"input": 0.00015, "output": 0.0002},
        "mixtral-8x7b-instruct": {"input": 0.00045, "output": 0.0007},
        "mistral-large": {"input": 0.004, "output": 0.012},
        "amazon-nova-pro": {"input": 0.0008, "output": 0.0032},
        "amazon-nova-lite": {"input": 0.00006, "output": 0.00024},
        "amazon-nova-micro": {"input": 0.000035, "output": 0.00014},
        "deepseek-r1": {"input": 0.00135, "output": 0.0054},
        # Meta Llama 3 models (US region)
        "llama3-3-70b-instruct": {"input": 0.00072, "output": 0.00072},
        "llama3-2-1b-instruct": {"input": 0.0001, "output": 0.0001},
        "llama3-2-3b-instruct": {"input": 0.00015, "output": 0.00015},
        "llama3-2-11b-instruct": {"input": 0.00016, "output": 0.00016},
        "llama3-2-90b-instruct": {"input": 0.00072, "output": 0.00072},
    },
    "us-west-2": {
        "claude-v4-opus": {"input": 0.015, "output": 0.075},
        "claude-v4-sonnet": {"input": 0.003, "output": 0.015},
        "claude-v3.7-sonnet": {"input": 0.00300, "output": 0.01500},
        "claude-v3-opus": {"input": 0.01500, "output": 0.07500},
        "mistral-7b-instruct": {"input": 0.00015, "output": 0.0002},
        "mixtral-8x7b-instruct": {"input": 0.00045, "output": 0.0007},
        "mistral-large": {"input": 0.004, "output": 0.012},
        "mistral-large-2": {"input": 0.002, "output": 0.06},
        "amazon-nova-pro": {"input": 0.0008, "output": 0.0032},
        "amazon-nova-lite": {"input": 0.00006, "output": 0.00024},
        "amazon-nova-micro": {"input": 0.000035, "output": 0.00014},
        "deepseek-r1": {"input": 0.00135, "output": 0.0054},
        # Meta Llama 3 models (US region)
        "llama3-3-70b-instruct": {"input": 0.00072, "output": 0.00072},
        "llama3-2-1b-instruct": {"input": 0.0001, "output": 0.0001},
        "llama3-2-3b-instruct": {"input": 0.00015, "output": 0.00015},
        "llama3-2-11b-instruct": {"input": 0.00016, "output": 0.00016},
        "llama3-2-90b-instruct": {"input": 0.00072, "output": 0.00072},
    },
    "ap-northeast-1": {},
    "default": {
        "claude-v4-opus": {"input": 0.015, "output": 0.075},
        "claude-v4-sonnet": {"input": 0.003, "output": 0.015},
        "claude-v3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-v3.5-haiku": {"input": 0.001, "output": 0.005},
        "claude-v3.5-sonnet": {"input": 0.00300, "output": 0.01500},
        "claude-v3.5-sonnet-v2": {"input": 0.00300, "output": 0.01500},
        "claude-v3.7-sonnet": {"input": 0.00300, "output": 0.01500},
        "claude-v3-opus": {"input": 0.01500, "output": 0.07500},
        "mistral-7b-instruct": {"input": 0.00015, "output": 0.0002},
        "mixtral-8x7b-instruct": {"input": 0.00045, "output": 0.0007},
        "mistral-large": {"input": 0.004, "output": 0.012},
        "mistral-large-2": {"input": 0.002, "output": 0.06},
        "amazon-nova-pro": {"input": 0.0008, "output": 0.0032},
        "amazon-nova-lite": {"input": 0.00006, "output": 0.00024},
        "amazon-nova-micro": {"input": 0.000035, "output": 0.00014},
        "deepseek-r1": {"input": 0.00135, "output": 0.0054},
        # Meta Llama 3 models (US region)
        "llama3-3-70b-instruct": {"input": 0.00072, "output": 0.00072},
        "llama3-2-1b-instruct": {"input": 0.0001, "output": 0.0001},
        "llama3-2-3b-instruct": {"input": 0.00015, "output": 0.00015},
        "llama3-2-11b-instruct": {"input": 0.00016, "output": 0.00016},
        "llama3-2-90b-instruct": {"input": 0.00072, "output": 0.00072},
    },
    # EU regions (eu-central-1, eu-west-1, eu-west-3)
    "eu-central-1": {
        "llama3-2-1b-instruct": {"input": 0.00013, "output": 0.00013},
        "llama3-2-3b-instruct": {"input": 0.00019, "output": 0.00019},
    },
    "eu-west-1": {
        "llama3-2-1b-instruct": {"input": 0.00013, "output": 0.00013},
        "llama3-2-3b-instruct": {"input": 0.00019, "output": 0.00019},
    },
    "eu-west-3": {
        "llama3-2-1b-instruct": {"input": 0.00013, "output": 0.00013},
        "llama3-2-3b-instruct": {"input": 0.00019, "output": 0.00019},
    },
}
