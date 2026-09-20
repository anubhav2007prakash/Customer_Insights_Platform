"""Sample datasets for OmniMall AI demo frontend."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

def _get_dynamic_dataset() -> pd.DataFrame | None:
    """Return the user-uploaded dataset if it exists."""
    try:
        if "dynamic_dataset" in st.session_state:
            df = st.session_state["dynamic_dataset"]
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df
    except Exception:
        pass
    return None

def _guess_column(df: pd.DataFrame, keywords: list[str]) -> str | None:
    """Find a column in df that matches any of the keywords (case-insensitive)."""
    cols = [str(c).lower() for c in df.columns]
    for kw in keywords:
        for i, c in enumerate(cols):
            if kw in c:
                return df.columns[i]
    return None


def _dates(n: int) -> list[datetime]:
    start = datetime.now() - timedelta(days=n)
    return [start + timedelta(days=i) for i in range(n)]


def get_kpis(role: str | None = None) -> list[dict[str, Any]]:
    """Today's KPI metrics, with optional role-based variants."""
    df = _get_dynamic_dataset()
    if df is not None:
        rev_col = _guess_column(df, ["rev", "amount", "total", "price", "value", "sales"])
        date_col = _guess_column(df, ["date", "time", "created", "month", "year"])
        
        total_rows = len(df)
        revenue = int(df[rev_col].sum()) if rev_col else 0
        
        return [
            {"label": "Total Mall Revenue" if rev_col else "Total Value", "value": f"${revenue:,.0f}" if rev_col else "N/A", "raw": revenue, "change": 12.4, "icon": "dollar-sign", "tone": "primary"},
            {"label": "Total Footfall", "value": f"{total_rows:,}", "raw": total_rows, "change": 8.2, "icon": "users", "tone": "accent"},
            {"label": "Avg Spend/Visitor", "value": f"${revenue/total_rows:,.0f}" if (rev_col and total_rows > 0) else "N/A", "raw": 12847, "change": 5.6, "icon": "shopping-cart", "tone": "success"},
            {"label": "Data Columns", "value": f"{len(df.columns)}", "raw": 94.2, "change": 1.8, "icon": "layers", "tone": "success"},
        ]

    default_kpis = [
        {"label": "Total Tenant Revenue", "value": "$12.4M", "raw": 12400000, "change": 8.4, "icon": "dollar-sign", "tone": "primary"},
        {"label": "Mall Footfall", "value": "148,291", "raw": 148291, "change": 12.2, "icon": "users", "tone": "accent"},
        {"label": "Active Leases", "value": "242", "raw": 242, "change": 2.1, "icon": "building", "tone": "success"},
        {"label": "Occupancy Rate", "value": "96.4%", "raw": 96.4, "change": 0.8, "icon": "check-circle", "tone": "success"},
        {"label": "Growth", "value": "18.7%", "raw": 18.7, "change": 3.2, "icon": "trending-up", "tone": "primary"},
        {"label": "Churn (Lease)", "value": "1.2%", "raw": 1.2, "change": -0.4, "icon": "activity", "tone": "danger"},
        {"label": "Forecast Footfall", "value": "165K", "raw": 165000, "change": 11.0, "icon": "target", "tone": "warning"},
        {"label": "Event Attendance", "value": "14K", "raw": 14000, "change": 4.5, "icon": "calendar", "tone": "accent"},
    ]

    role_kpis = {
        "Data Analyst": [
            {"label": "Sensor Uptime", "value": "99.4%", "raw": 99.4, "change": 0.1, "icon": "shield-check", "tone": "success"},
            {"label": "Tenant Reporting", "value": "91.8%", "raw": 91.8, "change": 2.6, "icon": "layers", "tone": "accent"},
            {"label": "Data Freshness", "value": "12m", "raw": 12, "change": 1.2, "icon": "clock", "tone": "primary"},
            {"label": "Anomalies", "value": "7", "raw": 7, "change": -1.4, "icon": "activity", "tone": "warning"},
        ],
        "Data Scientist": [
            {"label": "Footfall Model Acc", "value": "94.2%", "raw": 94.2, "change": 2.8, "icon": "brain", "tone": "primary"},
            {"label": "Features", "value": "183", "raw": 183, "change": 5.4, "icon": "layers", "tone": "accent"},
            {"label": "Experiments", "value": "24", "raw": 24, "change": 4.1, "icon": "flask-conical", "tone": "success"},
            {"label": "Promo Lift", "value": "+18.3%", "raw": 18.3, "change": 3.9, "icon": "trending-up", "tone": "warning"},
        ],
        "Manager": [
            {"label": "Maintenance SLA", "value": "96%", "raw": 96, "change": 3.6, "icon": "tool", "tone": "success"},
            {"label": "Staffing Level", "value": "92%", "raw": 92, "change": 0.8, "icon": "users", "tone": "accent"},
            {"label": "Open Work Orders", "value": "12", "raw": 12, "change": -2.1, "icon": "alert-triangle", "tone": "warning"},
            {"label": "Avg Resolve Time", "value": "45m", "raw": 45, "change": -12.4, "icon": "zap", "tone": "primary"},
        ],
        "Admin": [
            {"label": "Security Patrols", "value": "100%", "raw": 100, "change": 0.0, "icon": "shield", "tone": "success"},
            {"label": "HVAC Uptime", "value": "99.98%", "raw": 99.98, "change": 0.1, "icon": "activity", "tone": "primary"},
            {"label": "Incident Reports", "value": "4", "raw": 4, "change": -2.0, "icon": "clipboard-list", "tone": "accent"},
            {"label": "Fire Code Comp.", "value": "100%", "raw": 100, "change": 0.0, "icon": "check-circle", "tone": "success"},
        ],
    }

    return role_kpis.get(role or "", default_kpis)[:4]


def get_revenue_trend(days: int = 90) -> pd.DataFrame:
    """Daily revenue time series."""
    df = _get_dynamic_dataset()
    if df is not None:
        rev_col = _guess_column(df, ["rev", "amount", "total", "price", "value", "sales"])
        date_col = _guess_column(df, ["date", "time", "created", "month", "year"])
        
        if rev_col and date_col:
            try:
                temp = df.copy()
                temp[date_col] = pd.to_datetime(temp[date_col], errors='coerce')
                temp = temp.dropna(subset=[date_col])
                grouped = temp.groupby(temp[date_col].dt.date)[rev_col].sum().reset_index()
                grouped.columns = ["date", "revenue"]
                grouped = grouped.sort_values("date").tail(days)
                grouped["footfall"] = grouped["revenue"] / 45 
                return grouped
            except Exception:
                pass 

    rng = np.random.default_rng(42)
    dates = _dates(days)
    base = np.linspace(150000, 220000, days) + rng.normal(0, 15000, days)
    return pd.DataFrame({"date": dates, "revenue": base.astype(int), "footfall": (base / 45).astype(int)})


def get_customer_acquisition(days: int = 12) -> pd.DataFrame:
    """Monthly loyalty member acquisition."""
    months = pd.date_range(end=datetime.now(), periods=days, freq="ME")
    rng = np.random.default_rng(7)
    new = rng.integers(1200, 3500, days)
    return pd.DataFrame({"month": months, "new_members": new, "inactive": rng.integers(200, 600, days)})


def get_conversion_funnel() -> pd.DataFrame:
    """Mall footfall funnel stages."""
    return pd.DataFrame({
        "stage": ["Mall Entry (Sensors)", "Zone Traffic", "Store Walk-ins", "POS Transactions (Tenants)"],
        "count": [148000, 112000, 75000, 42000],
    })


def get_traffic_sources() -> pd.DataFrame:
    """Traffic entry breakdown."""
    df = _get_dynamic_dataset()
    if df is not None:
        source_col = _guess_column(df, ["source", "gate", "entrance", "origin", "traffic"])
        if source_col:
            try:
                grouped = df.groupby(source_col).size().reset_index(name="entries")
                grouped = grouped.sort_values("entries", ascending=False).head(6)
                grouped.columns = ["source", "entries"]
                rng = np.random.default_rng(4)
                grouped["conversion"] = np.round(rng.uniform(10.5, 38.5, len(grouped)), 1)
                return grouped
            except Exception:
                pass
                
    return pd.DataFrame({
        "source": ["North Main Gate", "South Entrance", "Parking Garage A", "Subway Link", "East Wing", "Parking Garage B"],
        "entries": [45200, 38400, 28100, 18800, 12600, 9400],
        "conversion": [32.2, 28.8, 45.1, 16.2, 22.4, 47.8],
    })


def get_top_products(n: int = 8) -> pd.DataFrame:
    """Top tenants by revenue/footfall."""
    tenants = [
        "Apple Store", "Zara", "Sephora", "H&M",
        "AMC Theatres", "Nike Flagship", "Starbucks", "Din Tai Fung",
    ][:n]
    rng = np.random.default_rng(3)
    rev = sorted(rng.integers(320000, 1890000, n), reverse=True)
    return pd.DataFrame({"tenant": tenants, "revenue": rev, "footfall": (rev / rng.integers(40, 120, n)).astype(int)})


def get_top_segments() -> pd.DataFrame:
    """Mall zone performance."""
    df = _get_dynamic_dataset()
    if df is not None:
        cat_col = _guess_column(df, ["segment", "category", "zone", "wing", "type"])
        rev_col = _guess_column(df, ["rev", "amount", "total", "price", "value", "sales"])
        
        if cat_col:
            try:
                if rev_col:
                    grouped = df.groupby(cat_col).agg({rev_col: 'sum', cat_col: 'count'})
                    grouped.columns = ["revenue", "visitors"]
                else:
                    grouped = df.groupby(cat_col).agg({cat_col: 'count'})
                    grouped.columns = ["visitors"]
                    grouped["revenue"] = grouped["visitors"] * 100
                
                grouped = grouped.reset_index().rename(columns={cat_col: "zone"})
                grouped["avg_spend"] = grouped["revenue"] / grouped["visitors"]
                return grouped.sort_values("revenue", ascending=False).head(5)
            except Exception:
                pass 

    return pd.DataFrame({
        "zone": ["Luxury Wing", "Food Court", "Entertainment Hub", "Apparel Strip", "Pop-up Kiosks"],
        "visitors": [12842, 45210, 28420, 32840, 18979],
        "revenue": [2980000, 920000, 1410000, 2180000, 310000],
        "avg_spend": [232, 20, 49, 66, 16],
    })


def get_recent_activities(n: int = 8, role: str | None = None) -> list[dict[str, Any]]:
    """Recent mall activities."""
    role_items = {
        "Data Analyst": [
            ("Data quality check passed for tenant POS feed", "Data Ops", "analytics"),
            ("Tenant sales report imported successfully", "System", "integrations"),
            ("Weekend traffic analysis exported", "Analyst Team", "reports"),
            ("Anomaly detected in parking garage flow", "AI Insights", "ai"),
        ],
        "Data Scientist": [
            ("Footfall prediction model updated for Black Friday", "ML Platform", "ai"),
            ("Cross-promo Experiment B outperformed baseline by 12%", "Research Lab", "ai"),
            ("Tenant churn classifier retrained", "ML Pipeline", "ai"),
            ("Mall weather impact features engineered", "Data Science", "integrations"),
        ],
        "Manager": [
            ("Security detail increased for weekend event", "Ops Desk", "sales"),
            ("Cleaning crew dispatched to Food Court spill", "Facilities Team", "admin"),
            ("Zara lease renewal signed", "Leasing Office", "customers"),
            ("Holiday event schedule shared with tenants", "Planning", "reports"),
        ],
        "Admin": [
            ("Escalator maintenance logged for East Wing", "Facilities", "admin"),
            ("Mall Wi-Fi health check passed 99.9% uptime", "IT Ops", "integrations"),
            ("Access badge revoked for former tenant staff", "Security", "admin"),
            ("Fire drill report archived", "Compliance", "reports"),
        ],
    }

    items = role_items.get(role or "", [
        ("Lease signed — New Anchor Store", "Leasing Team", "sales"),
        ("Weekend 'Farmers Market' drove 18% footfall lift", "Marketing Bot", "marketing"),
        ("Crowd crush warning: Main Atrium", "AI Insights", "ai"),
        ("Tenant sales data synced", "Integrations", "integrations"),
        ("Report 'Monthly Occupancy' exported", "Alex Morgan", "reports"),
        ("Loyalty Program updated — 12,841 new members", "Alex Morgan", "customers"),
        ("Footfall forecast retrained — 96.2% accuracy", "ML Pipeline", "ai"),
        ("New security guard account created", "Admin", "admin"),
    ])
    now = datetime.now()
    return [
        {
            "text": text,
            "user": user,
            "type": typ,
            "time": now - timedelta(minutes=i * 23 + 5),
        }
        for i, (text, user, typ) in enumerate(items[:n])
    ]


def get_alerts(role: str | None = None) -> list[dict[str, str]]:
    """Dashboard alert banners."""
    role_alerts = {
        "Data Analyst": [
            {"level": "warning", "title": "Data quality alert", "message": "Footfall cameras at South Gate miscalibrated by 4%."},
            {"level": "info", "title": "Data fresh", "message": "Tenant POS aggregation is now under 15 minutes latency."},
        ],
        "Data Scientist": [
            {"level": "success", "title": "Model refresh complete", "message": "Event attendance classifier accuracy improved to 92.4%."},
            {"level": "info", "title": "Feature store update", "message": "New weather features are available for experimentation."},
        ],
        "Manager": [
            {"level": "warning", "title": "Maintenance required", "message": "HVAC unit 4 in the Food Court is operating at reduced capacity."},
            {"level": "success", "title": "Event prep aligned", "message": "Security and cleaning crews confirmed for Saturday's concert."},
        ],
        "Admin": [
            {"level": "success", "title": "Wi-Fi stable", "message": "Public Mall Wi-Fi uptime remains above 99.9% this week."},
            {"level": "info", "title": "Access review due", "message": "Tenant contractor badge review closes tomorrow at 5 PM."},
        ],
    }

    return role_alerts.get(role or "", [
        {"level": "warning", "title": "Parking Capacity", "message": "Garage A is currently at 94% capacity. Redirecting signs activated."},
        {"level": "info", "title": "Scheduled maintenance", "message": "Elevator bank 2 maintenance tonight at 2:00 AM."},
        {"level": "success", "title": "Footfall target achieved", "message": "Weekend visitor target exceeded by 12%."},
    ])


def get_ai_insights(role: str | None = None) -> list[dict[str, str]]:
    """AI-generated insight cards."""
    if role == "Data Scientist":
        return [
            {"title": "Model accuracy shift", "body": "Event attendance model accuracy improved to 94.1% following feature retuning."},
            {"title": "Footfall acceleration", "body": "The new Din Tai Fung opening drove 24% of this week's traffic growth in the South Wing."},
            {"title": "Tenant Risk", "body": "Three apparel stores show declining sales over 60 days, risking lease renewal defaults."},
        ]
    return [
        {"title": "Footfall acceleration", "body": "The new Din Tai Fung opening drove 24% of this week's traffic growth in the South Wing."},
        {"title": "Tenant Risk", "body": "Three apparel stores show declining sales over 60 days, risking lease renewal defaults."},
        {"title": "Cross-promo opportunity", "body": "Cinema-goers are 40% more likely to visit the arcade post-movie. Suggest bundle."},
        {"title": "Event optimization", "body": "Live music in the Atrium increased dwell time by 32 mins on average."},
    ]


def get_recommendations() -> list[dict[str, str]]:
    """Action recommendations for Mall Management."""
    return [
        {"action": "Deploy 'Dine & Shop' Promo", "impact": "High", "segment": "Food Court / Apparel"},
        {"action": "Increase security patrols", "impact": "Medium", "segment": "North Garage"},
        {"action": "Offer rent deferral discussion", "impact": "High", "segment": "At-Risk Tenants"},
        {"action": "Push push-notification map", "impact": "Medium", "segment": "Lost Shoppers"},
    ]


def get_upcoming_tasks() -> list[dict[str, Any]]:
    """Upcoming tasks."""
    base = datetime.now()
    return [
        {"task": "Review Q2 tenant occupancy report", "due": base + timedelta(days=1), "priority": "High"},
        {"task": "Approve holiday decoration budget", "due": base + timedelta(days=2), "priority": "Medium"},
        {"task": "Lease renewal meetings", "due": base + timedelta(days=3), "priority": "High"},
        {"task": "Fire safety inspection", "due": base + timedelta(days=5), "priority": "High"},
    ]


def get_campaign_performance() -> pd.DataFrame:
    """Mall Campaign metrics."""
    return pd.DataFrame({
        "campaign": ["Holiday Lights", "Back to School", "Black Friday", "Food Truck Fest", "Local Artists Market"],
        "reach": [142000, 82800, 228400, 48600, 35200],
        "engagement": [48900, 24200, 114200, 15100, 9800],
        "footfall_lift": [12400, 8320, 41120, 6410, 2520],
        "roi": [4.2, 3.8, 8.1, 2.2, 1.4],
    })


def get_sales_performance() -> pd.DataFrame:
    """Leasing agent performance."""
    return pd.DataFrame({
        "agent": ["Sarah Chen", "Marcus Lee", "Priya Patel", "James Wilson", "Elena Rossi"],
        "deals_closed": [8, 5, 7, 3, 6],
        "sq_ft_leased": [42000, 18000, 39500, 12000, 24000],
        "quota_pct": [112, 98, 105, 87, 94],
    })


def get_top_cities() -> pd.DataFrame:
    """Geographic distribution of visitors."""
    return pd.DataFrame({
        "zip_code": ["90210", "90001", "90401", "90028", "91101", "90245", "90045", "90012"],
        "visitors": [24200, 13800, 12900, 12100, 11800, 9600, 8400, 7200],
        "loyalty_members": [8200, 4800, 5200, 3800, 3400, 2900, 2600, 2200],
        "lat": [34.0901, 33.9731, 34.0195, 34.1016, 34.1478, 33.9184, 33.9534, 34.0522],
        "lon": [-118.4065, -118.2479, -118.4912, -118.3278, -118.1445, -118.4079, -118.4117, -118.2437],
    })


def get_customers(n: int = 50) -> pd.DataFrame:
    """Mall Loyalty Member directory."""
    df = _get_dynamic_dataset()
    if df is not None:
        mapped = pd.DataFrame()
        name_col = _guess_column(df, ["name", "customer", "first", "full_name"])
        email_col = _guess_column(df, ["email", "mail"])
        tier_col = _guess_column(df, ["tier", "level", "status", "segment"])
        rev_col = _guess_column(df, ["points", "spend", "ltv", "amount", "total"])
        
        mapped["id"] = df.index if "id" not in df.columns else df["id"]
        mapped["name"] = df[name_col] if name_col else [f"Shopper {i}" for i in range(len(df))]
        mapped["email"] = df[email_col] if email_col else [f"user{i}@example.com" for i in range(len(df))]
        mapped["tier"] = df[tier_col] if tier_col else ["Silver"] * len(df)
        
        if rev_col:
            mapped["points_balance"] = pd.to_numeric(df[rev_col], errors='coerce').fillna(0).astype(int)
        else:
            mapped["points_balance"] = 0
            
        mapped["visits_ytd"] = 12
        mapped["last_visit"] = datetime.now() - timedelta(days=2)
        mapped["engagement_score"] = 85
        
        return mapped.head(n)

    rng = np.random.default_rng(99)
    first = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Quinn", "Avery", "Blake", "Drew"]
    last = ["Morgan", "Chen", "Patel", "Wilson", "Garcia", "Kim", "Singh", "Brown", "Lee", "Martinez"]
    tiers = ["Platinum", "Gold", "Silver", "Bronze"]
    rows = []
    for i in range(n):
        fn, ln = rng.choice(first), rng.choice(last)
        rows.append({
            "id": f"MAL-{10000 + i}",
            "name": f"{fn} {ln}",
            "email": f"{fn.lower()}.{ln.lower()}@example.com",
            "tier": rng.choice(tiers),
            "points_balance": int(rng.integers(120, 85000)),
            "visits_ytd": int(rng.integers(1, 140)),
            "last_visit": datetime.now() - timedelta(days=int(rng.integers(0, 90))),
            "engagement_score": int(rng.integers(35, 99)),
        })
    return pd.DataFrame(rows)


def get_customer_timeline() -> list[dict[str, Any]]:
    """Single mall shopper timeline."""
    now = datetime.now()
    return [
        {"event": "Redeemed points at Starbucks", "time": now - timedelta(hours=2), "type": "purchase"},
        {"event": "Entered North Garage", "time": now - timedelta(hours=5), "type": "engagement"},
        {"event": "Purchased AMC Movie Tickets", "time": now - timedelta(days=12), "type": "purchase"},
        {"event": "Upgraded to Gold Tier", "time": now - timedelta(days=28), "type": "upgrade"},
        {"event": "Loyalty Account created", "time": now - timedelta(days=180), "type": "signup"},
    ]


def get_purchase_history() -> pd.DataFrame:
    """Mall tenant purchase history."""
    return pd.DataFrame({
        "date": _dates(6)[::-1],
        "tenant": ["Zara", "Apple Store", "Food Court (Panda Express)", "Sephora", "AMC Theatres", "H&M"],
        "amount": [124, 1299, 18, 85, 42, 65],
        "points_earned": [124, 1299, 18, 85, 42, 65],
    })


def get_reports_library() -> pd.DataFrame:
    """Report library entries."""
    return pd.DataFrame({
        "name": ["Monthly Mall Footfall", "Tenant Revenue Aggregation", "Lease Expiry Watchlist", "Security Incident Log", "Energy Usage (HVAC)"],
        "type": ["Operations", "Financial", "Leasing", "Security", "Facilities"],
        "author": ["Alex Morgan", "Finance Team", "Leasing Dept", "Head of Security", "Facilities Manager"],
        "updated": [datetime.now() - timedelta(days=d) for d in [1, 3, 5, 2, 7]],
        "format": ["PDF", "Excel", "PDF", "PDF", "Excel"],
        "pinned": [True, True, False, True, False],
    })


def get_scheduled_reports() -> pd.DataFrame:
    """Scheduled report jobs."""
    return pd.DataFrame({
        "report": ["Monthly Mall Revenue", "Weekly Footfall KPIs", "Event Performance", "Parking Utilization"],
        "schedule": ["Monthly", "Weekly", "Weekly", "Daily"],
        "next_run": [datetime.now() + timedelta(days=d) for d in [7, 2, 4, 1]],
        "recipients": [3, 8, 4, 12],
        "status": ["Active", "Active", "Paused", "Active"],
    })


def get_integrations() -> pd.DataFrame:
    """Mall integration catalog."""
    return pd.DataFrame({
        "name": ["ShopperTrak Sensors", "Tenant POS Aggregator", "ParkAssist", "Honeywell HVAC", "Mall Wi-Fi Analytics", "Security Cameras"],
        "category": ["Footfall", "Revenue", "Facilities", "Facilities", "Footfall", "Security"],
        "status": ["Connected", "Connected", "Connected", "Connected", "Connected", "Connected"],
        "last_sync": [datetime.now() - timedelta(minutes=m) for m in [2, 14, 1, 6, 3, 0]],
    })


def get_admin_users() -> pd.DataFrame:
    """Admin user list."""
    return pd.DataFrame({
        "name": ["Alex Morgan", "Sarah Chen", "Marcus Lee", "Priya Patel", "James Wilson"],
        "email": ["alex.m@omnimall.com", "sarah.c@omnimall.com", "marcus.l@omnimall.com", "priya.p@omnimall.com", "james.w@omnimall.com"],
        "role": ["Mall Manager", "Facilities Head", "Data Analyst", "Leasing Director", "Security Chief"],
        "status": ["Active", "Active", "Active", "Active", "Invited"],
        "last_login": [datetime.now() - timedelta(days=d) for d in [0, 1, 0, 3, 30]],
    })


def get_audit_logs(n: int = 10) -> pd.DataFrame:
    """Audit log entries."""
    actions = ["Login", "Export Tenant Report", "Override HVAC Settings", "Issue Security Badge", "Update Lease Terms"]
    users = ["Alex Morgan", "Sarah Chen", "System", "Priya Patel"]
    rng = np.random.default_rng(11)
    return pd.DataFrame({
        "timestamp": [datetime.now() - timedelta(hours=i * 4) for i in range(n)],
        "user": [rng.choice(users) for _ in range(n)],
        "action": [rng.choice(actions) for _ in range(n)],
        "ip": [f"10.0.{rng.integers(1,255)}.{rng.integers(1,255)}" for _ in range(n)],
        "status": ["Success"] * n,
    })


def get_chat_history() -> list[dict[str, str]]:
    """AI chat conversation."""
    return [
        {"role": "user", "content": "What drove the footfall increase last weekend?"},
        {"role": "ai", "content": "The 'Summer Food Fest' in the Atrium contributed to a 28% overall footfall lift. The Food Court and South Wing saw the highest traffic spikes, with parking capacity reaching 98% on Saturday afternoon."},
        {"role": "user", "content": "Which tenants are up for lease renewal next quarter?"},
        {"role": "ai", "content": "There are 12 tenants with leases expiring in Q4. The highest priority is Sephora (Anchor), currently in negotiations. Three smaller kiosks have indicated they will not renew."},
    ]


def get_ai_suggestions(role: str | None = None) -> list[str]:
    """AI prompt suggestions."""
    if role == "Data Scientist":
        return [
            "Run model experiment on footfall predictors",
            "Show feature importance for churn classifier",
            "Forecast parking utilization for Black Friday",
            "Compare North Wing vs South Wing traffic",
        ]
    return [
        "Summarize this weekend's footfall KPIs",
        "Which mall events had the highest ROI?",
        "Show at-risk tenant leases",
        "Forecast parking utilization for Black Friday",
        "Compare North Wing vs South Wing traffic",
        "What categories drive the most cross-shopping?",
    ]


def get_analytics_metrics() -> pd.DataFrame:
    """Mall footfall and analytics data."""
    df = _get_dynamic_dataset()
    if df is not None:
        prod_col = _guess_column(df, ["tenant", "store", "shop", "name", "category"])
        reg_col = _guess_column(df, ["zone", "wing", "level", "location", "area"])
        rev_col = _guess_column(df, ["rev", "amount", "total", "sales", "rent"])
        unit_col = _guess_column(df, ["footfall", "visitors", "traffic", "entries"])
        
        if prod_col and rev_col:
            try:
                temp = df.copy()
                if not reg_col:
                    temp["zone"] = "Main Level"
                    reg_col = "zone"
                if not unit_col:
                    temp["footfall"] = 1000
                    unit_col = "footfall"
                
                temp[rev_col] = pd.to_numeric(temp[rev_col], errors='coerce').fillna(0)
                temp[unit_col] = pd.to_numeric(temp[unit_col], errors='coerce').fillna(0)
                
                grouped = temp.groupby([prod_col, reg_col]).agg({rev_col: 'sum', unit_col: 'sum'}).reset_index()
                grouped.columns = ["tenant", "zone", "revenue", "footfall"]
                grouped["rent_yield"] = 0.12
                return grouped.head(50)
            except Exception:
                pass
                
    rng = np.random.default_rng(55)
    categories = ["Apparel", "Electronics", "Food & Bev", "Entertainment", "Services"]
    regions = ["North Wing", "South Wing", "East Wing", "Food Court", "Atrium"]
    rows = []
    for cat in categories:
        for reg in regions:
            rows.append({
                "tenant_category": cat,
                "zone": reg,
                "revenue": int(rng.integers(500000, 4000000)),
                "footfall": int(rng.integers(10000, 200000)),
                "rent_yield": round(rng.uniform(0.08, 0.25), 2),
            })
    return pd.DataFrame(rows)


def get_heatmap_data() -> pd.DataFrame:
    """Mall Footfall heatmap matrix."""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = [f"{h:02d}:00" for h in range(8, 22)]
    rng = np.random.default_rng(33)
    data = []
    for d in days:
        for h in hours:
            base = 100 if d in ["Sat", "Sun"] else 40
            peak = 50 if h in ["12:00", "13:00", "18:00", "19:00"] else 0
            data.append({"day": d, "hour": h, "engagement": int(base + peak + rng.integers(-20, 40))})
    return pd.DataFrame(data)


def get_predictions() -> pd.DataFrame:
    """Tenant risk ML prediction results."""
    return pd.DataFrame({
        "tenant": ["Toy Kiosk", "Local Cafe", "Shoe Outlet", "VR Arcade", "Tech Accessories"],
        "churn_prob": [0.82, 0.67, 0.45, 0.31, 0.18],
        "monthly_rent": [4200, 8500, 15200, 8900, 6200],
        "zone": ["East Wing", "Food Court", "South Wing", "Atrium", "North Wing"],
        "risk": ["High", "High", "Medium", "Low", "Low"],
    })


def get_forecast_series(months: int = 12) -> pd.DataFrame:
    """Mall footfall forecast with confidence bands."""
    df = _get_dynamic_dataset()
    if df is not None:
        rev_col = _guess_column(df, ["footfall", "traffic", "visitors", "entries"])
        date_col = _guess_column(df, ["date", "time", "created", "month", "year"])
        
        if rev_col and date_col:
            try:
                temp = df.copy()
                temp[date_col] = pd.to_datetime(temp[date_col], errors='coerce')
                temp = temp.dropna(subset=[date_col])
                grouped = temp.groupby(temp[date_col].dt.to_period("M"))[rev_col].sum().reset_index()
                grouped[date_col] = grouped[date_col].dt.to_timestamp()
                grouped = grouped.sort_values(date_col).tail(months//2)
                
                actual_vals = grouped[rev_col].values
                if len(actual_vals) > 0:
                    last_val = actual_vals[-1]
                    trend = (actual_vals[-1] - actual_vals[0]) / max(len(actual_vals), 1) if len(actual_vals) > 1 else last_val * 0.05
                    forecast_vals = [last_val + (i+1)*trend for i in range(months - len(actual_vals))]
                    idx = list(grouped[date_col].values)
                    last_date = pd.to_datetime(idx[-1]) if len(idx) > 0 else datetime.now()
                    future_dates = pd.date_range(start=last_date + pd.offsets.MonthBegin(1), periods=len(forecast_vals), freq="ME")
                    
                    all_dates = list(idx) + list(future_dates)
                    all_vals = list(actual_vals) + forecast_vals
                    
                    return pd.DataFrame({
                        "month": all_dates,
                        "value": np.array(all_vals).astype(int),
                        "lower": (np.array(all_vals) * 0.92).astype(int),
                        "upper": (np.array(all_vals) * 1.08).astype(int),
                        "type": ["Actual"] * len(actual_vals) + ["Forecast"] * len(forecast_vals),
                    })
            except Exception:
                pass
                
    rng = np.random.default_rng(21)
    idx = pd.date_range(end=datetime.now() + timedelta(days=180), periods=months, freq="ME")
    actual = np.linspace(800000, 1100000, months // 2)
    forecast = np.linspace(1100000, 1500000, months - months // 2)
    
    # Add holiday spike
    forecast[-2] *= 1.4
    
    values = np.concatenate([actual, forecast])
    return pd.DataFrame({
        "month": idx,
        "value": values.astype(int),
        "lower": (values * 0.85).astype(int),
        "upper": (values * 1.15).astype(int),
        "type": ["Actual"] * (months // 2) + ["Forecast"] * (months - months // 2),
    })
