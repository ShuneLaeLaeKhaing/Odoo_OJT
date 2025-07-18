import json
from datetime import datetime

class Person:
    def __init__(self,name,age,gender,person_id):
        self. name = name
        self.age = age
        self.gender = gender
        self.person_id = person_id

class Doctor(Person):
    def __init__(self,name,age,gender,person_id,specialization):
        super().__init__(name,age,gender,person_id)
        self.specialization = specialization
        self.schedule = []
        self.patients_assigned = []
        

class Nurse(Person):
    def __init__(self,name,age,gender,person_id,assigned_ward,shift_time):
        super().__init__(name,age,gender,person_id)
        self.assigned_ward = assigned_ward
        self.shift_time = shift_time

class Patient(Person):
    def __init__(self,name,age,gender,person_id):
        super().__init__(name,age,gender,person_id)
        self.symptoms = []
        self.medical_history = []
        self.assigned_doctor = None

class Appointment:
    def __init__(self,appointment_id,doctor,patient,datetime,status="Scheduled"):
        self.appointment_id = appointment_id
        self.doctor = doctor
        self.patient = patient
        self.datetime = datetime
        self.status = status

    def add_entry(self,new_status):
        self.status = new_status

    def view_history(self):
        return f"Appointment {self.appointment_id}: {self.datetime} - Status : { self.status}"

class MedicalRecord:
    def __init__(self,record_id,patient,diagnosis,prescription,doctor,date):
        self.record_id = record_id
        self.patient = patient
        self.diagnosis = diagnosis
        self.prescription = prescription
        self.doctor = doctor
        self.date = date

    def add_entry(self,new_diagnosis,new_prescription):
        self.diagnosis = new_diagnosis
        self.prescription = new_prescription

    def view_history(self):
        return f"Record {self.record_id} ({self.date}):\nDiagnosis:{self.diagnosis}\nPrescription: {self.prescription}"

class HospitalSystem:
    def __init__(self):
        self.patients ={}
        self.nurses = {}
        self.doctors = {}
        self.appointments = {}
        self.records = {}
        self.current_user = None

    def add_person(self,person_type,**kwargs):
        if person_type == "patient":
            person = Patient(**kwargs)
            self.patients[person.person_id] = person
        elif person_type == "doctor":
            person = Doctor(**kwargs)
            self.doctors[person.person_id] = person
        elif person_type == 'nurse':
            person = Nurse(**kwargs)
            self.nurses[person.person_id] = person
        return person

    def find_person_by_id(self,person_id):
        if person_id in self.patients:
            return self.patients[person_id]
        elif person_id in self.doctors:
            return self.doctors[person_id]
        elif person_id in self.nurses:
            return self.nurses[person_id]
        return None

    def create_appointment(self,appointment_id,doctor_id,patient_id, datetime):
        doctor = self.doctors.get(doctor_id)
        patient = self.patients.get(patient_id)
        if doctor and patient:
            appointment = Appointment(appointment_id,doctor,patient,datetime)
            self.appointments[appointment_id] = appointment
            doctor.schedule.append(appointment)
            patient.medical_history.append(appointment)
            return appointment
        return None

    def assign_doctor_to_patient(self,doctor_id,patient_id):
        doctor = self.doctors.get(doctor_id)
        patient = self.patients.get(patient_id)
        if doctor and patient:
            patient.assigned_doctor = doctor
            doctor.patients_assigned.append(patient)
            return True
        return False
        

    def log_medical_record(self,record_id,patient_id,diagnosis,prescription,doctor_id):
        patient = self.patients.get(patient_id)
        doctor = self.doctors.get(doctor_id)
        if patient and doctor:
            record = MedicalRecord(record_id, patient,diagnosis,prescription,doctor,datetime.now().strftime("%Y-%m-%d"))
            self.records[record_id] = record
            patient.medical_history.append(record)
            return record
        return None

    def view_all_appointments(self):
        return list(self.appointments.values())

    def save_data(self,filename):
        data = {
            "patients": {pid: vars(p) for pid,p in self.patients.items()},
            "doctors": {pid: vars(d) for pid,d in self.doctors.items()},
            "nurses": {pid: vars(n) for pid, n in self.nurses.items()},
            "appointments": {aid:{
                "appointment_id": a.appointment_id,
                "doctor_id": a.doctor.person_id,
                "patient_id": a.patient.person_id,
                "datetime": a.dateime,
                "status": a.status
            } for aid,a in self.appointments.items()},
            "records":{rid: {
                "record_id": r.record_id,
                "patient_id": r.patient.person_id,
                "diagnosis": r.diagnosis,
                "prescription": r.prescription,
                "doctor_id": r.doctor.person_id,
                "date": r.date
            } for rid, r in self.records.items()}
            }
        with open(filename,'w') as f:
            json.dump(data,f)

    def load_data(self,filename):
        try:
            with open(filename,'r') as f:
                data = json.load(f)

                for p_data in data.get("patients",{}).items():
                    self.add_person("patient",**p_data)

                for d_data in data.get("doctors",{}).items():
                    self.add_person("doctor",**d_data)

                for n_data in data.get("nurses",{}).items():
                    self.add_person("nurse",**n_data)

                for aid,a_data in data.get("appointments",{}).items():
                    doctor = self.doctors.get(a_data["doctor_id"])
                    patient = self.patients.get(a_data["patient_id"])
                    if doctor and patient:
                        appointment = Appointment(
                            a_data["appointment_id"],
                            doctor,
                            patient,
                            a_data["datetime"],
                            a_data["status"]
                        )
                        self.appointments[aid] = appointment
                        doctor.schedule.append(appointment)
                        patient.medical_history.append(appointment)

                for rid, r_data in data.get("records", {}).items():
                    patient = self.patients.get(r_data["patient_id"])
                    doctor = self.doctors.get(r_data["doctor_id"])
                    if patient and doctor:
                        record = MedicalRecord(
                            r_data["record_id"],
                            patient,
                            r_data["diagnosis"],
                            r_data["prescription"],
                            doctor,
                            r_data["date"]
                        )
                        self.records[rid] = record
                        patient.medical_history.append(record)
        except FileNotFoundError:
            pass

def hospital_menu():
    hospital = HospitalSystem()
    hospital.load_data("hospital_data.json")

    if not hospital.doctors:
        hospital.add_person("doctor",name="Dr. Smith",age=45, gender="Male", person_id = "D001",specialization ="Cardiology")
        hospital.add_person("doctor",name="Dr. Jhonson", age=38, gender="Female",person_id ="D002",specialization ="Pediatrics")

    while True:
        if not hospital.current_user:
            print("\nHospital Management System")
            print("Please log in as:")
            print("1. Doctor")
            print("2. Nurse")
            print("3. Receptionist")
            print("4. Patient")
            print("5. Exit")

            choice = input("Enter your choice: ")

            if choice == '1':
                person_id = input("Enter your doctor ID: ")
                if person_id in hospital.doctors:
                    hospital.current_user = hospital.doctors[person_id]
                    print(f"Welcome Dr. {hospital.current_user.name}!")
                else:
                    print("Doctor not found.")

            elif choice == '2':
                person_id = input("Enter your nurse ID: ")
                if person_id in hospital.nurses:
                    hospital.current_user = hospital.nurses[person_id]
                    print(f"Welcome Nurse {hospital.current_user.name}!")
                else:
                    print("Nurse not found.")

            elif choice == '3':
                hospital.current_user ={"role": "receptionist"}
                print("Welcome Receptionist!")

            elif choice == '4':
                person_id = input("Enter your patient ID: ")
                if person_id in hospital.patients:
                    hospital.current_user = hospital.patients[person_id]
                    print(f"Welcome {hospital.current_user.name}!")
                else:
                    print("Patient not found.")

            elif choice == '5':
                hospital.save_data("hospital_data.json")
                print("Exiting Hospital System.")
                break

            else:
                print("Invalid choice.Please try again.")

        elif isinstance(hospital.current_user, Doctor):
            print("\nDoctor Menu")
            print("1. View Appointments")
            print("2. Log Medical Record")
            print("3. View Patient Hsitory")
            print("4. Logout")

            choice = input("Enter your choice: ")

            if choice == '1':
                print("\nYour Appointments: ")
                for appt in hospital.current_user.schedule:
                    print(f"{appt.datetime} - {appt.patient.name} (Status: {appt.status})")

            elif choice == '2':
                patient_id = input("Ente patient ID: ")
                diagnosis = input("Enter diagnosis: ")
                prescription = input("Enter prescription: ")
                record_id = f"REC --{datetime.now().strftime('%Y%m%d%H%M%S')}"
                if hospital.log_medical_record(record_id,patient_id, diagnosis,prescription,hospital.current_user.person_id):
                    print("Medical record logged successfully.")
                else:
                    print("Failed to log medical record.")

            elif choice =='3':
                patient_id = input("Enter patient ID: ")
                patient = hospital.patients.get(patient_id)
                if patient and patient in hospital.current_user.patients_assigned:
                    print(f"\nMedical History for {patient.name}: ")
                    for entry in patient.medical_history:
                        if isinstance(entry,Appointment):
                            print(f"Appointment: {entry.datetime} - {entry.status}")
                        elif isinstance(entry,MedicalRecord):
                            print(f"Record: {entry.date}\nDiagnosis: {entry.diagnosis}\nPrescription: {entry.prescription}\n")
                else:
                    print("Patient not found or not assigned to you.")

            elif choice == '4':
                hospital.current_user = None
                print("Logged out successfully.")
            
            else:
                print("Invalid choice. Please try again.")

        elif isinstance(hospital.current_user,dict ) and hospital.current_user.get("role") == "receptionist":
            print("\nReceptionist Menu")
            print("1. Register Patient")
            print("2. Book Appointment")
            print("3. Assign Doctor")
            print("4. Cancel Appointment")
            print("5. Logout")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                name = input("Patient name: ")
                age = input("Patient age: ")
                gender = input("Patient gender: ")
                patient_id = f"P{len(hospital.patients) + 1:03d}"
                hospital.add_person("patient", name=name, age=age, gender=gender, person_id=patient_id)
                print(f"Patient registered successfully. ID: {patient_id}")
            
            elif choice == '2':
                patient_id = input("Patient ID: ")
                doctor_id = input("Doctor ID: ")
                datetime_str = input("Appointment datetime (YYYY-MM-DD HH:MM): ")
                appointment_id = f"APT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                if hospital.create_appointment(appointment_id, doctor_id, patient_id, datetime_str):
                    print("Appointment booked successfully.")
                else:
                    print("Failed to book appointment. Check IDs.")
            
            elif choice == '3':
                patient_id = input("Patient ID: ")
                doctor_id = input("Doctor ID: ")
                if hospital.assign_doctor_to_patient(doctor_id, patient_id):
                    print("Doctor assigned successfully.")
                else:
                    print("Failed to assign doctor. Check IDs.")
            
            elif choice == '4':
                appointment_id = input("Appointment ID to cancel: ")
                appointment = hospital.appointments.get(appointment_id)
                if appointment:
                    appointment.add_entry("Cancelled")
                    print("Appointment cancelled.")
                else:
                    print("Appointment not found.")
            
            elif choice == '5':
                hospital.current_user = None
                print("Logged out successfully.")
            
            else:
                print("Invalid choice. Please try again.")
        
        elif isinstance(hospital.current_user, Patient):
            print("\nPatient Menu")
            print("1. View My Appointments")
            print("2. View My Medical History")
            print("3. Logout")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                print("\nYour Appointments:")
                for entry in hospital.current_user.medical_history:
                    if isinstance(entry, Appointment):
                        print(f"{entry.datetime} with Dr. {entry.doctor.name} - {entry.status}")
            
            elif choice == '2':
                print("\nYour Medical History:")
                for entry in hospital.current_user.medical_history:
                    if isinstance(entry, MedicalRecord):
                        print(f"\nDate: {entry.date}")
                        print(f"Doctor: Dr. {entry.doctor.name}")
                        print(f"Diagnosis: {entry.diagnosis}")
                        print(f"Prescription: {entry.prescription}")
            
            elif choice == '3':
                hospital.current_user = None
                print("Logged out successfully.")
            
            else:
                print("Invalid choice. Please try again.")
        
        elif isinstance(hospital.current_user, Nurse):
            print("\nNurse Menu")
            print("1. View Ward Patients")
            print("2. Logout")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                print(f"\nPatients in {hospital.current_user.assigned_ward}:")
                for patient in hospital.patients.values():
                    print(f"{patient.name} (ID: {patient.person_id})")
            
            elif choice == '2':
                hospital.current_user = None
                print("Logged out successfully.")
            
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    hospital_menu()