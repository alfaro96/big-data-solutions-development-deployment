# Big Data solutions: Development and deployment

This repository provides code examples and reference implementations for the development and deployment of Big Data solutions.

It leverages tools for large-scale data processing, experiment tracking, model management, and reproducible machine learning workflows.

---

## Repository structure

* `.gitignore`: Ignore rules
* `environment.yml`: `Conda`-based environment definition
* `LICENSE`: License information for the repository  
* `README.md`: Project documentation
* `requirements.txt`: Dependencies for installation with `pip` or other package managers 

---

## Environment setup

This repository provides an [`environment.yml`](environment.yml) file, typically used for installing environments in conda-based package managers such as `conda`, `mamba`, or `micromamba`.

If you prefer to use another package manager such as `venv`, the required dependencies are also listed in [`requirements.txt`](requirements.txt).  

Please refer to the installation instructions of the corresponding package manager to learn how to create and activate environments, and how to install the listed dependencies.

---

## Usage

### Launch `mlflow` user interface

```bash
mlflow ui --port 5000
```

Then open your browser at `http://127.0.0.1:5000`

This interface allows you to explore and compare experiment runs, metrics, parameters, and artifacts.

### Launch `mlflow` tracking server

If you would like to use a more flexible setup instead of the simple user interface, you can run a managed instance of the `mlflow` tracking server:

```bash
mlflow server --host 127.0.0.1 --port 8080
```

This starts a dedicated tracking server at `http://127.0.0.1:8080`.

Make sure to keep the command prompt open while the server is running, as closing it will shut it down.

---

## Tech stack

This project uses the following core technologies:

* `pyspark`: Distributed data processing and machine learning pipelines
* `mlflow`: Experiment tracking, model management, reproducibility
* `jupyterlab`: Interactive exploration and prototyping
* `pyarrow`: Columnar data format
* `great-expectations`: Data validation and quality checks

---

## Notes

* The directory `mlruns/` and `mlartifacts/` are ignored by `git` via `.gitignore`.

* Runs executed locally will only appear in your machine; they are not pushed.

* The environment can be extended with additional packages as the project evolves.

---

## License

This repository is shared for educational and reference purposes. You are free to use and adapt the code for your own projects.
