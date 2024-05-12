from datetime import datetime, timedelta
from collections import UserDict
import pickle

class Field:
    # Базовий клас для полів запису
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    # Клас для зберігання імені контакту. Обов'язкове поле.
    pass


class Phone(Field):
    # Клас для зберігання номера телефону. Має валідацію формату (10 цифр).
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Invalid phone number format")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        try:
            # Перетворюємо рядок на об'єкт datetime
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    # Клас для зберігання інформації про контакт, включаючи ім'я та список телефонів.
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        raise ValueError("Phone not found")

    def __str__(self):
        return f"Contact name: {self.name}, phones: {', '.join(map(str, self.phones))}, birthday: {self.birthday}"


class AddressBook(UserDict):
    def save_data(self, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.data, f)

    @classmethod
    def load_data(cls, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                data = pickle.load(f)
                book = cls()
                book.data = data
                return book
        except FileNotFoundError:
            return cls()

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = record.birthday.value.replace(year=today.year)
                if birthday_date < today:
                    birthday_date = birthday_date.replace(year=today.year + 1)

                days_until_birthday = (birthday_date - today).days

                if days_until_birthday <= 7:
                    if birthday_date.weekday() >= 5:
                        # Переносимо на наступний понеділок, якщо вихідний
                        birthday_date += timedelta(days=(7 - birthday_date.weekday()))
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": birthday_date.strftime("%d.%m.%Y")
                    })

        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Incomplete command. Please provide all necessary arguments."
        except Exception as e:
            return str(e)
    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.phones.remove(Phone(old_phone))
        record.add_phone(new_phone)
        return "Phone number updated."
    else:
        return "Contact not found."


@input_error
def show_phone(args, book):
    name, *_ = args
    record = book.find(name)
    if record:
        return f"{record.name}'s phone numbers: {', '.join(map(str, record.phones))}"
    else:
        return "Contact not found."


@input_error
def show_all(book):
    if book:
        return "\n".join([str(record) for record in book.values()])
    else:
        return "No contacts available."


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        return "Contact not found."


@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is on {record.birthday}."
    elif record and not record.birthday:
        return f"{name} doesn't have a birthday set."
    else:
        return "Contact not found."


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join([f"{user['name']} - {user['congratulation_date']}" for user in upcoming_birthdays])
    else:
        return "No upcoming birthdays."


def main():
    book = AddressBook.load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            book.save_data()
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
