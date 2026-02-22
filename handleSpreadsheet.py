import pandas as pd
from CoolProp.CoolProp import PropsSI
from calculator import (
    calculateEnthalpy,
    calculateIsentropicEnthalpy,
    calculateEfficiency,
    calculateMassFlowWithEnthalpy,
)


def calcula_entalpia(temperatura_celsius, pressao_kgcm2):
    if pd.isna(temperatura_celsius) or pd.isna(pressao_kgcm2):
        return 0.0

    if temperatura_celsius <= 0:
        return 0.0

    pressao_pa = float(pressao_kgcm2) * 98066.5
    temperatura_kelvin = float(temperatura_celsius) + 273.15

    try:
        entalpia = PropsSI("H", "P", pressao_pa, "T", temperatura_kelvin, "Water")
    except Exception:
        return None

    return entalpia / 1000  # kJ/kg


def calcular_entalpia_isentropica(pressao_entrada, temperatura_entrada, pressao_saida):
    if (
        pd.isna(pressao_entrada)
        or pd.isna(pressao_saida)
        or pd.isna(temperatura_entrada)
    ):
        return 0.0

    if temperatura_entrada <= 0:
        return 0.0

    pressao_entrada_pa = pressao_entrada * 98066.5
    temperatura_entrada_kelvin = temperatura_entrada + 273.15
    pressao_saida_pa = pressao_saida * 98066.5

    # Entropia constante
    entropia = PropsSI(
        "S", "P", pressao_entrada_pa, "T", temperatura_entrada_kelvin, "Water"
    )
    # Entalpia na saída com S constante
    entalpiaIsentropica = PropsSI("H", "P", pressao_saida_pa, "S", entropia, "Water")

    return entalpiaIsentropica / 1000


def obter_entalpias(df, temperatura, pressao):
    entalpias = []
    for _, linha in df.iterrows():
        temperatura_celsius = linha[temperatura]
        pressao_kgcm2 = linha[pressao]

        entalpia = calcula_entalpia(temperatura_celsius, pressao_kgcm2)
        entalpias.append(entalpia)

    return entalpias


def obter_entalpias_isentropicas(
    df, pressao_entrada, temperatura_entrada, pressao_saida
):
    entalpias = []
    for _, linha in df.iterrows():
        temperatura_celsius = linha[temperatura_entrada]
        pressao_entrada_kgcm2 = linha[pressao_entrada]
        pressao_saida_kgcm2 = linha[pressao_saida]

        entalpia = calcular_entalpia_isentropica(
            pressao_entrada_kgcm2, temperatura_celsius, pressao_saida_kgcm2
        )
        entalpias.append(entalpia)

    return entalpias


def calcular_eficiencia(entalpia_entrada, entalpia_saida, entalpia_isentrocipa):

    if entalpia_entrada - entalpia_isentrocipa <= 0:
        return 0.0

    return (entalpia_entrada - entalpia_saida) / (
        entalpia_entrada - entalpia_isentrocipa
    )


def obter_eficiencias(entalpia_entrada, entalpia_saida, entalpia_isentrocipa):
    eficiencias = []
    for i in range(len(entalpia_entrada)):
        eficiencia = calcular_eficiencia(
            entalpia_entrada[i], entalpia_saida[i], entalpia_isentrocipa[i]
        )
        eficiencias.append(eficiencia)

    return eficiencias


def media_eficiencia(eficiencia):
    return sum(eficiencia) / len(eficiencia)


def handleSpreadsheet(filepath, temperature, pressure, output):
    spreadsheet = pd.read_excel(filepath)
    enthalpy = obter_entalpias(spreadsheet, temperature, pressure)
    spreadsheet[output] = enthalpy

    spreadsheet.to_excel("newFile.xlsx", index=False)


def receiveCalcSheetParams(
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
    try:
        boilerEffVal = float(boilerEfficiency)
        machineEffVal = float(machineEfficiency)
        electricalWorkVal = float(electricalWork)
    except (TypeError, ValueError):
        return

    df = pd.read_excel(filepath)

    enthalpiesInput = []
    enthalpiesOutput = []
    isentropicEnthalpies = []
    efficiencies = []
    massesFlow = []

    for _, linha in df.iterrows():
        try:
            temperatureInput = linha[temp_input_ecolumn]
            temperatureOutput = linha[temp_output_column]
            pressureInput = linha[pressure_input_column]
            pressureOutput = linha[pressure_output_column]

            if pd.isna(temperatureInput) or temperatureInput == "":
                temperatureInput = 0
            if pd.isna(temperatureOutput) or temperatureOutput == "":
                temperatureOutput = 0
            if pd.isna(pressureInput) or pressureInput == "":
                pressureInput = 0
            if pd.isna(pressureOutput) or pressureOutput == "":
                pressureOutput = 0

            enthalpyInput = calculateEnthalpy(temperatureInput, pressureInput)
            enthalpyOutput = calculateEnthalpy(temperatureOutput, pressureOutput)

            isentropicEnthalpy = calculateIsentropicEnthalpy(
                pressureInput, temperatureInput, pressureOutput
            )
            efficiency = calculateEfficiency(
                enthalpyInput, enthalpyOutput, isentropicEnthalpy
            )
            massFlow = calculateMassFlowWithEnthalpy(
                enthalpyInput,
                enthalpyOutput,
                electricalWorkVal,
                boilerEffVal,
                machineEffVal,
            )

            enthalpiesInput.append(enthalpyInput)
            enthalpiesOutput.append(enthalpyOutput)
            isentropicEnthalpies.append(isentropicEnthalpy)
            efficiencies.append(efficiency)
            massesFlow.append(massFlow)
        except (ValueError, TypeError, KeyError, ZeroDivisionError):
            enthalpiesInput.append(None)
            enthalpiesOutput.append(None)
            isentropicEnthalpies.append(None)
            efficiencies.append(None)
            massesFlow.append(None)

    df["Entalpia Entrada (kJ/kg)"] = enthalpiesInput
    df["Entalpia Saída (kJ/kg)"] = enthalpiesOutput
    df["Entalpia Isentrópica (kJ/kg)"] = isentropicEnthalpies
    df["Eficência Turbina (%)"] = efficiencies
    df["Vazão Mássica (kg/s)"] = massesFlow
    df.to_excel("newFile_mass_flow.xlsx", index=False)

def main():
    try:
        df = pd.read_excel("data-turbina.xlsx")

        entalpia_entrada = obter_entalpias(
            df, "TEMPERATURA ENTRADA (°C)", "PRESSÃO ADMISSÃO (kg/cm²)"
        )
        entalpia_saida = obter_entalpias(
            df, "TEMPERATURA SAÍDA (°C)", "PESSÃO SAÍDA (kg/cm²)"
        )

        entalpia_isentropica = obter_entalpias_isentropicas(
            df,
            "PRESSÃO ADMISSÃO (kg/cm²)",
            "TEMPERATURA ENTRADA (°C)",
            "PESSÃO SAÍDA (kg/cm²)",
        )

        eficiencia = obter_eficiencias(
            entalpia_entrada, entalpia_saida, entalpia_isentropica
        )

        df["Entalpia Entrada (kJ/kg)"] = entalpia_entrada
        df["Entalpia Saída (kJ/kg)"] = entalpia_saida
        df["Entalpia Isentrópica (kJ/kg)"] = entalpia_isentropica
        df["Eficência Turbina (%)"] = eficiencia

        df.to_excel("novo_arquivo.xlsx", index=False)

    except FileNotFoundError:
        print("Arquivo não encontrado!")
    except Exception as e:
        print(f"Erro ao ler/gerar arquivo: {e}")


if __name__ == "__main__":
    main()
