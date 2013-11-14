"""Common utility functions used by lvsm"""
import socket
import subprocess
import re
import sys
import termcolor
import logging

logger = logging.getLogger('lvsm')

def parse_config(filename):
    #open config file and read it
    lines = print_file(filename)
    # list of valid config keys and their default values
    config_items = {'ipvsadm': 'ipvsadm',
                    'iptables': 'iptables',
                    'pager': '/bin/more',
                    'director_config': '',
                    'firewall_config': '',
                    'director': '',
                    'maintenance_dir': '',
                    'director_cmd': '',
                    'firewall_cmd': '',
                    'nodes': '',
                    'version_control': ''
                    }
    linenum = 0
    for line in lines:
        linenum += 1
        conf, sep, comment = line.rstrip().partition('#')
        if conf:
            k, sep, v = conf.rstrip().partition('=')
            key = k.lstrip().rstrip()
            value = v.lstrip().rstrip()
            if config_items.get(key) is None:
                # print "[ERROR]: configuration file line %d: invalid variable '%s'"  % (linenum, key)
                logger.error("configuration file line %d: invalid variable '%s'"  % (linenum, key))
                sys.exit(1)
            else:
                config_items[key] = value
                # if the item is a config file, verify that the file exists
                if key.endswith('_config'):
                    try:
                        file = open(value)
                        file.close()
                    except IOError as e:
                        # print "[ERROR]: in lvsm configuration file line %d" % linenum
                        # print "[ERROR]: %s: '%s'" % (e.strerror, e.filename)
                        logger.error("in lvsm configuration file line %d" % linenum)
                        logger.error(e)
                        sys.exit(1)
    return config_items


def print_file(filename):
    """opens a file and returns its contents as list"""
    lines = list()
    try:
        file = open(filename)
        lines = file.readlines()
        file.close()
    except IOError as e:
        # print "[ERROR]: Unable to read '%s'" % e.filename
        # print "[ERROR]: %s: '%s'" % (e.strerror, e.filename)
        logger.error(e)
    return lines


def getportnum(port):
    """accepts a port name or number and returns the port number as an int.
    returns -1 in case of invalid port name"""
    try:
        portnum = int(port)
        if portnum < 0 or portnum > 65535:
            # print "[ERROR]: invalid port number"
            logger.error("invalid port number")
            portnum = -1
    except:
        try:
            p = socket.getservbyname(port)
            portnum = int(p)
        except socket.error, e:
            # print "[ERROR]: %s" % str(e)
            logger.error(e)
            portnum = -1
    return portnum


def gethostname(host):
    try:
        hostip = socket.gethostbyname(host)
    except socket.gaierror as e:
        logger.error(e.strerror)
        # print "[ERROR]: %s" % e.strerror
        return ''
    else:
        return hostip


def pager(pager,lines):
    """print lines to screen and mimic behaviour of MORE command"""
    text = "\n".join(lines)
    if pager.upper() == 'NONE':
        print text
    else:
        try:
            p = subprocess.Popen(pager.split(), stdin=subprocess.PIPE)
        except OSError as e:
            logger.error("Problem with pager: %s" % pager)
            logger.error(e)
        else:
            stdout, stderr = p.communicate(input=text)


def check_output(args):
    """Wrapper for subprocess.check_output"""
    logger.debug("Running: %s " % " ".join(args))
    try:
        output = subprocess.check_output(args)
        return output
    # python 2.6 compatibility code
    except AttributeError as e:
        output, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        return output

def has_quotes(value):
    """Check to see if a string is bounded in quotes"""
    m_re = re.search("^\"(.*)\"", value)
    if m_re is not None:
        return True
    else:
        return False

def config_check_ipv4(value):
    """Check that the IPv4 number is in the correct range"""
    m_re = re.search("^(\d+)\.(\d+)\.(\d+)\.(\d+)$", value)
    if m_re is not None:
        if (int(m_re.group(1)) >= 0 and int(m_re.group(1)) <= 255 and
            int(m_re.group(2)) >= 0 and int(m_re.group(2)) <= 255 and
            int(m_re.group(3)) >= 0 and int(m_re.group(3)) <= 255 and
            int(m_re.group(4)) >= 0 and int(m_re.group(4)) <= 255):
            return True
        else:
            return False
    else:
        return False
