#!/usr/bin/env python3

import serial
import time
import logging


###
# Constants
###

ACK = 0x50
SYNC = 0xFC

## Setting commands ##
SET_DENOM = 0xC0
SET_SECURITY = 0xC1
SET_INHIBIT = 0xC3
SET_DIRECTION = 0xC4
SET_OPT_FUNC = 0xC5
SET_BAR_FUNC = 0xC6
SET_BAR_INHIBIT = 0xC7

## Setting status requests ##
GET_DENOM = 0x80
GET_SECURITY = 0x81
GET_INHIBIT = 0x83
GET_DIRECTION = 0x84
GET_OPT_FUNC = 0x85
GET_BAR_FUNC = 0x86
GET_BAR_INHIBIT = 0x87

GET_VERSION = 0x88
GET_BOOT_VERSION = 0x89

################################
### Controller -> Acceptor ###
################################

STATUS_REQ = 0x11
STATUS_REQ_EXTENSAO = bytearray([0xF0, 0x1A])

## Operation commands ##
RESET = 0x40
STACK_1 = 0x41
STACK_2 = 0x42
RETURN = 0x43
HOLD = 0x44
WAIT = 0x45

################################
### Acceptor -> Controller ###
################################

## Status ##
ENABLE = 0x11
IDLE = 0x11  # Alias for ENABLE
ACEPTING = 0x12
ESCROW = 0x13
STACKING = 0x14
VEND_VALID = 0x15
STACKED = 0x16
REJECTING = 0x17
RETURNING = 0x18
HOLDING = 0x19
DISABLE = 0x1A
INHIBIT = 0x1A  # Alias for DISABLE
INITIALIZE = 0x1B
NORM_STATUSES = tuple(range(0x11, 0x1C))
## Status extension ##
NORMAL = 0x10 #  + data 
PAYING = 0x20
PAY_STAY= 0x24
PAY_VALID= 0x23
 
## Power up status ##
POW_UP = 0x40
POW_UP_BIA = 0x41  # Power up with bill in acceptor
POW_UP_BIS = 0x42  # Power up with bill in stacker
POW_STATUSES = 0x40, 0x41, 0x42

## Error status ##
STACKER_FULL = 0x43
STACKER_OPEN = 0x44
ACCEPTOR_JAM = 0x45
STACKER_JAM = 0x46
PAUSE = 0x47
CHEATED = 0x48
FAILURE = 0x49
COMM_ERROR = 0x4A
INVALID_COMMAND = 0x4B
ERROR_STATUSES = tuple(range(0x43, 0x4C))
## Error status Extension##
RECYCLER_JAM = 0x40
DOOR_OPEN = 0x41
MOTOR_ERROR = 0x42
EEPROM_ERROR = 0x43
PAY_OUT_NOTE_ERROR = 0x44
RECYCLE_BOX_OPEN = 0x45
HARDWARE_ERROR = 0x4A

################################
### Data constants ###
################################

## Escrow ##
DENOM_1 = 0x61
DENOM_2 = 0x62
DENOM_3 = 0x63
DENOM_4 = 0x64
DENOM_5 = 0x65
DENOM_6 = 0x66
DENOM_7 = 0x67
DENOM_8 = 0x68
BARCODE_TKT = 0x6F

ESCROW_EU = {  # 2 and 8 are reserved
    DENOM_1: '5',
    DENOM_3: '10',
    DENOM_4: '20',
    DENOM_5: '50',
    DENOM_6: '100',
    DENOM_7: '200',
    BARCODE_TKT: 'TITO',
}

## Reject reasons ##
INSERTION_ERR = 0x71
MAG_ERR = 0x72
REMAIN_ACC_ERR = 0x73
COMP_ERR = 0X74
CONVEYING_ERR = 0x75
DENOM_ERR = 0x76
PHOTO_PTN1_ERR = 0x77
PHOTO_LVL_ERR = 0x78
INHIBIT_ERR = 0x79
OPERATION_ERR = 0x7B
REMAIN_STACK_ERR = 0x7C
LENGTH_ERR = 0x7D
PHOTO_PTN2_ERR = 0x7E
MULTI_ERR = 0x98
TKT_BACKSIDE_ERR = 0x9B

REJECT_REASONS = {
    INSERTION_ERR: "Insertion error",
    MAG_ERR: "Magnetic sensor error",
    REMAIN_ACC_ERR: "Remaining bills in head error",
    COMP_ERR: "Compensation error",
    CONVEYING_ERR: "Conveying error",
    DENOM_ERR: "Error assessing denomination",
    PHOTO_PTN1_ERR: "Photo pattern 1 error",
    PHOTO_LVL_ERR: "Photo level error",
    INHIBIT_ERR: "Inhibited",
    OPERATION_ERR: "Operation error",
    REMAIN_STACK_ERR: "Remaining bills in stacker error",
    LENGTH_ERR: "Length error",
    PHOTO_PTN2_ERR: "Photo pattern 2 error",
    MULTI_ERR: "Multiple bills inserted",
    TKT_BACKSIDE_ERR: "Ticket inserted upside-down",
}

## Failure codes ##
STACK_MOTOR_FAULT = 0xA2
TRANS_SPEED_FAULT = 0xA5
TRANS_MOTOR_FAULT = 0xA6
CAN_NOT_RDY = 0xAB
HEAD_REMOVE = 0xAF
BOOT_ROM_FAULT = 0xB0
EXT_ROM_FAULT = 0xB1
ROM_FAULT = 0xB2
EXT_ROM_WRT_FAULT = 0xB3

FAILURE_CODES = {
    STACK_MOTOR_FAULT: "Stacker motor failure",
    TRANS_SPEED_FAULT: "Transport motor speed failure",
    TRANS_MOTOR_FAULT: "Transport motor failure",
    CAN_NOT_RDY: "Cash box not ready",
    HEAD_REMOVE: "Validator head removed",
    BOOT_ROM_FAULT: "Boot ROM failure",
    EXT_ROM_FAULT: "External ROM failure",
    ROM_FAULT: "ROM failure",
    EXT_ROM_WRT_FAULT: "External ROM write failure",
}

############################
### Bitfield constants ###
############################

## Denom inhibit (SET_DENOM) ##
# Two bytes, only first byte used
# 0 = enabled, 1 = disabled
DENOM_USA_1 = 1
DENOM_USA_RESERVED1 = 2
DENOM_USA_5 = 4
DENOM_USA_10 = 8
DENOM_USA_20 = 16
DENOM_USA_50 = 32
DENOM_USA_100 = 64
DENOM_USA_RESERVED2 = 128
DENOM_USA_DEFAULT = DENOM_USA_RESERVED1 | DENOM_USA_RESERVED2
DENOMS = {
    'denom1': 1,
    'denom2': 2,
    'denom3': 4,
    'denom4': 8,
    'denom5': 16,
    'denom6': 32,
    'denom7': 64,
    'denom8': 128,
}
DENOM_MAP = {
    'denom1': 0x61,
    'denom2': 0x62,
    'denom3': 0x63,
    'denom4': 0x64,
    'denom5': 0x65,
    'denom6': 0x66,
    'denom7': 0x67,
    'denom8': 0x68,
}

## Denom security (SET_SECURITY) ##
# Two bytes, only first byte used
# 0 = low security, 1 = high security
SECURITY_USA_1 = 1
SECURITY_USA_RESERVED1 = 2
SECURITY_USA_5 = 4
SECURITY_USA_10 = 8
SECURITY_USA_20 = 16
SECURITY_USA_50 = 32
SECURITY_USA_100 = 64
SECURITY_USA_RESERVED2 = 128
SECURITY_USA_DEFAULT = 0

## Direction inhibit (SET_DIRECTION) ##
# 0 = enabled, 1 = disabled
# When facing the obverse of the bill, A is on the left
DIR_FRONT_A = 1
DIR_FRONT_B = 2
DIR_BACK_A = 4
DIR_BACK_B = 8
DIR_DEFAULT = 0
DIRECTIONS = {
    'fa': 1,
    'fb': 2,
    'ba': 4,
    'bb': 8,
}

## Optional functions (SET_OPT_FUNC) ##
# 0 = disabled, 1 = enabled
OPT_POW_RECOV = 2  # power recovery
OPT_AUTO_RETRY = 4  # auto retry operation
OPT_24CHAR = 8  # accept 24-character barcodes
OPT_NEAR_FULL = 32  # nearly full stacker?
OPT_ENT_SENS = 64  # entrance sensor event
OPT_ENCRYPT = 128  # encryption
OPT_DEFAULT = 0
OPTIONS = {
    'power_recovery': 2,
    'auto_retry': 4,
    '24_char_barcode': 8,
    'near_full': 32,
    'entrance_event': 64,
    'encryption': 128,
}

## Barcode functions (SET_BAR_FUNC) ##
# first byte barcode type (only valid value is 0x01 = interleaved 2 of 5)
# second byte:
BAR_18_CHAR = 0x12
BAR_MULTI = 0xFF  # required if OPT_24CHAR is set?
##
# Exceptions
##
class CRCError(Exception):
    """Computed CRC does not match given CRC"""
    pass

class SyncError(Exception):
    """Tried to read a message, but got wrong start byte"""
    pass

class PowerUpError(Exception):
    """Expected power up, but received wrong status"""
    pass

class AckError(Exception):
    """Acceptor did not acknowledge as expected"""
    pass

class DenomError(Exception):
    """Unknown denomination reported in escrow"""
    pass
###################################################
# CRC CONFIG
###################################################

def get_crc(message):
    """Get CRC value for a given bytes object using CRC-CCITT Kermit"""

    TABLE = [
        0x0000, 0x1189, 0x2312, 0x329B, 0x4624, 0x57AD, 0x6536, 0x74BF,
        0x8C48, 0x9DC1, 0xAF5A, 0xBED3, 0xCA6C, 0xDBE5, 0xE97E, 0xF8F7,
        0x1081, 0x0108, 0x3393, 0x221A, 0x56A5, 0x472C, 0x75B7, 0x643E,
        0x9CC9, 0x8D40, 0xBFDB, 0xAE52, 0xDAED, 0xCB64, 0xF9FF, 0xE876,
        0x2102, 0x308B, 0x0210, 0x1399, 0x6726, 0x76AF, 0x4434, 0x55BD,
        0xAD4A, 0xBCC3, 0x8E58, 0x9FD1, 0xEB6E, 0xFAE7, 0xC87C, 0xD9F5,
        0x3183, 0x200A, 0x1291, 0x0318, 0x77A7, 0x662E, 0x54B5, 0x453C,
        0xBDCB, 0xAC42, 0x9ED9, 0x8F50, 0xFBEF, 0xEA66, 0xD8FD, 0xC974,
        0x4204, 0x538D, 0x6116, 0x709F, 0x0420, 0x15A9, 0x2732, 0x36BB,
        0xCE4C, 0xDFC5, 0xED5E, 0xFCD7, 0x8868, 0x99E1, 0xAB7A, 0xBAF3,
        0x5285, 0x430C, 0x7197, 0x601E, 0x14A1, 0x0528, 0x37B3, 0x263A,
        0xDECD, 0xCF44, 0xFDDF, 0xEC56, 0x98E9, 0x8960, 0xBBFB, 0xAA72,
        0x6306, 0x728F, 0x4014, 0x519D, 0x2522, 0x34AB, 0x0630, 0x17B9,
        0xEF4E, 0xFEC7, 0xCC5C, 0xDDD5, 0xA96A, 0xB8E3, 0x8A78, 0x9BF1,
        0x7387, 0x620E, 0x5095, 0x411C, 0x35A3, 0x242A, 0x16B1, 0x0738,
        0xFFCF, 0xEE46, 0xDCDD, 0xCD54, 0xB9EB, 0xA862, 0x9AF9, 0x8B70,
        0x8408, 0x9581, 0xA71A, 0xB693, 0xC22C, 0xD3A5, 0xE13E, 0xF0B7,
        0x0840, 0x19C9, 0x2B52, 0x3ADB, 0x4E64, 0x5FED, 0x6D76, 0x7CFF,
        0x9489, 0x8500, 0xB79B, 0xA612, 0xD2AD, 0xC324, 0xF1BF, 0xE036,
        0x18C1, 0x0948, 0x3BD3, 0x2A5A, 0x5EE5, 0x4F6C, 0x7DF7, 0x6C7E,
        0xA50A, 0xB483, 0x8618, 0x9791, 0xE32E, 0xF2A7, 0xC03C, 0xD1B5,
        0x2942, 0x38CB, 0x0A50, 0x1BD9, 0x6F66, 0x7EEF, 0x4C74, 0x5DFD,
        0xB58B, 0xA402, 0x9699, 0x8710, 0xF3AF, 0xE226, 0xD0BD, 0xC134,
        0x39C3, 0x284A, 0x1AD1, 0x0B58, 0x7FE7, 0x6E6E, 0x5CF5, 0x4D7C,
        0xC60C, 0xD785, 0xE51E, 0xF497, 0x8028, 0x91A1, 0xA33A, 0xB2B3,
        0x4A44, 0x5BCD, 0x6956, 0x78DF, 0x0C60, 0x1DE9, 0x2F72, 0x3EFB,
        0xD68D, 0xC704, 0xF59F, 0xE416, 0x90A9, 0x8120, 0xB3BB, 0xA232,
        0x5AC5, 0x4B4C, 0x79D7, 0x685E, 0x1CE1, 0x0D68, 0x3FF3, 0x2E7A,
        0xE70E, 0xF687, 0xC41C, 0xD595, 0xA12A, 0xB0A3, 0x8238, 0x93B1,
        0x6B46, 0x7ACF, 0x4854, 0x59DD, 0x2D62, 0x3CEB, 0x0E70, 0x1FF9,
        0xF78F, 0xE606, 0xD49D, 0xC514, 0xB1AB, 0xA022, 0x92B9, 0x8330,
        0x7BC7, 0x6A4E, 0x58D5, 0x495C, 0x3DE3, 0x2C6A, 0x1EF1, 0x0F78
    ]

    crc = 0x0000
    for byte in message:
        crc = (crc >> 8) ^ TABLE[(crc ^ byte) & 0xff]

    # convert to bytes
    crc = '%04x' % crc
    crc = [int(crc[-2:], 16), int(crc[:-2], 16)]

    return bytes(crc)

###################################################
# CLASS BILLVAL
# represena el billeterom, sus diferentes estados y repseustas
###################################################

class BillVal:
    """Represent an ID-003 bill validator as a subclass of `serial.Serial`"""

    def __init__(self, port, log_raw=False, threading=False):
        self.com = serial.Serial(
            port, 9600, serial.EIGHTBITS, serial.PARITY_EVEN, timeout=0.05)

        self.bv_status = None
        self.bv_version = None

        self.threading = threading

        self.all_statuses = NORM_STATUSES + ERROR_STATUSES + POW_STATUSES
#         se definen los eventos de la uart
        self.bv_events = {
            IDLE: self._on_idle,
            ACEPTING: self._on_accepting,
            ESCROW: self._on_escrow,
            STACKING: self._on_stacking,
            VEND_VALID: self._on_vend_valid,
            STACKED: self._on_stacked,
            REJECTING: self._on_rejecting,
            RETURNING: self._on_returning,
            HOLDING: self._on_holding,
            INHIBIT: self._on_inhibit,
            INITIALIZE: self._on_init,
            STACKER_FULL: self._on_stacker_full,
            STACKER_OPEN: self._on_stacker_open,
            ACCEPTOR_JAM: self._on_acceptor_jam,
            STACKER_JAM: self._on_stacker_jam,
            PAUSE: self._on_pause,
            CHEATED: self._on_cheated,
            FAILURE: self._on_failure,
            COMM_ERROR: self._on_comm_error,
            INVALID_COMMAND: self._on_invalid_command,
        }

        self.bv_denoms = ESCROW_EU

        self.bv_on = False

        # set up logging
        self.raw = log_raw
#         LOGGING
        if not logging.getLogger('').hasHandlers():
            logging.basicConfig(level=logging.DEBUG,
                                format="[%(asctime)s] %(levelname)s: %(message)s",
                                filename='debug.log',
                                filemode='w',
                                )
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            formatter = logging.Formatter("%(levelname)s: %(message)s")
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
# RAW LOGGING

    def _raw(self, pre, msg):
        if self.raw:
            msg = ['0x%02x' % x for x in msg]
            log = open('raw.log', 'a')
            log.write('{} {}\r\n'.format(pre, msg))
            log.close()
####################################
#  UART STATES
####################################
#       BOX FULL
    def _on_stacker_full(self, data):
        logging.error("Stacker full.")
#       Stacker OPEN

    def _on_stacker_open(self, data):
        logging.warning("Stacker open.")
#       ACEPTANDO BILLETES
    def _on_acceptor_jam(self, data):
        logging.error("Acceptor jam.")
#
    def _on_stacker_jam(self, data):
        logging.error("Stacker jam.")
#       Cuanto el estado es pausa
    def _on_pause(self, data):
        logging.warning(
            "BV paused. If there's a second bill being inserted, remove it.")
#
    def _on_cheated(self, data):
        logging.warning("BV cheated.")
#
    def _on_failure(self, data):
        fault = ord(data)
        if fault not in FAILURE_CODES:
            logging.error("Unknown failure: %02x" % fault)
        else:
            logging.error(FAILURE_CODES[fault])
#
    def _on_comm_error(self, data):
        logging.warning("Communication error.")
        logging.debug("Details: %r" % ['0x%02x' % x for x in data])
#
    def _on_invalid_command(self, data):
#
        logging.warning("Invalid command.")
#
    def _on_idle(self, data):
        logging.info("BV idle.")
#
    def _on_accepting(self, data):
        logging.info("BV accepting...")
#
    def _on_escrow(self, data):
        """
        CUANDO RECIBE DINERO EL BILLETERO
        llama a esta funci??n
        mediante la seleccion del billetero
        debe de enviar los billetes de un tipo a un sitio
        y los de otro al otro
        """
        escrow = data[0]
        if escrow not in self.bv_denoms:
            raise DenomError("No se que denom es: %x" % escrow)
        elif escrow == BARCODE_TKT:
            barcode = data[1:]
            logging.info("Barcode: %s" % barcode)
        else:
            logging.info("Denom: %s" % self.bv_denoms[escrow])

        s_r = ''
        while s_r not in ('1', '2', 'r'):
            s_r = input("(1) Stack and acknowledge when bill passes stacker lever\n"
                        "(2) Stack and acknowledge when bill is stored\n"
                        "(R)eturn ").lower()
            if self.bv_denoms[escrow] == 10:
                print("Billete de 10 ")
            if self.bv_denoms[escrow] == 20:
                print("Billete de 20 ")
            if self.bv_denoms[escrow] == 5:
                print("Billete de 5 ")
            if self.bv_denoms[escrow] == 50:
                print("Billete de 50 ")
            if s_r == '1':
                logging.info("Sending Stack-1 command...")
                self.accepting_denom = self.bv_denoms[escrow]
                status = None
                while status != ACK:
                    self.send_command(STACK_1, b'')
                    status, data = self.read_response()
                logging.debug("Received ACK")
                self.bv_status = None
            elif s_r == '2':
                logging.info("Sending Stack-2 command...")
                self.accepting_denom = self.bv_denoms[escrow]
                status = None
                while status != ACK:
                    self.send_command(STACK_2, b'')
                    status, data = self.read_response()
                logging.debug("Received ACK")
                self.bv_status = None
            elif s_r == 'r':
                logging.info("BV to return...")
                status = None
                while status != ACK:
                    self.send_command(RETURN, b'')
                    status, data = self.read_response()
                logging.debug("Received ACK")
                self.bv_status = None
#
    def _on_stacking(self, data):
        logging.info("BV stacking...")
#
    def _on_vend_valid(self, data):
        logging.info("Vend valid for %s." % self.accepting_denom)
        self.send_command(ACK, b'')
        self.accepting_denom = None
#
    def _on_stacked(self, data):
        logging.info("Stacked.")
#
    def _on_rejecting(self, data):
        reason = ord(data)
        if reason in REJECT_REASONS:
            logging.warning("BV rejecting, reason: %s" %
                            REJECT_REASONS[reason])
        else:
            logging.warning("BV rejecting, unknown reason: %02x" % reason)
#
    def _on_returning(self, data):
        logging.info("BV Returning...")
#
    def _on_holding(self, data):
        logging.info("Holding...")
#
    def _on_inhibit(self, data):
        logging.warning("BV inhibited.")
        input("Press enter to reset and initialize BV.")
        status = None
        while status != ACK:
            logging.debug("Sending reset command")
            self.send_command(RESET, b'')
            status, data = self.read_response()
            time.sleep(0.2)
        logging.debug("Received ACK")
        if self.req_status()[0] == INITIALIZE:
            logging.info("Initializing bill validator...")
            self.initialize()
        self.bv_status = None
#
    def _on_init(self, data):
        logging.warning("BV waiting for initialization")
        input("Press enter to reinitialize the BV.")
        self.initialize()
###################################################
# Send default command
#       HEAD => SYNC(FC) LENGTH [command] [data] CRC1 CRC2
###################################################
 
    def send_command(self, command, data=b''):
        """Send a generic command to the bill validator"""

        length = 5 + len(data)  # SYNC, length, command, and 16-bit CRC
        message = bytes([SYNC, length, command]) + data
        message += get_crc(message)

        # log message
        self._raw('>', message)

        return self.com.write(message)
###################################################
# Send expansion command
#       HEAD => SYNC(FC) LENGTH [command] [data] CRC1 CRC2
###################################################
        # FC 09 F0 20 4A 01 02 8B 5C
    def sendRawCommand(self):
        return self.com.write(bytes([0xFC ,0x09, 0xF0, 0x20, 0x4A, 0x01, 0x02, 0x8B, 0x5C]))
        
    def send_expansion_command(self, command, data=b''):
        """Send a expansion command to the bill validator"""
        commandA = 0xF0
        length = 6 + len(data)  # SYNC, length, command, and 16-bit CRC
        message = bytes([SYNC, length, commandA,command]) + bytes(data)
        message += get_crc(message)
# [FC 0D F0 20 D0 04 00 01 08 00 02 40 5A
        # log message
        self._raw('>', message)

        return self.com.write(message)
###################################################
# Read default command
###################################################
    def read_response(self):
        """Parse data del billetero. Devuelve una tuple (command, data)"""

        start = None
        while start == None:
            start = self.com.read(1)
            if len(start) == 0:
                # read timed out, return None
                return (None, b'')
            elif start == b'\x00':
                return (0x00, b'')
            elif ord(start) != SYNC and start:
                raise SyncError("Wrong start byte, got %s" % start)

        total_length = self.com.read()
        data_length = ord(total_length) - 5

        command = self.com.read()

        if data_length:
            data = self.com.read(data_length)
        else:
            data = b''

        crc = self.com.read(2)

        # log message
        full_msg = start + total_length + command + data
        self._raw('<', full_msg)

        # check our data
        if get_crc(full_msg) != crc:
            pass
            #raise CRCError("CRC mismatch") (TODO:fallo con crc a veces revisar)

        return ord(command), data
###################################################
#  POWER ON FASE 1 
###################################################
    def power_on(self, *args, **kwargs):
        """Handle startup routines"""
        # Activamos el estado de ON
        self.bv_on = True
        # Limpiamos estado
        status = None
        # Esperamos nuevo estado cuando envia POW_STATUSES
        # Siguiente estado POW_STATUSES
        while status is None or status == 0x00:
            status, data = self.req_status()
            if not self.bv_on:
                # En caso de polling forzamos PowerUP
                self.init_status = None
                return
        # update estado
        self.init_status = status
       
        # Estado POW_SATUSES 
        # #Ya esta ready to fight 
        if status not in POW_STATUSES:
            logging.warning(
                "Acceptor already powered up, status: %02x" % status)
            return self.init_status
        # Estado POW_UP para inicializar
        elif status == POW_UP:
            logging.info("Powering up...")
            #Version Info
            logging.info("Getting version...")
            # Siguiente estado Get_VERSION
            self.send_command(GET_VERSION)
            status, self.bv_version = self.read_response()
            logging.info("BV software version: %s" % self.bv_version.decode())
            
            # Estado POW_UP para inicializar
            # Enviando 40H RESET 
            self.reset()
            while status != ACK:
                logging.debug("Sending reset command")
                self.send_command(RESET)
                status, data = self.read_response()
            # Comprobamos que cambia el estado
            if self.req_status()[0] == INITIALIZE:
                # AHORA ESTAMOS EN ESTADO INITIALIZED
                self.initialize(*args, **kwargs)
            ######################################
            #    TODO: Implement  DONE
            #             - community Mode 
            #             - security Mode
            #             - community Mode 
            ######################################
        else:
            # Esta en Reject  o Stack Mode
            while status != ACK:
                self.send_command(RESET)
                status, data = self.read_response()
            if self.req_status()[0] == INITIALIZE:
                self.initialize(*args, **kwargs)

        #  BillVal.poll() 

        return self.init_status

    def initialize(self, denom=[0x82, 0], sec=[0, 0], dir=[0], opt_func=[0, 0],
                   inhibit=[0], bar_func=[0x01, 0x12], bar_inhibit=[0]):
        
        """Initialize BV settings"""   
        self.set_denom(denom)
        self.set_security(sec)
        self.set_direction(dir)
        self.set_optional_func(opt_func)
        self.set_inhibit(inhibit)
        self.set_barcode_inhibit(bar_inhibit)
        self.set_barcode_function(bar_func)
        while self.req_status()[0] == INITIALIZE:
            # wait for initialization to finish
            time.sleep(0.2)

###################################################
#  POLL FASE 2 Recoleccion de billetes 
###################################################
    def poll(self, interval=0.2):
        """Send a status request to the bill validator every `interval` seconds
        and fire event handlers. `interval` defaults to 200 ms

        Event handlers are only fired upon status changes. Event handlers can
        set `self.bv_status` to None to force event handler to fire on the next
        status request.
        """
        while True:
            poll_start = time.time()
            status, data = self.req_status()
            if (status, data) != self.bv_status:
                if status in self.bv_events:
                    self.bv_events[status](data)
            self.bv_status = (status, data)
            wait = interval - (time.time() - poll_start)
            if wait > 0.0:
                time.sleep(wait)

###################################################
#  PAYOUT FASE 3 Pago de billetes 
###################################################
    def payout(self):
        """ """
        print("payout start")
        (status,data) = self.req_status()
        while (status != INHIBIT):
            self.set_inhibit(1) 
            time.sleep(0.2)
            (status,data) = self.req_status()
        print("payout state inhibit 01 DONE")
        
    def settingsCurrencyRecycler():
        print("settingsCurrencyRecycler")
        (status,data) = self.req_status()
        while (status != INHIBIT):
            self.send_command(0xF0,0x20,0xD0,0x04,0x00,0x01,0x08,0x00,0x02) 
            time.sleep(0.2)
            (status,data) = self.req_status()
        print("settingsCurrencyRecycler DONE")
              
    """
        # STATUS REQUEST ==>
        # PAYING 20 <==
        (status,data) = self.req_status()
        while(status != PAYING):
            print("PAYING ...")
            time.sleep(0.2)
            (status,data) = self.req_status()
        
        # STATUS REQUEST ==>
        # PAY STAY 24 <==
        (status,data) = self.req_status()
        while(status != PAY_STAY):
            print("PAY_STAY ...")
            time.sleep(0.2)
            (status,data) = self.req_status()
        
        # STATUS REQUEST ==>
        # PAY VALID 23 <==
        (status,data) = self.req_status()
        while(status != PAY_VALID):
            print("PAY_VALID ...")
            time.sleep(0.2)
            (status,data) = self.req_status()
        # STATUS REQUEST ==>
        # PAY VALID 50 <==
        # ACK ==>

        (status,data) = self.req_status()
        while(status != ACK):
            print("ACK ...")
            self.send_command(ACK)
            time.sleep(0.2)
            (status,data) = self.req_status()
        #---------------------------
        # STATUS REQUEST ==>
        # DISABLE 1A  <==
    """

###################################################
# BUCHUHELPER
###################################################

    def req_status(self):
        """Send status request to bill validator"""

        if not self.bv_on:
            # in case polling thread needs to be terminated before power up
            return None, b''

        if self.com.in_waiting:
            # discard any unused data
            logging.warning("Found unused data in buffer, %r" %
                            self.com.read(self.com.in_waiting))

        self.send_command(STATUS_REQ)

        stat, data = self.read_response()
        if stat not in self.all_statuses + (0x00, None):
            logging.warning(
                "Unknown status code received: %02x, data: %r" % stat, data)

        return stat, data

    def set_denom(self,denom):
        """
        Command to set the receiving of each bill denomintation
        ->:param bytes denom: [0x82, 0] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting denom inhibit: %r" % denom)
        denom = bytes(denom)
        self.send_command(SET_DENOM, denom)
        status, data = self.read_response()
        if (status, data) != (SET_DENOM, denom):
            logging.warning("Acceptor did not echo denom settings")
        
    def set_security(self,sec):
        """
        Command to set the security config
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting security: %r" % sec)
        sec = bytes(sec)
        self.send_command(SET_SECURITY, sec)
        status, data = self.read_response()
        if (status, data) != (SET_SECURITY, sec):
            logging.warning("Acceptor did not echo security settings")
     
    def set_direction(self,dir):
        """
        Command to set the direction config
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting direction inhibit: %r" % dir)
        dir = bytes(dir)
        self.send_command(SET_DIRECTION, dir)
        status, data = self.read_response()
        if (status, data) != (SET_DIRECTION, dir):
            logging.warning("Acceptor did not echo direction settings")
    
    def set_optional_func(self,opt_func):
        """
        Command to set the optional function config
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting optional functions: %r" % opt_func)
        opt_func = bytes(opt_func)
        self.send_command(SET_OPT_FUNC, opt_func)
        status, data = self.read_response()
        if (status, data) != (SET_OPT_FUNC, opt_func):
            logging.warning("Acceptor did not echo option function settings")

    def set_inhibit(self,inhibit):
        """
        Command to set the inhibit state
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting inhibit: %r" % inhibit)
        inhibit = bytes(inhibit)
        self.send_command(SET_INHIBIT, inhibit)
        status, data = self.read_response()
        if (status, data) != (SET_INHIBIT, inhibit):
            logging.warning("Acceptor did not echo inhibit settings")

    def set_barcode_function(self,bar_func):
        """
        Command to set the bar code config
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting barcode functions: %r" % bar_func)
        bar_func = bytes(bar_func)
        self.send_command(SET_BAR_FUNC, bar_func)
        status, data = self.read_response()
        if (status, data) != (SET_BAR_FUNC, bar_func):
            logging.warning("Acceptor did not echo barcode settings")

    def set_barcode_inhibit(self,bar_inhibit):
        """
        Command to set the bar code config
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("Setting barcode inhibit: %r" % bar_inhibit)
        bar_inhibit = bytes(bar_inhibit)
        self.send_command(SET_BAR_INHIBIT, bar_inhibit)
        status, data = self.read_response()
        if (status, data) != (SET_BAR_INHIBIT, bar_inhibit):
            logging.warning("Acceptor did not echo barcode inhibit settings")

    def rc_status_request(self,data):
        """
        Command to set the bar code config
        ->:param bytes sec: [0x00, 0x00] default
        :send_command bytes: [SYNC LNG CMD DATA CRCL CRCH] 
        """
        logging.debug("RC request status (extension) ")
        RC_STATUS_REQUEST = bytes(0xF0,0x1A)
        self.send_command(RC_STATUS_REQUEST, bytes(data))
        status, data = self.read_response()
        if (status, data) != (0xF0, data):
            logging.warning("Acceptor did not echo status request (extension)")

    def reset(self):
        status = None
        while status != ACK:
            print("Sending buchu reset command")
            self.send_command(RESET)
            status, data = self.read_response()
            if self.req_status()[0] == RESET:
                print('BUCHU DONE')
                
#      TEST 2
    def buchu_set_recycler_config(self, data=bytes([0x02, 0x00, 0x01, 0x08, 0x00, 0x02])):
        status = None
        while status != ACK:
            print("Sending buchu_set_recycler_config")
            length = 8 + len(data)  # SYNC, length, command, and 16-bit CRC
            message = bytes([SYNC, length, 240, 32, 208]) + data
            message += get_crc(message)
            self._raw('>', message)
            self.com.write(message)
            status, data = self.read_response()
            if self.req_status()[0] == SET_INHIBIT:
                print('BUCHU DONE SET_INHIBIT')
