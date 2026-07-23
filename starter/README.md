# Udatracker Starter Code

- When adding orders I added multiple ValueError checks with differing messages depending on the type of error. I then added a test for each of these errors, but needed to match the error message in the app.py routes to account for the different types of errors based on the messages.
- If I continued the project, instead of matching on error message for various ValueErrors, we could create custom exception as subclasses of ValueError for each type of error, and then match on the exception type instead of the message. This would be a more robust solution.
- Once I thought I was done, I tested adding orders, and realized that adding orders witha blank spaces would make it through the validation checks. I added some version of the following logical check `not isinstance(<field>, str) or not <field>.strip()` throughout my tests to test and catch fields that are strings with just blank spaces. By doing this approach, it short-circuits from left to right, so that if `<field>` was not a string, Python never evaluates `field.strip()`, otherwise it does, and catches blank spaces.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```
