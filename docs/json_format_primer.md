# JSON config file

JavaScript Object Notation (JSON) is a popular data format that is easy for humans and computers to read and write. It has become the most popular way for applications and APIs to exchange data. JSON is also very easy to use with python (programming language) lists and dictionaries, which makes it perfect for storing information in python based applications.

The `.json` format is a plain text file that has a hierarchical format, and can store text and numerical values (among others) in key-value pairs.

**Example 1:** Curly braces `{ }` hold objects in key-value pairs

```bash
{ "gp_practice_name": "Whinfield Medical Practice" }
```

Values can also be stored in arrays (lists), which is the main benefit over `.csv` and other tabular formats that only store one value in each cell of the table.

**Example 2:** Square brackets `[ ]` hold arrays

```bash
{"list_of_gp_practices": ["A83005: Whinfield Medical Practice", "A83013: Neasham Road Surgery", "A83034: Blacketts Medical Practice"]}
```

The example below is a session state file from the AIF tool that shows that the application has saved two groups (‘Group 1’ and ‘Group 2’) and a list of those groups (called ‘group_list’). Within each group, the JSON stores both a list (array) of which GP practices are in that group and the associated ICB from which those GPs were selected. This list of groups is there to keep track of how many groups have been saved and make looping through them easier.

**Example 3:** A complete `.json` file

```bash
{
    "Group 1": {
        "gps": [
            "A83005: Whinfield Medical Practice",
            "A83013: Neasham Road Surgery",
            "A83034: Blacketts Medical Practice"
        ],
        "icb": "Cumbria and North East"
    },
    "Group 2": {
        "gps": [
            "A83013: Neasham Road Surgery",
            "A83034: Blacketts Medical Practice"
        ],
        "icb": "Cumbria and North East"
    },
    "group_list": [
        "Group 1",
        "Group 2"
    ]
}
```

`session_state_20211215.json`
