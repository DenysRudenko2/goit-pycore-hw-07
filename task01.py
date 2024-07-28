from collections import UserDict
import re
import datetime as dt
from datetime import datetime


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name):
        if not name:
            raise ValueError("Name is required field")
        super().__init__(name)


class Phone(Field):
    #  10 digits phone number
    phone_pattern = re.compile(r"^\d{10}$")

    def __init__(self, phone):
        if not phone:
            raise ValueError("Name is required field")
        if not self.phone_pattern.match(phone):
            raise ValueError("Phone number must contain 10 digits")
        super().__init__(phone)

    def __str__(self):
        return f"{self.value}"


class Birthday(Field):
    def __init__(self, value):
        pattern = re.compile(r"^\d{2}-\d{2}-\d{4}$")
        if not pattern.match(value):
            raise ValueError("Invalid date format. Use DD-MM-YYYY")
        try:
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD-MM-YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = (Birthday(birthday))

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        if name in self.data:
            return self.data[name]
        return None

    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthdays(self):
        celebrators = []
        for user in self.data.values():
            if user.birthday is None:
                continue

            parsed_birthday = dt.datetime.strptime(user.birthday.value, '%d-%m-%Y').date()
            today = dt.date.today()

            # Add a day or two for congratulation date if birthday is on a weekend:
            def calculate_congrats_day(date: datetime.date):
                if date.weekday() == 5:
                    return date + dt.timedelta(days=2)
                elif date.weekday() == 6:
                    return date + dt.timedelta(days=1)
                return date

            # Check b-day this year:
            this_year_birthday = parsed_birthday.replace(year=today.year)
            if this_year_birthday >= today:
                if 0 <= (this_year_birthday - today).days <= 7:
                    this_year_birthday = calculate_congrats_day(this_year_birthday)
                    celebrators.append({'name': user.name.value, 'congratulation_date': this_year_birthday.__str__()})
                continue

            # Check if less than 7 days left to the new year:
            if today.month == 12 and today.day > 25:
                # Check b-day next year:
                next_year_birthday = parsed_birthday.replace(year=today.year + 1)
                if (next_year_birthday - today).days <= 7:
                    next_year_birthday = calculate_congrats_day(next_year_birthday)
                    celebrators.append({'name': user['name'], 'congratulation_date': next_year_birthday})

        print(celebrators)


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (IndexError, KeyError, ValueError) as err:
            print(str(err))

    return inner


@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Name and phone are required fields.")
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    print(message)


@input_error
def change_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        raise ValueError("Contact not found.")
    else:
        record.edit_phone(phone, args[2])
    print(message)


@input_error
def show_phones(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    else:
        phones = (o.value for o in record.phones)
        print(f"{name} phones: {', '.join(phones)}")


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    message = "Birthday added."
    if record is None:
        raise ValueError("Contact not found.")
    else:
        record.add_birthday(birthday)
    print(message)


@input_error
def show_birthday_by_name(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    elif record.birthday is None:
        print(f"{name} has no birthday.")
    else:
        print(f"{name} birthday: {record.birthday}")


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

        #  add [ім'я] [телефон]: Додати або новий контакт з іменем та телефонним номером,
        #  або телефонний номер к контакту який вже існує.
        elif command == "add":
            add_contact(args, book)

        #  change [ім'я] [старий телефон] [новий телефон]: Змінити телефонний номер для вказаного контакту.
        elif command == "change":
            change_contact(args, book)

        #  phone [ім'я]: Показати телефонні номери для вказаного контакту.
        elif command == "phone":
            show_phones(args, book)


        #  all: Показати всі контакти в адресній книзі.
        elif command == "all":
            for contact in book.data.values():
                print(contact)

        #  add-birthday [ім'я] [дата народження]: Додати дату народження для вказаного контакту.
        elif command == "add-birthday":
            add_birthday(args, book)

        #  show-birthday [ім'я]: Показати дату народження для вказаного контакту.
        elif command == "show-birthday":
            show_birthday_by_name(args, book)

        #  birthdays: Показати дні народження, які відбудуться протягом наступного тижня.
        elif command == "birthdays":
            book.get_upcoming_birthdays()

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()


