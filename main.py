import streamlit as st
from huggingface_hub import InferenceClient
import time
import streamlit as st
import streamlit.components.v1 as components

st.markdown("""
<style>
    /* Fundo escuro e texto principal */
    [data-testid="stAppViewContainer"] {
        background-color: #0e0b16;
        color: #e7dfdd;
    }
    
    /* Estilo do título */
    .stTitle h1 {
        color: #a239ca !important;
        text-shadow: 0 0 5px #47126b;
        border-bottom: 2px solid #47126b;
        padding-bottom: 10px;
    }
    
    /* Input do usuário */
    .stTextInput input {
        background-color: #1a1a2e !important;
        color: #e7dfdd !important;
        border: 1px solid #47126b;
    }
    
    /* Mensagens do jogador */
    .player-message {
        background-color: #16213e;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid #0f3460;
    }
    
    /* Mensagens do narrador */
    .narrador-message {
        background-color: #1a1a2e;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid #a239ca;
    }
    
    /* Botão Enviar */
    .stButton>button {
        background-color: #47126b !important;
        color: white !important;
        border: 1px solid #a239ca !important;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #a239ca !important;
        border: 1px solid #e7dfdd !important;
    }
    
    /* Efeito de foco nas mensagens */
    .stMarkdown {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

HF_TOKEN = "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" # Usadas para fins de teste

client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=HF_TOKEN
)

def carregar_historia_base():
    try:
        with open("base_historia.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

historia_base = carregar_historia_base()

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

st.markdown("<h1 class='title-text'>Histor.IA</h1>", unsafe_allow_html=True)
st.caption("Uma experiência interativa de storytelling inspirado no universo de Ordem Paranormal RPG")

components.html("""
    <html>
    <head>
        <style>
            p{
                font-family: fantasy;
            }
            
            .typing-text {
                display: inline-block;
                color: #a239ca;
            }

            .dynamic-header {
                color: #e7dfdd;
                background-color: #0e0b16;
            }
        </style>
    </head>
    <body>
        <div class="dynamic-header">
            <p>Crie uma história <span id="dynamic-text" class="typing-text"></span></p>
        </div>

        <script>
        const words = ["única...", "cheia de enigmas...", "dramática...", "imersiva...", "de tirar o fôlego...", "paranormal..."];
        const dynamicText = document.getElementById("dynamic-text");

        let wordIndex = 0;
        let charIndex = 0;
        let isDeleting = false;
        let typingSpeed = 150;
        let displayTime = 2500;

        function typeEffect() {
            if (!dynamicText) return;

            const currentWord = words[wordIndex];
            dynamicText.textContent = currentWord.substring(0, charIndex);

            if (!isDeleting && charIndex < currentWord.length) {
                charIndex++;
                setTimeout(typeEffect, typingSpeed);
            } else if (isDeleting && charIndex > 0) {
                charIndex--;
                setTimeout(typeEffect, typingSpeed / 2);
            } else {
                isDeleting = !isDeleting;
                if (!isDeleting) {
                    wordIndex = (wordIndex + 1) % words.length;
                    setTimeout(typeEffect, typingSpeed);
                } else {
                    setTimeout(typeEffect, displayTime);
                }
            }
        }

        window.onload = typeEffect;
        </script>
    </body>
    </html>
""", height=80)

for autor, texto in st.session_state.mensagens:
    if autor == "Você":
        st.markdown(f"""
        <div class="player-message">
            <strong>{autor}:</strong> {texto}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="narrador-message">
            <strong>{autor}:</strong> {texto}
        </div>
        """, unsafe_allow_html=True)

with st.form(key='chat_form'):
    user_input = st.text_input("Você:", key="user_input")
    submit_button = st.form_submit_button(label="Enviar")

if submit_button and user_input:
    with st.spinner('Consultando os mistérios...'):
        time.sleep(0.3)
        
        st.session_state.mensagens.append(("Você", user_input))

        prompt = """Você é um narrador de RPG com estilo investigação, mistério e terror. Gosta de descrever com emoção e drama. 
        Evita longas explicações. Foca em criar tensão e atmosfera.
        Exemplos do seu estilo:
        - "Vocês veem sigilos amarelos subindo pelas tatuagens dela e formando uma espécie de coroa fina ao redor da cabeça dela. Ela olha diretamente para os 4 convidados que estavam quando vocês chegaram e diz: "Ataque ser próximo""
        - "Assim que essa confusão termina, vocês escutam a voz da Michelle ecoando pela casa, através de auto falantes espalhados pela casa".\n\n"""
        prompt += f"História anterior:\n{historia_base}\n\n"
        prompt += "Sempre finalize a resposta com uma frase completa. Não interrompa a narrativa no meio da frase."
        for autor, texto in st.session_state.mensagens:
            prefixo = "Usuário" if autor == "Você" else "Narrador"
            prompt += f"{prefixo}: {texto}\n"
        prompt += "Narrador:"
            
        resposta = client.chat_completion(
            messages=[
                {"role": "system", "content": "Você é um narrador criativo de Ordem Paranormal RPG em portugues-br. Narre em até 5 frases e sempre finalize a última frase. Seja breve, direto e imersivo."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200,
            stop=["Usuário:", "Narrador:"], 
        )

        resposta_texto = resposta.choices[0].message["content"].strip()
        st.session_state.mensagens.append(("Narrador", resposta_texto))
    
        st.rerun()
