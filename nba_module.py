from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd
from nba_api.stats.library.parameters import SeasonAll
import os
import pickle
from datetime import datetime

CACHE_DIR = "data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_player_id(player_name):
    """Búsqueda inteligente de jugadores"""
    name = str(player_name).strip().lower()
    
    # Búsqueda exacta
    player_dict = players.find_players_by_full_name(player_name)
    if player_dict:
        return player_dict[0]['id']
    
    # Búsqueda flexible
    all_players = players.get_players()
    matches = [p for p in all_players if name in p['full_name'].lower()]
    
    if not matches:
        raise ValueError(f"❌ No se encontró '{player_name}'. Prueba: KAT, Towns, LeBron, Curry, Edwards, etc.")
    
    # Tomar el más reciente
    best = sorted(matches, key=lambda x: x.get('id', 0), reverse=True)[0]
    print(f"✅ Usando: {best['full_name']}")
    return best['id']


def get_player_games(player_name, season_type="Regular Season", last_n=40):
    try:
        player_id = get_player_id(player_name)
    except ValueError as e:
        print(e)
        return pd.DataFrame()

    cache_file = f"{CACHE_DIR}/{player_id}_{season_type}.pkl"
    
    # === Caché inteligente (12 horas) ===
    use_cache = False
    if os.path.exists(cache_file):
        age = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))).seconds
        if age < 43200:  # 12 horas
            use_cache = True
    
    if use_cache:
        with open(cache_file, 'rb') as f:
            df = pickle.load(f)
        print(f"✅ Caché usado: {season_type}")
        return df.head(last_n)
    
    # Descargar datos frescos
    print(f"🔄 Descargando datos frescos de {season_type}...")
    try:
        logs = playergamelog.PlayerGameLog(
            player_id=player_id,
            season=SeasonAll.all,
            season_type_all_star=season_type
        )
        df = logs.get_data_frames()[0]
    except Exception as e:
        print(f"Error API: {e}")
        return pd.DataFrame()
    
    if df.empty:
        return pd.DataFrame()
    
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], format="%b %d, %Y", errors='coerce')
    df = df.sort_values('GAME_DATE', ascending=False).reset_index(drop=True)
    
    cols = ['GAME_DATE', 'PTS', 'REB', 'AST', 'FG3M', 'STL', 'BLK', 'TOV', 'PLUS_MINUS', 'MATCHUP', 'WL']
    df = df[cols]
    
    # Props compuestos
    df['PRA'] = df['PTS'] + df['REB'] + df['AST']
    df['PR'] = df['PTS'] + df['REB']
    df['PA'] = df['PTS'] + df['AST']
    
    # Guardar caché
    with open(cache_file, 'wb') as f:
        pickle.dump(df, f)
    
    return df.head(last_n)


def analyze_prop(player_name, prop='PTS', line=25.5, last_n=25):
    print(f"🔄 Analizando {player_name} - {prop}")
    
    df_reg = get_player_games(player_name, "Regular Season", last_n=last_n*2)
    df_play = get_player_games(player_name, "Playoffs", last_n=last_n*2)
    
    # Combinado para gráfica
    df_combined = pd.concat([df_play, df_reg]).drop_duplicates(subset=['GAME_DATE'])
    df_combined = df_combined.sort_values('GAME_DATE', ascending=False).head(last_n)
    
    if df_combined.empty:
        print("❌ Sin datos disponibles")
        return None, None, None, None
    
    if prop not in df_combined.columns:
        prop = 'PTS'
    
    # Función para calcular stats
    def get_stats(df):
        if df.empty:
            return {"avg": 0.0, "hit_rate": 0.0, "games": 0}
        df_temp = df.copy()
        df_temp['Over'] = df_temp[prop] > line
        return {
            "avg": df_temp[prop].mean(),
            "hit_rate": df_temp['Over'].mean() * 100,
            "games": len(df_temp)
        }
    
    stats_reg = get_stats(df_reg)
    stats_play = get_stats(df_play)
    stats_total = get_stats(df_combined)
    
    print(f"Regular → Prom: {stats_reg['avg']:.1f} | Hit: {stats_reg['hit_rate']:.1f}% ({stats_reg['games']} juegos)")
    print(f"Playoffs → Prom: {stats_play['avg']:.1f} | Hit: {stats_play['hit_rate']:.1f}% ({stats_play['games']} juegos)")
    
    return df_combined, stats_reg, stats_play, stats_total