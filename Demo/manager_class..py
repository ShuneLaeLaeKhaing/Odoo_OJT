class Employee:
    def __init__(self,emp_id,name,position):
        self.emp_id = emp_id
        self.name = name
        self.position = position

    def __str__(self):
        return f"{self.emp_id}: {self.name} - {self.position}"
    
class EmployeeManager:
    def __init__(self):
        self.employees = []

    def add_employee(self,emp):
        self.employees.append(emp)
        print(f"Added: {emp.name}")

    def remove_employee(self,emp_id):
        self.employees = [e for e in self.employees if e.emp_id != emp_id]
        print(f"Removed employee with ID: {emp_id}")

    def find_employee(self,emp_id):
        for emp in self.employees:
            if emp.emp_id == emp_id:
                return emp
        return None
    
    def list_employees(self):
        print("Employee List:")
        for emp in self.employees:
            print(f" -{emp}")

manager = EmployeeManager()

e1 = Employee(1,"Alice","Developer")
e2 = Employee(2,"Bob","Designer")
e3 = Employee(3,"Charlie","Manager")

manager.add_employee(e1)
manager.add_employee(e2)
manager.add_employee(e3)

manager.list_employees()

found = manager.find_employee(2)
print("Found: ", found)

manager.remove_employee(1)

manager.list_employees()