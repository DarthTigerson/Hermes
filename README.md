# Hermes v1.2.8

Hermes is a FastAPI powered employee management web application. It allows you to manage your employees, their roles, and their onboarding/offboarding status.
![Screenshot of the Home page](/static/img/screenshot1.png)
![Screenshot of the Manage list](/static/img/screenshot2.png)
![Screenshot of the Admin page](/static/img/screenshot3.png)

## Features

- Add, edit, and delete employees
- Assign roles to employees
- Onboard and Offboard employees
- View and search employee details and history
- Generate reports on employee data
- Create test admin account with unique employee checks and confirmation boxes
- Automated Slack and E-mail triggers with employee onboarding, updating or offboarding
- Security notification for access to privilages data
- API call for generating active employee lists

## Installation

1. Clone the repository: `git clone https://github.com/DarthTigerson/Hermes.git`
2. Install the dependencies: `pip install -r requirements.txt`
3. Create a `.env` file and set the environment variables (see `.env.example` for an example)
4. Run the application: `uvicorn main:app --reload`

## Usage

1. Open your web browser and go to `http://localhost:8000`
2. Use the navigation menu to access the different features of the application
3. To add a new employee, click the "Add Employee" button and fill out the form. Click "Save" to add the employee.
4. To edit an existing employee, go to the employee details page and click the "Edit" button. Make the necessary changes and click "Save" to update the employee.
5. To delete an employee, go to the employee details page and click the "Delete" button. Confirm the deletion when prompted.
6. To assign a role to an employee, go to the employee details page and select a role from the dropdown menu. Click "Save" to assign the role.
7. To create a test admin account, click the "Create Test Admin" button and follow the prompts.

**Note:** On the first run, you need to create an admin user by running the `startup.py` script. Uncomment the bottom lines of the file and run it with `python startup.py`. The default username and password for the admin user is `hermes` and `hermes`, respectively.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue on GitHub. If you want to contribute code, please fork the repository and create a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
