"""
Lambda functions for Math Dojo Alexa skill.
"""
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard

gametype_to_operator = {'ADDITION': '+',
                        'SUBTRACTION': '-',
                        'MULTIPLICATION': '*',
                        'DIVISION': '/'}

sb = SkillBuilder()


@sb.request_handler(can_handle_func=is_request_type('LaunchRequest'))
def launch_request_handler(handler_input: HandlerInput) -> Response:
    """Handler for skill launch."""
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['gameStarted'] = False

    speech_text = ('Welcome to the Math Dojo! Would you like to play? '
                   'If so, specify whether you\'d like to practice Addition, '
                   ' Subtraction, Multiplication, or Division')
    reprompt = ('Would you like to practice Addition, Subtraction, '
                'Multiplication, or Division?')

    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=lambda input:
                    not currently_playing(input) and
                    is_intent_name('GameTypeIntent')(input))
def choose_game_type_handler(handler_input: HandlerInput) -> Response:
    """Handler for choosing which game type to play.

    Sets the 'operator' value in session attributes.
    """
    game_type = handler_input.request_envelope.request.intent.slots[
        'GameType'].value.upper()  # Uppercase for consistency across inputs.
    session_attr = handler_input.attributes_manager.session_attributes
    # Will never yield KeyError, as Alexa should automatically ensure that
    # slots will have a valid GameType (addition, subtraction, etc).
    session_attr['operator'] = gametype_to_operator[game_type]

    speech_text = (f'Okay! You are about to begin your {game_type} training, '
                   'but first, choose which number you\'d like to practice.')
    reprompt = ('Choose which number you\'d like to practice by saying a '
                'number like 3 or 7.')

    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


"""Helper Functions."""


def is_currently_playing(handler_input: HandlerInput) -> bool:
    """Determines whether user is in the middle of a game."""
    session_attr = handler_input.attributes_manager.session_attributes
    return session_attr.get('gameStarted') == True


handler = sb.lambda_handler()
