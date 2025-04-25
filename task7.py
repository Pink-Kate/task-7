import re
from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


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
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)



class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_birthday(self, birthday):
        if self.birthday:
            raise ValueError(f"Birthday for {self.name.value} already exists.")
        self.birthday = Birthday(birthday)

    def add_phone(self, phone_number):
        if self.find_phone(phone_number):
            raise ValueError("Такий номер вже існує")
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)
        else:
            raise ValueError("Номер не знайдено") 

    def edit_phone(self, old_number, new_number):
        if not self.find_phone(old_number):
            raise ValueError("Номер не знайдено")
        new_phone = Phone(new_number)

        self.remove_phone(old_number)
        self.add_phone(new_number)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None    

    def __str__(self):
        birthday = f", Birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record 
    
    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.today().date()
        end_period = today + timedelta(days=7)

        for record in self.data.values():
            if record.birthday:
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = bday.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if birthday_this_year.weekday() == 5:  
                    birthday_this_year += timedelta(days=2)
                elif birthday_this_year.weekday() == 6:  
                    birthday_this_year += timedelta(days=1)

                if today <= birthday_this_year <= end_period:
                    upcoming_birthdays.append((record.name.value, birthday_this_year.strftime("%d.%m.%Y")))

        return upcoming_birthdays
    
    def __str__(self):
        if not self.data:
            return "AddressBook is empty."
        return "\n".join(str(record) for record in self.data.values())

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"Error: {e}")
        except KeyError:
            print("Контакт не знайдений.")
        except Exception as e:
            print(f"Невідома помилка: {e}")
    return wrapper

@input_error
def add_contact(address_book, name, phone):
    if address_book.find(name):
        address_book.find(name).add_phone(phone)
    else:
        record = Record(name)
        record.add_phone(phone)
        address_book.add_record(record)
    return f"Контакт {name} з телефоном {phone} додано."

@input_error
def change_phone(address_book, name, old_phone, new_phone):
    record = address_book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        print(f"Телефон для контакту {name} змінено на {new_phone}.")
    else:
        print("Контакт не знайдений.")

@input_error
def show_phone(address_book, name):
    record = address_book.find(name)
    if record:
        print(f"Телефон(и) для контакту {name}: {'; '.join(p.value for p in record.phones)}")
    else:
        print("Контакт не знайдений.")

@input_error
def show_all(address_book):
    print(address_book)

@input_error
def add_birthday(address_book, name, birthday):
    record = address_book.find(name)
    if record:
        record.add_birthday(birthday)
        print(f"Дата народження для {name} додана.")
    else:
        print("Контакт не знайдений.")

@input_error
def show_birthday(address_book, name):
    record = address_book.find(name)
    if record and record.birthday:
        print(f"Дата народження {name}: {record.birthday.value}")
    else:
        print("Контакт або дата народження не знайдені.")

@input_error
def show_upcoming_birthdays(address_book):
    upcoming_birthdays = address_book.get_upcoming_birthdays()
    if upcoming_birthdays:
        print("Найближчі дні народження:")
        for name, congrats_date in upcoming_birthdays:
            print(f"{name}: {congrats_date}")
    else:
        print("Немає найближчих днів народження.")



@input_error
def hello():
    print("Привіт! Я твій особистий асистент для управління контактами.")

def main():
    address_book = AddressBook()

    while True:
        command = input("Введіть команду: ").strip().lower()

        if command == "hello":
            print(hello())

        elif command.startswith("add "):
            _, name, phone = command.split()
            print(add_contact(address_book, name, phone))

        elif command.startswith("change "):
            _, name, old_phone, new_phone = command.split()
            print(change_phone(address_book, name, old_phone, new_phone))

        elif command.startswith("phone "):
            _, name = command.split()
            print(show_phone(address_book, name))

        elif command == "all":
             print(address_book)


        elif command.startswith("add-birthday "):
            _, name, birthday = command.split()
            print(add_birthday(address_book, name, birthday))

        elif command.startswith("show-birthday "):
            _, name = command.split()
            print(show_birthday(address_book, name))

        elif command == "birthdays":
            print(show_upcoming_birthdays(address_book))

        elif command in ["close", "exit"]:
            print("До побачення!")
            break

        else:
            print("Невідома команда. Спробуйте ще раз.")


 
if __name__ == "__main__":
    main()