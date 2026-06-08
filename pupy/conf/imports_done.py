# Python 3 only - list of imports considered "done" for payload (getLinuxImportedModules)
from collections import OrderedDict
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util import Counter
from io import BytesIO, StringIO
from itertools import starmap
from operator import xor
from struct import Struct
import argparse
import base64
import binascii
import code
import collections
import contextlib
import copy
import configparser
import datetime
import errno
import fractions
import getpass
import glob
import hashlib
import hmac
import importlib
import inspect
import json
import logging
import math
import multiprocessing
import os
import pkgutil
import platform
import queue
import random
import re
import shlex
import shutil
import site
import socket
import socketserver
import ssl
import string
import struct
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import urllib
import urllib.request
import uuid
import yaml
import zlib

if os.name == 'nt':
    import ctypes
    import ctypes.wintypes

if os.name == 'posix':
    import pty
