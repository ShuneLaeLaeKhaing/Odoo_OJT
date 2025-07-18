from abc import ABC, abstractmethod
from datetime import datetime

class Vehicle(ABC):
    def __init__(self,license_plate,vehicle_type):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type
        self.entry_time = None

    @abstractmethod
    def get_parking_rate(self):
        pass

class Bike(Vehicle):
    def __init__(self,license_plate):
        super().__init__(license_plate,"bike")

    def get_parking_rate(self):
        return 0.5

class Car(Vehicle):
    def __init__(self,license_plate):
        super().__init__(license_plate,"car")

    def get_parking_rate(self):
        return 1.0

class Truck(Vehicle):
    def __init__(self,license_plate):
        super().__init__(license_plate,"truck")

    def get_parking_rate(self):
        return 2.0

class ParkingSpot:
    def __init__(self,spot_id,vehicle_type):
        self.spot_id = spot_id 
        self.vehicle_type = vehicle_type
        self.is_available = True
        self.current_vehicle = None

    def assign_vehicle(self,vehicle):
        if self.is_available and vehicle.vehicle_type == self.vehicle_type:
            self.current_vehicle = vehicle
            self.is_available = False
            vehicle.entry_time = datetime.now()
            return True
        return False

    def remove_vehicle(self):
        if not self.is_available and self.current_vehicle:
            vehicle =self.current_vehicle
            self.current_vehicle = None
            self.is_available = True
            return vehicle
        return None
    
    def __str__(self):
        status = "Availbale" if self.is_available else f"Occupied by {self.current_vehicle.license_plate}"
        return f"Spot {self.spot_id} ({self.vehicle_type}): {status}"

class ParkingLot:
    def __init__(self):
        self.spots = {}
        self.tickets = {}
        self.earnings = 0.0
        self.__initialize_spots()

    def __initialize_spots(self):
        for i in range(1,11):
            self.spots[f"B{i}"] = ParkingSpot(f"B{i}", "bike")
            self.spots[f"C{i}"] = ParkingSpot(f"C{i}", "car")
            self.spots[f"T{i}"] = ParkingSpot(f"T{i}", "truck")
    

    def find_available_spot(self,vehicle_type):
        for spot in self.spots.values():
            if spot.vehicle_type == vehicle_type and spot.is_available:
                return spot 
        return None

    def park_vehicle(self,vehicle):
        spot = self.find_available_spot(vehicle.vehicle_type)
        if spot and spot.assign_vehicle(vehicle):
            ticket_id = f"TKT -{datetime.now().strftime('%Y%m%d%H%M%S')}"
            ticket = Ticket(ticket_id,vehicle,spot.spot_id)
            self.tickets[ticket_id] = ticket
            return ticket
        return None

    def release_vehicle(self,license_plate):
        ticket = None
        for t in self.tickets.values():
            if t.vehicle.license_plate == license_plate and t.exit_time is None:
                ticket = t
                break

        if ticket:
            spot = self.spots.get(ticket.spot_id)
            if spot and not spot.is_available:
                vehicle = spot.remove_vehicle()
                if vehicle:
                    ticket.exit_time = datetime.now()
                    ticket.fee = ticket.calculate_fee()
                    self.earnings += ticket.fee
                    return ticket
        return None

    def generate_report(self):
        available_spots = {
            "bike": sum(1 for s in self.spots.values() if s.vehicle_type == "bike" and s.is_available),
            "car": sum(1 for s in self.spots.values() if s.vehicle_type == "car" and s.is_available),
            "truck": sum(1 for s in self.spots.values() if s.vehicle_type == "truck" and s.is_available)
        }
        
        occupied_spots = {
            "bike": sum(1 for s in self.spots.values() if s.vehicle_type == "bike" and not s.is_available),
            "car": sum(1 for s in self.spots.values() if s.vehicle_type == "car" and not s.is_available),
            "truck": sum(1 for s in self.spots.values() if s.vehicle_type == "truck" and not s.is_available)
        }
        
        active_tickets = sum(1 for t in self.tickets.values() if t.exit_time is None)
        
        return {
            "available_spots": available_spots,
            "occupied_spots": occupied_spots,
            "total_earnings": self.earnings,
            "active_tickets": active_tickets
        }
    
    def get_lot_status(self):
        return [str(spot) for spot in self.spots.values()]
    
    def get_active_tickets(self):
        return [t for t in self.tickets.values() if t.exit_time is None]

class FeeStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, hours):
        pass

class BikeFeeStrategy(FeeStrategy):
    def calculate_fee(self, hours):
        return round(hours * 0.5, 2)  
    
class CarFeeStrategy(FeeStrategy):
    def calculate_fee(self, hours):
        return round(hours * 1.0, 2)

class TruckFeeStrategy(FeeStrategy):
    def calculate_fee(self, hours):
        return round(hours * 2.0, 2)  

class FeeCalculator:
    def __init__(self):
        self.strategies = {
            "bike": BikeFeeStrategy(),
            "car": CarFeeStrategy(),
            "truck": TruckFeeStrategy()
        }
    
    def calculate(self, vehicle_type, hours):
        strategy = self.strategies.get(vehicle_type)
        if strategy:
            return strategy.calculate_fee(hours)
        return 0.0

class Ticket:
    def __init__(self, ticket_id, vehicle, spot_id):
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.spot_id = spot_id
        self.entry_time = datetime.now()
        self.exit_time = None
        self.fee = None
        self.fee_calculator = FeeCalculator()
    
    def calculate_fee(self):
        if self.exit_time is None:
            self.exit_time = datetime.now()
        
        hours_parked = (self.exit_time - self.entry_time).total_seconds() / 3600
        return self.fee_calculator.calculate(self.vehicle.vehicle_type, hours_parked)

def parking_lot_menu():
    parking_lot = ParkingLot()
    
    while True:
        print("\nParking Lot Management System")
        print("1. Park Vehicle")
        print("2. Remove Vehicle")
        print("3. View Lot Status")
        print("4. View Active Tickets")
        print("5. View Earnings Report")
        print("6. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            print("\nVehicle Types:")
            print("1. Bike ($0.50/hr)")
            print("2. Car ($1.00/hr)")
            print("3. Truck ($2.00/hr)")
            vehicle_choice = input("Select vehicle type: ")
            
            license_plate = input("Enter license plate: ")
            
            vehicle = None
            if vehicle_choice == '1':
                vehicle = Bike(license_plate)
            elif vehicle_choice == '2':
                vehicle = Car(license_plate)
            elif vehicle_choice == '3':
                vehicle = Truck(license_plate)
            else:
                print("Invalid vehicle type.")
                continue
            
            ticket = parking_lot.park_vehicle(vehicle)
            if ticket:
                print(f"\nVehicle parked successfully!")
                print(f"Ticket ID: {ticket.ticket_id}")
                print(f"Spot ID: {ticket.spot_id}")
                print(f"Entry Time: {ticket.entry_time}")
            else:
                print("No available spots for this vehicle type.")
        
        elif choice == '2':
            license_plate = input("Enter license plate of vehicle to remove: ")
            ticket = parking_lot.release_vehicle(license_plate)
            if ticket:
                print(f"\nVehicle released successfully!")
                print(f"Ticket ID: {ticket.ticket_id}")
                print(f"Parking Duration: {(ticket.exit_time - ticket.entry_time).total_seconds()/3600:.2f} hours")
                print(f"Fee: ${ticket.fee:.2f}")
            else:
                print("Vehicle not found or already released.")
        
        elif choice == '3':
            print("\nCurrent Lot Status:")
            for spot_status in parking_lot.get_lot_status():
                print(spot_status)
        
        elif choice == '4':
            active_tickets = parking_lot.get_active_tickets()
            print(f"\nActive Tickets ({len(active_tickets)}):")
            for ticket in active_tickets:
                print(f"- {ticket.vehicle.license_plate} at {ticket.spot_id} (since {ticket.entry_time})")
        
        elif choice == '5':
            report = parking_lot.generate_report()
            print("\nParking Lot Report:")
            print(f"Total Earnings: ${report['total_earnings']:.2f}")
            print("\nAvailable Spots:")
            print(f"Bike: {report['available_spots']['bike']}")
            print(f"Car: {report['available_spots']['car']}")
            print(f"Truck: {report['available_spots']['truck']}")
            print("\nOccupied Spots:")
            print(f"Bike: {report['occupied_spots']['bike']}")
            print(f"Car: {report['occupied_spots']['car']}")
            print(f"Truck: {report['occupied_spots']['truck']}")
            print(f"\nActive Tickets: {report['active_tickets']}")
        
        elif choice == '6':
            print("Exiting Parking Lot System.")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    parking_lot_menu()

