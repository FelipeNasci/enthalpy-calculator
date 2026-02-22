from CoolProp.CoolProp import PropsSI

def convertToPA(pressure):
    return float(pressure) * 98066.5

def convertToKelvin(celsiusValue):
    return float(celsiusValue) + 273.15

def convertToKiloJauleForKilogram(jauleValue):
    return jauleValue / 1000

def calculateEnthalpy(temperature, pressure):
    if temperature <= 0:
        return 0.0
    return PropsSI('H', 'P', pressure, 'T', temperature, 'Water')

def calculateMassFlow(enthalpyInput, enthalpyOutput, power, boilerEfficiency, machineEfficiency):
    mass = power / (boilerEfficiency * machineEfficiency * (enthalpyInput - enthalpyOutput))
    return mass

def calculateIsentropicEnthalpy(pressureInput, temperature, pressureOutput):
    entropy = PropsSI('S', 'P', pressureInput, 'T', temperature, 'Water')
    IsentropicEnthalpy = PropsSI('H', 'P', pressureOutput, 'S', entropy, 'Water') 
    return IsentropicEnthalpy

def calculateEfficiency(enthalpyInput, enthalpyOutput, isentropicEnthalpy):
    if (enthalpyInput - isentropicEnthalpy <= 0):
      return 0.0

    return (enthalpyInput - enthalpyOutput) / (enthalpyInput - isentropicEnthalpy)
