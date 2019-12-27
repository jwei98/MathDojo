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
                   'Subtraction, Multiplication, or Division')
    reprompt = ('Would you like to practice Addition, Subtraction, '
                'Multiplication, or Division?')

    handler_input.response_builder.speak(speech_text).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=lambda input:
                    not currently_playing(input) and
                    is_intent_name('TableNumberIntent')(input))
def table_number_intent_handler(handler_input):
    """Handler for Yes Intent, only if the player said yes for
    a new game.
    """
    # type: (HandlerInput) -> Response
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['tableNumber'] = int(handler_input.request_envelope.request.intent.slots[
                                          'number'].value)
    session_attr['score'] = 0
    session_attr['numQuestionsRemaining'] = 10
    session_attr['lastQuestionAsked'] = (session_attr['tableNumber'],
                                         random.randint(0, session_attr['tableNumber']))
    session_attr['gameStarted'] = True;

    speech_text = ('Great! Let\'s begin. What is '
                   + session_attr['lastQuestionAsked'][0] + ' '
                   + session_attr['operator'] + ' '
                   + session_attr['lastQuestionAsked'][1] + '?'
                   )

    reprompt = ('What is the solution to '
                + session_attr['lastQuestionAsked'][0] + ' '
                + session_attr['operator'] + ' '
                + session_attr['lastQuestionAsked'][1] + '?'
                )
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


@sb.request_handler(can_handle_func=lambda input:
                    is_currently_playing(input) and
                    is_intent_name('NumberGuessIntent')(input))
def number_guess_handler(handler_input):
    """Handler for processing guess with target."""
    # type: (HandlerInput) -> Response
    session_attr = handler_input.attributes_manager.session_attributes
    target_num = eval(session_attr['lastQuestionAsked'][0]
                      + session_attr['operator']
                      + session_attr['lastQuestionAsked'][1]
                      )
    
    guess_num = int(handler_input.request_envelope.request.intent.slots[
        'number'].value)
    
    # check answer.
    if guess_num == target_num:
        speech_text = (
            f'That\'s correct!'
            )
        session_attr['score']++
        session_attr['numQuestionsRemaining']--
        lastQuestionAsked[1] = random.randint(0, session_attr['tableNumber'])
    else:
        speech_text = (
            f'That\'s incorrect. The answer was actually {target_num}'
            )
        session_attr['numQuestionsRemaining']--
        lastQuestionAsked[1] = random.randint(0, session_attr['tableNumber'])
    if session_attr['numQuestionsRemaining'] == 0:
        final_score = session_attr['score']
        speech_text = ('Congratulations. Your final score was '
                       f'{final_score} out of 10')
        reprompt = ('Would you like to play a new game? If so, '
                    'tell me if you want to practice Addition, Subtraction, '
                    'Multiplication, or Division')
        session_attr['gameStarted'] = false;
        session_attr['games_played'] += 1;
    else:
        speech_text += ('Here\'s the next question... What is '
                        + session_attr['lastQuestionAsked'][0] + ' '
                        + session_attr['operator'] + ' '
                        + session_attr['lastQuestionAsked'][1] + '?'
                        )
        reprompt = ('Sorry, I didn\'t get that. What is the solution to '
                    + session_attr['lastQuestionAsked'][0] + ' '
                    + session_attr['operator'] + ' '
                    + session_attr['lastQuestionAsked'][1] + '?'
                    )
    handler_input.response_builder.speak(speech_text).ask(reprompt)


@sb.request_handler(
    can_handle_func=lambda input:
        is_intent_name('AMAZON.CancelIntent')(input) or
        is_intent_name('AMAZON.StopIntent')(input))
def cancel_and_stop_intent_handler(handler_input: HandlerInput) -> Response:
    """Single handler for Cancel and Stop Intent."""
    speech_text = 'Thanks for playing Math Dojo!!'

    handler_input.response_builder.speak(
        speech_text).set_should_end_session(True)
    return handler_input.response_builder.response


"""Helper Functions."""


def is_currently_playing(handler_input: HandlerInput) -> bool:
    """Determines whether user is in the middle of a game."""
    session_attr = handler_input.attributes_manager.session_attributes
    return session_attr.get('gameStarted') == True


handler = sb.lambda_handler()
