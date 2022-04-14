from typing import Callable

from ._load_only import (
    right_click_setup,
    player_on_event,
    trigger_setup,
    timer_add,
    recipe_table,
    debug_track,
    debug_history,
    debug_cleanup
)
from ..tokenizer import Token, Tokenizer
from ..datapack import DataPack

LOAD_ONLY_COMMANDS: dict[str, Callable[
    [
        Token,
        DataPack,
        Tokenizer,
    ], str]] = {

    'Rightclick.setup': right_click_setup,
    'Player.onEvent': player_on_event,
    'Trigger.setUp': trigger_setup,
    'Timer.add': timer_add,
    'Recipe.table': recipe_table,
    'Debug.track': debug_track,
    'Debug.History': debug_history,
    'Debug.cleanup': debug_history
}
