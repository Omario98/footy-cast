import numpy as np
from scipy import stats
from typing import Dict, Tuple, List

class FootballPredictor:
    """
    Football match prediction engine using statistical analysis of team metrics.
    """
    
    def __init__(self):
        # Weights for different metrics in prediction
        self.offensive_weights = {
            'xg': 0.30,
            'total_shots': 0.08,
            'shots_on_target': 0.12,
            'xgot': 0.22,
            'xa': 0.13,
            'passes_rate': 0.15
        }
        
        self.defensive_weights = {
            'xgot_conceded': 0.40,
            'tackles_rate': 0.30,
            'ball_recoveries': 0.30
        }
    
    def calculate_team_strength(self, team_data: Dict) -> Tuple[float, float]:
        """
        Calculate offensive and defensive strength scores for a team.
        
        Args:
            team_data: Dictionary containing team statistics
            
        Returns:
            Tuple of (offensive_score, defensive_score)
        """
        # Normalize and calculate offensive score (including passes rate)
        offensive_score = (
            team_data['xg'] * self.offensive_weights['xg'] +
            (team_data['total_shots'] / 20) * self.offensive_weights['total_shots'] +
            (team_data['shots_on_target'] / 10) * self.offensive_weights['shots_on_target'] +
            team_data['xgot'] * self.offensive_weights['xgot'] +
            team_data['xa'] * self.offensive_weights['xa'] +
            (team_data['passes_rate'] / 100) * self.offensive_weights['passes_rate']
        )
        
        # Normalize and calculate defensive score (higher is better)
        defensive_score = (
            (1 / (team_data['xgot_conceded'] + 0.1)) * self.defensive_weights['xgot_conceded'] +
            (team_data['tackles_rate'] / 100) * self.defensive_weights['tackles_rate'] +
            (team_data['ball_recoveries'] / 100) * self.defensive_weights['ball_recoveries']
        )
        
        return offensive_score, defensive_score
    
    def predict_match_outcome(self, home_data: Dict, away_data: Dict) -> Dict:
        """
        Predict match outcome based on team statistics.
        
        Args:
            home_data: Home team statistics
            away_data: Away team statistics
            
        Returns:
            Dictionary containing all predictions
        """
        # Calculate team strengths
        home_off, home_def = self.calculate_team_strength(home_data)
        away_off, away_def = self.calculate_team_strength(away_data)
        
        # Calculate expected goals with home advantage
        home_advantage = 1.15
        home_expected_goals = home_data['xg'] * home_advantage * (1 / (away_def + 0.5))
        away_expected_goals = away_data['xg'] * (1 / (home_def + 0.5))
        
        # Predict win probabilities
        win_probs = self._calculate_win_probabilities(home_expected_goals, away_expected_goals)
        
        # Predict both teams to score
        btts = self._predict_btts(home_expected_goals, away_expected_goals, home_data, away_data)
        
        # Predict over/under goals
        over_under = self._predict_over_under(home_expected_goals, away_expected_goals)
        
        # Predict most likely scorelines
        scorelines = self._predict_scorelines(home_expected_goals, away_expected_goals)
        
        return {
            'win_probabilities': win_probs,
            'btts': btts,
            'over_under': over_under,
            'scorelines': scorelines,
            'expected_goals': {
                'home': round(home_expected_goals, 2),
                'away': round(away_expected_goals, 2),
                'total': round(home_expected_goals + away_expected_goals, 2)
            }
        }
    
    def _calculate_win_probabilities(self, home_xg: float, away_xg: float) -> Dict[str, float]:
        """Calculate probabilities for home win, draw, and away win using Poisson distribution."""
        # Use Poisson distribution to calculate probability of each scoreline
        home_win_prob = 0.0
        draw_prob = 0.0
        away_win_prob = 0.0
        
        # Calculate probabilities for realistic scorelines (0-7 goals each)
        for home_goals in range(8):
            for away_goals in range(8):
                # Poisson probability for each team's goals
                home_goal_prob = stats.poisson.pmf(home_goals, home_xg)
                away_goal_prob = stats.poisson.pmf(away_goals, away_xg)
                
                # Joint probability of this exact scoreline
                scoreline_prob = home_goal_prob * away_goal_prob
                
                # Add to appropriate outcome
                if home_goals > away_goals:
                    home_win_prob += scoreline_prob
                elif home_goals < away_goals:
                    away_win_prob += scoreline_prob
                else:
                    draw_prob += scoreline_prob
        
        # Normalize to ensure they sum to 100% (handle rounding)
        total = home_win_prob + draw_prob + away_win_prob
        
        return {
            'home_win': round((home_win_prob / total) * 100, 1),
            'draw': round((draw_prob / total) * 100, 1),
            'away_win': round((away_win_prob / total) * 100, 1)
        }
    
    def _predict_btts(self, home_xg: float, away_xg: float, 
                      home_data: Dict, away_data: Dict) -> Dict[str, any]:
        """Predict if both teams will score using Poisson distribution."""
        # Calculate probability that home team scores at least 1 goal
        # P(X >= 1) = 1 - P(X = 0)
        home_scoring_prob = 1 - stats.poisson.pmf(0, home_xg)
        
        # Calculate probability that away team scores at least 1 goal
        away_scoring_prob = 1 - stats.poisson.pmf(0, away_xg)
        
        # Factor in defensive vulnerabilities (xGOT conceded indicates defensive weakness)
        # Higher xGOT conceded means opponent is more likely to score
        # Apply modest adjustment factor based on goalkeeper performance
        home_def_factor = min(1.15, 1 + (home_data['xgot_conceded'] - 1.0) * 0.1)
        away_def_factor = min(1.15, 1 + (away_data['xgot_conceded'] - 1.0) * 0.1)
        
        # Adjust probabilities with defensive factors and ensure they stay in [0,1]
        home_scoring_prob = min(0.99, home_scoring_prob * away_def_factor)
        away_scoring_prob = min(0.99, away_scoring_prob * home_def_factor)
        
        # Probability both teams score (independent events)
        btts_prob = home_scoring_prob * away_scoring_prob
        
        # Convert to percentage (guaranteed to be in [0, 100])
        btts_percentage = round(btts_prob * 100, 1)
        
        return {
            'prediction': 'Yes' if btts_percentage >= 50 else 'No',
            'probability': btts_percentage
        }
    
    def _predict_over_under(self, home_xg: float, away_xg: float) -> Dict[str, Dict]:
        """Predict over/under goals for various thresholds."""
        total_xg = home_xg + away_xg
        
        results = {}
        for threshold in [1.5, 2.5, 3.5]:
            # Use Poisson distribution for more accurate probability
            lambda_param = total_xg
            
            # Calculate probability of over threshold
            over_prob = 1 - stats.poisson.cdf(threshold - 0.5, lambda_param)
            over_percentage = round(over_prob * 100, 1)
            
            results[f'{threshold}'] = {
                'over': over_percentage,
                'under': round(100 - over_percentage, 1),
                'prediction': 'Over' if over_percentage >= 50 else 'Under'
            }
        
        return results
    
    def _predict_scorelines(self, home_xg: float, away_xg: float) -> List[Dict]:
        """Predict the 3 most likely scorelines."""
        scoreline_probs = []
        
        # Calculate probabilities for realistic scorelines (0-5 goals each)
        for home_goals in range(6):
            for away_goals in range(6):
                # Poisson probability for each team's goals
                home_prob = stats.poisson.pmf(home_goals, home_xg)
                away_prob = stats.poisson.pmf(away_goals, away_xg)
                
                # Joint probability
                prob = home_prob * away_prob
                
                scoreline_probs.append({
                    'scoreline': f'{home_goals}-{away_goals}',
                    'probability': prob
                })
        
        # Sort by probability and get top 3
        scoreline_probs.sort(key=lambda x: x['probability'], reverse=True)
        top_3 = scoreline_probs[:3]
        
        # Convert to percentages
        for scoreline in top_3:
            scoreline['probability'] = round(scoreline['probability'] * 100, 1)
        
        return top_3
