from datetime import datetime, timedelta
from collections import UserDict
import re

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (IndexError, ValueError) as e:
            return f"Error: {e}"
        except KeyError:
            return "Contact not found."
        except Exception as e:
            return f"Unexpected error: {e}"
    return wrapper
class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not self._is_valid_phone(value):
            raise ValueError("Потрібно мінімум 10 цифр")
        super().__init__(value)

    @staticmethod
    def _is_valid_phone(value):
        return re.fullmatch(r'\d{10}', value) is not None


class Birthday(Field):
    def __init__(self, value):
        self._value = None
        self.value = value 

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        try:
            self._value = datetime.strptime(new_value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    
    def change_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return True  # Номер змінено
        return False  #    

    def add_birthday(self, date_str):
        self.birthday = Birthday(date_str)

    def __str__(self):
        phones = ', '.join(p.value for p in self.phones)
        bday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"{self.name.value}: {phones} | Birthday: {bday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        end_date = today + timedelta(days=7)
        uncoming = []

        for record in self.data.values():
            if record.birthday:
                bday_this_year = record.birthday.value.replace(year=today.year).date()
                if today <= bday_this_year <= end_date:
                    congrats_date = bday_this_year
                    if congrats_date.weekday() >= 5:
                        congrats_date += timedelta(days=(7 - congrats_date.weekday()))
                    uncoming.append({
                        "name": record.name.value,
                        "birthday": congrats_date.strftime("%d.%m.%Y")
                    })
        return uncoming

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        return "Введіть ім'я та дату народження у форматі DD.MM.YYYY"

    name, birthday_str = args
    record = book.find(name)
    if not record:
        return f"Контакт з ім'ям '{name}' не знайдено"

    try:
        record.add_birthday(birthday_str)
    except ValueError as e:
        return str(e)

    return f"День народження для {name} додано."
@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
        msg = "Contact added."
    else:
        msg = "Contact updated."
    record.add_phone(phone)
    return msg

@input_error
def show_birthday(args, book):
    if len(args) != 1:
        return "Ведіть лише ім'я"

    name = args[0]
    record = book.find(name)
    if not record:
        return f"Контакт з ім'ям '{name}' не знайдено"
    if record.birthday:
        return f"День народження {name}: {record.birthday.value.strftime('%d.%m.%Y')}"
    else:
        return f"Для контакту '{name}' день народження не вказано."


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record and record.change_phone(old_phone, new_phone):
        return "Phone number updated."
    return "Old phone number not found."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "Немає днів народження протягом наступного тижня."

    result = "Найближчі дні народження:\n"
    for item in upcoming:
        result += f"{item['name']}: {item['birthday']}\n"
    return result.strip()
    
@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    return ', '.join(p.value for p in record.phones) if record else "Contact not found."

@input_error
def show_all(book):
    return '\n'.join(str(r) for r in book.values())
    
def parse_input(user_input):
        parts = user_input.strip().split()
        command = parts[0].lower()
        return command, parts[1:]
    



def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()

