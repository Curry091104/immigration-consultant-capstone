# Canadian Immigration Consultant Chatbot 🍁🤖

## Table of Contents
- [Project Description](#project-description)
- [Installation](#installation)
- [Usage](#usage)
- [Contributors](#contributors)
- [License](#license)


### Project Description

> Pend.

### Installation
<b><i>1. Clone the repository: </i></b>

```
git clone https://github.com/Curry091104/immigration-consultant-capstone.git
```

<b><i>2. Install dependencies: </i></b>

> ** Note **
> - Python version must be 3.11 (if your Python version is 3.12, please downgrade or create a new environment in Anaconda with Python 3.11. Check this [link](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html) for creating an environment with a specific version of Python).
> - It's recommended to create separate virtual environment folders for both the frontend and backend to prevent dependency conflicts.
> - To leverage GPU, after running ```pip install -r requirements.txt```, please run a command to reinstall PyTorch. Check this [link](https://pytorch.org/get-started/locally/) for the installation command.

Frontend
```
cd frontend
pip install -r requirements.txt
```

Backend
```
cd backend
pip install -r requirements.txt
```

### Usage
To run the project, use the following command: </br></br>

> ** Note **
> - Ensure that your environment is activated before running the command.
> - Verify that you have a .env file with all the required keys.


Frontend
```
cd frontend
streamlit run Home.py
```

Backend
```
cd backend
uvicorn main:app --reload
```

### Contributors
- Tuong Nguyen Pham - [@Curry091104](https://github.com/Curry091104)
- Ngoc Quynh Nhu Nguyen - [@NhuNhuNguyen](https://github.com/NhuNhuNguyen)
- Kwok Wing Tang - [@Patrickccca](https://github.com/Patrickccca)
- Joan Suaverdez - [@jsuaverd](https://github.com/jsuaverd)
- Huaye Zhan - [@howardzhan12](https://github.com/howardzhan12)
- Dongheun Yang - [@DongheunDanielYang](https://github.com/DongheunDanielYang)

### License
This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](LICENSE)
