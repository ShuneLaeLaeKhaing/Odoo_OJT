from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import uuid

class Person(ABC):
    def __init__(self,name,email,passport_id):
        self.name = name
        self.email = email
        self.passport_id  = passport_id

    def __str__(self):
        return f"{self.name} ({self.passport_id})"

class Passenger(Person):
    def __init__(self,name,email,passport_id,frequent_flyer=None):
        super().__init__(name,email,passport_id)
        self.frequent_flyer = frequent_flyer

class AirlineStaff(Person):
    def __init__(self,name,email,passport_id, staff_id ,role):
        super().__init__(name,email,passport_id)
        self.role = role

class Admin(AirlineStaff):
    def __init__(self,name,email,passport_id,staff_id):
        super().__init__(name,email,passport_id,staff_id,"Admin")

class CheckInAgent(AirlineStaff):
    def __init__(self, name, email, passport_id, staff_id):
        super().__init__(name, email, passport_id, staff_id, "Check-In Agent")

class Pilot(AirlineStaff):
    def __init__(self,name,email,passport_id,staff_id,license_number):
        super().__init__(name,email,passport_id,staff_id,"Pilot")
        self.license_number = license_number

class Flight:
    STATUSES = ["Scheduled","Boarding","Departed","Arrived","Cancelled"]

    def __init__(self,flight_id,origin,destination,departure_time,aircraft):
        self.flight_id = flight_id
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = departure_time + timedelta(hours = 2) #For default 2-hours flight
        self.aircraft = aircraft
        self.passenger_manifest = []
        self.status = "Scheduled"

    def add_passenger(self,passenger,seat_number=None):
        if len(self.passenger_manifest) >= self.aircraft.capacity:
            return False,"Flight is full"
        
        if seat_number:
            if not self.aircraft.assgn_seat(passenger,seat_number):
                return False, "Seat not available"
        else:
            available_seats = self.aircraft.get_available_seats()
            if not available_seats:
                return False, "No seats available"
            self.aircraft.assign_seat(passenger,available_seats[0])

        self.passenger_manifest.append(passenger)
        return True,"Passenger added"

    def cancel_passenger(self,passenger):
        for seat,p in self.aircraft.seat_map.items():
            if p == passenger:
                self.aircraft.seat_map[seat] = None
                self.passenger_manifest.remove(passenger)
                return True, "Passenger removed"
            return False, "Passenge not found"

    def check_seat_availablity(self):
        return len(self.aircraft.get_available_seats())
    
    def update_status(self,new_status):
        if new_status in self.STATUSES:
            self.status = new_status
            return True
        return False
    
    def __str__(self):
        return (f"Flight {self.flight_id}: {self.origin}-> {self.destination}\n"
                f"Departure {self.departure_time.strftime('%Y-%m-%d %H:%M')}\n"
                f"Status: {self.status} | Seats available: {self.check_seat_availablity()}")

class Aircraft:
    def __init__(self,aircraft_id,model,capacity):
        self.aircraft_id = aircraft_id
        self.model = model
        self.capacity = capacity
        self.seat_map = {f"{row}{seat}": None
                         for row in range(1,(capacity//6)+1)
                         for seat in ['A','B','C','D','E','F']}

    def assign_seats(self,passenger,seat_number):
        if seat_number in self.seat_map and self.seat_map[seat_number] is None:
            self.seat_map[seat_number] = passenger
            return True
        return False

    def get_available_seats(self):
        return [seat for seat, passenger in self.seat_map.items() if passenger is None]
    
    def __str__(self):
        return f"{self.model} (ID: {self.aircraft_id}) - {self.total_seats} seats"

class Ticket:
    def __init__(self,passenger,flight,seat_number):
        self.passenger = passenger
        self.flight = flight
        self.seat_number = seat_number
        self.status = "Confirmed"
        self.booking_time = datetime.now()

    def generate_ticket(self):
        self.ticket_id = str(uuid.uuid4())

    def cancel_ticket(self):
        if  self.status == "Cancelled":
            return False, "Ticket already cancelled"
        
        success, message = self.flight.cancel_passenger(self.passenger)
        if success:
            self.status = "Cancelled"
            return True,"Ticket cancelled"
        return False, message
        

    def reschedule_ticket(self,new_flight):
        if self.status == "Cancelled":
            return False, "Cannot reschedule cancelled ticket"
        
        success, message = self.cancel_ticket()
        if not success:
            return False, message
        
        success, message = new_flight.add_passenger(self.passenger,self.seat_number)
        if success:
            self.flight = new_flight
            self.status = "Confirmed"
            return True, "Ticket rescheduled"
        return False, message
    
    def __str__(self):
        return (f"Ticket {self.ticket_id}\n"
                f"Passenger: {self.passenger.name}\n"
                f"FLight: {self.flight.flight_id} ({self.flight.origin} -> {self.flight.destination})\n"
                f"Seat: {self.seat_number} | Status: {self.status}")              


class Route:
    def __init__(self,route_id,origin,destination,distance_km):
        self.route_id = route_id
        self.origin = origin
        self.destination = destination
        self.distance_km = distance_km
        self.estimated_time = self.calculate_flight_duration()

    def calculate_flight_duration(self):
        base_hours = (self.distance_km / 500)* 0.5 # Estimation : 30 minutes per  500 km + 30 minutes buffer
        return timedelta(hours=base_hours + 0.5)
    
    def __str__(self):
        return f"{self.origin} -> {self.destination} ({self.distance_km}km, ~{self.estimated_time})"

class ReservationSystem:
    def __init__(self):
        self.users = []
        self.flights = []
        self.routes = []
        self.tickets = []
        self.aircrafts = []
        self.current_user = None

    def add_user(self,user):
        self.users.append(user)

    def add_flight(self,flight):
        self.flights.append(flight)

    def add_aircraft(self,aircraft):
        self.aircrafts.append(aircraft)

    def add_route(self,route):
        self.routes.append(route)

    def search_flights(self,origin,destination,date):
        matching_flights = []
        for flight in self.flights:
            if (flight.origin.lower() == origin.lower() and
                flight.destination.lower() == destination.lower() and 
                flight.departure_time.date() == date.date()):
                matching_flights.append(flight)
        return matching_flights

    def book_ticket(self,passenger,flight_id,seat_number = None):
        flight = next((f for f in self.flights if f.flight_id == flight_id),None)
        if not flight:
            return None,"Flight not found"
        
        success,message = flight.add_passenger(passenger,seat_number)
        if not success:
            return None, message
        
        if not seat_number:
            seat_number = next(seat for seat,p in flight.aircraft.seat_map.items() if p == passenger)

        ticket = Ticket(passenger, flight, seat_number)
        self.tickets.append(ticket)
        return ticket,"Booking confirmed"

    def cancel_ticket(self,ticket_id):
        ticket = next((t for t in self.tickets if t.ticket_id == ticket_id),None)
        if not ticket:
            return False, "Ticket not found"
        
        return ticket.cancel_ticket()

    def generate_reports(self):
        return {
            "total_flights": len(self.flights),
            "total_passengers": sum(len(f.passenger_manifefst) for f in self.flights),
            "revenue": len(self.tickets) *200, #Assuming $200 per ticket
            "most_popular_route": max(
                [(r, sum(1 for f in self.flights if f.origin == r.origin and f.destination == r.destnation))
                 for r in self.routes], key = lambda x: x[1])[0] if self.routed else None
        }
    
def display_menu(role):
    menus ={
        "passenger":[
            "1. Search Flights",
            "2. Book Ticket",
            "3. Cancel Ticket",
            "4. View My Bookings",
            "5. Logout"
        ],
        "check-in agent":[
            "1. Check Passengere In",
            "2. View Flight Manifest",
            "3. Update Flight",
            "4. Logout"
        ]
        ,
        "admin":[
            "1. Add Flight",
            "2. Add Aircraft",
            "3. View All Tickets",
            "4. Generate Reports",
            "5. Logout"
        ]
    }
    return menus.get(role.lower(),[])

