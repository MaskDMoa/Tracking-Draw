# 🖌️ Tracking Draw

O **Tracking Draw** é um projeto interativo em Python utilizando bibliotecas de Visão Computacional de forma a permitir ao usuário *desenhar* na tela através do movimento e rastreamento (tracking) de elementos capturados pela webcam.

---

## 🎯 Sobre o Projeto
Unindo detecção de objetos/movimentos por câmera e processamento visual, este projeto traduz os deslocamentos de um elemento em foco para traços num painel de desenho digital e simula interações com o tempo (`3d_time`).

### ⚙️ Requisitos
- **Python** (Recomendado 3.8+)
- WebCam funcional no computador
- Bibliotecas descritas nos imports do projeto, como:
  - `opencv-python` (cv2)

---

## 🚀 Como Rodar

1. Faça o clone do projeto:
```bash
git clone https://github.com/MaskDMoa/Tracking-Draw.git
cd Tracking-Draw
```
2. Instale as dependências (ex: OpenCV):
```bash
pip install opencv-python
```
3. Rode o script de _tracking_ principal:
```bash
python my_tracking.py
```
> *Nota:* A webcam ligará e rastreará o objeto referenciado para desenhar! 🎨

---

## 📁 Estrutura do Projeto
A estrutura de arquivos do Tracking Draw é simples e direta:
| Arquivo | Descrição |
|---|---|
| `my_tracking.py` | Lógica central de tracking, processamento da imagem do vídeo e aplicação do desenho na tela. |
| `3d_time.py` | Outro componente iterativo para processamento visual / tempo. |

---

## 💻 Tecnologias Usadas
- **Python** (Linguagem Principal)
- **OpenCV (cv2)** (Para Visão Computacional)
