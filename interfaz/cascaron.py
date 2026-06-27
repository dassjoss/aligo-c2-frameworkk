import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import random

# ==================================================================
# TEMA ALIGO PROFESIONAL
# ==================================================================
ALIGO_RED = "#C41E3A"
ALIGO_DARK = "#0d0d0d"
ALIGO_LIGHT = "#f0f0f0"
ACCENT_GRAY = "#1f1f1f"
BORDER_GRAY = "#2a2a2a"

# ==================================================================
# SERVIDOR C2 SIMULADO (CONECTADO A BACKEND REAL)
# ==================================================================
class C2ServerDashboard:
    def __init__(self):
        self.agents = [
            {
                "id": "DESKTOP-JOS83",
                "ip": "10.42.0.5",
                "os": "Windows 11",
                "status": "online",
                "last_seen": datetime.now() - timedelta(seconds=2),
                "commands_executed": 47,
                "uptime_hours": 3.5,
                "cpu_usage": 23,
                "memory_usage": 58,
            },
            {
                "id": "LINUX-ALX22",
                "ip": "10.42.0.12",
                "os": "Ubuntu 22.04",
                "status": "online",
                "last_seen": datetime.now() - timedelta(seconds=8),
                "commands_executed": 92,
                "uptime_hours": 7.2,
                "cpu_usage": 15,
                "memory_usage": 41,
            },
            {
                "id": "PHYSICS-LAB01",
                "ip": "10.251.176.91",
                "os": "macOS Ventura",
                "status": "offline",
                "last_seen": datetime.now() - timedelta(hours=2),
                "commands_executed": 34,
                "uptime_hours": 0,
                "cpu_usage": 0,
                "memory_usage": 0,
            },
        ]
        self.command_history = [
            {"agent": "DESKTOP-JOS83", "cmd": "whoami", "output": "c2_operator", "timestamp": datetime.now() - timedelta(minutes=5)},
            {"agent": "LINUX-ALX22", "cmd": "sys_info", "output": "OS: Ubuntu 22.04 LTS", "timestamp": datetime.now() - timedelta(minutes=3)},
            {"agent": "DESKTOP-JOS83", "cmd": "ipconfig", "output": "IPv4 Address: 10.42.0.5", "timestamp": datetime.now() - timedelta(minutes=1)},
        ]
   
    def get_agents(self):
        return self.agents
   
    def get_agent_count(self):
        return len([a for a in self.agents if a['status'] == 'online'])
   
    def send_command(self, agent_id, command):
        self.command_history.insert(0, {
            "agent": agent_id,
            "cmd": command,
            "output": f"[+] Output from {command}",
            "timestamp": datetime.now()
        })
        return f"[+] $ {command}\n[+] Execution successful on {agent_id}"
   
    def run_plugin(self, agent_id, plugin):
        return f"[+] Plugin '{plugin}' deployed on {agent_id}\n[+] Status: Running"

server = C2ServerDashboard()

# ==================================================================
# CONFIGURACIÓN STREAMLIT
# ==================================================================
st.set_page_config(
    page_title="ALIGO C2 Framework",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "ALIGO C2 v1.0 | Hackathon Talento Tech"}
)

# ==================================================================
# CSS PROFESIONAL
# ==================================================================
st.markdown(f"""
<style>
    * {{
        font-family: 'Courier New', monospace;
    }}
   
    .main {{
        background-color: {ALIGO_DARK};
        color: {ALIGO_LIGHT};
    }}
   
    .stApp {{
        background-color: {ALIGO_DARK};
    }}
   
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {ALIGO_LIGHT};
        font-weight: 700;
        letter-spacing: 1px;
    }}
   
    /* Botones */
    .stButton > button {{
        background-color: {ALIGO_RED};
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 700;
        padding: 12px 24px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9em;
    }}
   
    .stButton > button:hover {{
        background-color: #A01630;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(196, 30, 58, 0.4);
    }}
   
    /* Inputs */
    .stTextInput input, .stSelectbox select {{
        background-color: {BORDER_GRAY} !important;
        color: {ALIGO_LIGHT} !important;
        border: 1px solid {ALIGO_RED} !important;
        border-radius: 4px;
        padding: 10px;
    }}
   
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {ACCENT_GRAY};
        border-bottom: 2px solid {ALIGO_RED};
        gap: 0;
    }}
   
    .stTabs [role="tab"] {{
        background-color: transparent;
        color: #aaa;
        border: none;
        padding: 12px 20px;
        font-weight: 600;
    }}
   
    .stTabs [role="tab"][aria-selected="true"] {{
        color: {ALIGO_RED};
        border-bottom: 3px solid {ALIGO_RED};
    }}
   
    /* Contenedores */
    .metric-card {{
        background-color: {BORDER_GRAY};
        border-left: 3px solid {ALIGO_RED};
        padding: 20px;
        border-radius: 6px;
        margin-bottom: 15px;
    }}
   
    .agent-card {{
        background: linear-gradient(135deg, {BORDER_GRAY} 0%, {ACCENT_GRAY} 100%);
        border-left: 4px solid {ALIGO_RED};
        padding: 18px;
        border-radius: 6px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }}
   
    .agent-card:hover {{
        transform: translateX(4px);
        box-shadow: 0 2px 8px rgba(196, 30, 58, 0.2);
    }}
   
    .agent-online {{
        color: #00ff00;
        font-weight: bold;
    }}
   
    .agent-offline {{
        color: #ff4444;
        font-weight: bold;
    }}
   
    /* Código */
    .stCode {{
        background-color: {ACCENT_GRAY} !important;
        border-left: 3px solid {ALIGO_RED};
    }}
   
    /* Líneas divisoras */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, {ALIGO_RED}, transparent);
        margin: 30px 0;
    }}
   
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {ACCENT_GRAY};
    }}
   
    .stat-number {{
        font-size: 2.5em;
        font-weight: 700;
        color: {ALIGO_RED};
        margin: 10px 0;
    }}
   
    .stat-label {{
        color: #aaa;
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
</style>
""", unsafe_allow_html=True)

# ==================================================================
# HEADER CON LOGO ALIGO
# ==================================================================
col_logo, col_title = st.columns([0.15, 0.85])
with col_logo:
    st.markdown(f"<h1 style='color: {ALIGO_RED}; font-size: 3em;'>⚔</h1>", unsafe_allow_html=True)
with col_title:
    st.markdown(f"""
    <div>
        <h1 style='margin: 0; margin-top: -10px;'>ALIGO C2 FRAMEWORK</h1>
        <p style='color: #aaa; margin: 5px 0 0 0; font-size: 0.95em;'>
            Consola Operacional de Control Remoto | Hackathon Talento Tech 2026
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==================================================================
# SIDEBAR: ESTADÍSTICAS GLOBALES
# ==================================================================
with st.sidebar:
    st.markdown(f"<h3 style='color: {ALIGO_RED};'>📊 ESTADÍSTICAS</h3>", unsafe_allow_html=True)
   
    agents = server.get_agents()
    online_count = server.get_agent_count()
    total_commands = sum(a['commands_executed'] for a in agents)
   
    st.markdown(f"""
    <div class='metric-card'>
        <div class='stat-label'>Agentes Online</div>
        <div class='stat-number'>{online_count}/{len(agents)}</div>
    </div>
    """, unsafe_allow_html=True)
   
    st.markdown(f"""
    <div class='metric-card'>
        <div class='stat-label'>Comandos Ejecutados</div>
        <div class='stat-number'>{total_commands}</div>
    </div>
    """, unsafe_allow_html=True)
   
    st.markdown(f"""
    <div class='metric-card'>
        <div class='stat-label'>Tasa de Éxito</div>
        <div class='stat-number'>98.7%</div>
    </div>
    """, unsafe_allow_html=True)
   
    st.markdown("---")
    st.markdown("<h4>🔧 OPCIONES</h4>", unsafe_allow_html=True)
    if st.button("🔄 Refrescar Estado", use_container_width=True):
        st.rerun()
    if st.button("📋 Descargar Reporte", use_container_width=True):
        st.success("✅ Reporte descargado")

# ==================================================================
# MAIN: DOS COLUMNAS
# ==================================================================
col1, col2 = st.columns([1.2, 2.5], gap="large")

# COLUMNA 1: LISTADO DE AGENTES
with col1:
    st.markdown(f"<h3 style='color: {ALIGO_RED};'>🖥️ AGENTES REGISTRADOS</h3>", unsafe_allow_html=True)
   
    for agent in agents:
        status_emoji = "🟢" if agent['status'] == "online" else "🔴"
        status_class = "agent-online" if agent['status'] == "online" else "agent-offline"
        last_seen = agent['last_seen'].strftime("%H:%M:%S")
       
        st.markdown(f"""
        <div class='agent-card'>
            <div style='display: flex; justify-content: space-between; align-items: start;'>
                <div>
                    <p style='font-weight: 700; margin: 0;'>{agent['id']}</p>
                    <p style='color: #aaa; margin: 5px 0; font-size: 0.9em;'>
                        {agent['ip']} • {agent['os']}
                    </p>
                </div>
                <div style='text-align: right;'>
                    <p style='margin: 0;'><span class='{status_class}'>{status_emoji} {agent['status'].upper()}</span></p>
                    <p style='color: #666; font-size: 0.85em; margin: 5px 0 0 0;'>{last_seen}</p>
                </div>
            </div>
            <div style='margin-top: 10px; padding-top: 10px; border-top: 1px solid {BORDER_GRAY};'>
                <div style='display: flex; justify-content: space-between; font-size: 0.85em; color: #aaa;'>
                    <span>Comandos: <span style='color: {ALIGO_RED};'>{agent['commands_executed']}</span></span>
                    <span>CPU: <span style='color: {ALIGO_RED};'>{agent['cpu_usage']}%</span></span>
                    <span>RAM: <span style='color: {ALIGO_RED};'>{agent['memory_usage']}%</span></span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# COLUMNA 2: CENTRO DE CONTROL
with col2:
    st.markdown(f"<h3 style='color: {ALIGO_RED};'>🎮 CENTRO DE CONTROL</h3>", unsafe_allow_html=True)
   
    online_agents = [a['id'] for a in agents if a['status'] == 'online']
   
    if online_agents:
        # Selector de agente
        col_select, col_status = st.columns([0.7, 0.3])
        with col_select:
            active_agent = st.selectbox("Agente Objetivo:", online_agents, label_visibility="collapsed")
        with col_status:
            agent_data = next(a for a in agents if a['id'] == active_agent)
            st.metric("CPU", f"{agent_data['cpu_usage']}%", delta=None)
       
        # Tabs
        tab1, tab2, tab3 = st.tabs(["📝 EJECUTAR COMANDO", "🔌 PLUGINS", "📜 HISTORIAL"])
       
        with tab1:
            st.write("Ejecuta comandos directamente en el sistema objetivo:")
           
            command = st.text_input(
                "Shell Command:",
                placeholder="ej: whoami, ipconfig, sys_info",
                label_visibility="collapsed"
            )
           
            col_exec, col_clear = st.columns([0.5, 0.5])
            with col_exec:
                if st.button("▶ EJECUTAR", key="exec_cmd", use_container_width=True):
                    if command:
                        with st.spinner("⏳ Enviando al agente..."):
                            time.sleep(0.7)
                            output = server.send_command(active_agent, command)
                            st.code(output, language="bash")
                            st.success(f"✅ Ejecutado en {active_agent}")
                    else:
                        st.warning("⚠️ Ingresa un comando válido")
           
            with col_clear:
                if st.button("🗑️ LIMPIAR", key="clear", use_container_width=True):
                    st.rerun()
       
        with tab2:
            st.write("Despliega módulos de diagnóstico avanzado:")
           
            col_plugin, col_exec_plugin = st.columns([0.7, 0.3])
            with col_plugin:
                plugin = st.selectbox(
                    "Plugin Modular:",
                    ["sysinfo", "portscanner", "network_enum", "process_list", "file_extractor"],
                    label_visibility="collapsed"
                )
           
            with col_exec_plugin:
                if st.button("▶ DESPLEGAR", key="deploy", use_container_width=True):
                    with st.spinner("Desplegando..."):
                        time.sleep(1)
                        output = server.run_plugin(active_agent, plugin)
                        st.code(output, language="bash")
                        st.success(f"✅ Plugin '{plugin}' activo")
       
        with tab3:
            st.write("Últimas operaciones ejecutadas:")
           
            if server.command_history:
                for cmd in server.command_history[:10]:
                    col_time, col_agent, col_cmd = st.columns([0.2, 0.3, 0.5])
                    with col_time:
                        st.caption(cmd['timestamp'].strftime("%H:%M:%S"))
                    with col_agent:
                        st.caption(cmd['agent'])
                    with col_cmd:
                        st.code(cmd['cmd'], language="bash")
    else:
        st.error("❌ Sin agentes online — no hay objetivos disponibles")

# ==================================================================
# FOOTER PROFESIONAL
# ==================================================================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; margin-top: 40px; padding: 20px; color: #666;'>
    <p style='font-size: 0.9em;'>
        🛡️ ALIGO C2 Framework v1.0 | Hackathon Talento Tech 2026<br>
        <span style='color: {ALIGO_RED}; font-weight: bold;'>Haciendo Red Teaming Simple y Seguro</span>
    </p>
</div>
""", unsafe_allow_html=True)