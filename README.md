# ICS Place Based Allocation Tool 

This project is a tool built in Python to assist Integrated Care Systems (ICSs) to perform need based allocation based on defined place. It uses the most recently produced GP Registered Practice Populations as well as the weighted populations calculated from the Allocation model for each of its components. More information on the Allocations process, as well as useful documentation can be found at https://www.england.nhs.uk/allocations/

The tool has been built using Streamlit, a Python app framework that can be used to create web apps. It can be installed by using the package manager pip. 

```bash
pip install streamlit
```

The tool is deployed from a public GitHub repository using Streamlit's cloud service. 

To run the tool locally, in the terminal, whilst in the directory containing the tool run 

```bash
streamlit run allocation_tool.py 
```

More information about Streamlit can be found from the following link: 
https://docs.streamlit.io/en/stable/

## Usage

Full instructions for using the tool can be found in the user guide. The tool allows 'place' to be defined in an ICS as a cluster of GP practices. This allows place to be flexibly defined, whether that is as GP practices in the same Primary Care Network (PCN), Local Authority or that feed into the same Secondary services for example, that is at the discretion of the ICS. Once GP practices have been allocated to place, the relative need indices can be calculated and the output can be downloaded as a CSV. The underlying data for the tool is pulled from the Excel workbook in the repository. When new allocations are calculated or updates are made to GP Practice populations, the tool can be updated by replacing this workbook with one containing the new data, ensuring to maintain the same file name.  

## Support 

Enquiries about the overall allocation process can be directed to: england.revenue-allocations@nhs.net


