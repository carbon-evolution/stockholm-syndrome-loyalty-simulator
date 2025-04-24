import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.colors import LinearSegmentedColormap

class LoyaltyTracker:
    def __init__(self, name):
        self.name = name
        self.history = []
        self.loyalty_states = {
            "Healthy": {"color": "#2ecc71", "threshold": 75},
            "Stable": {"color": "#3498db", "threshold": 60},
            "At Risk": {"color": "#f1c40f", "threshold": 50},
            "Unstable": {"color": "#e67e22", "threshold": 40},
            "Toxic": {"color": "#e74c3c", "threshold": 0}
        }

    def calculate_metrics(self, satisfaction, dependency, manipulation):
        """Calculate comprehensive loyalty metrics"""
        # Normalize inputs
        satisfaction = max(0, min(10, satisfaction))
        dependency = max(0, min(10, dependency))
        manipulation = max(0, min(10, manipulation))

        # Calculate core metrics
        true_satisfaction = satisfaction * (1 - manipulation/15)
        emotional_vulnerability = min(10, dependency * 0.7 + manipulation * 0.3)
        autonomy = max(0, 10 - (dependency * 0.5 + manipulation * 0.5))
        power_imbalance = min(10, manipulation * 0.6 + dependency * 0.4)

        # Calculate health score (0-100)
        health_score = (
            (true_satisfaction/10 * 30) +  # 30% weight
            (autonomy/10 * 25) +          # 25% weight
            ((10-dependency)/10 * 25) +   # 25% weight
            ((10-power_imbalance)/10 * 20) # 20% weight
        )

        # Calculate risk factors
        risk_factors = []
        if manipulation > 6: risk_factors.append("High Manipulation")
        if dependency > 7: risk_factors.append("High Dependency")
        if true_satisfaction < 4: risk_factors.append("Low Satisfaction")
        if autonomy < 3: risk_factors.append("Low Autonomy")

        # Determine loyalty state
        loyalty_state = "Toxic"  # default state
        for state, props in self.loyalty_states.items():
            if health_score >= props["threshold"]:
                loyalty_state = state
                break

        return {
            'timestamp': len(self.history) + 1,
            'satisfaction': satisfaction,
            'true_satisfaction': round(true_satisfaction, 2),
            'dependency': dependency,
            'manipulation': manipulation,
            'emotional_vulnerability': round(emotional_vulnerability, 2),
            'autonomy': round(autonomy, 2),
            'power_imbalance': round(power_imbalance, 2),
            'health_score': round(health_score, 1),
            'loyalty_state': loyalty_state,
            'risk_factors': risk_factors
        }

    def add_measurement(self, satisfaction, dependency, manipulation):
        """Add a new measurement point"""
        metrics = self.calculate_metrics(satisfaction, dependency, manipulation)
        self.history.append(metrics)

    def plot_analysis(self):
        """Create an advanced visualization of the loyalty analysis"""
        if not self.history:
            print("No data to plot")
            return

        # Create figure and subplots with adjusted spacing
        fig = plt.figure(figsize=(16, 9))
        gs = plt.GridSpec(2, 1, height_ratios=[4, 1], hspace=0.2)
        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])

        # Adjust the layout to prevent text cutoff
        plt.subplots_adjust(right=0.85, left=0.1, top=0.93, bottom=0.12)

        # Get data for plotting
        x = [h['timestamp'] for h in self.history]
        metrics = {
            'Satisfaction': ([h['satisfaction'] for h in self.history], '#2ecc71', 'o', 1.0),
            'True Satisfaction': ([h['true_satisfaction'] for h in self.history], '#27ae60', 's', 0.8),
            'Dependency': ([h['dependency'] for h in self.history], '#3498db', '^', 1.0),
            'Manipulation': ([h['manipulation'] for h in self.history], '#e74c3c', 'D', 1.0),
            'Emotional Vulnerability': ([h['emotional_vulnerability'] for h in self.history], '#9b59b6', 'p', 0.7),
            'Autonomy': ([h['autonomy'] for h in self.history], '#f1c40f', 'h', 0.7)
        }

        # Plot main metrics with smooth lines
        for label, (values, color, marker, alpha) in metrics.items():
            # Create smooth line using interpolation
            x_smooth = np.linspace(min(x), max(x), 200)
            y_smooth = np.interp(x_smooth, x, values)
            
            # Plot smooth line and points
            ax1.plot(x_smooth, y_smooth, color=color, alpha=alpha*0.6, linewidth=2)
            ax1.scatter(x, values, color=color, marker=marker, s=100, 
                       label=label, zorder=5, alpha=alpha)

        # Plot health score in background
        health_scores = [h['health_score']/10 for h in self.history]
        ax1.fill_between(x, 0, health_scores, color='#ecf0f1', alpha=0.2, 
                        label='Health Score Zone')

        # Add loyalty state indicators with improved spacing
        for i, h in enumerate(self.history):
            state_color = self.loyalty_states[h['loyalty_state']]['color']
            # Add state marker
            ax1.scatter(x[i], health_scores[i], color=state_color, s=150, zorder=4,
                       marker='o', edgecolor='white', linewidth=2)
            
            # Calculate vertical offset based on position
            if i % 2 == 0:
                offset = 0.8
            else:
                offset = -1.5
            
            # Add state label with risk factors
            label = f"{h['loyalty_state']}\nHealth: {h['health_score']}%"
            if h['risk_factors']:
                label += f"\n{', '.join(h['risk_factors'])}"
            
            bbox_props = dict(
                boxstyle='round,pad=0.5',
                facecolor='white',
                edgecolor=state_color,
                alpha=0.8
            )
            
            ax1.annotate(label, 
                        xy=(x[i], health_scores[i]),
                        xytext=(0, offset),
                        textcoords='offset points',
                        ha='center',
                        va='bottom' if offset > 0 else 'top',
                        fontsize=8,
                        bbox=bbox_props,
                        zorder=6)

        # Style the main plot
        ax1.set_title(f"Loyalty Analysis for {self.name}", 
                     pad=20, fontsize=14, fontweight='bold')
        ax1.set_ylabel("Value (0-10)", fontsize=12)
        ax1.grid(True, alpha=0.2, linestyle='--')
        
        # Adjust legend position and style
        legend = ax1.legend(bbox_to_anchor=(1.02, 1), 
                          loc='upper left',
                          borderaxespad=0,
                          frameon=True,
                          fancybox=True,
                          shadow=True,
                          fontsize=10)
        legend.get_frame().set_alpha(0.8)
        
        ax1.set_ylim(-0.5, 11)
        ax1.set_xlim(min(x) - 0.2, max(x) + 0.2)

        # Create health score timeline in bottom subplot with improved gradient
        health_gradient = np.array([h['health_score'] for h in self.history])
        im = ax2.imshow([health_gradient], 
                       aspect='auto',
                       cmap='RdYlGn',
                       extent=[min(x), max(x), 0, 1],
                       vmin=0,
                       vmax=100)
        
        # Add loyalty state markers to timeline with improved visibility
        for i, h in enumerate(self.history):
            ax2.text(x[i], 0.5, h['loyalty_state'],
                    ha='center',
                    va='center',
                    fontsize=9,
                    fontweight='bold',
                    bbox=dict(facecolor='white',
                             alpha=0.8,
                             edgecolor='none',
                             pad=0.5))

        # Style the timeline
        ax2.set_yticks([])
        ax2.set_xlabel("Time Steps", fontsize=12)
        cbar = plt.colorbar(im, ax=ax2, label='Health Score %', 
                          orientation='horizontal',
                          pad=0.35)
        cbar.ax.tick_params(labelsize=10)

        # Add legend for loyalty states with improved styling
        legend_elements = [Patch(facecolor=props['color'],
                               label=state,
                               alpha=0.8,
                               edgecolor='white',
                               linewidth=1)
                         for state, props in self.loyalty_states.items()]
        state_legend = ax2.legend(handles=legend_elements,
                                title="Loyalty States",
                                title_fontsize=10,
                                bbox_to_anchor=(1.02, 1),
                                loc='upper left',
                                borderaxespad=0,
                                frameon=True,
                                fancybox=True,
                                shadow=True,
                                fontsize=9)
        state_legend.get_frame().set_alpha(0.8)

        # Ensure proper layout
        plt.tight_layout()
        plt.show()

# Example usage with more detailed simulation
tracker = LoyaltyTracker("Customer Analysis")

# Simulate a progression of states with smoother transitions
scenarios = [
    (7, 3, 2),  # Initially healthy
    (6.5, 3.5, 2.5),  # Gradual change
    (6, 4, 3),  # Slight decline
    (5.5, 4.5, 3.5),  # Continuing decline
    (5, 5, 4),  # Growing dependency
    (4.5, 5.5, 4.5),  # Increasing risk
    (4, 6, 5),  # High risk
    (3.5, 6.5, 5.5),  # Deteriorating
    (3, 7, 6),  # Critical state
    (2.5, 7.5, 6.5),  # Near toxic
    (2, 8, 7),  # Toxic state
    (2.5, 7.5, 6.5),  # Small improvement
    (3, 7, 6),  # Slight recovery
    (3.5, 6.5, 5.5),  # Continuing recovery
    (4, 6, 5),  # Improvement
    (4.5, 5.5, 4.5),  # Steady improvement
    (5, 5, 4),  # Stabilizing
    (5.5, 4.5, 3.5),  # Good progress
    (6, 4, 3),  # Nearly stable
    (6.5, 3.5, 2.5),  # Almost healthy
    (7, 3, 2),  # Return to healthy
]

# Add each scenario to the tracker
for satisfaction, dependency, manipulation in scenarios:
    tracker.add_measurement(satisfaction, dependency, manipulation)

# Generate the analysis plot
tracker.plot_analysis()
