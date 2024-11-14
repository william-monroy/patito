class VirtualMemory:
    def __init__(self):
        # Definir los rangos de direcciones para cada segmento y tipo
        self.segments = {
            'global': {
                'entero': {'start': 1000, 'end': 1999, 'current': 1000},
                'flotante': {'start': 2000, 'end': 2999, 'current': 2000},
                'booleano': {'start': 3000, 'end': 3999, 'current': 3000},
                'cadena': {'start': 4000, 'end': 4999, 'current': 4000},
            },
            'local': {
                'entero': {'start': 5000, 'end': 5999, 'current': 5000},
                'flotante': {'start': 6000, 'end': 6999, 'current': 6000},
                'booleano': {'start': 7000, 'end': 7999, 'current': 7000},
                'cadena': {'start': 8000, 'end': 8999, 'current': 8000},
            },
            'temporal': {
                'entero': {'start': 9000, 'end': 9999, 'current': 9000},
                'flotante': {'start': 10000, 'end': 10999, 'current': 10000},
                'booleano': {'start': 11000, 'end': 11999, 'current': 11000},
                'cadena': {'start': 12000, 'end': 12999, 'current': 12000},
            },
            'constante': {
                'entero': {'start': 13000, 'end': 13999, 'current': 13000},
                'flotante': {'start': 14000, 'end': 14999, 'current': 14000},
                'booleano': {'start': 15000, 'end': 15999, 'current': 15000},
                'cadena': {'start': 16000, 'end': 16999, 'current': 16000},
            }
        }

    def get_address(self, segment, var_type):
        if self.segments[segment][var_type]['current'] > self.segments[segment][var_type]['end']:
            raise Exception(f"Memory overflow in segment {segment} for type {var_type}")
        address = self.segments[segment][var_type]['current']
        self.segments[segment][var_type]['current'] += 1
        return address

    def reset_local_memory(self):
        # Reinicia las direcciones de variables locales y temporales
        for var_type in self.segments['local']:
            self.segments['local'][var_type]['current'] = self.segments['local'][var_type]['start']
        for var_type in self.segments['temporal']:
            self.segments['temporal'][var_type]['current'] = self.segments['temporal'][var_type]['start']
