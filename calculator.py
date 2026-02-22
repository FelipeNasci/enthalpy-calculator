from CoolProp.CoolProp import PropsSI

def convertToPA(pressure):
    return float(pressure) * 98066.5

def convertToKelvin(temperature):
    return float(temperature) + 273.15

def convertToKiloJauleForKilogram(jauleValue):
    return jauleValue / 1000000 

def calculateEnthalpy(temperature, pressure):
    if temperature <= 0:
        return 0.0
    try:
        enthalpy = PropsSI('H', 'P', pressure, 'T', temperature, 'Water')
    except Exception:
        return None

    return enthalpy

def calculateMassFlow(temperatureInput, temperatureOutput, pressureInput, pressureOutput, power, boilerEfficiency, machineEfficiency):
    enthalpyInput = calculateEnthalpy(temperatureInput, pressureInput)
    enthalpyOutput = calculateEnthalpy(temperatureOutput, pressureOutput)

    mass = power / (boilerEfficiency * machineEfficiency * (enthalpyInput - enthalpyOutput))

    return mass / 10000000

def calculateMassFlowWithEnthalpy(enthalpyInput, enthalpyOutput, power, boilerEfficiency, machineEfficiency):
    mass = power / (boilerEfficiency * machineEfficiency * (enthalpyInput - enthalpyOutput))
    return mass / 10000000

def calculateIsentropicEnthalpy(pressureInput, temperature, pressureOutput):
    # if pressureInput <= 0 or pressureOutput <= 0 or temperature <= 0:
    #     return 0.0
    
    # _pressureInput = convertToPA(pressureInput)
    # _temperature = convertToKelvin(temperature)
    # _pressureOutput = convertToPA(pressureOutput)

    # Entropia constante
    entropy = PropsSI('S', 'P', pressureInput, 'T', temperature, 'Water')
    # Entalpia na saída com S constante
    IsentropicEnthalpy = PropsSI('H', 'P', pressureOutput, 'S', entropy, 'Water')
    
    return IsentropicEnthalpy / 1000

def calculateEfficiency(enthalpyInput,  enthalpyOutput, isentropicEnthalpy):
    if (enthalpyInput - isentropicEnthalpy <= 0):
      return 0.0

    return (enthalpyInput - enthalpyOutput) / (enthalpyInput - isentropicEnthalpy)
