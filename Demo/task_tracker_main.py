import sys
from task_tracker import Task,ProjectManagerSystem,TaskBoard,display_menu

def main():
    system = ProjectManagerSystem()

    admin, _ = system.create_user({
        "name": "System Admin",
        "email": "admin@company.com",
        "role": "admin"
    })

    while True:
        if not system.current_user:
            print("\nProject Management System")
            print("1. Login")
            print("2. Exit")
            choice = input("Enter choice: ")

            if choice == "1":
                email = input("Email: ")
                _, message = system.authenticate(email)
                print(message)
            elif choice == "2":
                sys.exit()
            else:
                print("Invalid choice")
            continue

        print(f"\n{system.current_user.role.upper()} DASHBOARD")
        for option in display_menu(system.current_user.role):
            print(option)

        choice = input("Enter choice: ")

        if system.current_user.role == "admin":
            if choice == "1":  
                user_data = {
                    "name": input("Full name: "),
                    "email": input("Email: "),
                    "role": input("Role (admin/manager/developer): ")
                }
                user, message = system.create_user(user_data, system.current_user)
                print(message)

            elif choice == "2":  
                project_data = {
                    "title": input("Project title: ")
                }
                project, message = system.create_project(project_data, system.current_user)
                print(message)

            elif choice == "3":  
                for project in system.projects.values():
                    print(f"{project.project_id}: {project.title}")

            elif choice == "4":  
                project_id = input("Project ID: ")
                project = system.projects.get(project_id)
                if project:
                    print(project)
                    print("\nMembers:")
                    for member in project.members:
                        print(f"- {member.name} ({member.role})")
                else:
                    print("Project not found")

            elif choice == "5":  
                print("\nSYSTEM REPORT")
                print(f"Total users: {len(system.users)}")
                print(f"Total projects: {len(system.projects)}")
                print("\nProjects:")
                for project in system.projects.values():
                    print(f"- {project.title}: {project.get_progress():.1f}% complete")

            elif choice == "6":  
                system.current_user = None

            else:
                print("Invalid choice")

        elif system.current_user.role == "manager":
            if choice == "1":  
                project_id = input("Project ID: ")
                project = system.projects.get(project_id)
                if project:
                    title = input("Task title: ")
                    task, message = project.add_task(title, system.current_user)
                    print(message)
                else:
                    print("Project not found")

            elif choice == "2":  
                project_id = input("Project ID: ")
                project = system.projects.get(project_id)
                if project:
                    print("\nAvailable Tasks:")
                    for task_id, task in project.tasks.items():
                        print(f"{task_id}: {task.title}")

                    task_id = input("Task ID to assign: ")
                    task = project.tasks.get(task_id)
                    if task:
                        print("\nAvailable Team Members:")
                        for member in project.members:
                            print(f"{member.user_id}: {member.name}")

                        user_id = input("Assign to user ID: ")
                        user = system.users.get(user_id)
                        if user and user in project.members:
                            task.assigned_to = user
                            print(f"Task assigned to {user.name}")
                        else:
                            print("Invalid user selection")
                    else:
                        print("Task not found")
                else:
                    print("Project not found")

            elif choice == "3":  
                project_id = input("Project ID: ")
                project = system.projects.get(project_id)
                if project:
                    print("\nAvailable Users:")
                    for user in system.users.values():
                        if user not in project.members:
                            print(f"{user.user_id}: {user.name}")

                    user_id = input("User ID to add: ")
                    user = system.users.get(user_id)
                    if user:
                        success, message = project.assign_user(user, system.current_user)
                        print(message)
                    else:
                        print("User not found")
                else:
                    print("Project not found")

            elif choice == "4":  
                project_id = input("Project ID: ")
                project = system.projects.get(project_id)
                if project:
                    print(f"\nProject Progress: {project.get_progress():.1f}%")
                    board = TaskBoard(project)
                    report = board.generate_report()
                    print(f"Total tasks: {report['total_tasks']}")
                    print(f"Time logged: {report['total_time_logged']} hours")
                else:
                    print("Project not found")

            elif choice == "5":  
                project_id = input("Project ID: ")
                project = system.projects.get(project_id)
                if project:
                    board = TaskBoard(project)
                    groups = board.group_tasks_by_status()
                    print("\nTASK BOARD")
                    for status, tasks in groups.items():
                        print(f"\n{status} ({len(tasks)}):")
                        for task in tasks:
                            print(f"- {task.title} (Assigned to: {task.assigned_to.name if task.assigned_to else 'Unassigned'})")
                else:
                    print("Project not found")

            elif choice == "6": 
                system.current_user = None

            else:
                print("Invalid choice")

        elif system.current_user.role == "developer":
            if choice == "1":  
                print("\nYOUR TASKS:")
                for project in system.projects.values():
                    if system.current_user in project.members:
                        tasks = [t for t in project.tasks.values() if t.assigned_to == system.current_user]
                        if tasks:
                            print(f"\nProject: {project.title}")
                            for task in tasks:
                                print(f"- {task.task_id}: {task.title} ({task.status})")

            elif choice == "2": 
                task_id = input("Task ID: ")
                for project in system.projects.values():
                    if task_id in project.tasks:
                        task = project.tasks[task_id]
                        print(f"\nCurrent status: {task.status}")
                        print("Available statuses:", ", ".join(Task.STATUSES))
                        new_status = input("New status: ")
                        success, message = task.update_status(new_status, system.current_user)
                        print(message)
                        break
                else:
                    print("Task not found")

            elif choice == "3":  
                task_id = input("Task ID: ")
                hours = input("Hours worked: ")
                for project in system.projects.values():
                    if task_id in project.tasks:
                        success, message = project.tasks[task_id].log_time(system.current_user, hours)
                        print(message)
                        break
                else:
                    print("Task not found")

            elif choice == "4":  
                task_id = input("Task ID: ")
                comment = input("Comment: ")
                for project in system.projects.values():
                    if task_id in project.tasks:
                        success, message = project.tasks[task_id].add_comment(system.current_user, comment)
                        print(message)
                        break
                else:
                    print("Task not found")

            elif choice == "5": 
                task_id = input("Task ID: ")
                for project in system.projects.values():
                    if task_id in project.tasks:
                        task = project.tasks[task_id]
                        print("\nTASK DETAILS")
                        print(task)
                        if task.comments:
                            print("\nCOMMENTS:")
                            for comment in task.comments:
                                print(comment)
                        break
                else:
                    print("Task not found")

            elif choice == "6":  
                system.current_user = None

            else:
                print("Invalid choice")

if __name__ == "__main__":
    main()