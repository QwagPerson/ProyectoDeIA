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

        await send_text_msg(self.user_ID, f'Buenos días {user_name}. Soy el BOT de la MUNI')

    """
    clasify the sms with the model
    """

    async def clasify(self, text):
        label = await classifier_handler.predict(text)

        if label == 4:
            self.error_count += 1

            if self.error_count >= 3:
                self.contact_call_center()

            else:
                print('No logro entender tu mensaje, intenta ser un poco mas claro. Gracias!')

        else:
            self.state = label
            self.manage_states()

    def ask_hour(self, text):

        if self.action_stage == 'User Denied':
            print('No entiendo el mensaje')
            self.error_count += 1

            if self.error_count >= 3:
                self.contact_call_center()

            elif self.state == 'Reagendar':
                self.set_reschedule()

            else:  # self.state == 'Agendar':
                self.set_schedule()

        else:
            text_translated = sp_to_en(text)

            # Extraction of the date
            date = extract_dates(text_translated)
            date_name = transform_date_string(date)

            print(f'Entiendo que quiere una hora para {date_name}')

            self.action_stage = 'Por confirmar hora'

    """
    contacto to the call center
    """

    def contact_call_center(self):
        self.state = 'Error'
        self.action_stage = 'end'
        print('No pude entender tu mensaje')
        print("Contactando con Call Center...")

    """
    Manage states
    """

    def manage_states(self):
        if self.state == 0:
            print('Veo que quieres confirmar asistencia.')
            self.state = 'Asistencia'

        elif self.state == 1:
            print('Veo que quieres cancelar')
            self.state = 'Cancelar'

        elif self.state == 2:
            print('Veo que quieres reagendar la hora')
            self.state = 'Reagendar'

        elif self.state == 3:
            print('Veo que quieres agendar la hora')
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
                self.confirm_hour()

        elif self.action_stage == 'Por confirmar' and self.state == 'Cancelar':
            if self.user_confirmation(text):
                self.cancel_hour()

        elif self.action_stage == 'Por confirmar' and self.state == 'Reagendar':
            if self.user_confirmation(text):
                self.set_reschedule()

        elif self.action_stage == 'Por confirmar' and self.state == 'Agendar':
            if self.user_confirmation(text):
                self.set_schedule()

        elif self.action_stage == 'Buscar hora':
            self.ask_hour(text)

        elif self.action_stage == 'Por confirmar hora':
            if self.user_confirmation(text):
                self.manage_hour()

            else:
                self.ask_hour(text)

        # User Denied the clasification
        if self.action_stage == 'User Denied':
            self.state = -1
            self.action_stage = 'init'
            self.error_count += 1

            if self.error_count >= 3:
                self.contact_call_center()
            else:
                print(f'Por favor sea mas explicito con lo que desea realizar')

    def manage_hour(self):
        print('Buscando Disponibilidad de ese dia')
        self.action_stage = 'end'

    """
    Connection to DDBB to confirm hour
    """

    def confirm_hour(self):
        print("Confirmando hora...")
        self.action_stage = 'end'
        return

    """
    Connection to DDBB to cancel hour
    """

    def cancel_hour(self):
        print("Cancelando hora...")
        self.action_stage = 'end'
        return

    """
    reschedule an hour
    """

    def set_reschedule(self):
        '''
        Obtenemos la hora del usuario
        '''
        print('Usted tiene una hora agendada para el día DD-MM-YYYY')

        print('Indique la nueva fecha')

        self.action_stage = 'Buscar hora'

    """
    schedule an hour
    """

    def set_schedule(self):
        print('Indique una fecha para ver disponibilidad')

        self.action_stage = 'Buscar hora'


