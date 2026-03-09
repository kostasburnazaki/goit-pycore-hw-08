from __future__ import annotations

import pickle
from typing import Dict, List, Tuple, Callable, Optional
from functools import wraps
from collections import UserDict


class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Required field. No extra validation needed."""
    pass


class Phone(Field):
    """Phone must contain exactly 10 digits."""

    def __init__(self, value: str):
        value = value.strip()
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: List[Phone] = []

    def add_phone(self, phone: str) -> None:
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        for i, p in enumerate(self.phones):
            if p.value == phone:
                self.phones.pop(i)
                return
        raise ValueError("Phone not found.")

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        new_p = Phone(new_phone)

        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = new_p
                return

        raise ValueError("Old phone not found.")

    def find_phone(self, phone: str) -> Optional[Phone]:
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self) -> str:
        phones_str = "; ".join(
            p.value for p in self.phones) if self.phones else "-"
        return f"Contact name: {self.name.value}, phones: {phones_str}"


class AddressBook(UserDict):
    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> Record:
        try:
            return self.data[name]
        except KeyError:
            raise KeyError("Contact not found.")

    def delete(self, name: str) -> None:
        try:
            del self.data[name]
        except KeyError:
            raise KeyError("Contact not found.")


def save_data(book: AddressBook, filename: str = "addressbook.pkl") -> None:
    """Save address book to file using pickle."""
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename: str = "addressbook.pkl") -> AddressBook:
    """Load address book from file."""
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def input_error(func: Callable) -> Callable:
    """Decorator to handle user input errors in command handlers."""

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Enter user name."
        except KeyError:
            return "Contact not found."

    return inner


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    parts = user_input.strip().split()

    if not parts:
        return "", []

    command = parts[0].lower()
    args = parts[1:]

    return command, args


@input_error
def add_contact(args: List[str], book: AddressBook) -> str:
    """add <name> <phone>"""
    name, phone = args

    record = book.data.get(name)

    if record is None:
        record = Record(name)
        book.add_record(record)

    record.add_phone(phone)

    return "Contact added."


@input_error
def change_contact(args: List[str], book: AddressBook) -> str:
    """change <name> <old_phone> <new_phone>"""
    name, old_phone, new_phone = args

    record = book.find(name)

    record.edit_phone(old_phone, new_phone)

    return "Contact updated."


@input_error
def show_phone(args: List[str], book: AddressBook) -> str:
    """phone <name>"""
    name = args[0]

    record = book.find(name)

    return str(record)


def show_all(book: AddressBook) -> str:
    if not book.data:
        return "No contacts saved."

    return "\n".join(str(record) for record in book.data.values())


def main() -> None:
    book = load_data()

    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            save_data(book)
            print("Good bye!")
            break

        if command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()