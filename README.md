# Hermes v1.5.2

Hermes is a FastAPI powered employee management web application.  
It allows you to manage your employees, their roles, and their onboarding/offboarding status.
![Capture of Hermes](/static/img/capture.gif)

## Features

- Add, edit, and delete employees
- Assign roles to employees
- Onboard and Offboard employees
- View and search employee details and history
- Upload employee contracts
- Generate reports on employee data
- Create test admin account with unique employee checks and confirmation boxes
- Automated Slack and E-mail triggers with employee onboarding, updating or offboarding
- Security notification for access to privileges data
- API call for generating active employee lists
- Customise Hermes with your company's logo and color scheme

# Installation

You can install the [project locally](#local-installation), and run it on your own machine, or you could run it in a [docker container](#run-docker-image).

## Local installation

1. Clone the repository: `git clone https://github.com/DarthTigerson/Hermes.git`
2. Install the dependencies: `pip install -r requirements.txt`
3. Create a `.env` file and set the environment variables (see `.env.example` for an example)
4. Give executable permissions to the launcher script: `chmod +x run.sh`
5. Run the application: `./run.sh`

## Build Docker image

It is possible to build your own docker image from the `Dockerfile` in this repository.  
Although, the preferred way to do it is to pull a [prebuilt image](#run-prebuilt-image).   
This project creates a local database on your system. So in order to use this in a container,
you need to link an empty directory from your host system to the container.

1. Clone the repository: `git clone https://github.com/DarthTigerson/Hermes.git`
2. Build the image from the Dockerfile `docker build --tag <YOUR_TAG> .`
3. Create and run a container from the image:  
`docker run --mount type=bind,source=<DB_FILE_PATH>,target=/hermes/db -p 8000:8000 <YOUR_TAG>`  

[Learn more](https://docs.docker.com/engine/reference/commandline/run/) on running docker containers.

## Run prebuilt image

1. Pull the image from Dockerhub: `docker pull w3edd/hermes:latest`
2. Run the docker image and set the forwarding web port:  
`docker run --mount type=bind,source=<DB_FILE_PATH>,target=/hermes/db -p 8000:8000 w3edd/hermes:latest`  

[Learn more](https://docs.docker.com/engine/reference/commandline/run/) on running docker containers.

## Usage

> [!NOTE]  
> When not running on a container, on the first run, you need to create an admin user by running the `python startup.py` script.    
> The default username and password for the admin user is `hermes` and `hermes`, respectively.

1. Open your web browser and go to `http://localhost:8000`
2. Use the navigation menu to access the different features of the application
3. To add a new employee, click the "Add Employee" button and fill out the form. Click "Save" to add the employee.
4. To edit an existing employee, go to the employee details page and click the "Edit" button. Make the necessary changes and click "Save" to update the employee.
5. To delete an employee, go to the employee details page and click the "Delete" button. Confirm the deletion when prompted.
6. To assign a role to an employee, go to the employee details page and select a role from the dropdown menu. Click "Save" to assign the role.
7. To create a test admin account, click the "Create Test Admin" button and follow the prompts.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue on GitHub. If you want to contribute code, please fork the repository and create a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
