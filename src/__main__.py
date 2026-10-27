import json
import os
from llm_sdk import Small_LLM_Model

from .parser import parsing
from .helper import voc_getter, reader, trie_maker
from .chooser import func_chooser, param_chooser

if __name__ == "__main__":
    try:
        parser = parsing()
        llm = Small_LLM_Model()
        voc = voc_getter(llm)
        prompts = reader(parser['input'])
        functions = reader(parser['functions_definition'])
        trie = trie_maker(functions, llm)
        choosen_func = [func_chooser(prompts[i]['prompt'],
                                     functions,
                                     trie, llm)
                        for i in range(len(prompts))]

        choosen_param = []
        for i in range(len(prompts)):
            choosen_param.append(param_chooser(prompts[i]['prompt'],
                                               functions, choosen_func[i],
                                               llm,
                                               voc))

        with open(parser['output'], 'w') as f:
            result = []
            for i in range(len(prompts)):
                answer = {
                    "prompt": prompts[i]['prompt'],
                    "name": choosen_func[i],
                    "parameters": choosen_param[i]
                }
                result.append(answer)
            json.dump(result, f, indent=2)
    except KeyboardInterrupt:
        os.system('clear')
    except Exception as e:
        if e.args != ():
            print(e)
    finally:
        print("Program stopped")
