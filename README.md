# ICB Place Based Allocation Tool

[![Python v3.8](https://img.shields.io/badge/python-v3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

This project is a tool built in Python to assist Integrated Care Boards (ICBs) to perform need based allocation based on defined place. It uses the most recently produced GP Registered Practice Populations as well as the weighted populations calculated from the Allocation model for each of its components. More information on the Allocations process, as well as useful documentation can be found at [https://www.england.nhs.uk/allocations/](https://www.england.nhs.uk/allocations/)

The tool allows a new 'place' to be defined in an ICB as a cluster of GP practices. This allows place to be flexibly defined, whether that is as GP practices in the same Primary Care Network (PCN), Local Authority, or that feed into the same Secondary services for example. That is at the discretion of the ICB. Once GP practices have been allocated to a place, the relative need indices can be calculated and the output can be downloaded as a CSV.

![ICB Place Based Allocation Tool](/docs/screenshot-min.png?raw=true "ICB Place Based Allocation Tool")

## Deployment (local)

The tool has been built using Streamlit, a Python app framework that can be used to create web apps. To deploy the streamlit app locally we advise using a virtual environment (venv for example) and following the instructions below:

The project virtual environment can be activated in bash using the following command

```bash
python3 -m venv <path to virtual env>
source <path to virtual env>/bin/activate
```

To activate the virtual environment in Windows the following command can be used

```shell
<path to virtual env>\Scripts\activate
```

To install all the prerequisite packages to run the tool, in the terminal run the following command:

```shell
pip install -r requirements.txt
```

To run the tool locally, open a terminal whilst in the directory containing the app and run

```bash
streamlit run dashboard.py
```

Streamlit will then render the tool and display it in your default web browser at

```bash
http://localhost:8501/
```

When run in this way, any changes to the script in your editor will change the app running locally.

More information about Streamlit can be found from the following link:
https://docs.streamlit.io/en/stable/

## Deployment (cloud)

The tool is deployed from the GitHub repository using Streamlit's sharing service. To make changes to the deployed app, push changes that have been made to the source code to the GitHub repository, these changes will then be reflected in the app. Full instructions for using the tool can be found in the user guide.

The .streamlit directory contains configuration settings that affect the appearance of the application when it is deployed.

## Support

For support with using the AIF Allocation tool, or enquiries about the overall allocation process can be directed to: [england.revenue-allocations@nhs.net](mailto:england.revenue-allocations@nhs.net)

## Copyright and License

Unless otherwise specified, all content in this repository and any copies are subject to [Crown Copyright](http://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/copyright-and-re-use/crown-copyright/), dual licensed under the [MIT License](./LICENSE) and the [Open Government License v3](./LICENSE).

Any new work added to this repository must conform to the conditions of these licenses. In particular this means that this project may not depend on GPL-licensed or AGPL-licensed libraries, as these would violate the terms of those libraries' licenses.
