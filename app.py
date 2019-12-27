"""
Lambda functions for Math Dojo Alexa skill.
"""
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard


sb = SkillBuilder()


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input: HandlerInput) -> Response:
    """Handler for skill launch.

    Also handles setting initial game state.
    """
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['gameStarted'] = False

    speech_text = ("Welcome to the Math Dojo! Would you like to play? "
                   "If so, specify whether you'd like to practice Addition, "
                   " Subtraction, Multiplication, or Division")
    reprompt = ("Would you like to practice Addition, Subtraction, "
                "Multiplication, or Division?")

    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


"""Helper Functions."""


def is_currently_playing(handler_input: HandlerInput) -> bool:
    """Determines whether user is in the middle of a game."""
    session_attr = handler_input.attributes_manager.session_attributes
    return session_attr.get('game_state') == 'STARTED'


handler = sb.lambda_handler()
