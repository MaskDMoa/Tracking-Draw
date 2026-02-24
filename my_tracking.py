import mediapipe as mp
import cv2


class Detector:
    def __init__(self, modo=False, max_maos=2, model_complex=1, detc_conf=0.5, rast_conf=0.5, corp=(170, 0, 255),
                 corc=(0, 180, 255)):
        self.modo = modo
        self.max_maos = max_maos
        self.model_complex = model_complex
        self.detc_conf = detc_conf
        self.rast_conf = rast_conf
        self.corp = corp
        self.corc = corc

        # Configuração do MediaPipe
        self.maos_mp = mp.solutions.hands
        self.maos = self.maos_mp.Hands(
            static_image_mode=self.modo,
            max_num_hands=self.max_maos,
            model_complexity=self.model_complex,
            min_detection_confidence=self.detc_conf,
            min_tracking_confidence=self.rast_conf
        )

        self.draw_mp = mp.solutions.drawing_utils
        self.draw_conf_p = self.draw_mp.DrawingSpec(color=self.corp, thickness=2, circle_radius=2)
        self.draw_conf_c = self.draw_mp.DrawingSpec(color=self.corc, thickness=2)

    def encounter_Hand(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.result = self.maos.process(img_rgb)

        if self.result.multi_hand_landmarks:
            for pontos in self.result.multi_hand_landmarks:
                if draw:
                    self.draw_mp.draw_landmarks(
                        img,
                        pontos,
                        self.maos_mp.HAND_CONNECTIONS,
                        self.draw_conf_p,
                        self.draw_conf_c
                    )
        return img

    def encounter_pontos(self, img, mao_num=0, draw=True, cor=(170, 0, 255), raio=7, ponto_detect=0):
        lista_pontos = []

        if self.result.multi_hand_landmarks:
            if len(self.result.multi_hand_landmarks) > mao_num:
                mao = self.result.multi_hand_landmarks[mao_num]

                for id, ponto in enumerate(mao.landmark):
                    altura, largura, _ = img.shape
                    centro_x, centro_y = int(ponto.x * largura), int(ponto.y * altura)

                    lista_pontos.append([id, centro_x, centro_y])

                    if draw and id == ponto_detect:
                        cv2.circle(img, (centro_x, centro_y), raio, cor, cv2.FILLED)

        return lista_pontos


def main():

    print("Iniciando...")
    cap = cv2.VideoCapture(0)
    detector = Detector()

    while cap.isOpened():
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img = detector.encounter_Hand(img)

        lista_pontos = detector.encounter_pontos(img, ponto_detect=8)  # 8 é a ponta do indicador

        if lista_pontos:
            print(f"Ponta do indicador: {lista_pontos[8][1:]}")

        cv2.imshow('Captura', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()