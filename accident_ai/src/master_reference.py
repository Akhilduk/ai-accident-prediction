PATTERN_OF_COLLISION = {
    1: "Single Vehicle",
    2: "Vehicle to Vehicle",
    3: "Vehicle to Pedestrian",
    4: "Vehicle to Bicycle",
    5: "Vehicle to Animal",
    6: "Hit Standing/Parked Vehicle",
    7: "Hit Fixed/Stationary Object",
    8: "Others (Specify)",
}

TYPE_OF_COLLISION = {
    1: "Hit from Back",
    2: "Hit from Side",
    3: "Run Off Road",
    4: "Vehicle Overturn/Skidding",
    5: "Head On Collision",
    6: "Hit and Run",
    7: "Side Swipe",
    8: "Hit Pedestrian",
    9: "Passenger Fell Down",
    10: "Not Known",
    11: "Others (Specify)",
}

TYPE_OF_VEHICLE = {
    1: "Motorised Two-Wheeler",
    2: "Passenger Auto",
    3: "Car/Jeep/Taxi",
    4: "Bus",
    5: "Mini Bus/Passenger Tempo/Passenger Van",
    6: "Goods Auto/Goods Pick-up Van",
    7: "Goods LCV/Goods Tempo/Mini Lorry/Mini Truck",
    8: "Truck/Lorry",
    9: "Multi-Axle Truck",
    10: "Bicycle",
    11: "Pedestrian",
    12: "Unknown Vehicle",
    13: "Ambulance",
    14: "Others (Specify)",
}

MASTER_REF_TABLES = {
    "Pattern of Collision": PATTERN_OF_COLLISION,
    "Type of Collision": TYPE_OF_COLLISION,
    "Type of Vehicle": TYPE_OF_VEHICLE,
}
