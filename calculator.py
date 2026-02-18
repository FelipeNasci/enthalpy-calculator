from CoolProp.CoolProp import PropsSI

def convertToPA(pressure):
    return float(pressure) * 98066.5

def convertToKelvin(temperature):
    return float(temperature) + 273.15

def convertToKiloJauleForKilogram(jauleValue):
    return jauleValue / 1000

def calculateEnthalpy(temperature, pressure):
    if temperature <= 0:
        return 0.0

    _pressure = convertToPA(pressure)
    _temperature = convertToKelvin(temperature)

    try:
        enthalpy = PropsSI('H', 'P', _pressure, 'T', _temperature, 'Water')
    except Exception:
        return None

    return convertToKiloJauleForKilogram(enthalpy) / 1000  # kJ/kg

def calculateMassFlow(temperatureInput, temperatureOutput, pressureInput, pressureOutput, power, boilerEfficiency, machineEfficiency):
    enthalpyInput = calculateEnthalpy(temperatureInput, pressureInput)
    enthalpyOutput = calculateEnthalpy(temperatureOutput, pressureOutput)

    mass = power / (boilerEfficiency * machineEfficiency * (enthalpyInput - enthalpyOutput))

    return mass / 10000000