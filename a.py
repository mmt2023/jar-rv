import pygame
import random
import sys

# Inicializar Pygame
pygame.init()

# Configuraciones de la pantalla
ANCHO = 400
ALTO = 600
pantalla = pygame.display.set_caption("Flappy Bird - Simple")
ventana = pygame.display.set_mode((ANCHO, ALTO))
reloj = pygame.time.Clock()

# Colores (Equivalentes al CSS y Canvas original)
COLOR_FONDO_TOP = (135, 206, 235)  # Cielo
COLOR_PAJARO = (255, 215, 0)       # Amarillo
COLOR_PAJARO_BORDE = (255, 140, 0) # Naranja
COLOR_TUBERIA = (34, 139, 34)      # Verde
COLOR_TUBERIA_BORDE = (26, 107, 26)
COLOR_TEXTO = (255, 255, 255)      # Blanco
COLOR_OVERLAY = (0, 0, 0, 230)      # Negro con transparencia para Game Over
COLOR_BOTON = (102, 126, 234)

# Constantes del Juego
GRAVEDAD = 0.2
VELOCIDAD_SALTO = 5
VELOCIDAD_TUBERIA = 3
GAP = 150  # Espacio entre tuberías

# Fuentes
fuente_score = pygame.font.SysFont("Arial", 24, bold=True)
fuente_game_over = pygame.font.SysFont("Arial", 48, bold=True)
fuente_boton = pygame.font.SysFont("Arial", 16)


class Pajaro:
    def __init__(self):
        self.x = 50
        self.y = ALTO / 2
        self.ancho = 30
        self.alto = 30
        self.velocidad = 0

    def actualizar(self):
        self.velocidad += GRAVEDAD
        self.y += self.velocidad

        # Límites de pantalla
        if self.y < 0:
            self.y = 0
            self.velocidad = 0
        if self.y + self.alto > ALTO:
            self.y = ALTO - self.alto

    def saltar(self):
        self.velocidad = -VELOCIDAD_SALTO

    def dibujar(self, superficie):
        # Cuerpo Amarillo
        rect_pajaro = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        pygame.draw.rect(superficie, COLOR_PAJARO, rect_pajaro)
        pygame.draw.rect(superficie, COLOR_PAJARO_BORDE, rect_pajaro, 2)

        # Ojos (Simulando los cuadraditos del JS)
        pygame.draw.rect(superficie, (255, 255, 255), (self.x + 8, self.y + 8, 8, 8))
        pygame.draw.rect(superficie, (255, 255, 255), (self.x + 16, self.y + 8, 8, 8))
        # Pupilas
        pygame.draw.rect(superficie, (0, 0, 0), (self.x + 10, self.y + 10, 5, 5))
        pygame.draw.rect(superficie, (0, 0, 0), (self.x + 18, self.y + 10, 5, 5))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)


class Tuberia:
    def __init__(self, x):
        self.x = x
        self.ancho = 50
        # Altura aleatoria respetando márgenes mínimos
        self.altura_top = random.uniform(40, ALTO - GAP - 40)
        self.altura_bottom = ALTO - self.altura_top - GAP
        self.scored = False

    def actualizar(self):
        self.x -= VELOCIDAD_TUBERIA

    def dibujar(self, superficie):
        # Tubería superior
        rect_top = pygame.Rect(self.x, 0, self.ancho, self.altura_top)
        pygame.draw.rect(superficie, COLOR_TUBERIA, rect_top)
        pygame.draw.rect(superficie, COLOR_TUBERIA_BORDE, rect_top, 2)

        # Tubería inferior
        rect_bottom = pygame.Rect(self.x, self.altura_top + GAP, self.ancho, self.altura_bottom)
        pygame.draw.rect(superficie, COLOR_TUBERIA, rect_bottom)
        pygame.draw.rect(superficie, COLOR_TUBERIA_BORDE, rect_bottom, 2)

    def esta_fuera(self):
        return self.x + self.ancho < 0

    def detectar_colision(self, pajaro):
        rect_pajaro = pajaro.get_rect()
        rect_top = pygame.Rect(self.x, 0, self.ancho, self.altura_top)
        rect_bottom = pygame.Rect(self.x, self.altura_top + GAP, self.ancho, self.altura_bottom)

        # Colisión con bordes del mapa
        if pajaro.y <= 0 or pajaro.y + pajaro.alto >= ALTO:
            return True

        # Colisión con tuberías
        if rect_pajaro.colliderect(rect_top) or rect_pajaro.colliderect(rect_bottom):
            return True

        return False


def dibujar_pantalla_game_over(puntuacion, boton_rect):
    # Fondo semitransparente para el recuadro de Game Over
    overlay = pygame.Surface((300, 250), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    ventana.blit(overlay, (50, 175))

    # Texto GAME OVER
    texto_go = fuente_game_over.render("GAME OVER!", True, (255, 107, 107))
    ventana.blit(texto_go, (ANCHO // 2 - texto_go.get_width() // 2, 200))

    # Puntuación final
    texto_final = fuente_score.render(f"Puntuación Final: {puntuacion}", True, COLOR_TEXTO)
    ventana.blit(texto_final, (ANCHO // 2 - texto_final.get_width() // 2, 270))

    # Botón Reiniciar
    pygame.draw.rect(ventana, COLOR_BOTON, boton_rect, border_radius=5)
    texto_btn = fuente_boton.render("Reiniciar Juego", True, COLOR_TEXTO)
    ventana.blit(texto_btn, (boton_rect.x + (boton_rect.width - texto_btn.get_width()) // 2, 
                             boton_rect.y + (boton_rect.height - texto_btn.get_height()) // 2))


def main():
    pajaro = Pajaro()
    tuberias = []
    puntuacion = 0
    contador_tuberia = 0
    juego_activo = True

    # Rectángulo interactivo para el botón de reiniciar
    boton_reiniciar_rect = pygame.Rect(ANCHO // 2 - 75, 330, 150, 45)

    ejecutando = True
    while ejecutando:
        reloj.tick(60) # Limitar a 60 FPS

        # --- Gestión de Eventos (Entradas) ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and juego_activo:
                    pajaro.saltar()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: # Click izquierdo
                    if juego_activa := juego_activo:
                        pajaro.saltar()
                    else:
                        # Si está en Game Over y hace click en el botón
                        pos_raton = pygame.mouse.get_pos()
                        if boton_reiniciar_rect.collidepoint(pos_raton):
                            # Reiniciar juego (Reseteo de variables)
                            pajaro = Pajaro()
                            tuberias = []
                            puntuacion = 0
                            contador_tuberia = 0
                            juego_activo = True

        # --- Actualización de la Lógica del juego ---
        if juego_activo:
            pajaro.actualizar()

            # Crear nuevas tuberías (Equivalente al contador > 100 de JS)
            contador_tuberia += 1
            if contador_tuberia > 100:
                tuberias.append(Tuberia(ANCHO))
                contador_tuberia = 0

            # Actualizar tuberías al revés (para poder borrar elementos de la lista sin bugs)
            for i in range(len(tuberias) - 1, -1, -1):
                tuberias[i].actualizar()

                # Detectar colisión
                if tuberias[i].detectar_colision(pajaro):
                    juego_activo = False

                # Contar puntuación
                if not tuberias[i].scored and pajaro.x > tuberias[i].x + tuberias[i].ancho:
                    tuberias[i].scored = True
                    puntuacion += 1

                # Eliminar tuberías fuera de pantalla
                if tuberias[i].esta_fuera():
                    tuberias.pop(i)

        # --- Renderizado (Dibujo en Pantalla) ---
        # Rellenar fondo azul cielo
        ventana.fill(COLOR_FONDO_TOP)

        # Dibujar tuberías
        for tuberia in tuberias:
            tuberia.dibujar(ventana)

        # Dibujar pájaro
        pajaro.dibujar(ventana)

        # Dibujar puntuación en la esquina superior izquierda
        texto_puntos = fuente_score.render(f"Score: {puntuacion}", True, COLOR_TEXTO)
        ventana.blit(texto_puntos, (10, 15))

        # Dibujar interfaz de Game Over si corresponde
        if not juego_activo:
            dibujar_pantalla_game_over(puntuacion, boton_reiniciar_rect)

        pygame.display.flip()

if __name__ == "__main__":
    main()