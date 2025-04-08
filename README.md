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

> - Python version must be 3.11.
> - To prevent dependency conflicts, it's recommended that separate virtual environment folders for both the front end and back end be created.
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

> - Ensure that your environment is activated before running the command.
> - Verify that you have a .env file with all required keys.
> - Run the backend (server) first and let it finish loading, then run the frontend (client).

Backend
```
cd backend
uvicorn main:app
```
Frontend
```
cd frontend
streamlit run Home.py
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
