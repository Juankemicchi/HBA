import matplotlib.pyplot as plt

def plot_prop_chart(df, player_name, prop_name, line_value):
    df_plot = df.copy().sort_values('GAME_DATE')   # Orden cronológico
    
    df_plot['Hit'] = df_plot[prop_name] > line_value
    colors = ['green' if hit else 'red' for hit in df_plot['Hit']]
    
    plt.figure(figsize=(14, 8))
    bars = plt.bar(range(len(df_plot)), df_plot[prop_name], color=colors, alpha=0.9, edgecolor='black')
    
    plt.axhline(y=line_value, color='blue', linestyle='--', linewidth=2.5, label=f'Línea: {line_value}')
    
    plt.title(f'{player_name} - {prop_name} (Últimos {len(df_plot)} juegos)', fontsize=16, fontweight='bold')
    plt.xlabel('Juegos (más antiguo → más reciente)')
    plt.ylabel(prop_name)
    plt.legend()
    
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                 f'{height:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    return plt