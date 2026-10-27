from llm_sdk import Small_LLM_Model
from numpy import inf
from typing import Any

from .helper import prompt_maker, is_number


def param_chooser(
    prompt: str,
    functions: list[dict[str, Any]],
    func_name: str,
    llm: Small_LLM_Model,
    voc: dict[int, str],
) -> dict[str, Any]:
    """Use constrained decoding to extract the arguments for a function call.

    Args:
        prompt: The natural-language user prompt.
        functions: List of available function definitions.
        func_name: The name of the function whose arguments must be filled.
        llm: The LLM SDK instance.
        voc: Vocabulary mapping token IDs to token strings.

    Returns:
        A dictionary mapping each parameter name to its extracted value.
    """
    call = prompt_maker(functions, prompt) + func_name + '\n'
    stopper: dict[str, list[str]] = {
        'string': ['Ċ', '"', '"ĊĊ', "\\", ' \"ĊĊ'],
        'integer': [",", "}", "?", " "],
        'number': [",", "}", "?", " "]
    }
    parameters: dict[str, Any] = {}
    for func in functions:
        if func['name'] == func_name:
            break
    for param_name, param_info in func['parameters'].items():
        answer: list[int] = []
        call += f"\n Argument '{param_name}' = "
        if param_info['type'] == "string":
            call += '"'
        tokens: list[int] = llm.encode(call)[0].tolist()
        odds: list[float] = llm.get_logits_from_input_ids(tokens)
        for i in range(len(odds)):
            if i not in voc:
                odds[i] = -inf
            elif voc[i] in stopper[param_info['type']]:
                continue
            elif (param_info['type'] != "string"
                  and not (is_number(voc[i], param_info['type']))):
                odds[i] = -inf
        best = odds.index(max(odds))
        count = 1
        while voc[best] not in stopper[param_info['type']] and count < 100:
            count += 1
            tokens.append(best)
            answer.append(best)
            call += voc[best]
            odds = llm.get_logits_from_input_ids(tokens)
            for i in range(len(odds)):
                if i not in voc:
                    odds[i] = -inf
                elif voc[i] in stopper[param_info['type']]:
                    continue
                elif (param_info['type'] != "string"
                      and not (is_number(llm.decode(answer)+voc[i],
                                         param_info['type']))):
                    odds[i] = -inf
            best = odds.index(max(odds))
            for stop in stopper[param_info['type']]:
                if stop in voc[best]:
                    break
        parameters[param_name] = llm.decode(answer)\
            if param_info['type'] == "string"\
            else float(llm.decode(answer))
    print(parameters)
    return parameters


def func_chooser(
    prompt: str,
    functions: list[dict[str, Any]],
    trie: dict[int, Any],
    llm: Small_LLM_Model,
) -> str:
    """Use constrained decoding to select the function name for a prompt.

    Args:
        prompt: The natural-language user prompt.
        functions: List of available functiondefinitions.
        trie: Trie of valid function-name token sequences.
        llm: The LLM SDK instance.

    Returns:
        The name of the selected function as a string.
    """
    call = prompt_maker(functions, prompt)
    choice: list[int] = []
    tokens: list[int] = llm.encode(call)[0].tolist()
    node: dict[int, Any] = trie
    count = 0
    while node and count <= 50:
        count += 1
        odds: list[float] = llm.get_logits_from_input_ids(tokens)
        for i in range(len(odds)):
            if i not in node:
                odds[i] = -inf
        best: int = odds.index(max(odds))
        choice.append(best)
        tokens.append(best)
        node = node[best]
    print(llm.decode(choice))
    return llm.decode(choice)
