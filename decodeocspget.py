#!/usr/bin/python
#####################################################
# Author: Malini Kothapalli
# Date:   Oct 20, 2014
# Script: The script decodes ocsp get urls and prints
#         the ocsp requests in a text format.
#######################################################
import urllib
import re
import os
import base64
import subprocess
import sys
import argparse

# Functions
def printerror( str1, str2="", exit=0 ):
  "A common interface to print errors to either stderr or to a defined "
  "error file and quit"
  if not args.errorfile:
    print(str1+' '+str2)
  else:
    errorfile.write(str1+' '+str2+'\n')
  if exit:
    if args.errorfile:
        errorfile.close()
    sys.exit

derfilename = "/tmp/derfile"

def processurl( url ):
  "A function to parse url of the form http://<ocsp url>/<path component> "
  "and decode path component to ASN.1 format"
  try:
        ocspreq = re.search('http://.*?/(.+)', url).group(1)
  except AttributeError:
        printerror("invalid url", url, 0)
        return
 
  ocspreqbase64  = urllib.unquote(ocspreq)

  try:
        ocspderreq = base64.decodestring(ocspreqbase64)
  except: 
        printerror("Failed to decode", ocspreq, 0)
        return

  derfile = open(derfilename, 'w')
  derfile.write(ocspderreq)
  derfile.close()

  cmd =  '/usr/bin/openssl ocsp -reqin '
  cmd += derfilename
  cmd += ' -req_text'
  if args.outputfile:
      cmd += '>>' + args.outputfile 

  try:
      retcode = subprocess.call(cmd, shell=True)
      if retcode < 0:
        printerror("Error running cmd", cmd, 0)
  except OSError as e:
      printerror("Execution failed", e.strerror, 1)
 
def processfile( filename ):
    with open(args.inputfile, 'r') as finput:
      for line in finput:
        processurl(line)
### end of functions

### parse input arguments 
parser = argparse.ArgumentParser(description="decode get ocsp requests and print in ASN.1 format")
group  = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-r",  "--request",    help="get ocsp request url")
group.add_argument("-i",  "--inputfile",  help="file with multiple ocsp request urls")
parser.add_argument("-o", "--outputfile", help="output to this file, default is stdout")
parser.add_argument("-e", "--errorfile",  help="write errors to this file, by default errors are written to stderr")

args   = parser.parse_args()

if args.errorfile:
  try:
      global errorfile 
      errorfile = open(args.errorfile, 'w')
  except IOError as e:
      printerror("Failed to open file", e.strerror, 1)

if args.request:
    processurl(args.request)
elif args.inputfile:
    processfile(args.inputfile)

if args.errorfile:
    errorfile.close()

sys.exit

