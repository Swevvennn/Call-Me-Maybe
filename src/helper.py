import json
from llm_sdk import Small_LLM_Model
from typing import Any


def prompt_maker(functions: list[dict[str, Any]], prompt: str) -> str:
    """Build the instruction string sent to the LLM.

    Args:
        functions: List of available function definitions.
        prompt: The natural-language user prompt.

    Returns:
        A formatted string listing available functions and asking which
        one should be called for the given prompt.
    """
    call: str = "You have access to the following functions:\n"
    for func in functions:
        call += f"{func['name']}: {func['description']}\n"
    call += f"\nWich function should be called for: \"{prompt}\" ?\n"
    return call


def reader(file: str) -> Any:
    """Read and parse a JSON file.

    Args:
        file: Path to the JSON file.

    Returns:
        Parsed JSON content.
    """
    with open(file, 'r') as f:
        return json.load(f)


def is_number(s: str, t: str) -> bool:
    """Check whether a string is a valid representation of a numeric type.

    Args:
        s: The string to check.
        t: The expected type, either ``"number"`` or ``"integer"``.

    Returns:
        ``True`` if ``s`` is a valid representation of ``t``, else ``False``.
    """
    if not s:
        return False
    i = 0
    if s[i] == '-':
        i += 1
    for i in range(i, len(s)):
        if s[i] == '.':
            if t == 'integer':
                return False
            else:
                break
        elif not (s[i].isdigit()):
            return False
    for i in range(i, len(s)):
        if not (s[i].isdigit()):
            return False
    return True


def voc_getter(llm: Small_LLM_Model) -> dict[int, str]:
    """Build a token-id → token-string vocabulary dictionary.

    Args:
        llm: The LLM SDK instance.

    Returns:
        A dictionary mapping every token ID to its string representation.
        Missing IDs are mapped to an empty string.
    """
    content: dict[str, int] = reader(llm.get_path_to_vocab_file())
    dico: dict[int, str] = {v: k for k, v in content.items()}
    for i in range(max(dico.keys()) + 1):
        if i not in dico:
            dico[i] = ''
    return dico


def trie_maker(
    functions: list[dict[str, Any]],
    llm: Small_LLM_Model,
) -> dict[int, Any]:
    """Build a trie from the function names encoded as token IDs.

    Args:
        functions: List of available function definitions.
        llm: The LLM SDK instance.

    Returns:
        A nested dictionary representing the trie of valid token sequences.
    """
    trie: dict[int, Any] = {}
    for func in functions:
        node = trie
        tensor: list[int] = llm.encode(func['name'])[0].tolist()
        for token in tensor:
            if token not in node:
                node[token] = {}
            node = node[token]
    return trie
