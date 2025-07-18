from datetime import datetime
from abc import ABC, abstractmethod
import uuid

class User(ABC):
    def __init__(self,user_id,name,email,role):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role

    @abstractmethod
    def get_permission(self):
        pass

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.role}"

class AdminUser(User):
    def get_permission(self):
        return [
            "create_users",
            "delete_users",
            "create_projects",
            "delete_projects",
            "assign_managers",
            "view_all_tasks",
            "edit_all_tasks",
            "generate_reports"
        ]
    
class ManagerUser(User):
    def get_permission(self):
        return [
            "create_tasks",
            "assign_tasks",
            "view_project_tasks",
            "edit_project_tasks",
            "add_project_members"
        ]
        
class DeveloperUser(User):
    def get_permission(self):
        return [
            "view_assigned_tasks",
            "update_task_status",
            "log_time",
            "add_comments"
        ]

    
class Project:
    def __init__(self,project_id,title,manager):
        self.project_id = project_id
        self.title = title
        self.description = ""
        self.manager = manager
        self.members = [manager]
        self.tasks = {}
        self.created_at = datetime.now()

    def add_task(self,title,creator):
        if "create_tasks" not in creator.get_permission():
            return None, "Permission denied"
        
        task_id = f"TASK --{datetime.now().strftime('%Y%m%d%H%M%S')}"
        task = Task(task_id, title, self.project_id)
        self.tasks[task_id] = task
        return task, "Task created"

    def assign_user(self,user,assigner):
        if "add_project_members" not in assigner.get_permission():
            return False, "Permission denied"
        
        if user not in self.members:
            self.members.append(user)
            return True, "User added to project"
        return False, "User already in project"

    def get_progress(self):
        if not self.tasks:
            return 0.0
        
        completed = sum(1 for t in self.tasks.value() if t.status == "Completed")
        return (completed / len(self.tasks)) * 100
        
    def __str__(self):
        return (f"Project {self.project_id}: {self.title}\n"
                f"Manager: {self.manager.name}\n"
                f"Members: {len(self.members)} | Tasks: {len(self.tasks)}\n"
                f"Progress: {self.get_progress():.1f}%"
                )

class Task:
    STATUSES = ["Open","In Progress","Blocked","Completed"]
    PRIORITIES = ["Low","Medium","High"]

    def __init__(self,task_id,title,project_id):
        self.task_id = task_id
        self.title = title
        self.project_id = project_id
        self.status = "Open"
        self.priority = "Medium"
        self.assigned_to = None
        self.time_logged = 0.0
        self.comments = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def update_status(self,new_status,user):
        if new_status not in self.STATUSES:
            return False, "Invalid status"
        
        if "edit_all_tasks" in user.get_permission() or \
        ("update_task_status" in user.get_permission() and self.assigned_to == user):
            self.status = new_status
            self.updated_at = datetime.now()
            return True, "Status updated"
        return False, "Permission denied"

    def add_comment(self,user,content):
        if not content.strip():
            return False, "Comment cannot be empty"
        
        if "add_comments" in user.get_permission():
            self.comments.append(Comment(user,content))
            self.updated_at = datetime.now()
            return True, "Comment added"
        return False, "Permission denied"

    def log_time(self,user,hours):
        try:
            hours = float(hours)
            if hours <= 0:
                return False, "Hours must be positive"
        except ValueError:
            return False, "Invalid hours value"
        
        if "edit_all_tasks" in user.get_permission() or \
        ("log_time" in user.get_permission() and self.assigned_to == user):
            self.time_logged += hours
            self.updated_at = datetime.now()
            return True, "Time logged"
        return False, "Permission denied"
    
    def __str__(self):
        assigned = self.assigned_to.name if self.assigned_to else "Unassigned"
        return (
                f"Task {self.task_id}: {self.title}\n"
                f"Status: {self.status} | Priority: {self.priority}\n"
                f"Assigned to: {assigned} | Time logged: {self.time_logged}h\n"
                f"Created: {self.created_at.strftime('%Y-%m-%d')}"
                )

        
class Comment:
    def __init__(self,user,content):
        self.comment_id = str(uuid.uuid4())
        self.user = user
        self.content = content
        self.timestamp = datetime.now()

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.user.name}: {self.content}"

class TaskBoard:
    def __init__(self,project):
        self.project = project

    def group_tasks_by_status(self):
        groups = {status: [] for status in Task.STATUSES}
        for task in self.project.tasks.values():
            groups[task.status].append(task)
        return groups

    def filter_tasks_by_user(self,user):
        return [t for t in self.project.tasks.values() if t.assigned == user]

    def generate_report(self):
        status_groups = self.group_tasks_by_status()
        return {
            "project": self.project.title,
            "manager": self.project.manager.name,
            "total_tasks": len(self.project.tasks),
            "progress": f"{self.project.get_progress():.1f}%",
            "status_counts": {status: len(tasks) for status,tasks in status_groups.items()},
            "total_time_logged": sum(t.time_logged for t in self.project.tasks.values())
        }

class ProjectManagerSystem:
    def __init__(self):
        self.users = {}
        self.projects = {}
        self.current_user = None

    def authenticate(self,email):
        for user in self.users.values():
            if user.email.lower() == email.lower():
                self.current_user = user
                return user, "Login successful"
        return None, "User not found"
    
    def create_user(self,user_data,creator = None):
        if creator and "create_users" not in creator.get_permission():
            return None, "Permission denied"
        
        user_id = str(uuid.uuid4())
        role = user_data.get("role","developer").lower()

        if role == "admin":
            user = AdminUser(user_id, user_data["name"],user_data["email"],role)
        elif role == "manager":
            user = ManagerUser(user_id, user_data["name"],user_data["email"],role)
        elif role == "developer":
            user = DeveloperUser(user_id, user_data["name"],user_data["email"],role)
        else:
            return None, "Invalid role"
        
        self.users[user_id] = user
        return user, "User created"
    
    def create_project(self, project_data, creator):
        if "create_projects" not in creator.get_permission():
            return None, "Permission denied"
        
        project_id = f"PROJ--{datetime.now().strftime('%Y%m%d%H%M%S')}"
        project = Project(project_id, project_data["title"],creator)
        self.projects[project_id] = project
        return project, "Project created"
    
def display_menu(role):
    menus ={
        "admin":[
            "1. Create User",
            "2. Create Project",
            "3. List Projects",
            "4. View Project Details",
            "5. Generate System Report",
            "6. Logout"
        ],
        "manager": [
            "1. Create Task",
            "2. Assign Task",
            "3. Add Project Member",
            "4. View Project Progress",
            "5. View Task Board",
            "6. Logout"
        ],
        "developer": [
            "1. View My Tasks",
            "2. Update Task Status",
            "3. Log Time",
            "4. Add Comment",
            "5. View Task Details",
            "6. Logout"
        ]
    }
    return menus.get(role,[])
