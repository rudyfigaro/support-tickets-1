import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Show app title and description.
st.set_page_config(page_title="HatElectric Support tickets", page_icon="🎫")
st.title("🎫 HatElectric Support tickets")
st.write(
    """
    Create a ticket, edit existing tickets, and view some statistics.
    """
)

# Show a section to add a new ticket.
st.header("Add a ticket")

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_ticket_form"):
    issue = st.text_area("Describe the issue")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    submitted = st.form_submit_button("Submit")

import streamlit as st
import pandas as pd
import datetime
import pytz

eastern = pytz.timezone("America/New_York")

if submitted:
    # Get the most recent ticket number
    if "df" in st.session_state and not st.session_state.df.empty:
        recent_ticket_number = int(max(st.session_state.df["ID"]).split("-")[1])
    else:
        recent_ticket_number = 0  # Start from 0 if no tickets exist yet

    # → e.g., 04-08-2025 02:15 PM
    today = datetime.datetime.now(eastern).strftime("%m-%d-%Y %I:%M %p")
    # → e.g., 04-08-2025 02:15 PM

    # Create new ticket
    new_ticket = pd.DataFrame(
        [
            {
                "ID": f"HATEL-{recent_ticket_number + 1}",
                "Issue": issue,
                "Status": "Open",
                "Priority": priority,
                "Date Submitted": today,
            }
        ]
    )

    # Update session state
    if "df" not in st.session_state or st.session_state.df.empty:
        st.session_state.df = new_ticket
    else:
        st.session_state.df = pd.concat([new_ticket, st.session_state.df], ignore_index=True)

    # Show success message
    st.success("Ticket submitted! Here are the ticket details:")
    st.dataframe(new_ticket, use_container_width=True, hide_index=True)


# Only show the existing tickets and stats if a dataframe exists
if "df" in st.session_state and not st.session_state.df.empty:
    # Show section to view and edit existing tickets in a table.
    st.header("Existing tickets")
    st.write(f"Number of tickets: `{len(st.session_state.df)}`")

    st.info(
        "You can edit the tickets by double clicking on a cell. Note how the plots below "
        "update automatically! You can also sort the table by clicking on the column headers.",
        icon="✍️",
    )

    # Editable data table
    edited_df = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                help="Ticket status",
                options=["Open", "In Progress", "Closed"],
                required=True,
            ),
            "Priority": st.column_config.SelectboxColumn(
                "Priority",
                help="Priority",
                options=["High", "Medium", "Low"],
                required=True,
            ),
        },
        disabled=["ID", "Date Submitted"],  # Disable editing certain fields
    )

    # Show ticket stats
    st.header("Statistics")

    # Compute statistics
    num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Open"])
    prev_open_tickets = st.session_state.get("prev_open_tickets", 0)
    st.session_state.prev_open_tickets = num_open_tickets

    # Assume these columns exist; if not, default to 0
    avg_first_response_time = (
        st.session_state.df["First Response Time"].mean()
        if "First Response Time" in st.session_state.df.columns else 0.0
    )
    avg_resolution_time = (
        st.session_state.df["Resolution Time"].mean()
        if "Resolution Time" in st.session_state.df.columns else 0.0
    )

    # Show metrics
    col1, col2, col3 = st.columns(3)
    col1.metric(
        label="Number of open tickets",
        value=num_open_tickets,
        delta=num_open_tickets - prev_open_tickets
    )
    col2.metric(
        label="First response time (hours)",
        value=round(avg_first_response_time, 1),
        delta=None
    )
    col3.metric(
        label="Average resolution time (hours)",
        value=round(avg_resolution_time, 1),
        delta=None
    )

    # Altair charts
    st.write("")
    st.write("##### Ticket status per month")
    status_plot = (
        alt.Chart(edited_df)
        .mark_bar()
        .encode(
            x="month(Date Submitted):O",
            y="count():Q",
            xOffset="Status:N",
            color="Status:N",
        )
        .configure_legend(
            orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
        )
    )
    st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

    st.write("##### Current ticket priorities")
    priority_plot = (
        alt.Chart(edited_df)
        .mark_arc()
        .encode(theta="count():Q", color="Priority:N")
        .properties(height=300)
        .configure_legend(
            orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
        )
    )
    st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")

else:
    st.info("No tickets have been submitted yet. Submit a ticket to get started.", icon="ℹ️")
