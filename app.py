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
    """Handler for skill launch."""
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['gameStarted'] = False

    speech_text = ("Welcome to the Math Dojo! Would you like to play? "
                   "If so, specify whether you'd like to practice Addition, "
                   " Subtraction, Multiplication, or Division")
    reprompt = ("Would you like to practice Addition, Subtraction, "
                "Multiplication, or Division?")

    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=lambda input:
                    not currently_playing(input) and
                    is_intent_name("TableNumberIntent")(input))
def table_number_intent_handler(handler_input):
    """Handler for Yes Intent, only if the player said yes for
    a new game.
    """
    # type: (HandlerInput) -> Response
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['tableNumber'] = int(handler_input.request_envelope.request.intent.slots[
                                          "number"].value)
    session_attr['score'] = 0
    session_attr['numQuestionsRemaining'] = 10
    session_attr['lastQuestionAsked'] = (session_attr['tableNumber'],
                                         random.randint(0, session_attr['tableNumber']))
    session_attr['gameStarted'] = True;

    speech_text = ("Great! Let's begin. What is "
                   + session_attr['lastQuestionAsked'][0] + ' '
                   + session_attr['operator'] + ' '
                   + session_attr['lastQuestionAsked'][1] + '?'
                   )

    reprompt = ("What is the solution to "
                + session_attr['lastQuestionAsked'][0] + ' '
                + session_attr['operator'] + ' '
                + session_attr['lastQuestionAsked'][1] + '?'
                )

    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


"""Helper Functions."""


def is_currently_playing(handler_input: HandlerInput) -> bool:
    """Determines whether user is in the middle of a game."""
    session_attr = handler_input.attributes_manager.session_attributes
    return session_attr.get('gameStarted') == True


handler = sb.lambda_handler()
