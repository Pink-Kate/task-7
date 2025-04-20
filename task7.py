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
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


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
        today = datetime.today()
        for record in self.data.values():
            if record.birthday:
               birthday_date = record.birthday.value.replace(year=today.year)
            if birthday_date < today:
                birthday_date = birthday_date.replace(year=today.year + 1)
            if today <= birthday_date <= today + timedelta(days=7):
                upcoming_birthdays.append(record)
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
    print(f"Контакт {name} з телефоном {phone} додано.")

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
        for record in upcoming_birthdays:
            print(f"{record.name.value}: {record.birthday.value}")
    else:
        print("Немає найближчих днів народження.")

@input_error
def hello():
    print("Привіт! Я твій особистий асистент для управління контактами.")


def main():
    address_book = AddressBook()

    while True:
        command = input("Введіть команду: ").strip()

        if command.lower() == "hello":
            hello()

        elif command.lower().startswith("add "):
            try:
                _, name, phone = command.split()
                add_contact(address_book, name, phone)
            except ValueError:
                print("Використовуйте: add [ім'я] [телефон]")

        elif command.lower().startswith("change "):
            try:
                _, name, old_phone, new_phone = command.split()
                change_phone(address_book, name, old_phone, new_phone)
            except ValueError:
                print("Використовуйте: change [ім'я] [старий телефон] [новий телефон]")

        elif command.lower().startswith("phone "):
            try:
                _, name = command.split()
                show_phone(address_book, name)
            except ValueError:
                print("Використовуйте: phone [ім'я]")

        elif command.lower() == "all":
            show_all(address_book)

        elif command.lower().startswith("add-birthday "):
            try:
                _, name, birthday = command.split()
                add_birthday(address_book, name, birthday)
            except ValueError:
                print("Використовуйте: add-birthday [ім'я] [дата у форматі DD.MM.YYYY]")

        elif command.lower().startswith("show-birthday "):
            try:
                _, name = command.split()
                show_birthday(address_book, name)
            except ValueError:
                print("Використовуйте: show-birthday [ім'я]")

        elif command.lower() == "birthdays":
            show_upcoming_birthdays(address_book)

        elif command.lower() in ["close", "exit"]:
            print("До побачення!")
            break

        else:
            print("Невідома команда. Спробуйте ще раз.")
 
if __name__ == "__main__":
    main()