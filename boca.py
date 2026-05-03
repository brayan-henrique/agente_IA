import pyttsx3

def falar(texto):
    # Inicializa o motor de voz
    motor_voz = pyttsx3.init()
    
    # Ajusta a velocidade da fala (175 é um ritmo natural, 200 é muito rápido)
    motor_voz.setProperty('rate', 175)
    
    # Procura as vozes instaladas no seu PC e escolhe a brasileira (Maria ou Daniel geralmente)
    vozes = motor_voz.getProperty('voices')
    for voz in vozes:
        nome_voz = voz.name.lower()
        if "brazil" in nome_voz or "portuguese" in nome_voz or "maria" in nome_voz or "daniel" in nome_voz:
            motor_voz.setProperty('voice', voz.id)
            break
            
    # Imprime na tela e fala o texto em voz alta
    print(f"\n[🔊 BOCA]: {texto}")
    motor_voz.say(texto)
    motor_voz.runAndWait() # Pausa o script até ele terminar de falar