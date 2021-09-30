# ICS Place Based Allocation Tool 

This project is a tool built in Python to assist Integrated Care Systems (ICSs) to perform need based allocation based on defined place. It uses the most recently produced GP Registered Practice Populations as well as the weighted populations calculated from the Allocation model for each of its components. More information on the Allocations process, as well as useful documentation can be found at https://www.england.nhs.uk/allocations/

The tool has been built using Streamlit, a Python app framework that can be used to create web apps. It can be installed by using the package manager pip. 

```bash
pip install streamlit
```

The project virtual environment can be activated in bash using the following command

```bash
source venv/bin/activate 
```

To activate the virtual environment in Windows the following command can be used 

```shell
venv\Scripts\activate
```

To explicitly install all the prerequisite packages to run the tool's script, in the terminal run the following command:  
```shell
pip install -r requirements.txt
```
To run the tool locally, in the terminal, whilst in the directory containing the tool run 

```bash
streamlit run allocation_tool.py 
```

Streamlit will then render the tool and display it in your default web browser. When run in this way, any changes to the script in your editor will change the app running locally. 

More information about Streamlit can be found from the following link: 
https://docs.streamlit.io/en/stable/  

The .streamlit directory contains configuration settings that affect the appearance of the application when it is deployed. 

## Usage

The tool is deployed from a GitHub repository using Streamlit's sharing service. To make changes to the deployed app, push changes that have been made to the source code to the GitHub repository, these changes will then be reflected in the app.  
Full instructions for using the tool can be found in the user guide. The tool allows 'place' to be defined in an ICS as a cluster of GP practices. This allows place to be flexibly defined, whether that is as GP practices in the same Primary Care Network (PCN), Local Authority or that feed into the same Secondary services for example, that is at the discretion of the ICS. Once GP practices have been allocated to place, the relative need indices can be calculated and the output can be downloaded as a CSV. The underlying data for the tool is pulled from the Excel workbook in the repository, gp_practice_weighted_population.xlsx. When new allocations are calculated or updates are made to GP Practice populations, the tool can be updated by replacing this workbook with one containing the new data, ensuring to maintain the same file name. The tool is resilient to changes in rows in this spreadsheet but any changes to column names or column order from the previous version may lead to issues and this will have to be debugged. 

## Support 

Enquiries about the overall allocation process can be directed to: england.revenue-allocations@nhs.net

## Copyright and License

Unless otherwise specified, all content in this repository and any copies are subject to [Crown Copyright](http://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/copyright-and-re-use/crown-copyright/) under the [Open Government License v3](./LICENSE).

Any code is dual licensed under the MIT license and the [Open Government License v3](./LICENSE). 

Any new work added to this repository must conform to the conditions of these licenses. In particular this means that this project may not depend on GPL-licensed or AGPL-licensed libraries, as these would violate the terms of those libraries' licenses.****
