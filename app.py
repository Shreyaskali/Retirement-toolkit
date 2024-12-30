import streamlit as st
import pandas as pd
import numpy_financial as npf
import plotly_express as px
# App title
st.title("Retirement Toolkit")

# Sidebar for all inputs
st.sidebar.header("User Inputs")

# General inputs
current_age = st.sidebar.number_input("Your Current Age", min_value=18, max_value=70, value=30, step=1)
retirement_age = st.sidebar.number_input("Retirement Age / Target FIRE Age", min_value=current_age+1, max_value=80, value=max(50, current_age+1), step=1)
current_investments = st.sidebar.number_input("Current Investments", min_value=0, value=0, step=50000)
# monthly_savings = st.sidebar.number_input("Your Monthly Savings / Investments (₹)", min_value=0, value=10000, step=1000)
monthly_savings = 0
current_monthly_expenses = st.sidebar.number_input("Your Current Monthly Expenses (₹)", min_value=0, value=50000, step=5000)
mode = st.sidebar.selectbox("Do You want your investments back?", options=["Yes", "No"])

expected_return = st.sidebar.slider("Expected Annual Return on Investments (%)", min_value=3.0, max_value=25.0, value=12.0, step=0.5)
inflation_rate = st.sidebar.slider("Expected Annual Inflation Rate (%)", min_value=0.0, max_value=12.0, value=8.0, step=0.5)

safe_withdrawal_rate = 4
expected_mortality = 80
years_to_fire = retirement_age - current_age + 1

def SWP(corpus, withdrawal_amount, rate, retirement_age, mortality):
    corpus_left = []
    retirement_period = mortality - retirement_age
    for i in range(retirement_period):
        corpus -= 12 * withdrawal_amount
        corpus = corpus * (1 + rate/100)
        corpus_left.append(corpus)
    left_over = corpus
    return left_over, corpus_left

# Calculate values common to both planners
annual_savings = monthly_savings * 12
rate_of_return = expected_return / 100
inflation_adjusted_return = (1 + rate_of_return) / (1 + inflation_rate / 100) - 1
annual_expenses = current_monthly_expenses * 12

monthly_expenses = current_monthly_expenses * (1 + inflation_rate/100) ** (years_to_fire)

# fire_corpus = annual_expenses / (safe_withdrawal_rate / 100)

fire_corpus = 0
left_over, SWP_corpus = SWP(fire_corpus, monthly_expenses, 8, retirement_age, expected_mortality)

threshold = 0
if mode == "Yes":
    threshold = current_investments
else:
    threshold = 0

while left_over < threshold:
    left_over, SWP_corpus = SWP(fire_corpus, monthly_expenses, 8, retirement_age, expected_mortality)
    fire_corpus += 100000
# fire_corpus = future_value(fire_corpus_today, inflation_rate/100, n)

# Retirement Planner Calculation
# future_retirement_corpus = npf.fv(rate_of_return, retirement_age-current_age+1, -annual_savings, -current_investments)
# st.write(future_retirement_corpus/100000)

# FIRE Progress Calculation
fire_progress = [npf.fv(pv=-current_investments+annual_savings, pmt=-annual_savings, rate=rate_of_return, nper=i) for i in range(years_to_fire)]
# st.write(len(fire_progress)) 
while fire_progress[-1] < fire_corpus:
    monthly_savings += 1000
    fire_progress = [npf.fv(pv=-current_investments+annual_savings, pmt=-monthly_savings*12, rate=rate_of_return, nper=i) for i in range(years_to_fire)]

# Tab-based layout for Retirement Planner and FIRE Number Calculator
tab1, tab2, tab3 = st.tabs(["Retirement Planner", "FIRE Number Calculator", "Simulation"])

# Tab 1: Retirement Planner
# Tab 1: Retirement Planner
with tab1:
    if monthly_savings == 0:
        st.success(f"Your Investments are in Place! You can retire safely at {retirement_age}!")
    else:
        st.warning(f"You Retirement Plans can be met with monthly SIP of ₹{monthly_savings}")
    c1, c2 = st.columns([3, 4])
    with c2:
        # Pie Chart: Contributions vs. Returns Breakdown
        total_contributions = monthly_savings * 12 * years_to_fire
        total_returns = fire_progress[-1] - total_contributions - current_investments
        breakdown = pd.DataFrame({
            "Source": ["Contributions", "Returns", "Initial Investments"],
            "Amount": [total_contributions, total_returns, current_investments]
        })
        st.plotly_chart(
            px.pie(breakdown, values="Amount", names="Source", title="Retirement Corpus Breakdown"),
            use_container_width=True
        )

    with c1:
        # Metrics for quick insights
        st.metric("Estimated Corpus at Retirement", f"₹{fire_progress[-1]:,.2f}")
        st.metric("Monthly Savings Required", f"₹{monthly_savings}")
        st.metric("Remaining Years to Retirement", f"{years_to_fire} years")
        st.metric("Retirement Period", f"{expected_mortality - retirement_age} Years")

    years = list(range(current_age, retirement_age+1))

    st.info(f"Your inflation adjusted monthly expenses of ₹{round(monthly_expenses)} post retirement are all covered!")
             


    # Graph 3: Inflation Impact on Purchasing Power
    st.subheader("Inflation-Adjusted Corpus vs. Expenses")
    inflation_adjusted_corpus = [
        corpus / (1 + inflation_rate / 100) ** i for i, corpus in enumerate(fire_progress)
    ]
    projected_expenses = [annual_expenses * (1 + inflation_rate / 100) ** i for i in range(len(years))]
    if len(years) == len(inflation_adjusted_corpus) == len(projected_expenses):
        df_inflation_impact = pd.DataFrame({
            "Year": years,
            "Inflation-Adjusted Corpus (₹)": inflation_adjusted_corpus,
            "Projected Annual Expenses (₹)": projected_expenses
        })
        st.line_chart(df_inflation_impact.set_index("Year"), use_container_width=True)
    else:
        st.error("Mismatch in lengths for inflation-adjusted corpus and expenses.")


# Tab 2: FIRE Number Calculator
with tab2:
    st.header("FIRE Number Calculator")
    
    # Metrics
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Your FIRE Number", f"₹{fire_corpus / 10000000:,.2f} Cr." if fire_corpus > 10000000 else f"₹{fire_corpus:,.2f}")
        # st.metric("Annual Investment Needed", f"₹{fire_corpus / (years_to_fire * 100000):,.2f} L" if years_to_fire > 0 else "N/A")
    with col2:
        # st.metric("Left Over Amount", f"₹{left_over:,.2f}")
        st.metric("Monthly Investments Required", f"₹{monthly_savings}")

    #### SAFE WITHDRAWAL RATE ######
    # st.metric("Safe Withdrawal Rate", f"{monthly_expenses * 100 / fire_corpus:,.2f}%")
    # Combined DataFrame for Pre- and Post-Retirement Phases

    # Generate inflation-adjusted monthly withdrawal amounts for withdrawal phase
    inflation_adjusted_withdrawal = [monthly_expenses * (1 + inflation_rate / 100) ** i 
                                    for i in range(expected_mortality - retirement_age)]

    # Updated DataFrame with Monthly Withdrawal (Inflation Adjusted)
    df_combined = pd.concat([
        pd.DataFrame({
            "Year": list(range(current_age, years_to_fire + current_age)),
            "Phase": "Accumulation",
            "Corpus (₹)": fire_progress,
            "Monthly Withdrawal (₹)": [0] * years_to_fire,  # No withdrawal during accumulation
            "Yearly SIP Contribution (₹)": [monthly_savings * 12] * years_to_fire,
        }),
        pd.DataFrame({
            "Year": list(range(retirement_age, expected_mortality)),
            "Phase": "Withdrawal",
            "Corpus (₹)": SWP_corpus,
            "Monthly Withdrawal (₹)": inflation_adjusted_withdrawal,  # Inflation-adjusted withdrawal during retirement
            "Yearly SIP Contribution (₹)": [0] * (expected_mortality - retirement_age),
        })
    ], ignore_index=True)

    # Convert columns to proper types and format
    df_combined["Corpus (₹)"] = df_combined["Corpus (₹)"].fillna(0).astype(float)
    df_combined["Monthly Withdrawal (₹)"] = df_combined["Monthly Withdrawal (₹)"].astype(float)
    df_combined["Yearly SIP Contribution (₹)"] = df_combined["Yearly SIP Contribution (₹)"].astype(float)


    # Combined Graph
    st.subheader("FIRE Corpus Growth (Accumulation + Withdrawal)")
    st.line_chart(df_combined.pivot(index="Year", columns="Phase", values="Corpus (₹)"), use_container_width=True)


    # Graph 4: Yearly Net Corpus Growth
    st.subheader("Yearly Corpus Growth")
    net_growth = [round(fire_progress[i] - fire_progress[i - 1], 2) if i > 0 else 0 for i in range(len(fire_progress))]

    # Combine Net and Gross Corpus Growth
    if len(years) == len(fire_progress) == len(net_growth):
        # Create a DataFrame with both Net and Gross Corpus Growth
        df_combined_growth = pd.DataFrame({
            "Year": years,
            "Net Corpus Growth (₹)": net_growth,
            "Gross Corpus Growth (₹)": fire_progress
        })
        
        # Melt DataFrame for grouped bar chart
        df_melted = df_combined_growth.melt(id_vars=["Year"], 
                                            var_name="Growth Type", 
                                            value_name="Amount (₹)")
        
        # Plot using Streamlit
        st.bar_chart(
            df_melted.pivot(index="Year", columns="Growth Type", values="Amount (₹)"),
            use_container_width=True
        )

# Display in the Simulation Tab
with tab3:
    # Generate inflation-adjusted monthly withdrawal amounts for withdrawal phase
    inflation_adjusted_withdrawal = [monthly_expenses * (1 + inflation_rate / 100) ** i 
                                    for i in range(expected_mortality - retirement_age)]
    
    excess_saved = max(fire_progress[-2] - SWP_corpus[0], 0)
    total_corpus = [SWP_corpus[i] + excess_saved*(1+rate_of_return)**i for i in range(len(SWP_corpus))]
    # Plot
    df_combined = pd.concat([
        pd.DataFrame({
            "Year": list(range(current_age, retirement_age)),
            "Corpus (₹)": fire_progress[:years_to_fire - 1],  # Exclude the retirement year from accumulation
            "Yearly SIP Contribution (₹)": [monthly_savings * 12] * (years_to_fire-1),
            "Monthly Withdrawal (₹)": [0] * (years_to_fire - 1),  # No withdrawals during accumulation
            "Phase": "Accumulation",
        }),
        pd.DataFrame({
            "Year": list(range(retirement_age, expected_mortality)),
            "Corpus (₹)": total_corpus,
            "Yearly SIP Contribution (₹)": [0] * len(SWP_corpus),  # No SIP during withdrawal
            "Monthly Withdrawal (₹)": inflation_adjusted_withdrawal,
            "Phase": "Withdrawal",
        })
    ])

    
    # Prepare data for plotting
    df_combined_plot = pd.DataFrame({
        "Year": df_combined["Year"],
        "Corpus (₹)": df_combined["Corpus (₹)"],
        # "Yearly SIP Contribution (₹)": df_combined["Yearly SIP Contribution (₹)"],
        "Yearly Withdrawals (₹)": df_combined["Monthly Withdrawal (₹)"] * 12,  # Convert monthly to yearly
    })

    # Melt the data for Plotly Express
    df_combined_long = df_combined_plot.melt(
        id_vars=["Year"],
        value_vars=["Corpus (₹)", "Yearly Withdrawals (₹)"],
        var_name="Type",
        value_name="Amount"
    )

    # Create the stacked bar chart
    fig = px.bar(
        df_combined_long,
        x="Year",
        y="Amount",
        color="Type",
        title="Withdrawals and Corpus Growth Over Time",
        labels={"Amount": "Amount (₹ in Lakhs)", "Year": "Year"},
        text_auto=".2s"
    )

    # Adjust the layout to improve visibility and title alignment
    fig.update_traces(textfont_size=10, textposition="inside")
    fig.update_layout(
        barmode="stack",
        legend_title="Type",
        title_x=0.0,  # Align the title to the left
        xaxis=dict(title="Year"),
        yaxis=dict(title="Amount (₹)", tickformat=".1f"),
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=80),  # Adjust bottom margin for labels
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)  # Place legend below chart
    )

    # Show chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Simulation Table")
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"Monthly SIP: ₹{monthly_savings}")
    with c2: 
        st.info(f"Post Retirement Expenses: ₹{round(monthly_expenses)}")

    ## Simulation Table
    st.dataframe(
        df_combined.style.format({
            "Corpus (₹)": "₹{:.2f}",
            "Monthly Withdrawal (₹)": "₹{:.2f}",
            "Yearly SIP Contribution (₹)": "₹{:.2f}",
        }),
        height=35 * len(df_combined) + 38,
        use_container_width=True,
        hide_index=True
    )
