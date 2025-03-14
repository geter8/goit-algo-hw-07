from datetime import datetime, timedelta
from collections import UserDict
import re


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not re.fullmatch(r'\d{10}', value):
            raise ValueError("Phone must be 10 digits.")
        super().__init__(value)


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

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        if not re.fullmatch(r'\d{10}', new_phone):
            raise ValueError("Phone must be 10 digits.")

        found = False
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                found = True
        if not found:
            raise ValueError("Phone not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}{birthday}, phones: {phones}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if not record.birthday:
                continue

            b_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            this_year_bday = b_date.replace(year=today.year)

            if this_year_bday < today:
                this_year_bday = this_year_bday.replace(year=today.year + 1)

            days_to_bday = (this_year_bday - today).days

            if 0 <= days_to_bday <= 7:
                if this_year_bday.weekday() >= 5:  # Weekend
                    this_year_bday += timedelta(days=7 - this_year_bday.weekday())

                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": this_year_bday.strftime("%d.%m.%Y")
                })

        return upcoming


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Invalid command format."

    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Give me name and phone please.")
    name, phone = args[0], args[1]
    record = book.find(name) or Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added/updated."


@input_error
def change_contact(args, book):
    if len(args) != 3:
        raise ValueError("Give me name, old phone and new phone.")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone changed."
    raise KeyError("Contact not found.")


@input_error
def show_phone(args, book):
    if not args:
        raise ValueError("Enter contact name.")
    name = args[0]
    record = book.find(name)
    if record:
        return '; '.join(p.value for p in record.phones)
    raise KeyError("Contact not found.")


@input_error
def show_all(book):
    if not book.data:
        return "No contacts found."
    return '\n'.join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise ValueError("Give me name and birthday in DD.MM.YYYY format.")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    raise KeyError("Contact not found.")


@input_error
def show_birthday(args, book):
    if not args:
        raise ValueError("Enter contact name.")
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value
    return "No birthday set." if record else "Contact not found."


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in next week."
    return '\n'.join(
        f"{entry['name']}: {entry['congratulation_date']}"
        for entry in upcoming
    )


def parse_input(input_str):
    return input_str.strip().split()


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

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