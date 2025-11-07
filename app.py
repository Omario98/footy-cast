import streamlit as st
import plotly.graph_objects as go
from prediction_engine import FootballPredictor

# Page configuration
st.set_page_config(
    page_title="Footy-cast by Omario",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTitle {
        color: #1e3a8a;
        font-size: 3rem !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stSubheader {
        color: #1e40af;
        font-weight: 600;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .prediction-box {
        background: #f8fafc;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        margin: 15px 0;
    }
    .team-section {
        background: #ffffff;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 15px 0;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def create_gauge_chart(value, title, max_value=100):
    """Create a gauge chart for visualizing percentages."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 16}},
        number={'suffix': "%", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1},
            'bar': {'color': "#3b82f6"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_value/3], 'color': '#fee2e2'},
                {'range': [max_value/3, 2*max_value/3], 'color': '#fef3c7'},
                {'range': [2*max_value/3, max_value], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#1e293b", 'family': "Arial"}
    )
    
    return fig

def create_probability_bar(home_prob, draw_prob, away_prob, home_name, away_name):
    """Create a horizontal stacked bar chart for match outcome probabilities."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=['Match Outcome'],
        x=[home_prob],
        name=home_name,
        orientation='h',
        marker=dict(color='#3b82f6'),
        text=[f'{home_prob}%'],
        textposition='inside',
        hovertemplate=f'<b>{home_name} Win</b><br>Probability: {home_prob}%<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        y=['Match Outcome'],
        x=[draw_prob],
        name='Draw',
        orientation='h',
        marker=dict(color='#94a3b8'),
        text=[f'{draw_prob}%'],
        textposition='inside',
        hovertemplate=f'<b>Draw</b><br>Probability: {draw_prob}%<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        y=['Match Outcome'],
        x=[away_prob],
        name=away_name,
        orientation='h',
        marker=dict(color='#ef4444'),
        text=[f'{away_prob}%'],
        textposition='inside',
        hovertemplate=f'<b>{away_name} Win</b><br>Probability: {away_prob}%<extra></extra>'
    ))
    
    fig.update_layout(
        barmode='stack',
        height=150,
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(showgrid=False, showticklabels=False, range=[0, 100]),
        yaxis=dict(showticklabels=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'size': 14, 'color': 'white', 'family': 'Arial'}
    )
    
    return fig

def main():
    # Title
    st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>⚽ Footy-cast by Omario</h1>", 
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.2rem;'>Professional Match Analysis & Prediction Tool</p>", 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize predictor
    predictor = FootballPredictor()
    
    # Create two columns for team data entry
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='team-section'>", unsafe_allow_html=True)
        st.subheader("🏠 Home Team")
        home_name = st.text_input("Team Name", value="Home Team", key="home_name")
        
        st.markdown("**Attacking Metrics**")
        home_xg = st.number_input("Expected Goals (xG)", min_value=0.0, max_value=10.0, 
                                   value=1.5, step=0.1, key="home_xg",
                                   help="Average expected goals based on shot quality")
        home_shots = st.number_input("Total Shots", min_value=0, max_value=50, 
                                      value=12, step=1, key="home_shots")
        home_sot = st.number_input("Shots on Target", min_value=0, max_value=30, 
                                    value=5, step=1, key="home_sot")
        home_xgot = st.number_input("Expected Goals on Target (xGOT)", min_value=0.0, 
                                     max_value=10.0, value=1.3, step=0.1, key="home_xgot",
                                     help="Expected goals from shots on target")
        home_xa = st.number_input("Expected Assists (xA)", min_value=0.0, max_value=5.0, 
                                   value=1.0, step=0.1, key="home_xa")
        
        st.markdown("**Defensive Metrics**")
        home_passes = st.number_input("Successful Passes Rate (%)", min_value=0.0, 
                                       max_value=100.0, value=75.0, step=0.5, key="home_passes")
        home_tackles = st.number_input("Successful Tackles Rate (%)", min_value=0.0, 
                                        max_value=100.0, value=70.0, step=0.5, key="home_tackles")
        home_recoveries = st.number_input("Ball Recoveries", min_value=0, max_value=200, 
                                           value=50, step=1, key="home_recoveries")
        
        st.markdown("**Goalkeeper Metric**")
        home_xgot_conceded = st.number_input("xGOT Conceded", min_value=0.0, max_value=10.0, 
                                              value=1.0, step=0.1, key="home_xgot_conceded",
                                              help="Expected goals on target conceded by goalkeeper")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='team-section'>", unsafe_allow_html=True)
        st.subheader("✈️ Away Team")
        away_name = st.text_input("Team Name", value="Away Team", key="away_name")
        
        st.markdown("**Attacking Metrics**")
        away_xg = st.number_input("Expected Goals (xG)", min_value=0.0, max_value=10.0, 
                                   value=1.2, step=0.1, key="away_xg",
                                   help="Average expected goals based on shot quality")
        away_shots = st.number_input("Total Shots", min_value=0, max_value=50, 
                                      value=10, step=1, key="away_shots")
        away_sot = st.number_input("Shots on Target", min_value=0, max_value=30, 
                                    value=4, step=1, key="away_sot")
        away_xgot = st.number_input("Expected Goals on Target (xGOT)", min_value=0.0, 
                                     max_value=10.0, value=1.0, step=0.1, key="away_xgot",
                                     help="Expected goals from shots on target")
        away_xa = st.number_input("Expected Assists (xA)", min_value=0.0, max_value=5.0, 
                                   value=0.8, step=0.1, key="away_xa")
        
        st.markdown("**Defensive Metrics**")
        away_passes = st.number_input("Successful Passes Rate (%)", min_value=0.0, 
                                       max_value=100.0, value=72.0, step=0.5, key="away_passes")
        away_tackles = st.number_input("Successful Tackles Rate (%)", min_value=0.0, 
                                        max_value=100.0, value=68.0, step=0.5, key="away_tackles")
        away_recoveries = st.number_input("Ball Recoveries", min_value=0, max_value=200, 
                                           value=45, step=1, key="away_recoveries")
        
        st.markdown("**Goalkeeper Metric**")
        away_xgot_conceded = st.number_input("xGOT Conceded", min_value=0.0, max_value=10.0, 
                                              value=1.2, step=0.1, key="away_xgot_conceded",
                                              help="Expected goals on target conceded by goalkeeper")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Predict button
    st.markdown("<br>", unsafe_allow_html=True)
    col_button = st.columns([1, 1, 1])
    with col_button[1]:
        predict_button = st.button("🔮 Generate Predictions", type="primary", use_container_width=True)
    
    if predict_button:
        # Prepare data
        home_data = {
            'xg': home_xg,
            'total_shots': home_shots,
            'shots_on_target': home_sot,
            'xgot': home_xgot,
            'passes_rate': home_passes,
            'xa': home_xa,
            'tackles_rate': home_tackles,
            'ball_recoveries': home_recoveries,
            'xgot_conceded': home_xgot_conceded
        }
        
        away_data = {
            'xg': away_xg,
            'total_shots': away_shots,
            'shots_on_target': away_sot,
            'xgot': away_xgot,
            'passes_rate': away_passes,
            'xa': away_xa,
            'tackles_rate': away_tackles,
            'ball_recoveries': away_recoveries,
            'xgot_conceded': away_xgot_conceded
        }
        
        # Get predictions
        predictions = predictor.predict_match_outcome(home_data, away_data)
        
        # Display results
        st.markdown("---")
        st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>📊 Match Predictions</h2>", 
                    unsafe_allow_html=True)
        
        # Expected Goals Summary
        st.markdown("<br>", unsafe_allow_html=True)
        col_xg1, col_xg2, col_xg3 = st.columns(3)
        with col_xg1:
            st.metric(label=f"{home_name} Expected Goals", 
                     value=f"{predictions['expected_goals']['home']} xG",
                     delta=None)
        with col_xg2:
            st.metric(label="Total Expected Goals", 
                     value=f"{predictions['expected_goals']['total']} xG",
                     delta=None)
        with col_xg3:
            st.metric(label=f"{away_name} Expected Goals", 
                     value=f"{predictions['expected_goals']['away']} xG",
                     delta=None)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Win Probabilities
        st.subheader("🏆 Match Outcome Probabilities")
        win_probs = predictions['win_probabilities']
        
        # Probability bar chart
        fig_bar = create_probability_bar(
            win_probs['home_win'], 
            win_probs['draw'], 
            win_probs['away_win'],
            home_name,
            away_name
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Determine most likely outcome
        max_prob = max(win_probs['home_win'], win_probs['draw'], win_probs['away_win'])
        if max_prob == win_probs['home_win']:
            outcome_text = f"**{home_name}** is more likely to win"
            outcome_color = "#3b82f6"
        elif max_prob == win_probs['draw']:
            outcome_text = "Match is likely to end in a **Draw**"
            outcome_color = "#94a3b8"
        else:
            outcome_text = f"**{away_name}** is more likely to win"
            outcome_color = "#ef4444"
        
        st.markdown(f"<div style='background: {outcome_color}; padding: 15px; border-radius: 10px; "
                   f"text-align: center; color: white; font-size: 1.3rem; font-weight: 600; margin: 20px 0;'>"
                   f"{outcome_text} with {max_prob}% probability</div>", 
                   unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Both Teams To Score
        st.subheader("⚽ Both Teams To Score (BTTS)")
        btts = predictions['btts']
        
        col_btts1, col_btts2 = st.columns(2)
        with col_btts1:
            fig_btts = create_gauge_chart(btts['probability'], "BTTS Probability")
            st.plotly_chart(fig_btts, use_container_width=True)
        
        with col_btts2:
            btts_color = "#10b981" if btts['prediction'] == "Yes" else "#ef4444"
            st.markdown(f"<div style='background: {btts_color}; padding: 40px; border-radius: 10px; "
                       f"text-align: center; color: white; margin-top: 40px;'>"
                       f"<div style='font-size: 2.5rem; font-weight: 700;'>{btts['prediction']}</div>"
                       f"<div style='font-size: 1.2rem; margin-top: 10px;'>{btts['probability']}% Probability</div>"
                       f"</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Over/Under Goals
        st.subheader("📈 Over/Under Goals Predictions")
        over_under = predictions['over_under']
        
        col_ou1, col_ou2, col_ou3 = st.columns(3)
        
        with col_ou1:
            st.markdown("<div class='prediction-box'>", unsafe_allow_html=True)
            st.markdown("**Over/Under 1.5 Goals**")
            fig_15 = create_gauge_chart(over_under['1.5']['over'], "Over 1.5")
            st.plotly_chart(fig_15, use_container_width=True)
            pred_color_15 = "#10b981" if over_under['1.5']['prediction'] == "Over" else "#ef4444"
            st.markdown(f"<div style='background: {pred_color_15}; padding: 10px; border-radius: 5px; "
                       f"text-align: center; color: white; font-weight: 600;'>"
                       f"Prediction: {over_under['1.5']['prediction']} 1.5</div>", 
                       unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_ou2:
            st.markdown("<div class='prediction-box'>", unsafe_allow_html=True)
            st.markdown("**Over/Under 2.5 Goals**")
            fig_25 = create_gauge_chart(over_under['2.5']['over'], "Over 2.5")
            st.plotly_chart(fig_25, use_container_width=True)
            pred_color_25 = "#10b981" if over_under['2.5']['prediction'] == "Over" else "#ef4444"
            st.markdown(f"<div style='background: {pred_color_25}; padding: 10px; border-radius: 5px; "
                       f"text-align: center; color: white; font-weight: 600;'>"
                       f"Prediction: {over_under['2.5']['prediction']} 2.5</div>", 
                       unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_ou3:
            st.markdown("<div class='prediction-box'>", unsafe_allow_html=True)
            st.markdown("**Over/Under 3.5 Goals**")
            fig_35 = create_gauge_chart(over_under['3.5']['over'], "Over 3.5")
            st.plotly_chart(fig_35, use_container_width=True)
            pred_color_35 = "#10b981" if over_under['3.5']['prediction'] == "Over" else "#ef4444"
            st.markdown(f"<div style='background: {pred_color_35}; padding: 10px; border-radius: 5px; "
                       f"text-align: center; color: white; font-weight: 600;'>"
                       f"Prediction: {over_under['3.5']['prediction']} 3.5</div>", 
                       unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Most Likely Scorelines
        st.subheader("🎯 Most Likely Scorelines")
        scorelines = predictions['scorelines']
        
        col_sc1, col_sc2, col_sc3 = st.columns(3)
        
        colors = ["#3b82f6", "#8b5cf6", "#ec4899"]
        cols = [col_sc1, col_sc2, col_sc3]
        
        for idx, (col, scoreline, color) in enumerate(zip(cols, scorelines, colors)):
            with col:
                st.markdown(f"<div style='background: {color}; padding: 30px; border-radius: 15px; "
                           f"text-align: center; color: white; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>"
                           f"<div style='font-size: 1rem; opacity: 0.9;'>#{idx + 1} Most Likely</div>"
                           f"<div style='font-size: 3rem; font-weight: 700; margin: 10px 0;'>"
                           f"{scoreline['scoreline']}</div>"
                           f"<div style='font-size: 1.3rem; font-weight: 600;'>"
                           f"{scoreline['probability']}% Probability</div>"
                           f"</div>", unsafe_allow_html=True)
        
        # Footer
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; color: #94a3b8; padding: 20px;'>"
                   "<p>Predictions are based on statistical analysis of the provided metrics.</p>"
                   "<p style='font-size: 0.9rem;'>Use this tool as guidance alongside your own analysis, All rights reserved © 2025</p>"
                   "</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
