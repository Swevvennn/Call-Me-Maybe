import json
import os
from sys import argv

from .helper import reader


def parsing() -> dict[str, str]:
    """Parse command-line arguments and validate the provided files.

    Returns:
        A dictionary with keys ``functions_definition``, ``input``, and
        ``output`` pointing to the resolved file paths.

    Raises:
        Exception: On any file or validation error, with a descriptive message
            printed to stdout before raising.
    """
    res: dict[str, str] = {}
    default: dict[str, str] = {
        'functions_definition': "data/input/functions_definition.json",
        'input': "data/input/function_calling_tests.json",
        'output': "data/output/function_calling_results.json"
    }
    if len(argv) > 1:
        for i in range(len(argv)):
            try:
                if '--' not in argv[i]:
                    continue
                elif '--' in argv[i+1]:
                    raise IndexError

                if argv[i] in ['--functions_definition', '--input']:
                    data = reader(argv[i+1])
                    for line in data:
                        if argv[i] == '--input':
                            for key, val in line.items():
                                if not (key == 'prompt'
                                        and isinstance(val, str)):
                                    raise ValueError
                        elif argv[i] == '--functions_definition':
                            for key in ['name', 'description',
                                        'parameters', 'returns']:
                                if key not in line:
                                    raise ValueError
                            if not (isinstance(line['name'], str)
                                    and isinstance(line['description'], str)):
                                raise ValueError
                            if not (isinstance(line['parameters'], dict)
                                    and isinstance(line['returns'], dict)):
                                raise ValueError
                            for key, val in line['parameters'].items():
                                if not (isinstance(val, dict)
                                        and 'type' in val
                                        and val['type'] in ['string',
                                                            'number',
                                                            'integer']):
                                    raise ValueError
                            if (not isinstance(line['returns'], dict)
                                or 'type' not in line['returns']
                                or line['returns']['type'] not in ['string',
                                                                   'number',
                                                                   'integer']):
                                raise ValueError

                elif argv[i] == '--output':
                    try:
                        open(argv[i+1], 'w')
                    except FileNotFoundError:
                        os.mkdir('/'.join(argv[i+1].split('/')[:-1]))
                        open(argv[i+1], 'w')
                    if argv[i+1].split('/')[-1].split('.')[1] != 'json':
                        raise json.JSONDecodeError('', '', -1)

                else:
                    continue

                res[argv[i][2:]] = argv[i+1]

            except FileNotFoundError:
                os.system('clear')
                print("\nMake sure that all the files exist")
                raise Exception
            except PermissionError:
                os.system('clear')
                print("\nMake sure that you have access to all the files")
                raise Exception
            except IndexError:
                os.system('clear')
                print("\nMake sure that the flags are followed by files name")
                raise Exception
            except IsADirectoryError:
                os.system('clear')
                print("\nMake sure that you gave a FILE name\
 and not a DIR name")
                raise Exception
            except json.JSONDecodeError:
                os.system('clear')
                print("\nMake sure that you gave only json files")
                raise Exception
            except ValueError:
                os.system('clear')
                print("\nMake sure that you gave correct json files")
                raise Exception

    for key, val in default.items():
        if key not in res:
            res[key] = val

            try:
                if key != 'output':
                    data = reader(val)
                else:
                    open(val, 'w')

            except FileNotFoundError:
                os.system('clear')
                print("\nMake sure that the default files exist")
                raise Exception
            except PermissionError:
                os.system('clear')
                print("\nMake sure that you have access to the default files")
                raise Exception

    return res
