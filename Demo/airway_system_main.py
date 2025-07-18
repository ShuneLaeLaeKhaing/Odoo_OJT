from datetime import datetime, timedelta
import sys
from airway_system import Aircraft,Route,Flight,Admin,Passenger,CheckInAgent,display_menu,ReservationSystem

def main():
    system = ReservationSystem()

    aircraft1 = Aircraft("AC-001", "Boeing 737", 150)
    aircraft2 = Aircraft("AC-002", "Airbus A320", 180)
    system.add_aircraft(aircraft1)
    system.add_aircraft(aircraft2)
    
    route1 = Route("R001", "JFK", "LAX", 3944)
    route2 = Route("R002", "LHR", "CDG", 344)
    system.add_route(route1)
    system.add_route(route2)
    
    flight1 = Flight("FL-001", "JFK", "LAX", datetime.now() + timedelta(days=1), aircraft1)
    flight2 = Flight("FL-002", "LHR", "CDG", datetime.now() + timedelta(days=2), aircraft2)
    system.add_flight(flight1)
    system.add_flight(flight2)
    
    admin = Admin("Admin User", "admin@airway.com", "P123456", "STAFF-001")
    system.add_user(admin)

    while True:
        if not system.current_user:
            print("\nWelcome to AirFlow - Airline Booking System")
            print("Choose your role:")
            print("1. Passenger")
            print("2. Check-In Agent")
            print("3. Admin")
            print("4. Exit")
            
            choice = input("Enter choice: ")

            if choice == "1":
                name = input("Name: ")
                email = input("Email: ")
                passport = input("Passport ID: ")
                passenger = Passenger(name, email, passport)
                system.current_user = passenger
                system.add_user(passenger)
                print(f"Welcome, {name}!")

            elif choice == "2":
                staff_id = input("Staff ID: ")
                user = next((u for u in system.users if isinstance(u,CheckInAgent) and u.staff_id == staff_id),None)
                if user:
                    system.current_user = user
                    print(f"Welcome, {user.name}!")
                else:
                    print("Staff not found")

            elif choice == "3":
                staff_id = input("Admin ID: ")
                user = next((u for u in system.users if isinstance(u,Admin) and u.staff_id == staff_id),None)
                if user:
                    system.current_user = user
                    print(f"Welcome,{user.name}!")
                else:
                    print("Admin not found")

            elif choice == "4":
                sys.exit()

            else:
                print("Invalid choice")
            continue

        role = system.current_user.role.lower() if hasattr(system.current_user, 'role') else "passenger"
        print(f"\n{role.upper()} MENU")
        
        for option in display_menu(role):
            print(option)
        
        choice = input("Enter choice: ")
        
        if role == "passenger":
            if choice == "1":  # Search Flights
                origin = input("From: ")
                destination = input("To: ")
                date_str = input("Date (YYYY-MM-DD): ")
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    flights = system.search_flights(origin, destination, date)
                    if flights:
                        print("\nAvailable Flights:")
                        for flight in flights:
                            print(flight)
                    else:
                        print("No flights found")
                except ValueError:
                    print("Invalid date format")
            
            elif choice == "2":  # Book Ticket
                flight_id = input("Flight ID: ")
                seat_pref = input("Seat preference (leave blank for auto-assign): ")
                ticket, message = system.book_ticket(system.current_user, flight_id, seat_pref or None)
                print(message)
                if ticket:
                    print("\nYour Ticket:")
                    print(ticket)
            
            elif choice == "3":  # Cancel Ticket
                ticket_id = input("Ticket ID: ")
                success, message = system.cancel_ticket(ticket_id)
                print(message)
            
            elif choice == "4":  # View Bookings
                my_tickets = [t for t in system.tickets if t.passenger == system.current_user]
                if my_tickets:
                    print("\nYour Bookings:")
                    for ticket in my_tickets:
                        print(ticket)
                        print("------")
                else:
                    print("No bookings found")
            
            elif choice == "5":  # Logout
                system.current_user = None
            
            else:
                print("Invalid choice")
        
        elif role == "check-in agent":
            if choice == "1":  # Check Passenger In
                flight_id = input("Flight ID: ")
                flight = next((f for f in system.flights if f.flight_id == flight_id), None)
                if not flight:
                    print("Flight not found")
                    continue
                
                passport = input("Passenger passport ID: ")
                passenger = next((p for p in flight.passenger_manifest if p.passport_id == passport), None)
                if passenger:
                    print(f"Passenger {passenger.name} checked in")
                else:
                    print("Passenger not found on this flight")
            
            elif choice == "2":  # View Manifest
                flight_id = input("Flight ID: ")
                flight = next((f for f in system.flights if f.flight_id == flight_id), None)
                if flight:
                    print(f"\nPassenger Manifest for Flight {flight_id}:")
                    for seat, passenger in flight.aircraft.seat_map.items():
                        if passenger:
                            print(f"Seat {seat}: {passenger.name}")
                else:
                    print("Flight not found")
            
            elif choice == "3":  # Update Flight Status
                flight_id = input("Flight ID: ")
                flight = next((f for f in system.flights if f.flight_id == flight_id), None)
                if flight:
                    print(f"Current status: {flight.status}")
                    print("Available statuses:", ", ".join(Flight.STATUSES))
                    new_status = input("New status: ")
                    if flight.update_status(new_status):
                        print("Status updated")
                    else:
                        print("Invalid status")
                else:
                    print("Flight not found")
            
            elif choice == "4":  # Logout
                system.current_user = None
            
            else:
                print("Invalid choice")
        
        elif role == "admin":
            if choice == "1":  # Add Flight
                flight_id = input("Flight ID: ")
                origin = input("Origin: ")
                destination = input("Destination: ")
                date_str = input("Departure date/time (YYYY-MM-DD HH:MM): ")
                
                print("Available Aircraft:")
                for aircraft in system.aircrafts:
                    print(aircraft)
                
                aircraft_id = input("Aircraft ID: ")
                aircraft = next((a for a in system.aircrafts if a.aircraft_id == aircraft_id), None)
                
                if aircraft:
                    try:
                        departure = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                        flight = Flight(flight_id, origin, destination, departure, aircraft)
                        system.add_flight(flight)
                        print("Flight added successfully")
                    except ValueError:
                        print("Invalid date format")
                else:
                    print("Aircraft not found")
            
            elif choice == "2":  # Add Aircraft
                aircraft_id = input("Aircraft ID: ")
                model = input("Model: ")
                seats = int(input("Total seats: "))
                aircraft = Aircraft(aircraft_id, model, seats)
                system.add_aircraft(aircraft)
                print("Aircraft added successfully")
            
            elif choice == "3":  # View All Tickets
                if system.tickets:
                    print("\nAll Tickets:")
                    for ticket in system.tickets:
                        print(ticket)
                        print("------")
                else:
                    print("No tickets issued yet")
            
            elif choice == "4":  # Generate Reports
                report = system.generate_reports()
                print("\nSYSTEM REPORT")
                print(f"Total flights: {report['total_flights']}")
                print(f"Total passengers: {report['total_passengers']}")
                print(f"Estimated revenue: ${report['revenue']}")
                if report['most_popular_route']:
                    print(f"Most popular route: {report['most_popular_route']}")
            
            elif choice == "5":  # Logout
                system.current_user = None
            
            else:
                print("Invalid choice")

if __name__ == "__main__":
    main()