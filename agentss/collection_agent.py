from agents import function_tool
from datetime import datetime
from zoneinfo import ZoneInfo
from agents import Agent
from openai import OpenAI
import streamlit as st

def check_ptp_date(ptp_input):
    # st.write("checking ptp...")
    pht = ZoneInfo("Asia/Manila")
    today = datetime.now(pht).date()

    client = OpenAI(
        api_key=st.secrets['OPENAI_API_KEY']
    )

    system_message = f"""The current date is {today}. Convert any date input format into natural language date into ISO format (YYYY-MM-DD).
    Always pertain to the preceeding future date.
    Only return the date format in the response. The current year is 2025. (e.g., "2025-mm-dd")
    """

    try:

        # Make the API call
        resp_date = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": ptp_input}
            ],
            temperature=0.0,  # Adjust creativity level (0.0 to 1.0)
            max_tokens=10,   # Limit response length
        )
        # st.write(resp_date.choices[0].message.content)
        ptp_date = datetime.strptime(resp_date.choices[0].message.content, "%Y-%m-%d").date()

        leeway = (ptp_date - today).days
        # st.write(ptp_date)
        # st.write(leeway)
        if leeway > 15:
            return "Please advise the customer to move the PTP date to an earlier date."
        else:
            return "PTP date is acceptable.", leeway
        

    except Exception as e:
         return f"Error generating response: {str(e)}"
    

def get_customer_info(customers, target_name):
    for customer in customers:
        if customer["name"].lower() == target_name.lower():
            amount_str = customer["Outstanding amount"]
            amount_int = int(''.join(filter(str.isdigit, amount_str)))
            
            due_date = customer["Due Date"]
            
            return {
                "Outstanding Amount": amount_int,
                "Due Date": due_date
            }
    
    return "Customer not found."


@function_tool
def collect_ptp(name: str, ptp_date: str):
    f"""This is responsible for collecting information about a customer for
    Promise to Pay (PTP) purposes:
    name - name of the customer
    ptp_date - the date the customer intend to make payment (PTP date)
    """
    # st.write("col_tool:", ptp_date)
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
    # st.write("col_tool:", ptp_date)

    users = [i['name'] for i in customers_information]

    check_date_validity = check_ptp_date(ptp_date)
    # st.write(check_date_validity)
    if name.lower() not in users:
        return "Sorry, customer not found"

    elif type(check_date_validity) == str:
        return check_date_validity
    elif type(check_date_validity) == tuple:
        date_difference = check_date_validity[-1]
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
    tools=[collect_ptp]  
)