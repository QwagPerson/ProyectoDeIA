## BOT in POO
from mtranslate import translate
import datefinder
import datetime
from model_connector.classifier_handler import ClassifierHandler
import os
import dotenv
from whatsapp_connector.message_controller import send_text_msg, send_interactive_msg

# load the environment variables
load_env = dotenv.load_dotenv(dotenv_path=f"../config_files/.env.dev")

classifier_handler = ClassifierHandler(
    model_url=os.environ.get('CLASSIFIER_APP_URL'),
    model_secret_key=os.environ.get('CLASSIFIER_APP_KEY')
)

dates = [datetime.date.today() + datetime.timedelta(days=i) for i in range(7)]
dates = [date.strftime("%d-%m-%Y") for date in dates]

# option1, option2 or option3
hours = ["10:00", "12:30", "14:00"]


# Create a dictionary with the dates and hours available
DB = {}
for date in dates:
    DB[date] = {}
    for hour in hours:
        DB[date][hour] = {
            "available": True,
            "ID": None,
            "confirmed": False
        }


# To testing, add keys
DB['24-07-2023']['10:00'] = {'available': False, 'ID': '966268841', 'confirmed': False}
DB['24-07-2023']['12:30'] = {'available': False, 'ID': '111111111', 'confirmed': True}
DB['24-07-2023']['14:00'] = {'available': False, 'ID': '999999999', 'confirmed': True}


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
    date = datetime.datetime.strptime(date_string, '%d-%m-%Y')

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
        self.last_day = ''
        self.hours = [None]

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
            #print(f'{text} -- {text_translated} -- {date}')
            date_name = transform_date_string(date)
            self.last_day = date
            await send_interactive_msg(
                self.user_ID,
                f'Entiendo que quiere una hora para {date_name}',
                [('yes', 'Si'), ('no', 'No')]
            )

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
            await send_interactive_msg(
                self.user_ID,
                '¿Quieres confirmar asistencia?',
                [('yes', 'Si'), ('no', 'No')]
            )
            self.state = 'Asistencia'

        elif self.state == 1:
            await send_interactive_msg(
                self.user_ID,
                '¿Quieres cancelar tu hora?',
                [('yes', 'Si'), ('no', 'No')]
            )
            self.state = 'Cancelar'

        elif self.state == 2:
            await send_interactive_msg(
                self.user_ID,
                '¿Quieres reagendar tu hora?',
                [('yes', 'Si'), ('no', 'No')]
            )
            self.state = 'Reagendar'

        elif self.state == 3:
            await send_interactive_msg(
                self.user_ID,
                '¿Quieres agendar una hora?',
                [('yes', 'Si'), ('no', 'No')]
            )
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

        elif self.action_stage == 'seleccionando hora':
            #print(f'text: {type(text)} -- {text}')
            if text == '0':
                self.action_stage = 'Buscar hora'
                await send_text_msg(self.user_ID,
                                    f'Por favor Indique el nuevo dia')
            else:
                await self.add_hour_user(int(text))

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

    async def add_hour_user(self, pos):
        """
        add the user with the last day-hoy saved
        """
        # Iterate over the BD and save the user with the 
        # day and hour selected

        DB[self.last_day][self.hours[pos]]['available'] = False
        DB[self.last_day][self.hours[pos]]['ID'] = self.user_ID

        await send_text_msg(self.user_ID,
                            f"Se ha reservado correctamente su hora para el día {self.last_day} a las {self.hours[pos]}")

        self.action_stage = 'init'



    async def manage_hour(self):
        await send_text_msg(self.user_ID,
                            'Buscando Disponibilidad de ese dia')

        try:
            day_hours = DB[self.last_day]
            opt = 1
            l_hours = []
            for an_hour in day_hours.keys():
                hour_info = day_hours[an_hour]
                                 
                print(f'{an_hour} -- {hour_info}')
                if hour_info['available'] == True:   
                    l_hours.append((opt,an_hour))
                    self.hours.append(an_hour)
                    opt+=1
        except:
            print('EASTEREGG JAJAJAJ')
        
        l_hours.append((0, 'Buscar Otra fecha'))
        await send_interactive_msg(
                self.user_ID,
                'A continuación se muestran las horas disponibles',
                l_hours
            )
        self.action_stage = 'seleccionando hora'

    """
    Connection to DDBB to confirm hour
    """

    async def confirm_hour(self):
        # loop through db searching for an hour with the same ID
        await send_text_msg(self.user_ID,
                            "Confirmando hora...")
        for day in DB.keys():
            day_hours = DB[day]
            for an_hour in day_hours.keys():
                hour_info = day_hours[an_hour]

                if hour_info['ID'] == self.user_ID:
                    hour_info['confirmed'] = True
                    await send_text_msg(self.user_ID,
                                        f"Hora confirmada exitosamente! para el día {day} a las {an_hour}")
                    self.action_stage = 'init'
                    return

        await send_text_msg(self.user_ID,
                            "No tienes horas reservadas")
        self.action_stage = 'init'

    """
    Connection to DDBB to cancel hour
    """

    async def cancel_hour(self):
        # loop through db searching for an hour with the same ID
        await send_text_msg(self.user_ID,
                            "Cancelando hora...")
        for day in DB.keys():
            day_hours = DB[day]
            for an_hour in day_hours.keys():
                hour_info = day_hours[an_hour]
                if hour_info["ID"] == self.user_ID:
                    hour_info['ID'] = None
                    hour_info['confirmed'] = False
                    hour_info['available'] = True
                    await send_text_msg(self.user_ID,
                                        "Hora cancelada exitosamente!")
                    self.action_stage = 'init'
                    return

    """
    reschedule an hour
    """

    async def set_reschedule(self):
        '''
        Obtenemos la hora del usuario
        '''
        await send_text_msg(self.user_ID,
                            'Consultando horas agendadas en la base de datos...')
        flag = False
        for day in DB.keys():
            if flag:
                break
            day_hours = DB[day]
            for an_hour in day_hours.keys():
                hour_info = hours[an_hour]
                if hour_info["ID"] == self.user_ID:
                    await send_text_msg(self.user_ID,
                                        f"Su hora agendada es: {hour_info['hour']} del día {day}")
                    flag = True
                    break
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
