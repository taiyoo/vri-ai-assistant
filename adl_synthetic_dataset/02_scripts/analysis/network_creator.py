#!/usr/bin/env python3
"""
Create a visual network graph of care interactions
"""
import json
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def create_care_network_visual():
    # Load data
    with open('../../01_data/raw/synthetic_adl_scenarios_openai.json', 'r') as f:
        data = json.load(f)
    
    # Extract dialogue data
    dialogue_data = []
    for i, scenario in enumerate(data):
        if 'Scenario' in scenario:
            scenario_data = scenario['Scenario']
        else:
            scenario_data = scenario
        
        dialogue_key = 'Dialogue' if 'Dialogue' in scenario_data else 'dialogue'
        
        if dialogue_key in scenario_data and isinstance(scenario_data[dialogue_key], list):
            for j, turn in enumerate(scenario_data[dialogue_key]):
                if isinstance(turn, dict):
                    dialogue_data.append({
                        'scenario_id': i,
                        'turn_number': j,
                        'speaker': turn.get('Speaker', 'unknown'),
                        'intent': turn.get('Intent', ''),
                        'text': turn.get('Utterance', '')
                    })
    
    dialogue_df = pd.DataFrame(dialogue_data)
    dialogue_df = dialogue_df[dialogue_df['intent'] != '']
    
    # Simplify intents into categories
    def categorize_intent(intent):
        intent_lower = intent.lower()
        if 'greet' in intent_lower or 'hello' in intent_lower:
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
    
    dialogue_df['intent_category'] = dialogue_df['intent'].apply(categorize_intent)
    
    # Create network graph
    G = nx.DiGraph()
    
    # Track transitions between intent categories
    for scenario_id in dialogue_df['scenario_id'].unique():
        scenario_dialogue = dialogue_df[dialogue_df['scenario_id'] == scenario_id].sort_values('turn_number')
        intents = scenario_dialogue['intent_category'].tolist()
        
        for i in range(len(intents) - 1):
            current = intents[i]
            next_intent = intents[i + 1]
            
            if G.has_edge(current, next_intent):
                G[current][next_intent]['weight'] += 1
            else:
                G.add_edge(current, next_intent, weight=1)
    
    # Create visualization
    plt.figure(figsize=(16, 12))
    
    # Use spring layout for better positioning
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
    
    # Calculate node sizes based on degree
    node_sizes = [G.degree(node) * 200 for node in G.nodes()]
    
    # Get edge weights
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
    
    # Normalize edge weights for visualization
    max_weight = max(edge_weights) if edge_weights else 1
    normalized_weights = [w/max_weight * 5 for w in edge_weights]
    
    # Define colors for different intent categories
    color_map = {
        'Greeting': '#FF6B6B',
        'Response': '#4ECDC4', 
        'Acknowledgment': '#45B7D1',
        'Assistance': '#96CEB4',
        'Reassurance': '#FFEAA7',
        'Assessment': '#DDA0DD',
        'Instruction': '#98D8C8',
        'Inquiry': '#F7DC6F',
        'Care Action': '#AED6F1'
    }
    
    node_colors = [color_map.get(node, '#CCCCCC') for node in G.nodes()]
    
    # Draw network
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, 
                          alpha=0.8, edgecolors='black', linewidths=1)
    
    nx.draw_networkx_edges(G, pos, width=normalized_weights, alpha=0.6, 
                          edge_color='gray', arrows=True, arrowsize=20, 
                          arrowstyle='->', connectionstyle='arc3,rad=0.1')
    
    # Add labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    # Add title and legend
    plt.title('Care Interaction Intent Flow Network\\n'
              f'Analyzing {len(dialogue_df)} dialogue turns from {dialogue_df["scenario_id"].nunique()} scenarios',
              fontsize=16, fontweight='bold', pad=20)
    
    # Create legend
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                 markerfacecolor=color, markersize=12, label=intent)
                      for intent, color in color_map.items() if intent in G.nodes()]
    
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05, 1))
    
    # Remove axes
    plt.axis('off')
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('/tmp/care_interaction_network.png', dpi=300, bbox_inches='tight')
    print("Network visualization saved to /tmp/care_interaction_network.png")
    
    # Show statistics
    print(f"\\nNetwork Statistics:")
    print(f"- Nodes (intent categories): {G.number_of_nodes()}")
    print(f"- Edges (transitions): {G.number_of_edges()}")
    print(f"- Most connected intents:")
    
    for node in sorted(G.nodes(), key=lambda x: G.degree(x), reverse=True)[:5]:
        in_degree = G.in_degree(node)
        out_degree = G.out_degree(node)
        print(f"  • {node}: {G.degree(node)} total ({in_degree} in, {out_degree} out)")
    
    print(f"\\nStrongest intent transitions:")
    edge_weights = [(u, v, d['weight']) for u, v, d in G.edges(data=True)]
    edge_weights.sort(key=lambda x: x[2], reverse=True)
    
    for u, v, weight in edge_weights[:8]:
        print(f"  • {u} → {v}: {weight} times")
    
    plt.show()
    
    return G

if __name__ == "__main__":
    create_care_network_visual()
