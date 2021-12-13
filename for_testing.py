


if __name__ == "__main__":
    measurements = {"IN1": {"u_nom": 0.0, "u_fact": 0.0, "error_rate": 0.0},
                    "IN2": {"u_nom": 0.0, "u_fact": 0.0, "error_rate": 0.0},
                    "IN3": {"u_nom": 0.0, "u_fact": 0.0, "error_rate": 0.0},
                    "U_OUT1": {"u_nom": 0.0, "u_fact": 0.0, "error_rate": 0.0},
                    "U_OUT2": {"u_nom": 0.0, "u_fact": 0.0, "error_rate": 0.0},
                    "I_OUT1": {"i_nom": 0.0, "i_fact": 0.0, "error_rate": 0.0},
                    "I_OUT2": {"i_nom": 0.0, "i_fact": 0.0, "error_rate": 0.0},
                    }
    voltage = {'Канал, U': ['IN1', 'IN2', 'IN3'], 'Unom': ['', '', ''], 'Ufact': ['', '', ''],
               'Uerror_rate': ['', '', '']}
    voltage['Unom'][0] = 2
    measurements["IN1"][1] = 24.0
    measurements["IN1"]["u_fact"] = 25.0
    measurements["IN1"]["error_rate"] = 1.0
    print(voltage['Unom'][0])