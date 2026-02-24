import cv2
import mediapipe as mp
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import os


class AreiaMagicaPro:
    def __init__(self):
        # Configuração MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

        self.cap = cv2.VideoCapture(0)

        # Estado inicial das partículas
        self.num_particulas = 1500
        self.pos_atuais = np.random.uniform(-2, 2, (self.num_particulas, 3))
        self.pos_atuais[:, 1] = -2.5  # Começam no "chão"

        self.modelos = self._gerar_modelos()

        # Estados de controle
        self.tipo_objeto = 0
        self.ativo = False
        self.escala = 1.0
        self.angulo_x = 0
        self.angulo_y = 0
        self.pinça_esq_travada = False

    def _gerar_modelos(self):
        """Gera os alvos geométricos para as partículas"""
        n = self.num_particulas
        # Cubo
        cubo = np.random.uniform(-1, 1, (n, 3))

        # Pirâmide
        pira = []
        for _ in range(n):
            z = np.random.uniform(-1, 1)
            larg = (1 - z) / 2
            pira.append([np.random.uniform(-larg, larg), z, np.random.uniform(-larg, larg)])

        # Esfera
        esf = np.random.normal(0, 1, (n, 3))
        esf /= np.linalg.norm(esf, axis=1)[:, np.newaxis]

        return [cubo, np.array(pira), esf]

    def _ajustar_quantidade(self, nova_qtd):
        """Muda o número de partículas em tempo real"""
        if nova_qtd == self.num_particulas: return

        # Criar novas posições
        novas_pos = np.random.uniform(-2, 2, (nova_qtd, 3))
        # Se estivermos caindo, manter o Y lá embaixo
        if not self.ativo: novas_pos[:, 1] = -2.5

        # Copiar posições antigas para evitar saltos bruscos
        min_p = min(self.num_particulas, nova_qtd)
        novas_pos[:min_p] = self.pos_atuais[:min_p]

        self.num_particulas = nova_qtd
        self.pos_atuais = novas_pos
        self.modelos = self._gerar_modelos()

    def processar(self):
        success, frame = self.cap.read()
        if not success: return
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.hands.process(rgb)
        self.ativo = False

        if results.multi_hand_landmarks:
            for i, hand_lms in enumerate(results.multi_hand_landmarks):
                lbl = results.multi_handedness[i].classification[0].label
                pts = hand_lms.landmark
                self.ativo = True  # Ativa a atração magnética

                # MÃO ESQUERDA: Quantidade (Altura) e Troca (Pinça)
                if lbl == "Left":
                    # Altura controla quantidade (500 a 4000)
                    qtd = int(np.interp(pts[8].y, [0.1, 0.9], [4000, 500]))
                    if abs(qtd - self.num_particulas) > 100:
                        self._ajustar_quantidade(qtd)

                    # Pinça troca forma
                    dist = math.hypot(pts[8].x - pts[4].x, pts[8].y - pts[4].y)
                    if dist < 0.05:
                        if not self.pinça_esq_travada:
                            self.tipo_objeto = (self.tipo_objeto + 1) % 3
                            self.pinça_esq_travada = True
                    else:
                        self.pinça_esq_travada = False

                # MÃO DIREITA: Giro (Posição) e Escala (Pinça)
                if lbl == "Right":
                    # Giro
                    self.angulo_y = (pts[8].x - 0.5) * 180
                    self.angulo_x = (pts[8].y - 0.5) * 180

                    # Escala
                    dist_esc = math.hypot(pts[8].x - pts[4].x, pts[8].y - pts[4].y)
                    self.escala = np.interp(dist_esc, [0.05, 0.3], [0.5, 3.5])

        # Lógica de Física (Lerp)
        if self.ativo:
            alvo = self.modelos[self.tipo_objeto] * self.escala
            # Aplicar rotação nos alvos para os pontos seguirem a mão
            ax, ay = np.radians(self.angulo_x), np.radians(self.angulo_y)
            Rx = np.array([[1, 0, 0], [0, np.cos(ax), -np.sin(ax)], [0, np.sin(ax), np.cos(ax)]])
            Ry = np.array([[np.cos(ay), 0, np.sin(ay)], [0, 1, 0], [-np.sin(ay), 0, np.cos(ay)]])
            alvo = alvo @ Rx.T @ Ry.T
        else:
            alvo = self.pos_atuais.copy()
            alvo[:, 1] = -2.5  # Gravidade
            alvo[:, 0] += np.random.uniform(-0.01, 0.01, self.num_particulas)  # Vento/Ruído

        # Suavização do movimento
        self.pos_atuais += (alvo - self.pos_atuais) * 0.12

        # Overlay de informações na câmera
        cv2.putText(frame, f"Particulas: {self.num_particulas}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.imshow("Preview Camera", frame)

    def desenhar(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Brilho Neon

        glTranslatef(0, 0, -6)

        glPointSize(2)
        glBegin(GL_POINTS)

        # Cores: Ciano, Verde Lima, Magenta
        cores = [(0, 1, 1, 0.7), (0.5, 1, 0, 0.7), (1, 0, 1, 0.7)]
        glColor4f(*cores[self.tipo_objeto])

        for p in self.pos_atuais:
            glVertex3f(p[0], p[1], p[2])

        glEnd()
        glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1024, 768)
    glutCreateWindow(b"Holograma de Areia Inteligente")

    glEnable(GL_DEPTH_TEST)
    app = AreiaMagicaPro()

    def loop():
        app.processar()
        app.desenhar()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            app.cap.release()
            cv2.destroyAllWindows()
            os._exit(0)

    glutIdleFunc(loop)
    glutDisplayFunc(app.desenhar)

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1024 / 768, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    glutMainLoop()


if __name__ == "__main__":
    main()