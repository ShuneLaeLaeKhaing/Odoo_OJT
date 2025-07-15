class Parent:
    def __init__(self, value):
        self.value = value

    def display(self):
        print(f"Parent's value: {self.value}")

class Child(Parent):
    def __init__(self, value, extra_value):
        super().__init__(value)  # Calls Parent's __init__
        self.extra_value = extra_value

    def display(self):
        super().display()  # Calls Parent's display method
        print(f"Child's extra value: {self.extra_value}")

child_obj = Child(10, 20)
child_obj.display()