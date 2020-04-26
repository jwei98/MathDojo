"""
Lambda functions for Math Dojo Alexa skill.
"""
# TODO: Figure out division.
# TODO: Add other miscellaneous like Help and Fallback intents.
# TODO: Don't ask same question multiple times.
import random
from typing import Dict, Tuple

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard

gametype_to_operator = {'ADDITION': '+',
                        'SUBTRACTION': '-',
                        'MULTIPLICATION': '*',
                        'DIVISION': '/'}

operator_to_string = {'+': 'plus',
                      '-': 'minus',
                      '/': 'divided by',
                      '*': 'times'}

sb = SkillBuilder()


@sb.request_handler(can_handle_func=is_request_type('LaunchRequest'))
def launch_request_handler(handler_input: HandlerInput) -> Response:
    """Handler for skill launch."""
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['gameStarted'] = False

    speech_text = ('Welcome to the Math Dojo! Would you like to practice '
                   'Addition, Subtraction, Multiplication, or Division?')
    reprompt = ('Would you like to practice '
                'Addition, Subtraction, '
                'Multiplication, or Division?')

    session_attr['lastReprompt'] = reprompt
    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=lambda input:
                    not is_currently_playing(input) and
                    is_intent_name('GameTypeIntent')(input))
def choose_game_type_handler(handler_input: HandlerInput) -> Response:
    """Handler for choosing which game type to play.

    Sets the 'operator' value in session attributes.
    """
    game_type = handler_input.request_envelope.request.intent.slots[
        'gameType'].value.upper()  # Uppercase for consistency across inputs.
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['gameType'] = game_type
    # Will never yield KeyError, as Alexa should automatically ensure that
    # slots will have a valid GameType (addition, subtraction, etc).
    session_attr['operator'] = gametype_to_operator[game_type]

    speech_text = f'Okay! Choose a number to practice your {game_type} with.'
    reprompt = ('Choose which number you\'d like to practice by saying a '
                'number like 3 or 7.')

    session_attr['lastReprompt'] = reprompt
    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=lambda input:
                    not is_currently_playing(input) and
                    is_intent_name('NumberResponseIntent')(input))
def table_number_intent_handler(handler_input: HandlerInput) -> Response:
    """Handles user specifying which number to practice."""
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['tableNumber'] = int(
        handler_input.request_envelope.request.intent.slots['number'].value
    )

    if session_attr['tableNumber'] < 1:
        speech_text = 'Try picking a number greater than 0'
        reprompt = ('Choose a number greater than 0.')
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response
    session_attr['gameStarted'] = True
    session_attr['score'] = 0
    session_attr['numQuestionsRemaining'] = 10
    session_attr['questionsAsked'] = []
    session_attr['lastQuestionAsked'] = new_question(session_attr)

    speech_text = ('Great! Let\'s begin. What is '
                   f'{stringify_equation(session_attr)}?')
    reprompt = f'What is {stringify_equation(session_attr)}?'

    session_attr['lastReprompt'] = reprompt
    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=lambda input:
                    is_currently_playing(input) and
                    is_intent_name('NumberResponseIntent')(input))
def answer_handler(handler_input: HandlerInput) -> Response:
    """Handler for processing answer to question asked."""
    session_attr = handler_input.attributes_manager.session_attributes
    correct_answer = eval(str(session_attr['lastQuestionAsked'][0])
                          + session_attr['operator']
                          + str(session_attr['lastQuestionAsked'][1]))

    guess_answer = int(handler_input.request_envelope.request.intent.slots[
        'number'].value)

    if guess_answer == correct_answer:
        speech_text = 'That\'s correct! '
        session_attr['score'] += 1
        session_attr['numQuestionsRemaining'] -= 1
    # Incorrect answer.
    else:
        speech_text = (
            f'That\'s incorrect. {stringify_equation(session_attr)} '
            f'is {correct_answer}. '
        )
        session_attr['numQuestionsRemaining'] -= 1

    # Game over.
    if session_attr['numQuestionsRemaining'] == 0:
        final_score = session_attr['score']
        speech_text += ('Congratulations! Your final score was '
                        f'{final_score} out of 10. ')
        new_game_prompt = ('If you would like to train again, just say '
                           'whether you\'d like to practice Addition, '
                           'Subtraction, Multiplication, or Division. '
                           'If you\'d like to quit, just say stop or cancel.')
        speech_text += new_game_prompt
        reprompt = new_game_prompt
        session_attr['gameStarted'] = False
    # Game continues...
    else:
        session_attr['lastQuestionAsked'] = new_question(session_attr)
        speech_text += (
            f'Next question: What is {stringify_equation(session_attr)}?')
        reprompt = ('Sorry, I didn\'t get that. What is '
                    f'{stringify_equation(session_attr)}?')

    session_attr['lastReprompt'] = reprompt
    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(
    can_handle_func=lambda input:
        is_intent_name('AMAZON.CancelIntent')(input) or
        is_intent_name('AMAZON.StopIntent')(input))
def cancel_and_stop_intent_handler(handler_input: HandlerInput) -> Response:
    """Single handler for Cancel and Stop Intent."""
    speech_text = 'Thanks for playing Math Dojo! Goodbye!'

    handler_input.response_builder.speak(
        speech_text).set_should_end_session(True)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type('SessionEndedRequest'))
def session_ended_request_handler(handler_input: HandlerInput) -> Response:
    """Handler for Session End."""
    # type: (HandlerInput) -> Response
    speech_text = 'Thanks for playing Math Dojo! Goodbye!'
    handler_input.response_builder.speak(
        speech_text).set_should_end_session(True)
    return handler_input.response_builder.response


"""Fallback Handlers"""


@sb.request_handler(can_handle_func=lambda input:
                    is_intent_name('AMAZON.FallbackIntent')(input) or
                    is_intent_name('AMAZON.YesIntent')(input) or
                    is_intent_name('AMAZON.NoIntent')(input))
def fallback_handler(handler_input: HandlerInput) -> Response:
    """ Fallback Handler deals with unexpected utterances"""
    # type: (HandlerInput) -> Response
    session_attr = handler_input.attributes_manager.session_attributes
    speech_text = ('Sorry, we couldn\'t understand that. '
                   f'{session_attr.get("lastReprompt")}')
    reprompt = speech_text
    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input: HandlerInput,
                          exception: Exception) -> Response:
    """Catch all exception handler,
    respond with custom message. Option to log Exception in the future.
    """
    # type: (HandlerInput, Exception) -> Response
    speech = 'Sorry, I didn\'t understand that. Please try again!'
    handler_input.response_builder.speak(speech).ask(speech)
    return handler_input.response_builder.response


"""Helper Functions."""


def is_currently_playing(handler_input: HandlerInput) -> bool:
    """Determines whether user is in the middle of a game."""
    session_attr = handler_input.attributes_manager.session_attributes
    return session_attr.get('gameStarted')


def stringify_equation(session_attr: Dict) -> str:
    """Constructs an arithmetic equation given session attributes."""
    return (f'{session_attr["lastQuestionAsked"][0]} '
            f'{operator_to_string[session_attr["operator"]]} '
            f'{session_attr["lastQuestionAsked"][1]}')


def new_question(session_attr: Dict) -> Tuple[int, int]:
    """Returns a new question based on the Game Type.

    Division is a special case.
    """
    num = random.randint(0, 15)
    while(num in session_attr['questionsAsked']):
        num = random.randint(0, 15)
    session_attr['questionsAsked'].append(num)
    if session_attr['operator'] == '/':
        return (num * session_attr['tableNumber'], session_attr['tableNumber'])
    return (session_attr['tableNumber'], num)


handler = sb.lambda_handler()
