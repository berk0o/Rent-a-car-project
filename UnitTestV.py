import os
import datetime
import csv
import unittest


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


class Person:
    def __init__(self, first_name, last_name, birth_date):
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = self._validate_birth_date(birth_date)

    def _validate_birth_date(self, birth_date):
        birth_date_dt = datetime.datetime.strptime(birth_date, '%Y-%m-%d')
        if birth_date_dt > datetime.datetime.now():
            raise ValueError("Birth date cannot be in the future.")
        return birth_date_dt

    def __str__(self):
        return f"{self.first_name} {self.last_name}, Birth Date: {self.birth_date.strftime('%Y-%m-%d')}"


class User(Person):
    def __init__(self, first_name, last_name, birth_date, license_date):
        super().__init__(first_name, last_name, birth_date)
        self.license_date = self._validate_license_date(license_date)

    def _validate_license_date(self, license_date):
        license_date_dt = datetime.datetime.strptime(license_date, '%Y-%m-%d')
        if license_date_dt > datetime.datetime.now():
            raise ValueError("License date cannot be in the future.")
        if license_date_dt < self.birth_date:
            raise ValueError("License date cannot be before birth date.")
        return license_date_dt

    def __str__(self):
        return f"{super().__str__()}, License Date: {self.license_date.strftime('%Y-%m-%d')}"


class Appointment:
    def __init__(self, user, vehicle_type, appointment_date, appointment_time):
        self.user = user
        self.vehicle_type = vehicle_type
        self.appointment_datetime = self._validate_appointment_datetime(appointment_date, appointment_time)

    def _validate_appointment_datetime(self, appointment_date, appointment_time):
        appointment_date_dt = datetime.datetime.strptime(appointment_date, '%Y-%m-%d')
        appointment_time_dt = datetime.datetime.strptime(appointment_time, '%H:%M')
        appointment_datetime = datetime.datetime.combine(
            appointment_date_dt.date(), appointment_time_dt.time()
        )
        if appointment_datetime < datetime.datetime.now():
            raise ValueError("Appointment date cannot be in the past.")
        return appointment_datetime

    def __str__(self):
        return (
            f"Appointment: {self.appointment_datetime.strftime('%Y-%m-%d %H:%M')} - "
            f"{self.user.first_name} {self.user.last_name} - Vehicle Type: {self.vehicle_type}"
        )


class UserFactory:
    @staticmethod
    def create_user(first_name, last_name, birth_date, license_date):
        return User(first_name, last_name, birth_date, license_date)


@singleton
class VehicleRental:
    def __init__(self):
        self.users = []
        self.appointments = []

    def add_user(self, first_name, last_name, birth_date, license_date):
        user = UserFactory.create_user(first_name, last_name, birth_date, license_date)
        self.users.append(user)
        return user

    def add_appointment(self, user, vehicle_type, appointment_date, appointment_time):
        appointment = Appointment(user, vehicle_type, appointment_date, appointment_time)
        self.appointments.append(appointment)
        return appointment

    def save_data_to_csv(self, users_file="users.csv", appointments_file="appointments.csv"):
        with open(users_file, 'w', newline='') as ufile:
            writer = csv.writer(ufile)
            writer.writerow(["First Name", "Last Name", "Birth Date", "License Date"])
            for user in self.users:
                writer.writerow([
                    user.first_name, user.last_name,
                    user.birth_date.strftime('%Y-%m-%d'),
                    user.license_date.strftime('%Y-%m-%d')
                ])

        with open(appointments_file, 'w', newline='') as afile:
            writer = csv.writer(afile)
            writer.writerow(["First Name", "Last Name", "Vehicle Type", "Appointment DateTime"])
            for appointment in self.appointments:
                writer.writerow([
                    appointment.user.first_name, appointment.user.last_name,
                    appointment.vehicle_type,
                    appointment.appointment_datetime.strftime('%Y-%m-%d %H:%M')
                ])

    def load_data_from_csv(self, users_file="users.csv", appointments_file="appointments.csv"):
        self.users.clear()
        self.appointments.clear()

        with open(users_file, 'r') as ufile:
            reader = csv.DictReader(ufile)
            for row in reader:
                self.add_user(
                    row["First Name"], row["Last Name"], row["Birth Date"], row["License Date"]
                )

        with open(appointments_file, 'r') as afile:
            reader = csv.DictReader(afile)
            for row in reader:
                user = next(
                    (u for u in self.users
                     if u.first_name == row["First Name"] and u.last_name == row["Last Name"]), None
                )
                if user:
                    self.add_appointment(user, row["Vehicle Type"], row["Appointment DateTime"].split()[0],
                                         row["Appointment DateTime"].split()[1])


def main():
    system = VehicleRental()

    first_name = input("First Name: ")
    last_name = input("Last Name: ")

    while True:
        try:
            birth_date = input("Birth Date (YYYY-MM-DD): ")
            license_date = input("License Date (YYYY-MM-DD): ")
            user = system.add_user(first_name, last_name, birth_date, license_date)
            break
        except ValueError as ve:
            print(f"Invalid input: {ve}")

    cars = {
        "Toyota": ["Corolla", "Camry", "RAV4"],
        "Honda": ["Civic", "Accord", "CR-V"],
        "Ford": ["Focus", "Mustang", "Explorer"]
    }
    motorcycles = {
        "Yamaha": ["MT-07", "YZF-R6", "FZ-10"],
        "Honda": ["CBR500R", "Africa Twin", "CB500X"],
        "Kawasaki": ["Ninja 400", "Z650", "Versys 650"]
    }
    vehicle_type = None

    while True:
        choice = input("Select vehicle type (1: Car, 2: Motorcycle): ")
        if choice == "1":
            brand = input(f"Select car brand ({', '.join(cars.keys())}): ")
            if brand in cars:
                model = input(f"Select model ({', '.join(cars[brand])}): ")
                if model in cars[brand]:
                    vehicle_type = f"{brand} {model}"
                    break
                else:
                    print("Invalid model. Please try again.")
            else:
                print("Invalid brand. Please try again.")
        elif choice == "2":
            brand = input(f"Select motorcycle brand ({', '.join(motorcycles.keys())}): ")
            if brand in motorcycles:
                model = input(f"Select model ({', '.join(motorcycles[brand])}): ")
                if model in motorcycles[brand]:
                    vehicle_type = f"{brand} {model}"
                    break
                else:
                    print("Invalid model. Please try again.")
            else:
                print("Invalid brand. Please try again.")
        else:
            print("Invalid choice. Please try again.")

    while True:
        try:
            appointment_date = input("Appointment Date (YYYY-MM-DD): ")
            appointment_time = input("Appointment Time (HH:MM): ")
            appointment = system.add_appointment(user, vehicle_type, appointment_date, appointment_time)
            break
        except ValueError as ve:
            print(f"Invalid input: {ve}")

    system.save_data_to_csv()
    print("User and appointment data successfully saved.")


if __name__ == "__main__":
    main()


# Unit Tests
class TestVehicleRental(unittest.TestCase):

    def setUp(self):
        self.system = VehicleRental()
        self.system.users = []
        self.system.appointments = []
        self.user = self.system.add_user(
            "Test", "User", "1990-05-21", "2010-05-21"
        )
        self.system.add_appointment(self.user, "Toyota Corolla", "2024-12-31", "12:00")

    def tearDown(self):
        if os.path.exists("test_users.csv"):
            os.remove("test_users.csv")
        if os.path.exists("test_appointments.csv"):
            os.remove("test_appointments.csv")

    def test_birth_date_validation(self):
        # Valid birth date
        birth_date = "1990-05-21"
        self.assertEqual(
            self.user.birth_date, datetime.datetime(1990, 5, 21)
        )

        # Future birth date
        with self.assertRaises(ValueError):
            self.system.add_user(
                "Test", "User", "3000-01-01", "2010-05-21"
            )

    def test_license_date_validation(self):
        # Valid license date
        license_date = "2010-05-21"
        self.assertEqual(
            self.user.license_date, datetime.datetime(2010, 5, 21)
        )

        # Future license date
        with self.assertRaises(ValueError):
            self.system.add_user(
                "Test", "User", "1990-05-21", "3000-01-01"
            )

        # License date before birth date
        with self.assertRaises(ValueError):
            self.system.add_user(
                "Test", "User", "1990-05-21", "1980-01-01"
            )

    def test_appointment_date_validation(self):
        # Valid appointment date
        appointment_date = "2024-12-31"
        appointment_time = "12:00"
        appointment = self.system.add_appointment(
            self.user, "Toyota Corolla", appointment_date, appointment_time
        )
        self.assertEqual(
            appointment.appointment_datetime, datetime.datetime(2024, 12, 31, 12, 0)
        )

        # Past appointment date
        with self.assertRaises(ValueError):
            self.system.add_appointment(
                self.user, "Toyota Corolla", "2000-01-01", "12:00"
            )

    def test_csv_save_load(self):
        # CSV save and load tests
        self.system.save_data_to_csv(
            "test_users.csv", "test_appointments.csv"
        )
        new_system = VehicleRental()
        new_system.load_data_from_csv(
            "test_users.csv", "test_appointments.csv"
        )
        self.assertEqual(len(new_system.users), 1)
        self.assertEqual(len(new_system.appointments), 1)  # Should be one appointment


if __name__ == '__main__':
    unittest.main()
