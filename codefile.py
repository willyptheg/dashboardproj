import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

df = pd.read_csv("layoff_data.csv")

# drop rows missing core fields
df = df.dropna(subset=["company_name", "industry", "country", "layoffs_count"])
df["company_name"] = df["company_name"].str.strip().str.title()
df["industry"] = df["industry"].str.strip().str.title()
df["country"] = df["country"].str.strip().str.title()

# months come in as abbreviations (Jan, Feb...) so convert to int first
df["month"] = pd.to_datetime(df["month"], format="%b").dt.month

# zfill pads single digit months so period sorts correctly (e.g. 03 not 3)
df["period"] = pd.to_datetime(
    df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2),
    format="%Y-%m"
)

df = df.sort_values("period")

companies = sorted(df["company_name"].unique())

app = Dash(__name__)

app.layout = html.Div([

    html.H1(
        "Tech Company Analytics Dashboard",
        style={"textAlign": "center", "color": "#2c3e50", "paddingTop": "20px"}
    ),
    html.P(
        "Select one or more companies to explore layoffs, AI impact, and job market trends",
        style={"textAlign": "center", "color": "gray", "marginBottom": "30px"}
    ),

    html.Div([
        html.Label(
            "Select Companies:",
            style={"fontWeight": "bold", "marginBottom": "8px", "display": "block"}
        ),
        dcc.Dropdown(
            id="company-selector",
            options=[{"label": c, "value": c} for c in companies],
            value=["Amazon", "Google", "Meta"],
            multi=True,
            placeholder="Select companies...",
            style={"width": "100%"}
        ),
    ], style={
        "width": "70%",
        "margin": "0 auto",
        "marginBottom": "40px",
        "padding": "20px",
        "backgroundColor": "white",
        "borderRadius": "8px",
        "boxShadow": "0 2px 6px rgba(0,0,0,0.1)"
    }),

    html.Div(
        id="dashboard-content",
        style={"padding": "0 40px"}
    )

], style={"fontFamily": "Arial", "backgroundColor": "#f4f6f9", "minHeight": "100vh"})


@app.callback(
    Output("dashboard-content", "children"),
    Input("company-selector", "value")
)
def update_dashboard(selected_companies):
    if not selected_companies:
        return html.P(
            "Please select at least one company above.",
            style={"textAlign": "center", "color": "gray", "marginTop": "40px"}
        )

    filtered = df[df["company_name"].isin(selected_companies)]

    # sum layoffs per company per month
    layoffs_time = (
        filtered.groupby(["company_name", "period"])["layoffs_count"]
        .sum()
        .reset_index()
    )
    fig_layoffs = px.line(
        layoffs_time,
        x="period",
        y="layoffs_count",
        color="company_name",
        title="Layoffs Over Time",
        markers=True,
        labels={
            "layoffs_count": "Total Layoffs",
            "period": "Date",
            "company_name": "Company"
        }
    )

    # average since multiple records can exist per company per month
    ai_time = (
        filtered.groupby(["company_name", "period"])["ai_adoption_level"]
        .mean()
        .reset_index()
    )
    fig_ai = px.line(
        ai_time,
        x="period",
        y="ai_adoption_level",
        color="company_name",
        title="AI Adoption Level Over Time",
        markers=True,
        labels={
            "ai_adoption_level": "AI Adoption Level",
            "period": "Date",
            "company_name": "Company"
        }
    )

    security_time = (
        filtered.groupby(["company_name", "period"])["job_security_score"]
        .mean()
        .reset_index()
    )
    fig_security = px.line(
        security_time,
        x="period",
        y="job_security_score",
        color="company_name",
        title="Job Security Score Over Time",
        markers=True,
        labels={
            "job_security_score": "Job Security Score",
            "period": "Date",
            "company_name": "Company"
        }
    )

    revenue_time = (
        filtered.groupby(["company_name", "period"])["revenue_growth_percent"]
        .mean()
        .reset_index()
    )
    fig_revenue = px.line(
        revenue_time,
        x="period",
        y="revenue_growth_percent",
        color="company_name",
        title="Revenue Growth % Over Time",
        markers=True,
        labels={
            "revenue_growth_percent": "Revenue Growth %",
            "period": "Date",
            "company_name": "Company"
        }
    )

    salary_time = (
        filtered.groupby(["company_name", "period"])["salary_budget_change"]
        .mean()
        .reset_index()
    )
    fig_salary = px.line(
        salary_time,
        x="period",
        y="salary_budget_change",
        color="company_name",
        title="Salary Budget Change Over Time",
        markers=True,
        labels={
            "salary_budget_change": "Salary Budget Change %",
            "period": "Date",
            "company_name": "Company"
        }
    )

    return html.Div([

        dcc.Graph(figure=fig_layoffs),

        html.Div([
            html.Div(dcc.Graph(figure=fig_ai), style={"width": "50%"}),
            html.Div(dcc.Graph(figure=fig_security), style={"width": "50%"}),
        ], style={"display": "flex"}),

        html.Div([
            html.Div(dcc.Graph(figure=fig_revenue), style={"width": "50%"}),
            html.Div(dcc.Graph(figure=fig_salary), style={"width": "50%"}),
        ], style={"display": "flex"}),

    ])


if __name__ == "__main__":
    app.run(debug=True)