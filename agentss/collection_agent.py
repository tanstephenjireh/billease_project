from agents import function_tool
from datetime import datetime
from zoneinfo import ZoneInfo
from agents import Agent 

def check_ptp_date(ptp_input, value=False):
    # Use Philippine timezone (PHT)
    pht = ZoneInfo("Asia/Manila")
    today = datetime.now(pht).date()
    current_year = today.year

    # Normalize and clean input
    ptp_input = ptp_input.strip()

    try:
        # Try with full format (e.g., April 15, 2025)
        ptp_date = datetime.strptime(ptp_input, '%B %d, %Y').date()
    except ValueError:
        try:
            # Try with no year (e.g., April 15), assume current year
            ptp_date = datetime.strptime(f"{ptp_input}, {current_year}", '%B %d, %Y').date()
        except ValueError:
            return "Invalid date format. Please use 'April 15' or 'April 15, 2025'."

    # Compare date difference
    if value == True:
        return (ptp_date - today).days
    elif (ptp_date - today).days > 15:
        return "Please advise the customer to move the PTP date to an earlier date."
    else:
        return "PTP date is acceptable."
    

def get_customer_info(customers, target_name):
    for customer in customers:
        if customer["name"].lower() == target_name.lower():
            # Extract and clean the amount
            amount_str = customer["Outstanding amount"]
            # Remove commas and non-digit characters (like ' pesos')
            amount_int = int(''.join(filter(str.isdigit, amount_str)))
            
            # Get due date as is (or you can parse it into a date if needed)
            due_date = customer["Due Date"]
            
            return {
                "Outstanding Amount": amount_int,
                "Due Date": due_date
            }
    
    return "Customer not found."


@function_tool
def collect_ptp(name: str, ptp_date: str):
    """This is responsible for collecting information about a customer for
    Promise to Pay (PTP) purposes:
    name - name of the customer
    ptp_date - the date the customer intend to make payment (PTP date)
    """

    customers_information = [
        {
            "name": "kim",
            "Outstanding amount": "1,000 pesos",
            "Due Date": "April 1, 2025"
        },
        {
            "name": "ivan",
            "Outstanding amount": "16,000 pesos",
            "Due Date": "December 1, 2024"
        }
    ]

    users = [i['name'] for i in customers_information]

    check_date_validity = check_ptp_date(ptp_date)

    if name.lower() not in users:
        return "Sorry, customer not found"

    elif check_date_validity != "PTP date is acceptable.":
        return check_date_validity
    else:
        date_difference = check_ptp_date(ptp_date, value=True)
        if name.lower() == "kim":
            cust_info = get_customer_info(customers_information, name.lower())
            outstanding_amount = cust_info["Outstanding Amount"]
            due_date = cust_info["Due Date"]

            total_amount = outstanding_amount + (date_difference)*20

            return f"The calculated total amount for {name} is {total_amount} due on {due_date}"

        elif name.lower() == "ivan":
            cust_info = get_customer_info(customers_information, name.lower())
            outstanding_amount = cust_info["Outstanding Amount"]
            due_date = cust_info["Due Date"]

            total_amount = outstanding_amount + (date_difference)*20

            return f"The calculated total amount for {name} is {total_amount} due on {due_date}"
        

collection_instruction = """You're a collection agent from the BillEase company. Remember to always
use the provided tools whenever possible. Do not rely on your own knowledge too much and instead
use your tools to help you answer queries. Answer in a fun tone and engaging for the customer.

You will be responsible to collect the necessary information from the customer if a customer wants to make a Promise to Pay (PTP).
Follow this flow in collecting:

1. Always ask first the name of the customer
2. Then ask the customer for their PTP date (the date they intend to make payment)
"""


collection_agent = Agent(
    name="Collection Agent",
    handoff_description="Specialist agent for assisting customer for Promise to Pay (PTP)",
    instructions=collection_instruction,
    model="gpt-4o-mini",
    tools=[collect_ptp]  # note that we expect a list of tools
)