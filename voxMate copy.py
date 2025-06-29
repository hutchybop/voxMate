#!/usr/bin/env python3
import os
import re
import struct
import signal
import atexit
import sys
import tempfile
import time
import subprocess
import wave
import logging
import numpy as np
import sounddevice as sd
import pvporcupine
import pyaudio
import socketio
import threading
from ctypes import *
from gtts import gTTS
from openai import OpenAI
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Optional, Tuple, Generator
from pymongo import MongoClient
import json
from pathlib import Path
from typing import Dict, Any











