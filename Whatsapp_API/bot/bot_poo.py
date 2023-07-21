## BOT in POO
from mtranslate import translate
import datefinder
import datetime
from .model_connector.classifier_handler import ClassifierHandler
import os
import dotenv
from whatsapp_connector.message_controller import send_text_msg, send_interactive_msg

# load the environment variables
load_env = dotenv.load_dotenv(dotenv_path=f"../config_files/.env.dev")

classifier_handler = ClassifierHandler(
    model_url=os.environ.get('CLASSIFIER_APP_URL'),
    model_secret_key=os.environ.get('CLASSIFIER_APP_KEY')
)


# Using the function to translate spanish to english
def sp_to_en(sentence):
    return translate(sentence, "en")


# Extract a date in an english text
def extract_dates(text):
    matches = datefinder.find_dates(text)
    for match in matches:
        formatted_date = match.strftime("%d-%m-%Y")
        return formatted_date


def transform_date_string(date_string):
    # Parse the input string as a datetime object
    date = datetime.strptime(date_string, '%d-%m-%Y')

    # Format the output string as "DAY NAME dd-mm-yyyy"
    day_name = date.strftime('%A')

    # Days Dict
    day_dict = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }

    # Replace Name
    day_name = day_dict.get(day_name)

    date_ = date.strftime(f'{day_name} %d-%m-%Y')

    return date_


class Bot:
    def __init__(self, user_ID, user_name):
        self.user_ID = user_ID
        self.user_name = user_name
        """
        -10  : error
         -1  : init
          0  : asistir
          1  : cancelar
          2  : reagendar
          3  : agendar
          4  : call center
          5  : esperando_confirmacion
        """

        self.state = -1
        self.action_stage = 'init'
        self.error_count = 0

        self.last_sms = ''

    async def saluo(self):
        await send_text_msg(self.user_ID, f'Buenos días {self.user_name}. Soy el BOT de la MUNI')

    """
    clasify the sms with the model
    """

    async def clasify(self, text):
        label = await classifier_handler.predict(text)

        if label == 4:
            self.error_count += 1

            if self.error_count >= 3:
                await self.contact_call_center()

            else:
                await send_text_msg(self.user_ID,
                                    'No logro entender tu mensaje, intenta ser un poco mas claro. Gracias!')

        else:
            self.state = label
            await self.manage_states()

    async def ask_hour(self, text):

        if self.action_stage == 'User Denied':
            await send_text_msg(self.user_ID,
                                'No entiendo el mensaje')
            self.error_count += 1

            if self.error_count >= 3:
                await self.contact_call_center()

            elif self.state == 'Reagendar':
                await self.set_reschedule()

            else:  # self.state == 'Agendar':
                await self.set_schedule()

        else:
            text_translated = sp_to_en(text)

            # Extraction of the date
            date = extract_dates(text_translated)
            date_name = transform_date_string(date)
            await send_text_msg(self.user_ID,
                                f'Entiendo que quiere una hora para {date_name}')

            self.action_stage = 'Por confirmar hora'

    """
    contacto to the call center
    """

    async def contact_call_center(self):
        self.state = 'Error'
        self.action_stage = 'end'
        await send_text_msg(self.user_ID,
                            'No pude entender tu mensaje')
        await send_text_msg(self.user_ID,
                            'Contactando con Call Center...')

    """
    Manage states
    """

    async def manage_states(self):
        if self.state == 0:
            await send_text_msg(self.user_ID,
                                'Veo que quieres confirmar asistencia.')
            self.state = 'Asistencia'

        elif self.state == 1:
            await send_text_msg(self.user_ID,
                                'Veo que quieres cancelar')
            self.state = 'Cancelar'

        elif self.state == 2:
            await send_text_msg(self.user_ID,
                                'Veo que quieres reagendar la hora')
            self.state = 'Reagendar'

        elif self.state == 3:
            await send_text_msg(self.user_ID,
                                'Veo que quieres agendar la hora')
            self.state = 'Agendar'

        self.action_stage = 'Por confirmar'

    """
    user confirmation
    """

    def user_confirmation(self, text):
        if text == 'yes':
            # [self.last_sms, self.state]

            self.action_stage = 'User Confirmed'
            self.error_count = 0
            return 1
        else:
            self.action_stage = 'User Denied'
            return 0

    """
    Method to control the actions    
    """

    async def action(self, text):
        if self.action_stage == 'init':
            await self.clasify(text)

        elif self.action_stage == 'Por confirmar' and self.state == 'Asistencia':
            if self.user_confirmation(text):
                await self.confirm_hour()

        elif self.action_stage == 'Por confirmar' and self.state == 'Cancelar':
            if self.user_confirmation(text):
                await self.cancel_hour()

        elif self.action_stage == 'Por confirmar' and self.state == 'Reagendar':
            if self.user_confirmation(text):
                await self.set_reschedule()

        elif self.action_stage == 'Por confirmar' and self.state == 'Agendar':
            if self.user_confirmation(text):
                await self.set_schedule()

        elif self.action_stage == 'Buscar hora':
            await self.ask_hour(text)

        elif self.action_stage == 'Por confirmar hora':
            if self.user_confirmation(text):
                await self.manage_hour()

            else:
                await self.ask_hour(text)

        # User Denied the clasification
        if self.action_stage == 'User Denied':
            self.state = -1
            self.action_stage = 'init'
            self.error_count += 1

            if self.error_count >= 3:
                await self.contact_call_center()
            else:
                await send_text_msg(self.user_ID,
                                    f'Por favor sea mas explicito con lo que desea realizar')

    async def manage_hour(self):
        await send_text_msg(self.user_ID,
                            'Buscando Disponibilidad de ese dia')
        self.action_stage = 'end'

    """
    Connection to DDBB to confirm hour
    """
    async def confirm_hour(self):
        await send_text_msg(self.user_ID,
                            "Confirmando hora...")
        self.action_stage = 'end'

    """
    Connection to DDBB to cancel hour
    """
    async def cancel_hour(self):
        await send_text_msg(self.user_ID,
                            "Cancelando hora...")
        self.action_stage = 'end'

    """
    reschedule an hour
    """
    async def set_reschedule(self):
        '''
        Obtenemos la hora del usuario
        '''
        await send_text_msg(self.user_ID,
                            'Usted tiene una hora agendada para el día DD-MM-YYYY')

        await send_text_msg(self.user_ID,
                            'Indique la nueva fecha')

        self.action_stage = 'Buscar hora'

    """
    schedule an hour
    """

    async def set_schedule(self):
        await send_text_msg(self.user_ID,
                            'Indique una fecha para ver disponibilidad')

        self.action_stage = 'Buscar hora'
