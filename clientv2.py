import c104

client = c104.Client(tick_rate_ms=1000, command_timeout_ms=5000)

# add RTU with station and points
connection = client.add_connection(ip="127.0.0.1", port=2404, init=c104.Init.INTERROGATION)
station = connection.add_station(common_address=47)
measurement_point = station.add_point(io_address=11, type=c104.Type.M_ME_NC_1)
command_point = station.add_point(io_address=12, type=c104.Type.C_RC_TA_1)

client.start()