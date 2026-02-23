import random
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import json
import os
import sys
from pathlib import Path

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent / 'bots'))

# Configuração da página
st.set_page_config(
    page_title="Polymarket Trading Bot - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .positive { 
        color: #2ecc71; 
        font-weight: bold;
    }
    .negative { 
        color: #e74c3c; 
        font-weight: bold;
    }
    .neutral {
        color: #f39c12;
        font-weight: bold;
    }
    .strategy-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 4px solid #1f77b4;
    }
    .trade-row {
        background-color: #ffffff;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 5px;
        border: 1px solid #e0e0e0;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .status-active { background-color: #2ecc71; }
    .status-paused { background-color: #f39c12; }
    .status-inactive { background-color: #e74c3c; }
    .log-entry {
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        padding: 5px;
        border-bottom: 1px solid #eee;
    }
    .stButton>button {
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Configurações
INITIAL_BANKROLL = 1000.0  # $1000 USD conforme solicitado

# ==================== FUNÇÕES DE DADOS ====================

def init_database():
    """Inicializa database se não existir"""
    db_path = Path(__file__).parent.parent / 'bots' / 'data' / 'trading_bot.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not db_path.exists():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                market_id TEXT,
                strategy TEXT,
                direction TEXT,
                entry_price REAL,
                exit_price REAL,
                size_usd REAL,
                quantity REAL,
                entry_time TIMESTAMP,
                exit_time TIMESTAMP,
                status TEXT,
                pnl REAL,
                pnl_pct REAL,
                exit_reason TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_metrics (
                date TEXT PRIMARY KEY,
                starting_bankroll REAL,
                ending_bankroll REAL,
                daily_pnl REAL,
                daily_pnl_pct REAL,
                num_trades INTEGER,
                win_rate REAL,
                sharpe_ratio REAL,
                max_drawdown REAL
            )
        ''')
        
        conn.commit()
        conn.close()

def get_mock_data():
    """Retorna dados mock para demonstração"""
    dates = pd.date_range(start='2026-02-20', periods=10, freq='H')
    
    # Simular curva de equity
    equity = [INITIAL_BANKROLL]
    for i in range(1, 10):
        change = equity[-1] * random.uniform(-0.02, 0.03)
        equity.append(equity[-1] + change)
    
    return pd.DataFrame({
        'timestamp': dates,
        'equity': equity
    })

def get_trading_stats():
    """Retorna estatísticas de trading"""
    # Mock data - substituir por dados reais da DB
    return {
        'current_bankroll': 1045.50,
        'total_pnl': 45.50,
        'total_pnl_pct': 4.55,
        'daily_pnl': 12.30,
        'daily_pnl_pct': 1.19,
        'open_positions': 2,
        'total_trades': 8,
        'winning_trades': 5,
        'losing_trades': 3,
        'win_rate': 62.5,
        'avg_trade_pnl': 5.69
    }

def get_open_positions():
    """Retorna posições abertas"""
    return [
        {
            'market': 'BTC > $100K by March 2026',
            'strategy': 'Momentum',
            'entry': 0.65,
            'current': 0.72,
            'pnl_pct': 10.77,
            'size': 50.00,
            'time': '2h 15m',
            'direction': 'LONG'
        },
        {
            'market': 'Trump says "Russia" in SOTU',
            'strategy': 'MeanReversion',
            'entry': 0.12,
            'current': 0.14,
            'pnl_pct': 16.67,
            'size': 40.00,
            'time': '4h 30m',
            'direction': 'LONG'
        }
    ]

def get_strategy_status():
    """Retorna status das estratégias"""
    return [
        {'name': 'Momentum', 'pnl': 28.50, 'win_rate': 65, 'status': 'active', 'trades': 4},
        {'name': 'MeanReversion', 'pnl': 17.00, 'win_rate': 60, 'status': 'active', 'trades': 3},
        {'name': 'Scalping', 'pnl': 0, 'win_rate': 0, 'status': 'paused', 'trades': 0},
        {'name': 'Contrarian', 'pnl': 0, 'win_rate': 0, 'status': 'inactive', 'trades': 0}
    ]

def get_recent_trades():
    """Retorna trades recentes"""
    return [
        {'time': '14:32:15', 'strategy': 'Momentum', 'market': 'BTC_100K', 'action': 'BUY', 'price': 0.65, 'pnl': None},
        {'time': '14:28:10', 'strategy': 'MeanRev', 'market': 'Trump_Russia', 'action': 'BUY', 'price': 0.12, 'pnl': None},
        {'time': '13:45:22', 'strategy': 'Momentum', 'market': 'ETH_5000', 'action': 'SELL', 'price': 0.45, 'pnl': '+3.2%'},
        {'time': '12:15:08', 'strategy': 'MeanRev', 'market': 'China_Coup', 'action': 'SELL', 'price': 0.05, 'pnl': '+8.0%'},
        {'time': '11:30:45', 'strategy': 'Momentum', 'market': 'NATO_Expand', 'action': 'BUY', 'price': 0.78, 'pnl': '-2.1%'}
    ]

# ==================== PÁGINAS ====================

def page_overview():
    """Página principal - Overview"""
    st.markdown('<p class="main-header">📊 Polymarket Trading Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Monitorização em tempo real das estratégias de trading</p>', unsafe_allow_html=True)
    
    stats = get_trading_stats()
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${stats['current_bankroll']:,.2f}</div>
            <div class="metric-label">Capital Atual</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        pnl_class = "positive" if stats['total_pnl'] > 0 else "negative" if stats['total_pnl'] < 0 else "neutral"
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <div class="metric-value ${pnl_class}">${stats['total_pnl']:,.2f}</div>
            <div class="metric-label">Lucro Total ({stats['total_pnl_pct']:.2f}%)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div class="metric-value">{stats['win_rate']:.1f}%</div>
            <div class="metric-label">Win Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-value">{stats['open_positions']}</div>
            <div class="metric-label">Posições Abertas</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Layout em duas colunas
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Gráfico de equity
        st.subheader("📈 Evolução do Capital")
        
        # Dados mock - substituir por dados reais
        equity_data = get_mock_data()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=equity_data['timestamp'],
            y=equity_data['equity'],
            mode='lines',
            name='Equity',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.2)'
        ))
        
        fig.add_hline(y=INITIAL_BANKROLL, line_dash="dash", line_color="red", 
                     annotation_text="Capital Inicial")
        
        fig.update_layout(
            xaxis_title="Data/Hora",
            yaxis_title="USD",
            hovermode='x unified',
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Estratégias
        st.subheader("🎯 Performance por Estratégia")
        
        strategies = get_strategy_status()
        
        for strat in strategies:
            status_class = f"status-{strat['status']}"
            status_text = "🟢 ATIVO" if strat['status'] == 'active' else "🟡 PAUSADO" if strat['status'] == 'paused' else "🔴 INATIVO"
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.markdown(f"**{strat['name']}**")
            with col2:
                pnl_class = "positive" if strat['pnl'] > 0 else "negative" if strat['pnl'] < 0 else "neutral"
                st.markdown(f"<span class='{pnl_class}'>${strat['pnl']:,.2f}</span>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"{strat['win_rate']}% WR")
            with col4:
                st.markdown(status_text)
            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
    
    with col_right:
        # Posições abertas
        st.subheader("💰 Posições Abertas")
        
        positions = get_open_positions()
        
        for pos in positions:
            pnl_class = "positive" if pos['pnl_pct'] > 0 else "negative"
            st.markdown(f"""
            <div class="trade-row">
                <strong>{pos['market'][:30]}...</strong><br>
                <small>{pos['strategy']} | {pos['direction']}</small><br>
                Entrada: ${pos['entry']:.3f} → Atual: ${pos['current']:.3f}<br>
                <span class="{pnl_class}">{pos['pnl_pct']:+.2f}%</span> | ${pos['size']:.0f} | {pos['time']}
            </div>
            """, unsafe_allow_html=True)
        
        # Trades recentes
        st.subheader("📋 Trades Recentes")
        
        trades = get_recent_trades()
        
        for trade in trades[:5]:
            pnl_display = f"<span class='positive'>{trade['pnl']}</span>" if trade['pnl'] and '+' in trade['pnl'] else f"<span class='negative'>{trade['pnl']}</span>" if trade['pnl'] and '-' in trade['pnl'] else "⏳"
            st.markdown(f"""
            <div class="log-entry">
                <small>[{trade['time']}]</small> <strong>{trade['strategy']}</strong><br>
                {trade['action']} {trade['market']} @ ${trade['price']:.3f} {pnl_display}
            </div>
            """, unsafe_allow_html=True)

def page_analysis():
    """Página de análise detalhada"""
    st.header("📊 Análise Detalhada")
    
    # Tabs para diferentes análises
    tab1, tab2, tab3 = st.tabs(["Performance", "Distribuição", "Histórico"])
    
    with tab1:
        st.subheader("Métricas por Estratégia")
        
        strategy_metrics = pd.DataFrame({
            'Estratégia': ['Momentum', 'MeanReversion', 'Scalping', 'Contrarian'],
            'Trades': [4, 3, 0, 0],
            'Win Rate (%)': [65, 60, 0, 0],
            'P&L Total ($)': [28.50, 17.00, 0, 0],
            'Avg Trade ($)': [7.13, 5.67, 0, 0],
            'Max Drawdown (%)': [5.2, 3.8, 0, 0]
        })
        
        st.dataframe(strategy_metrics, use_container_width=True)
        
        # Gráfico de barras comparativo
        fig = px.bar(strategy_metrics[strategy_metrics['Trades'] > 0], 
                    x='Estratégia', y='Win Rate (%)',
                    color='P&L Total ($)',
                    title="Win Rate vs P&L por Estratégia")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Distribuição de Retornos")
        
        # Histograma de P&L
        returns = [3.2, -1.5, 2.8, 5.2, -2.1, 1.8, 4.5, -0.5]
        fig = px.histogram(returns, nbins=10, 
                          title="Distribuição de P&L por Trade (%)",
                          labels={'value': 'P&L %', 'count': 'Frequência'})
        fig.add_vline(x=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)
        
        # Estatísticas descritivas
        st.metric("Média", f"{sum(returns)/len(returns):.2f}%")
        st.metric("Melhor Trade", f"+{max(returns):.1f}%")
        st.metric("Pior Trade", f"{min(returns):.1f}%")
    
    with tab3:
        st.subheader("Histórico Completo de Trades")
        
        trade_history = pd.DataFrame({
            'Data': ['22/02 14:32', '22/02 14:28', '22/02 13:45', '22/02 12:15', '22/02 11:30'],
            'Mercado': ['BTC_100K', 'Trump_Russia', 'ETH_5000', 'China_Coup', 'NATO_Expand'],
            'Estratégia': ['Momentum', 'MeanRev', 'Momentum', 'MeanRev', 'Momentum'],
            'Direção': ['LONG', 'LONG', 'SHORT', 'SHORT', 'LONG'],
            'Entrada': [0.65, 0.12, 0.48, 0.05, 0.78],
            'Saída': [None, None, 0.45, 0.05, 0.76],
            'P&L (%)': [None, None, 3.2, 8.0, -2.1],
            'Status': ['Aberto', 'Aberto', 'Fechado', 'Fechado', 'Fechado']
        })
        
        st.dataframe(trade_history, use_container_width=True)

def page_control():
    """Página de controlo dos bots"""
    st.header("🎮 Controlo dos Bots")
    
    # Status geral
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Bots Ativos", "2/4", "+1")
    with col2:
        st.metric("Uptime", "4h 23m", "")
    with col3:
        st.metric("Último Trade", "2 min", "")
    
    st.markdown("---")
    
    # Controlo de estratégias
    st.subheader("🤖 Estratégias")
    
    strategies = [
        {'name': 'Momentum Trading', 'status': True, 'pnl': 28.50, 'trades': 4},
        {'name': 'Mean Reversion', 'status': True, 'pnl': 17.00, 'trades': 3},
        {'name': 'Scalping', 'status': False, 'pnl': 0, 'trades': 0},
        {'name': 'Contrarian', 'status': False, 'pnl': 0, 'trades': 0}
    ]
    
    for strat in strategies:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                st.markdown(f"**{strat['name']}**")
                st.caption(f"P&L: ${strat['pnl']:.2f} | Trades: {strat['trades']}")
            
            with col2:
                new_status = st.toggle("Ativo", value=strat['status'], key=f"toggle_{strat['name']}")
                if new_status != strat['status']:
                    st.toast(f"{strat['name']} {'ativado' if new_status else 'desativado'}!")
            
            with col3:
                if st.button("⚙️ Config", key=f"config_{strat['name']}"):
                    st.session_state['config_strategy'] = strat['name']
                    st.rerun()
            
            with col4:
                if st.button("📊 Stats", key=f"stats_{strat['name']}"):
                    st.info(f"Estatísticas de {strat['name']}")
            
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
    
    # Gestão de risco
    st.subheader("⚠️ Gestão de Risco")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Limites Diários**")
        daily_loss_used = 450
        daily_loss_limit = 1000
        progress = daily_loss_used / daily_loss_limit
        st.progress(progress, text=f"Daily Loss: ${daily_loss_used}/${daily_loss_limit}")
        
        max_pos_used = 3
        max_pos_limit = 5
        st.progress(max_pos_used/max_pos_limit, text=f"Posições: {max_pos_used}/{max_pos_limit}")
    
    with col2:
        st.markdown("**Configurações**")
        st.slider("Max Position Size (%)", 1, 10, 5, key="max_pos")
        st.slider("Stop Loss (%)", 5, 50, 20, key="stop_loss")
        st.slider("Take Profit (%)", 5, 50, 8, key="take_profit")
    
    # Ações de emergência
    st.markdown("---")
    st.subheader("🚨 Ações de Emergência")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🛑 FECHAR TODAS AS POSIÇÕES", type="primary", use_container_width=True):
            st.error("⚠️ TODAS AS POSIÇÕES FORAM FECHADAS!")
            # Aqui viria código para fechar posições
    
    with col2:
        if st.button("⏸️ PAUSAR TODOS OS BOTS", use_container_width=True):
            st.warning("⏸️ TODOS OS BOTS FORAM PAUSADOS!")
            # Aqui viria código para pausar bots

def page_settings():
    """Página de configurações"""
    st.header("⚙️ Configurações")
    
    # Configurações gerais
    st.subheader("💰 Capital e Trading")
    
    col1, col2 = st.columns(2)
    
    with col1:
        initial_capital = st.number_input("Capital Inicial", value=1000.0, step=100.0)
        st.info(f"Capital atual: ${initial_capital:,.2f}")
    
    with col2:
        mode = st.selectbox("Modo", ["Paper Trading", "Backtest", "Live"], index=0)
        st.info(f"Modo atual: {mode}")
    
    # Configurações de risco
    st.subheader("🛡️ Gestão de Risco")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.number_input("Max Position (%)", 1, 20, 5)
        st.number_input("Max Daily Loss (%)", 1, 50, 10)
    
    with col2:
        st.number_input("Stop Loss (%)", 5, 50, 20)
        st.number_input("Take Profit (%)", 5, 100, 8)
    
    with col3:
        st.number_input("Max Concurrent Trades", 1, 20, 5)
        st.number_input("Time Stop (dias)", 1, 30, 3)
    
    # Notificações
    st.subheader("🔔 Notificações")
    
    st.checkbox("Discord (#alertas)", value=True)
    st.checkbox("Email", value=False)
    st.checkbox("Som no browser", value=False)
    
    st.text_input("Discord Webhook URL", type="password")
    
    # Guardar
    st.markdown("---")
    if st.button("💾 Guardar Configurações", type="primary"):
        st.success("✅ Configurações guardadas com sucesso!")
        st.balloons()

# ==================== MAIN ====================

def main():
    """Função principal"""
    # Inicializar database
    init_database()
    
    # Sidebar
    st.sidebar.title("🤖 Polymarket Bot")
    st.sidebar.markdown("---")
    
    # Navegação
    page = st.sidebar.radio("📍 Navegação", [
        "📊 Overview",
        "📈 Análise", 
        "🎮 Controlo",
        "⚙️ Configurações"
    ])
    
    st.sidebar.markdown("---")
    
    # Status na sidebar
    st.sidebar.markdown("""
    **🟢 Status:** Online  
    **⏱️ Uptime:** 4h 23m  
    **📅 Última atualização:**  
    {}  
    **💰 Capital:** $1,045.50  
    **📈 P&L:** +$45.50 (+4.55%)
    """.format(datetime.now().strftime("%H:%M:%S")))
    
    st.sidebar.markdown("---")
    
    # Links rápidos
    st.sidebar.markdown("🔗 **Links Rápidos**")
    st.sidebar.markdown("- [Polymarket](https://polymarket.com)")
    st.sidebar.markdown("- [PolymarketScan](https://polymarketscan.com)")
    st.sidebar.markdown("- [Documentação](https://docs.polymarket.com)")
    
    # Renderizar página selecionada
    if page == "📊 Overview":
        page_overview()
    elif page == "📈 Análise":
        page_analysis()
    elif page == "🎮 Controlo":
        page_control()
    elif page == "⚙️ Configurações":
        page_settings()
    
    # Footer
    st.markdown("---")
    st.caption("🤖 Polymarket Trading Bot v1.0 | Desenvolvido por JARVIS | Dashboard Streamlit")

if __name__ == "__main__":
    main()
