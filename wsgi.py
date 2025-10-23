import pytest, sys, click
from flask.cli import AppGroup
from App.main import create_app
from App.database import db, get_migrate
from App.controllers.controllers import (
    authenticate, schedule_shift, view_roster, time_in, time_out, view_shift_report
)
from App.models.staff import Staff
from App.models.shift import Shift
from App.models.timeentry import TimeEntry
from App.controllers.controllers import change_password

app = create_app()
migrate = get_migrate(app)
rostering_cli = AppGroup('rostering')

"""
@rostering_cli.command("login")
@click.argument("username")
@click.argument("password")
def login_command(username, password):
    user = login(username, password)
    if user:
        print(f"Logged in as {user.username} ({user.role})")
    else:
        print("Login failed")
"""

@rostering_cli.command("view_roster")
@click.argument("username")
@click.argument("password")
def view_roster_command(username, password):
    user = authenticate(username, password)
    if not user:
        print("Invalid username or password.")
        return

    roster = view_roster(user)
    if not roster:
        return

    print("Roster:")
    for r in roster:
        print(f"Shift ID: {r['shift_id']}, Staff: {r['staff']}, Date: {r['date']}, Start: {r['start']}, End: {r['end']}")

@rostering_cli.command("schedule")
@click.argument("admin_username")
@click.argument("admin_password")
@click.argument("staff_username")
@click.argument("date")
@click.argument("start_time")
@click.argument("end_time")
def schedule_shift_command(admin_username, admin_password, staff_username, date, start_time, end_time):
    admin = authenticate(admin_username, admin_password)
    staff = Staff.query.filter_by(username=staff_username).first()
    if not admin or not staff:
        print("Admin login failed or staff not found.")
        return

    shift = schedule_shift(admin, staff, date, start_time, end_time)
    if shift:
        print(f"Shift scheduled: Staff={staff.username}, Date={shift.date}, Start={shift.start_time}, End={shift.end_time}")


@rostering_cli.command("time_in")
@click.argument("username")
@click.argument("password")
@click.argument("shift_id", type=int)
def time_in_command(username, password, shift_id):
    user = authenticate(username, password)
    if not user:
        print("Invalid username or password.")
        return

    entry = time_in(user, shift_id)
    if entry:
        print(f"Time in recorded: {entry.time_in}")

@rostering_cli.command("time_out")
@click.argument("username")
@click.argument("password")
@click.argument("shift_id", type=int)
def time_out_command(username, password, shift_id):
    user = authenticate(username, password)
    if not user:
        print("Invalid username or password.")
        return

    entry = time_out(user, shift_id)
    if entry:
        print(f"Time out recorded: {entry.time_out}")

@rostering_cli.command("view_report")
@click.argument("admin_username")
@click.argument("admin_password")
def view_report_command(admin_username, admin_password):
    admin = authenticate(admin_username, admin_password)
    if not admin:
        print("Invalid username or password.")
        return

    report=view_shift_report(admin)
    if not report:
        print("No shifts found.")
        return

    for r in report:
        print(f"Staff: {r['staff']}, Date: {r['date']}, Start: {r['start']}, End: {r['end']}")
        e = r['time_entry']
        print(f"Time In: {e['in']}, Time Out: {e['out']}")

@rostering_cli.command("add_staff")
@click.argument("admin_username")
@click.argument("admin_password")
@click.argument("new_username")
@click.argument("new_password")
def add_staff_command(admin_username, admin_password, new_username, new_password):
    admin = authenticate(admin_username, admin_password)
    if not admin or admin.role != "Admin":
        print("Only Admins can add staff.")
        return

    if Staff.query.filter_by(username=new_username).first():
        print("User already exists.")
        return

    staff = Staff(username=new_username, password=new_password, role="Staff")
    db.session.add(staff)
    db.session.commit()
    print(f"User {new_username} added successfully.")

@rostering_cli.command("change_password")
@click.argument("username")
@click.argument("old_password")
@click.argument("new_password")
def change_password_command(username, old_password, new_password):
    change_password(username,old_password,new_password)


app.cli.add_command(rostering_cli)

@app.cli.command("init")
def init():
    db.create_all()
    if not Staff.query.first():
        admin=Staff(username="admin1",password="adminpass",role="Admin")
        staff1=Staff(username="staff1",password="staffpass",role="Staff")
        db.session.add_all([admin, staff1])
        db.session.commit()
    print("Database initialized with default users")

'''
Testing Commands
'''

test_cli = AppGroup('test', help="test commands for all objects")

@test_cli.cli.command("staff", help="Run Staff tests")
def user_tests_command():
        sys.exit(pytest.main(["-k", "User"]))

@test_cli.cli.command("shift", help="Run Shift tests")
def user_tests_command():
        sys.exit(pytest.main(["-k", "User"]))
    
@test_cli.cli.command("timeentry", help="Run TimeEntry tests")
def user_tests_command():
        sys.exit(pytest.main(["-k", "User"]))

@test_cli.cli.command("user", help="Run User tests")
def user_tests_command():
        sys.exit(pytest.main(["-k", "User"]))

app.cli.add_command(test_cli) # adds group to cli
