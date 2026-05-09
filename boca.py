import edge_tts
import asyncio
import pygame
import os

# Função para gerar e tocar a voz
async def comunicar(texto):
    # Escolha da voz: 'pt-BR-AntonioNeural' (Masculina/Séria) ou 'pt-BR-FranciscaNeural'
    VOZ = "pt-BR-AntonioNeural" 
    ARQUIVO_AUDIO = "fala_jairo.mp3"

    # 1. Gera o áudio usando a API da Microsoft
    comunicador = edge_tts.Communicate(texto, VOZ)
    await comunicador.save(ARQUIVO_AUDIO)

    # 2. Toca o áudio
    pygame.mixer.init()
    pygame.mixer.music.load(ARQUIVO_AUDIO)
    pygame.mixer.music.play()

    # Espera o áudio terminar de tocar
    while pygame.mixer.music.get_busy():
        continue
    
    pygame.mixer.quit()
    
    # 3. Limpa o arquivo temporário
    if os.path.exists(ARQUIVO_AUDIO):
        os.remove(ARQUIVO_AUDIO)

# Função auxiliar para chamar o async de forma simples
def falar(texto):
    asyncio.run(comunicar(texto))