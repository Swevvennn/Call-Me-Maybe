*This project has been created as part of the 42 curriculum by __mosmond__*.

# CALL ME MAYBE 

## Description

This project implements a function calling tool that translates natural language prompts into structured function calls using a small LLM (Qwen/Qwen3-0.6B). Given a prompt like *"What is the sum of 2 and 3?"*, the program outputs the matching function name and its typed arguments as valid JSON — without relying on the model to spontaneously produce structured output.

The key challenge is achieving 100% valid JSON output from a small, unreliable model. This is solved through **constrained decoding**: guiding the model token-by-token so that only valid tokens can be selected at each generation step.

## Instructions

### Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- The `llm_sdk/` directory must be present at the project root (copy it manually)
- The `data/input` directory must be present at the project root (copy it manually)

### Installation & execution

```bash
# Install dependencies & run programm
make install

# Run with default paths (data/input/ → data/output/)
make run

# Lint
make lint

# Clean
make clean
```

To run the program with custom files, edit directly `script_CMM.sh` at line 82 with:

``` bash
# Command that run correctly the programm following the setup made for the campus desktop
uv --cache-dir "$CMM_LOCATION/$CACHE_DIR" --project llm_sdk run --active python3 -m src

# File that contains all the possible function usable for Qwen
--functions_definition [<file/path/file_name.json>]

# File that contains all the prompts asked to Qwen
--input [<file/path/file_name.json>]

# File that will contain the result of the execution
--output [<file/path/file_name.json>]
```

**All flags are optional** and everything has to be **on a single line**.

### Input / Output (For default config)

**Input files** (in `data/input/`):
- `functions_definition.json` — list of available functions with name, description, parameters and return type
- `function_calling_tests.json` — list of natural language prompts

**Output file** (in `data/output/`):
- `function_calling_results.json` — array of objects with `prompt`, `name`, and `parameters`

## Algorithm explanation

The generation pipeline works in two constrained decoding phases:

**1. Function selection — trie-based decoding**

All function names are pre-encoded into token IDs and stored in a trie. At each generation step, the model produces logits over the entire vocabulary. Any token not present in the current trie node is masked to `-inf`, so the model can only generate tokens that continue a valid function name. This guarantees 100% valid function name selection.

**2. Argument extraction — type-constrained decoding**

For each parameter, the model generates tokens one by one. At each step, tokens are masked based on the expected type:
- `string`: any token is allowed until a stop character (`"`, newline, etc.) is reached
- `number` / `integer`: only tokens that form a valid numeric prefix are allowed; the running decoded string is checked at each step

## Design decisions

- **Trie** for function name decoding — compact, exact, and naturally constrains the token space to valid completions only
- **Vocabulary dictionary** (`id → token string`) built once from `get_path_to_vocabulary_json()` and reused across all parameter extractions
- **`json.dump()`** for output — the constrained decoding produces validated Python values; serialization is handled by standard Python, not the LLM

## Performance analysis

- **JSON validity**: 100% — every output is structurally valid by construction
- **Function selection accuracy**: near-perfect for unambiguous prompts; the trie ensures the output is always a real function name
- **Argument accuracy**: depends on model quality; numeric extraction is reliable due to prefix validation; string extraction relies on the model's understanding of the prompt
- **Speed**: limited by the number of LLM forward passes (one per token generated); all prompts should be processed in under 5 minutes on standard hardware

## Challenges faced

- **Logits are tensors**: `.get_logits_from_input_ids()` returns a tensor; `.tolist()` is required before using Python list operations like `.index(max(...))`
- **Token granularity for numbers**: a number like `265` may be tokenized as a single token or as `2`, `6`, `5` — the `is_number()` helper validates both the current token and the growing decoded string
- **Stop token detection**: stop characters for strings (e.g. `"`, `Ċ`) must be identified from the vocabulary, not hardcoded by token ID, since the same character can map to different IDs
- **Error management**: full parsing for a protection again custom files errors and sending back a message for the user

## Testing strategy

- Tested with the provided example prompts (`fn_add_numbers`, `fn_greet`, `fn_reverse_string`)
- Verified output JSON is parseable and schema-compliant after each run
- Tested edge cases: large numbers, multi-word strings, ambiguous phrasing
- Validated that function names in output always exactly match a definition from `functions_definition.json`
- Verified graceful error handling for missing files, bad JSON, and invalid flags

## Example usage

```bash
# For the 1st execution
make install

# For the next executions
make run
```

## Resources

- [Qwen3 model — HuggingFace](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Constrained decoding — Outlines library concepts](https://outlines-dev.github.io/outlines/)
- [BPE tokenization — OpenAI blog](https://openai.com/research/language-unsupervised)
- [Python `json` module](https://docs.python.org/3/library/json.html)

**AI usage**: Claude (Anthropic) was used to help refactor the code to meet the project's style requirements (type hints, docstrings) and to generate this README.

All logic, algorithmic choices, and constrained decoding implementation were made by hand and without help of generative AI.
