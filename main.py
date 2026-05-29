import streamlit as st
from nba_module import analyze_prop
from visualizations import plot_prop_chart

st.set_page_config(
    page_title="HBA - NBA Props",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🏀 HBA - NBA Player Props Analyzer")
st.markdown("**Análisis profesional • Datos en tiempo real**")

st.sidebar.header("⚙️ Configuración")

player = st.sidebar.text_input("Nombre del Jugador", "Jalen Brunson")
prop = st.sidebar.selectbox("Prop (Market)", 
    ["PTS", "REB", "AST", "PRA", "PR", "PA", "FG3M", "STL", "BLK", "TOV"])

common_lines = [round(i * 0.5, 1) for i in range(1, 192) if round(i * 0.5, 1) % 1 == 0.5]
line = st.sidebar.selectbox("Línea (Over/Under)", options=common_lines, 
                           index=common_lines.index(25.5) if 25.5 in common_lines else 0)

last_n = st.sidebar.slider("Últimos juegos", 10, 60, 25)

if st.sidebar.button("🔥 Analizar Prop", type="primary"):
    with st.spinner(f"Analizando {player}..."):
        df_combined, stats_reg, stats_play, stats_total = analyze_prop(player, prop, line, last_n)
        
        if df_combined is not None and not df_combined.empty:
            col1, col2 = st.columns([2.8, 1.2])
            
            with col1:
                fig = plot_prop_chart(df_combined, player, prop, line)
                st.pyplot(fig)
            
            with col2:
                st.subheader("📊 Estadísticas")
                st.metric("Regular Season", f"{stats_reg['avg']:.1f} | {stats_reg['hit_rate']:.1f}%")
                st.metric("Playoffs", f"{stats_play['avg']:.1f} | {stats_play['hit_rate']:.1f}%")
                st.metric("Total", f"{stats_total['avg']:.1f} | {stats_total['hit_rate']:.1f}%")
            
            st.subheader("📋 Últimos Juegos")
            display_df = df_combined[['GAME_DATE', prop, 'MATCHUP', 'WL']].copy()
            display_df['GAME_DATE'] = display_df['GAME_DATE'].dt.strftime('%d/%m/%Y')
            st.dataframe(display_df.head(20), use_container_width=True)
        else:
            st.error(f"❌ No se encontraron datos para **{player}**.")

st.caption("HBA - NBA Betting Analyzer | Actualizado en tiempo real")