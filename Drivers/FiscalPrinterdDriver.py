# -*- coding: iso-8859-1 -*-
from DriverInterface import DriverInterface

import sys

def debugEnabled( *args ):
    print >>sys.stderr, " ".join( map(str, args) )

def debugDisabled( *args ):
    pass

debug = debugDisabled

class PrinterException(Exception):
    pass

class UnknownServerError(PrinterException):
    errorNumber = 1

class ComunicationError(PrinterException):
    errorNumber = 2

class PrinterStatusError(PrinterException):
    errorNumber = 3

class FiscalStatusError(PrinterException):
    errorNumber = 4

ServerErrors = [UnknownServerError, ComunicationError, PrinterStatusError, FiscalStatusError]

class ProxyError(PrinterException):
    errorNumber = 5


class FiscalPrinterdDriver(DriverInterface):
    WAIT_TIME = 10
    RETRIES = 4
    WAIT_CHAR_TIME = 0.1
    NO_REPLY_TRIES = 200


    def __init__( self, speed = 9600 ):
        # self._serialPort = serial.Serial( port = path, timeout = None, baudrate = speed )
        self._initSequenceNumber()
        bufsize = 1 # line buffer
        self.file = open("hasard.txt", "a", bufsize)


	
    def sendCommand( self, commandNumber, fields, skipStatusErrors = False ):
        message = chr(0x02) + chr( self._sequenceNumber ) + chr(commandNumber)
        if fields:
            message += chr(0x1c)
        message += chr(0x1c).join( fields )
        message += chr(0x03)
        checkSum = sum( [ord(x) for x in message ] )
        checkSumHexa = ("0000" + hex(checkSum)[2:])[-4:].upper()
        message += checkSumHexa
        reply = self._sendMessage( message )
        self.file.write(message+"\n")
        self._incrementSequenceNumber()
        return self._parseReply( reply, skipStatusErrors )




    def _write( self, s ):
        debug( "_write", ", ".join( [ "%x" % ord(c) for c in s ] ) )
        print("Escribiendo ...")
        print(s.encode('ascii', 'ignore'))
        print("*-*-**-*-**-*-**-*-*")
        print(s.encode())


    def __del__( self ):
        if hasattr(self, "_serialPort" ):
            try:
                self.file.close()
                self.close()
            except:
                pass

    def _parseReply( self, reply, skipStatusErrors ):
        r = reply[4:-1] # Saco STX <Nro Seq> <Nro Comando> <Sep> ... ETX
        fields = r.split( chr(28) )
        printerStatus = fields[0]
        fiscalStatus = fields[1]
        if not skipStatusErrors:
            self._parsePrinterStatus( printerStatus )
        return fields

    def _parsePrinterStatus( self, printerStatus ):
        x = int( printerStatus, 16 )
        for value, message in self.printerStatusErrors:
            if (value & x) == value:
                raise PrinterStatusError, message

   

    def _checkReplyBCC( self, reply, bcc ):
        debug( "reply", reply, [ord(x) for x in reply] )
        checkSum = sum( [ord(x) for x in reply ] )
        debug( "checkSum", checkSum )
        checkSumHexa = ("0000" + hex(checkSum)[2:])[-4:].upper()
        debug( "checkSumHexa", checkSumHexa )
        debug( "bcc", bcc )
        return checkSumHexa == bcc.upper()



