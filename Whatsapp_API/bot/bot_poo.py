## BOT in POO
from mtranslate import translate
import datefinder
import datetime
import torch
from torch import nn


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


def make_pred(data, model, tokenizer, device):
    sf = nn.Softmax(dim=1)
    tokenizer_result = tokenizer(data)
    input_ids = torch.tensor(tokenizer_result["input_ids"]).to(device)
    attention_mask = torch.tensor(tokenizer_result["attention_mask"]).to(device)
    outputs = sf(model(input_ids, attention_mask).logits)
    return torch.argmax(outputs, dim=1)


class Bot:
    def __init__(self, user_ID, user_name, model, tokenizer, device):
        self.user_ID = user_ID
        self.user_name = user_name
        """
        -10:error
        -1 : init
        0 : asistir
        1 : cancelar
        2: reagendar
        3: agendar
        4: call center
        5: esperando_confirmacion
        """
        self.state = -1
        self.action_stage = 'init'
        self.error_count = 0

        self.model = model
        self.tokenizer = tokenizer
        self.device = device

        self.last_sms = ''

        # Try to clasify the first sms
        print(f'Buenos días {user_name}. Soy el BOT de la MUNI')

    """
    clasify the sms with the model
    """

    def clasify(self, text):
        label = make_pred([text], self.model, self.tokenizer, self.device)
        # label = int(text)
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
            [self.last_sms, self.state]

            self.action_stage = 'User Confirmed'
            self.error_count = 0
            return 1
        else:
            self.action_stage = 'User Denied'
            return 0

    """
    Method to control the actions    
    """

    def action(self, text):
        if self.action_stage == 'init':
            self.clasify(text)

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


def test_call():
    botcito = Bot("123", "Nahuel", 'model')

    input()

    botcito.action('4')

    input()

    botcito.action('4')

    input()

    botcito.action('4')


def test_select_label():
    botcito = Bot("123", "Nahuel", 'model')

    input()
    botcito.action('1')

    input()
    botcito.action('yes')


def test_select_date():
    botcito = Bot("123", "Nahuel", 'model')

    input()
    botcito.action('2')

    input()
    botcito.action('yes')

    input()
    botcito.action('Me gustaría el lunes 17')


def final():
    botcito = Bot("123", "Nahuel", 'model')

    while botcito.action_stage != 'end':
        x = input('Val: ')
        botcito.action(x)
