from enum import Enum

class WordCoder:
    class HOTKEY_PROGRAM(str, Enum):
        HOTKEY_RUN_1 = "HGR_1"
        HOTKEY_RUN_2 = "HGR_2"
        HOTKEY_RUN_3 = "HGR_3"


def WriteComandTags( tag, *command )->str:
    ## jeśli zostalu dodadane komendy to wpisywane zostaje do tagu
    cmds = "" if len(command)==0 else "*".join(
        map(str, [
            ( c.value if hasattr(c, 'value') else str(c) )
            for c in command
            ]
        )
    )
    return tag + "#" + cmds

commands = [ "aaa", "bbb", WordCoder.HOTKEY_PROGRAM.HOTKEY_RUN_1  ]

obj = next(c for c in commands if isinstance(c, WordCoder.HOTKEY_PROGRAM))

print(obj, type(obj))

program_name = str(obj)

print(program_name, type(program_name))

x = WriteComandTags("TAG", program_name )

print(x)