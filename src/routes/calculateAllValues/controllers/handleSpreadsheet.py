import pandas as pd
from src.domain.calculator import (
    convertToPA,
    convertToKelvin,
    convertToKiloJauleForKilogram,
    calculateEnthalpy,
    calculateMassFlow,
    calculateIsentropicEnthalpy,
    calculateEfficiency,
)

def readFile(filepath):
    return pd.read_excel(filepath)


def handleSpreadsheet(
    filepath,
    temp_input_ecolumn,
    temp_output_column,
    pressure_input_column,
    pressure_output_column,
    boilerEfficiency,
    machineEfficiency,
    electricalWork,
):
    if filepath is None:
        return

    spreadsheet = readFile(filepath)

    enthalpiesInput = []
    enthalpiesOutput = []
    isentropicEnthalpies = []
    efficiencies = []
    massesFlow = []

    for _, linha in spreadsheet.iterrows():
        try:
            temperatureInput = linha[temp_input_ecolumn]
            temperatureOutput = linha[temp_output_column]
            pressureInput = linha[pressure_input_column]
            pressureOutput = linha[pressure_output_column]
            boilerEffVal = linha[boilerEfficiency]
            machineEffVal = linha[machineEfficiency]
            electricalWorkVal = linha[electricalWork]

            if pd.isna(temperatureInput) or temperatureInput == "":
                temperatureInput = 0
            if pd.isna(temperatureOutput) or temperatureOutput == "":
                temperatureOutput = 0
            if pd.isna(pressureInput) or pressureInput == "":
                pressureInput = 0
            if pd.isna(pressureOutput) or pressureOutput == "":
                pressureOutput = 0
            if pd.isna(boilerEffVal) or boilerEffVal == "":
                boilerEffVal = 0
            if pd.isna(machineEffVal) or machineEffVal == "":
                machineEffVal = 0
            if pd.isna(electricalWorkVal) or electricalWorkVal == "":
                electricalWorkVal = 0

            temperatureInput = float(convertToKelvin(temperatureInput))
            temperatureOutput = float(convertToKelvin(temperatureOutput))
            pressureInput = float(convertToPA(pressureInput))
            pressureOutput = float(convertToPA(pressureOutput))
            boilerEffVal = float(boilerEffVal)
            machineEffVal = float(machineEffVal)
            electricalWorkVal = float(electricalWorkVal)

            enthalpyInput = calculateEnthalpy(temperatureInput, pressureInput)
            enthalpyOutput = calculateEnthalpy(temperatureOutput, pressureOutput)

            isentropicEnthalpy = calculateIsentropicEnthalpy(
                pressureInput, temperatureInput, pressureOutput
            )
            efficiency = calculateEfficiency(
                enthalpyInput, enthalpyOutput, isentropicEnthalpy
            )
            massFlow = calculateMassFlow(
                enthalpyInput,
                enthalpyOutput,
                electricalWorkVal,
                boilerEffVal,
                machineEffVal,
            )

            enthalpiesInput.append(convertToKiloJauleForKilogram(enthalpyInput))
            enthalpiesOutput.append(convertToKiloJauleForKilogram(enthalpyOutput))
            isentropicEnthalpies.append(convertToKiloJauleForKilogram(isentropicEnthalpy))
            efficiencies.append(efficiency)
            massesFlow.append(massFlow)
            
        except (ValueError, TypeError, KeyError, ZeroDivisionError):
            enthalpiesInput.append(None)
            enthalpiesOutput.append(None)
            isentropicEnthalpies.append(None)
            efficiencies.append(None)
            massesFlow.append(None)

    spreadsheet["Entalpia Entrada (kJ/kg)"] = enthalpiesInput
    spreadsheet["Entalpia Saída (kJ/kg)"] = enthalpiesOutput
    spreadsheet["Entalpia Isentrópica (kJ/kg)"] = isentropicEnthalpies
    spreadsheet["Eficência Turbina (%)"] = efficiencies
    spreadsheet["Vazão Mássica (kg/s)"] = massesFlow

    spreadsheet.to_excel("newFile_mass_flow.xlsx", index=False)
