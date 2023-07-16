
## BOT in POO
from mtranslate import translate
import datefinder

# Using the function to translate spanish to english
def sp_to_en(sentence):
    return translate(sentence, "en")

# Extract a date in an english text
def extract_dates(text):
    matches = datefinder.find_dates(text)
    for match in matches:
        formatted_date = match.strftime("%d-%m-%Y")
        return formatted_date

class Bot:
    def __init__(self, user_ID, user_name, model):
        self.user_ID = user_ID
        self.user_name = user_name
        """
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
        
        # Try to clasify the first sms
        print(f'Buenos días {user_name}. Soy el BOT de la MUNI')

    """
    clasify the sms with the model
    """
    def clasify(self, text):
        # label = sel.model.classify(text)
        label = int(text)
        
        if label == 4:
            self.error_count += 1
            if self.error_count>=3:
                self.contact_call_center()
            else:
                print('No logro entender tu mensaje, intenta ser un poco mas claro. Gracias!')
        else:
            self.error_count = 0
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
            
            else:# self.state == 'Agendar':
                self.set_schedule()

        else:
            text_translated = sp_to_en(text)

            # Extraction of the date
            date = extract_dates(text_translated)

            print(f'Entiendo que quiere una hora para {date}')
            
            self.action_stage = 'Por confirmar hora'

    
    """
    contacto to the call center
    """
    def contact_call_center(self):
        self.state = 'Error'
        self.action_stage = 'Connecting Call Center'
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
            self.action_stage = 'User Confirmed'
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
            print(f'Por favor sea mas explicito con lo que desea realizar')

    def manage_hour(self):
        print('Buscando Disponibilidad de ese dia')
        

    """
    Connection to DDBB to confirm hour
    """
    def confirm_hour(self):
        print("Confirmando hora...")
        return
    
    """
    Connection to DDBB to cancel hour
    """
    def cancel_hour(self):
        print("Cancelando hora...")
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
    botcito = Bot("123","Nahuel",'model')

    input()

    botcito.action('4')

    input()

    botcito.action('4')

    input()

    botcito.action('4')


def test_select_label():
    botcito = Bot("123","Nahuel",'model')

    input()
    botcito.action('1')

    input()
    botcito.action('yes')

def test_select_date():
    botcito = Bot("123","Nahuel",'model')

    input()
    botcito.action('2')

    input()
    botcito.action('yes')

    input()
    botcito.action('Me gustaría el lunes 17')


def final():
    botcito = Bot("123","Nahuel",'model')
    
    while botcito.action_stage != 'Connecting Call Center':
        x = input('Val: ')
        botcito.action(x)
        

final()