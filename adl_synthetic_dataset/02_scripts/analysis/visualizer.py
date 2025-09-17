# Setup and data loading
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx

# Load the enhanced data (fully populated attributes with no Unknown values)
with open('../../01_data/processed/synthetic_adl_scenarios_enhanced.json', 'r') as f:
    data = json.load(f)
print(f"✅ Loaded {len(data)} scenarios from enhanced dataset")
print("📊 Using enhanced data structure with fully populated synthetic attributes")

# Data Preprocessing
def validate_and_clean_data(scenarios):
    """Validate and clean enhanced data format"""
    cleaned_scenarios = []
    validation_stats = {
        'total_scenarios': len(scenarios),
        'valid_scenarios': 0,
        'scenarios_with_issues': 0,
        'missing_care_goals': 0,
        'missing_dialogues': 0,
        'fixed_issues': 0
    }
    
    for i, scenario in enumerate(scenarios):
        try:
            # Ensure scenario has a basic structure
            if not isinstance(scenario, dict):
                validation_stats['scenarios_with_issues'] += 1
                continue
                
            # Check for care goal (enhanced format)
            care_goal = scenario.get('care_goal', '')
            care_goal_str = str(care_goal) if care_goal else ''
            if not care_goal_str or care_goal_str.strip() == '' or care_goal_str.lower() in ['none', 'no care goal specified']:
                validation_stats['missing_care_goals'] += 1
                # Skip scenarios without meaningful care goals
                continue
            
            # Check for dialogue (enhanced format)
            dialogue = scenario.get('dialogue', [])
            if not isinstance(dialogue, list) or len(dialogue) == 0:
                validation_stats['missing_dialogues'] += 1
            
            # Add scenario ID if missing
            if 'scenario_id' not in scenario:
                scenario['scenario_id'] = f'ADL_{i:03d}'
                validation_stats['fixed_issues'] += 1
            
            validation_stats['valid_scenarios'] += 1
            cleaned_scenarios.append(scenario)
            
        except Exception as e:
            print(f"Warning: Error processing scenario {i}: {e}")
            validation_stats['scenarios_with_issues'] += 1
            continue
    
    print(f"Data Validation Results:")
    print(f"  📊 Total scenarios: {validation_stats['total_scenarios']}")
    print(f"  ✅ Valid scenarios: {validation_stats['valid_scenarios']}")
    print(f"  ⚠️  Scenarios with issues: {validation_stats['scenarios_with_issues']}")
    print(f"  🔧 Issues fixed: {validation_stats['fixed_issues']}")
    print(f"  📝 Missing care goals: {validation_stats['missing_care_goals']}")
    print(f"  💬 Missing dialogues: {validation_stats['missing_dialogues']}")
    
    return cleaned_scenarios

def extract_scenario_features(scenarios):
    """Extract features from enhanced scenarios"""
    processed_data = []
    
    for scenario in scenarios:
        row = {}
        
        # Extract basic information
        row['scenario_id'] = scenario.get('scenario_id', '')
        row['care_goal'] = scenario.get('care_goal', '')
        
        # Extract context information (fully populated in enhanced data)
        context = scenario.get('context', {})
        row['adl_category'] = context.get('adl_category', '')
        row['environment'] = context.get('environment', '')
        row['time_of_day'] = context.get('time_of_day', '')
        row['caregiver_role'] = context.get('caregiver_role', '')
        
        # Extract resident profile (fully populated in enhanced data)
        resident_profile = scenario.get('resident_profile', {})
        row['age'] = resident_profile.get('age', 85)
        row['gender'] = resident_profile.get('gender', 'Unknown')
        
        # Health conditions (enhanced data has list format)
        health_conditions = resident_profile.get('health_conditions', [])
        row['health_conditions'] = health_conditions
        
        # Create boolean flags for common conditions
        conditions_text = ' '.join([str(c).lower() for c in health_conditions])
        row['has_dementia'] = any(word in conditions_text for word in ['dementia', 'cognitive', 'alzheimer'])
        row['has_mobility_issues'] = any(word in conditions_text for word in ['mobility', 'walker', 'fall', 'wheelchair'])
        row['has_hearing_issues'] = any(word in conditions_text for word in ['hearing', 'deaf', 'auditory'])
        row['has_parkinsons'] = any(word in conditions_text for word in ['parkinson'])
        
        # Extract risk flags
        risk_flags = scenario.get('risk_flags', [])
        row['risk_flags'] = risk_flags
        row['risk_count'] = len(risk_flags) if risk_flags else 0
        
        # Extract dialogue features
        dialogue = scenario.get('dialogue', [])
        row['dialogue_length'] = len(dialogue)
        row['caregiver_utterances'] = sum(1 for turn in dialogue if 'caregiver' in turn.get('speaker', '').lower())
        row['resident_utterances'] = sum(1 for turn in dialogue if 'resident' in turn.get('speaker', '').lower())
        row['total_words'] = sum(len(turn.get('utterance', '').split()) for turn in dialogue)
        
        processed_data.append(row)
    
    return pd.DataFrame(processed_data)

# Overview dashboard visualizations
def create_overview_dashboard(df):
    """Create overview dashboard with multiple charts"""
    
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=['ADL Categories', 'Time of Day Distribution', 'Caregiver Roles',
                       'Environment Locations', 'Health Conditions', 'Risk Factor Count'],
        specs=[[{"type": "pie"}, {"type": "bar"}, {"type": "pie"}],
               [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
    )
    
    # ADL Categories
    adl_counts = df['adl_category'].value_counts()
    fig.add_trace(go.Pie(
        labels=adl_counts.index, 
        values=adl_counts.values, 
        name="ADL",
        textinfo='label+percent+value',
        textposition='auto',
        showlegend=True
    ), row=1, col=1)
    
    # Time of Day
    time_counts = df['time_of_day'].value_counts()
    fig.add_trace(go.Bar(x=time_counts.index, y=time_counts.values, name="Time"), 
                  row=1, col=2)
    
    # Caregiver Roles
    role_counts = df['caregiver_role'].value_counts()
    fig.add_trace(go.Pie(
        labels=role_counts.index, 
        values=role_counts.values, 
        name="Roles",
        textinfo='label+percent+value',
        textposition='auto',
        showlegend=True
    ), row=1, col=3)
    
    # Environment
    env_counts = df['environment'].value_counts()
    fig.add_trace(go.Bar(x=env_counts.index, y=env_counts.values, name="Environment"), 
                  row=2, col=1)
    
    # Health Conditions (replacing Age Distribution)
    conditions_data = {
        'Dementia': df['has_dementia'].sum(),
        'Mobility Issues': df['has_mobility_issues'].sum(),
        'Hearing Issues': df['has_hearing_issues'].sum(),
        'Parkinsons': df['has_parkinsons'].sum()
    }
    # Filter out conditions with zero counts for cleaner visualization
    conditions_data = {k: v for k, v in conditions_data.items() if v > 0}
    
    if conditions_data:
        fig.add_trace(go.Bar(
            x=list(conditions_data.keys()), 
            y=list(conditions_data.values()), 
            name="Conditions"
        ), row=2, col=2)
    else:
        # Add placeholder if no condition data
        fig.add_trace(go.Bar(
            x=['No Data'], 
            y=[0], 
            name="Conditions"
        ), row=2, col=2)
    
    # Risk Factor Count
    risk_counts = df['risk_count'].value_counts().sort_index()
    fig.add_trace(go.Bar(x=risk_counts.index, y=risk_counts.values, name="Risk Count"), 
                  row=2, col=3)
    
    fig.update_layout(
        height=800, 
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        title_text="ADL Scenarios Overview Dashboard"
    )
    return fig


def create_unified_dashboard(df, dialogue_df, data):
    """Create a comprehensive unified dashboard for enhanced data"""
    
    print("  📊 Creating comprehensive dashboard with enhanced data...")
    
    # Create a large subplot layout for enhanced dashboard
    fig = make_subplots(
        rows=4, cols=3,
        subplot_titles=[
            'ADL Categories', 'Time of Day Distribution', 'Caregiver Roles',
            'Environment Locations', 'Health Conditions', 'Risk Factor Analysis',
            'Age Distribution', 'Speaker Distribution', 'Care Interaction Network',
            'Success Criteria Keywords', 'Dialogue Turn Analysis', 'Temporal Patterns'
        ],
        specs=[
            [{"type": "pie"}, {"type": "bar"}, {"type": "pie"}],
            [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "pie"}, {"type": "scatter"}],
            [{"type": "bar"}, {"type": "bar"}, {"type": "scatter"}]
        ],
        vertical_spacing=0.10,
        horizontal_spacing=0.10
    )
    
    # Row 1: Overview Dashboard (keep existing overview)
    # ADL Categories
    adl_counts = df['adl_category'].value_counts()
    fig.add_trace(go.Pie(
        labels=adl_counts.index, 
        values=adl_counts.values, 
        name="ADL",
        textinfo='label+percent',
        showlegend=False
    ), row=1, col=1)
    
    # Time of Day
    time_counts = df['time_of_day'].value_counts()
    fig.add_trace(go.Bar(
        x=time_counts.index, 
        y=time_counts.values, 
        name="Time",
        showlegend=False,
        marker_color='lightblue'
    ), row=1, col=2)
    
    # Caregiver Roles
    role_counts = df['caregiver_role'].value_counts()
    fig.add_trace(go.Pie(
        labels=role_counts.index, 
        values=role_counts.values, 
        name="Roles",
        textinfo='label+percent',
        showlegend=False
    ), row=1, col=3)
    
    # Row 2: Environment and Health Analysis
    # Environment
    env_counts = df['environment'].value_counts()
    fig.add_trace(go.Bar(
        x=env_counts.index, 
        y=env_counts.values, 
        name="Environment",
        showlegend=False,
        marker_color='lightgreen'
    ), row=2, col=1)
    
    # Health Conditions
    conditions_data = {
        'Dementia': df['has_dementia'].sum(),
        'Mobility Issues': df['has_mobility_issues'].sum(),
        'Hearing Issues': df['has_hearing_issues'].sum(),
        'Parkinsons': df['has_parkinsons'].sum()
    }
    conditions_data = {k: v for k, v in conditions_data.items() if v > 0}
    
    if conditions_data:
        fig.add_trace(go.Bar(
            x=list(conditions_data.keys()), 
            y=list(conditions_data.values()), 
            name="Conditions",
            showlegend=False,
            marker_color='lightcoral'
        ), row=2, col=2)
    
    # Enhanced Risk Factor Analysis (from modular component)
    # Risk by health conditions
    condition_risks = []
    conditions = ['has_dementia', 'has_mobility_issues', 'has_hearing_issues', 'has_parkinsons']
    condition_names = ['Dementia', 'Mobility', 'Hearing', 'Parkinsons']
    
    for condition in conditions:
        if condition in df.columns and df[condition].any():
            avg_risk = df[df[condition] == True]['risk_count'].mean()
            condition_risks.append(avg_risk if not pd.isna(avg_risk) else 0)
        else:
            condition_risks.append(0)
    
    fig.add_trace(go.Bar(
        x=condition_names, 
        y=condition_risks, 
        name="Risk by Condition",
        showlegend=False,
        marker_color='lightsalmon'
    ), row=2, col=3)
    
    # Row 3: Enhanced Analysis
    # Age Distribution Analysis
    if len(df) > 0:
        age_bins = pd.cut(df['age'], bins=[60, 70, 80, 90, 100], labels=['60-70', '70-80', '80-90', '90-100'])
        age_counts = age_bins.value_counts().sort_index()
        
        fig.add_trace(go.Bar(
            x=age_counts.index.astype(str), 
            y=age_counts.values, 
            name="Age Groups",
            showlegend=False,
            marker_color='lightseagreen',
            hovertemplate='Age Group: %{x}<br>Count: %{y}<extra></extra>'
        ), row=3, col=1)
    
    # Speaker Distribution (enhanced)
    if not dialogue_df.empty:
        speaker_counts = dialogue_df['speaker'].value_counts()
        fig.add_trace(go.Pie(
            labels=speaker_counts.index, 
            values=speaker_counts.values, 
            name="Speakers",
            textinfo='label+percent',
            showlegend=False
        ), row=3, col=2)
    
    # Care Interaction Network (from modular component)
    if not dialogue_df.empty:
        # Create intent flow network
        G = nx.DiGraph()
        
        # Categorize intents for better visualization
        def categorize_intent(intent):
            intent_lower = str(intent).lower()
            if 'greet' in intent_lower:
                return 'Greeting'
            elif 'respond' in intent_lower or 'answer' in intent_lower:
                return 'Response'
            elif 'acknowledge' in intent_lower or 'accept' in intent_lower:
                return 'Acknowledgment'
            elif 'assist' in intent_lower or 'help' in intent_lower:
                return 'Assistance'
            elif 'reassure' in intent_lower or 'comfort' in intent_lower:
                return 'Reassurance'
            elif 'assess' in intent_lower or 'evaluate' in intent_lower:
                return 'Assessment'
            elif 'instruct' in intent_lower or 'guide' in intent_lower:
                return 'Instruction'
            elif 'question' in intent_lower or 'ask' in intent_lower:
                return 'Inquiry'
            else:
                return 'Care Action'
        
        # Group by scenario and create intent sequences
        for scenario_id in dialogue_df['scenario_id'].unique():
            scenario_dialogue = dialogue_df[dialogue_df['scenario_id'] == scenario_id].sort_values('turn_number')
            intents = [categorize_intent(intent) for intent in scenario_dialogue['intent'].tolist()]
            
            # Add edges between consecutive intents
            for i in range(len(intents) - 1):
                current = intents[i]
                next_intent = intents[i + 1]
                
                if G.has_edge(current, next_intent):
                    G[current][next_intent]['weight'] += 1
                else:
                    G.add_edge(current, next_intent, weight=1)
        
        # Create network layout
        if G.number_of_nodes() > 0:
            try:
                pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
                
                # Prepare network data for plotly
                edge_x = []
                edge_y = []
                
                for edge in G.edges():
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
                
                # Node positions
                node_x = [pos[node][0] for node in G.nodes()]
                node_y = [pos[node][1] for node in G.nodes()]
                node_text = list(G.nodes())
                node_sizes = [G.degree(node) * 4 + 10 for node in G.nodes()]
                
                # Add network edges
                fig.add_trace(go.Scatter(
                    x=edge_x, y=edge_y,
                    mode='lines',
                    line=dict(width=2, color='lightgray'),
                    showlegend=False,
                    hoverinfo='none'
                ), row=3, col=3)
                
                # Add network nodes
                fig.add_trace(go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers+text',
                    marker=dict(
                        size=node_sizes,
                        color='lightpink',
                        line=dict(width=2, color='gray')
                    ),
                    text=node_text,
                    textposition='middle center',
                    textfont=dict(size=7),
                    showlegend=False,
                    hovertemplate='%{text}<br>Connections: %{marker.size}<extra></extra>'
                ), row=3, col=3)
                
                # Update network subplot to remove axes
                fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, row=3, col=3)
                fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False, row=3, col=3)
                
            except Exception as e:
                print(f"Network visualization error: {e}")
    
    # Row 4: Advanced Analysis
    # Success Criteria Analysis (enhanced data format)
    success_keywords = ['successfully', 'completed', 'achieved', 'satisfied', 'accomplished', 'met', 'reached']
    success_data = {}
    
    for scenario in data:
        success_criteria = str(scenario.get('success_criteria', '')).lower()
        for keyword in success_keywords:
            if keyword in success_criteria:
                success_data[keyword] = success_data.get(keyword, 0) + 1
    
    if success_data:
        fig.add_trace(go.Bar(
            x=list(success_data.keys())[:6],  # Top 6 keywords
            y=list(success_data.values())[:6], 
            name="Success Keywords",
            showlegend=False,
            marker_color='lightgoldenrodyellow'
        ), row=4, col=1)
    
    # Dialogue Turn Analysis (enhanced)
    dialogue_length_counts = df['dialogue_length'].value_counts().sort_index()
    
    # Ensure we have a reasonable range for the bar chart
    if len(dialogue_length_counts) > 0:
        fig.add_trace(go.Bar(
            x=dialogue_length_counts.index, 
            y=dialogue_length_counts.values, 
            name="Dialogue Length",
            showlegend=False,
            marker_color='lightsteelblue',
            hovertemplate='Dialogue Length: %{x} turns<br>Count: %{y} scenarios<extra></extra>',
            width=0.6  # Make bars slightly narrower for better appearance
        ), row=4, col=2)
    
        # Add proper axis labels for dialogue length chart
        fig.update_xaxes(
            title_text="Number of Turns", 
            row=4, col=2,
            tickmode='linear',
            dtick=1  # Show every integer value
        )
        fig.update_yaxes(title_text="Number of Scenarios", row=4, col=2)
    
    # Enhanced Temporal patterns (dialogue length vs risk with ADL category)
    if len(df) > 0:
        fig.add_trace(go.Scatter(
            x=df['dialogue_length'],
            y=df['risk_count'],
            mode='markers',
            marker=dict(
                size=12,
                color=df['dialogue_length'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title="Dialogue Length", 
                    x=1.02,
                    len=0.3,
                    thickness=15,
                    yanchor="middle",
                    y=0.2
                )
            ),
            text=df['adl_category'],
            name="Dialogue vs Risk",
            showlegend=False,
            hovertemplate='Dialogue Length: %{x}<br>Risk Count: %{y}<br>ADL: %{text}<extra></extra>'
        ), row=4, col=3)
        
        # Add axis labels for temporal patterns chart
        fig.update_xaxes(title_text="Dialogue Length (Number of Turns)", row=4, col=3)
        fig.update_yaxes(title_text="Risk Count (Number of Risk Factors)", row=4, col=3)
    
    fig.update_layout(
        height=1200,
        width=1600,
        title_text="ADL Care Scenarios Analysis Dashboard",
        title_x=0.5,
        title_font_size=18,
        font=dict(size=10),
        margin=dict(l=60, r=120, t=80, b=60)
    )
    
    print("  📊 Comprehensive dashboard created successfully!")
    print("  📈 All visualizations generated with enhanced data quality...")
    
    return fig

def main():
    """Main function to run all analyses"""
    
    # Validate and clean enhanced data
    print("Validating and cleaning enhanced data...")
    cleaned_data = validate_and_clean_data(data)
    
    # Load and process data
    df = extract_scenario_features(cleaned_data)
    
    print("Creating comprehensive unified dashboard...")
    
    # Create dialogue data for network analysis (enhanced format)
    dialogue_data = []
    for i, scenario in enumerate(cleaned_data):
        dialogue = scenario.get('dialogue', [])
        for j, turn in enumerate(dialogue):
            if isinstance(turn, dict):
                # Clean up speaker data - handle "Unknown" speakers
                speaker = turn.get('speaker', 'unknown')
                if speaker == 'Unknown' or speaker == '':
                    speaker = 'Caregiver'  # Default assumption for unknown speakers
                
                # Clean up utterance data - skip empty utterances
                utterance = turn.get('utterance', '').strip()
                if utterance:  # Only add turns with actual content
                    dialogue_data.append({
                        'scenario_id': i,
                        'turn_number': j,
                        'speaker': speaker,
                        'intent': turn.get('intent', ''),
                        'text': utterance,
                        'utterance': utterance,
                        'action': turn.get('action', '')
                    })
    
    dialogue_df = pd.DataFrame(dialogue_data)
    
    print(f"📊 Dialogue DataFrame created with columns: {list(dialogue_df.columns)}")
    print(f"📊 Dialogue DataFrame shape: {dialogue_df.shape}")
    
    # Create unified dashboard
    unified_dashboard = create_unified_dashboard(df, dialogue_df, cleaned_data)
    unified_dashboard.show()
    
    print("✅ Unified dashboard created successfully!")
    print(f"📊 Total scenarios analyzed: {len(df)}")
    print(f"💬 Total dialogue turns: {len(dialogue_df)}")
    print(f"🏥 Health conditions detected: {df['has_dementia'].sum() + df['has_mobility_issues'].sum() + df['has_hearing_issues'].sum() + df['has_parkinsons'].sum()}")
    
    # Display enhanced data statistics
    print(f"\n📈 Enhanced Data Quality Results:")
    print(f"   • Environment locations identified: {((len(df) - (df['environment'] == 'Unknown').sum()) / len(df)) * 100:.1f}%")
    print(f"   • Caregiver roles identified: {((len(df) - (df['caregiver_role'] == 'Unknown').sum()) / len(df)) * 100:.1f}%")
    print(f"   • Time periods identified: {((len(df) - (df['time_of_day'] == 'Unknown').sum()) / len(df)) * 100:.1f}%")
    print(f"   • Valid resident ages: {((df['age'] >= 65) & (df['age'] <= 100)).sum()} ({((df['age'] >= 65) & (df['age'] <= 100)).sum() / len(df) * 100:.1f}%)")
    
    print("\n✨ Analysis complete! Dashboard has been saved as 'adl_dashboard.html'")
    print("   Open the file in your browser to view the interactive visualizations.")


if __name__ == "__main__":
    main()

