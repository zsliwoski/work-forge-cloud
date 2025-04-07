# Work-Forge Cloud 🌩️

This repository is a cloud-based component of the larger Work-Forge project. It integrates seamlessly with other repositories in the Work-Forge ecosystem to provide scalable and efficient cloud functionality. Additionally, it includes a **Sprint Checkpointing** feature to help teams track progress and milestones effectively.

[Frontend Repository](https://github.com/zsliwoski/work-forge-cloud)

## Features ✨

- **Serverless Architecture**: Built using serverless functions for efficient and cost-effective execution.
- **Cloud Scheduler**: Automates recurring tasks and background jobs.
- **PostgreSQL Database**: Connects to a PostgreSQL database for robust and reliable data storage.
- **Unit Testing**: Comprehensive unit tests ensure code quality and reliability.

## Technologies Used 🛠️

- **Python**: Core programming language for backend logic and serverless functions.
- **Terraform**: Infrastructure as Code (IaC) tool for managing and provisioning cloud resources.
- **Google Cloud Platform (GCP)**: Hosting and cloud services, including:
    - Cloud Functions
    - Cloud Scheduler
    - Cloud SQL (PostgreSQL)

## Getting Started 🚀

### Prerequisites ✅

- Python 3.x
- Terraform
- Google Cloud SDK
- PostgreSQL database

### Setup ⚙️

1. Clone the repository:
     ```bash
     git clone https://github.com/your-repo/work-forge-cloud.git
     cd work-forge-cloud
     ```

2. Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. Configure your Google Cloud project and set up Terraform:
     ```bash
     gcloud auth login
     terraform init
     terraform apply
     ```

5. Ensure you have a valid PostgreSQL database to connect to and update connection settings in the environment variables.

### Running Tests 🧪

Run unit tests to ensure everything is working as expected:
```bash
pytest
```

## Contributing 🤝

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License 📜

This project is licensed under the [MIT License](LICENSE).

## Contact 📧

For questions or support, please contact [zsliwoski@gmail.com].