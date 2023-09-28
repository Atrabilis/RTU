# Tramas IEC 60870-5-104 en forma de bytes

# STARTDT Act (Iniciar comunicación)
startdt_act = b'\x68\x04\x07\x00\x00\x00'

# STARTDT Con (Confirmación de inicio de comunicación)
startdt_con = b'\x68\x04\x0B\x00\x00\x00'

# STOPDT Act (Detener comunicación)
stopdt_act = b'\x68\x04\x13\x00\x00\x00'

# STOPDT Con (Confirmación de detención de comunicación)
stopdt_con = b'\x68\x04\x23\x00\x00\x00'

# TESTFR Act (Prueba de comunicación)
testfr_act = b'\x68\x04\x43\x00\x00\x00'

# TESTFR Con (Confirmación de prueba de comunicación)
testfr_con = b'\x68\x04\x83\x00\x00\x00'

# ACK (Acknowledge)
ack = b'\x68\x04\x0D\x00\x00\x00'

# NACK (Not Acknowledge)
nack = b'\x68\x04\x0E\x00\x00\x00'

# Solicitud de Enlace Activo (ACT)
solicitud_act = b'\x68\x04\x09\x00\x00\x00'

# Confirmación de Enlace Activo (ACT CON)
confirmacion_act_con = b'\x68\x04\x0F\x00\x00\x00'

#ASDU types:
C_IC_NA_1= bytes([100])


