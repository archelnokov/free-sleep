"""
This module defines the `StreamProcessor` class, which processes continuous piezoelectric
sensor data to track user presence and extract biometric metrics such as heart rate,
heart rate variability (HRV), and breathing rate.

Key functionalities:
- Buffers incoming piezoelectric sensor data to process trends over time.
- Detects user presence based on signal strength for both left and right sides.
- Uses `BiometricProcessor` to analyze heart rate, HRV, and breathing rate.
- Supports single and dual-sensor configurations.
- Maintains a rolling buffer of sensor readings to smooth out noise.
- Extracts timestamped biometric data and logs presence detections.

Usage:
Instantiate `StreamProcessor` with an initial piezo record and call `process_piezo_record(piezo_record)`
with new sensor data to continuously track and analyze biometric trends.
"""

from typing import Union, Tuple, TypedDict, List, Optional
from collections import deque
import math
from get_logger import get_logger
from biometric_processor import BiometricProcessor
from data_types import *
from typing import Deque
import numpy as np

logger = get_logger()


class StreamProcessor:
    def __init__(self, piezo_record, buffer_size=3, debug=False):
        if 'left2' in piezo_record:
            self.sensor_count = 2
        else:
            self.sensor_count = 1
        self.buffer_size = buffer_size
        # Dequeue only keeps the most recent <BUFFER_SIZE> items here
        self.piezo_buffer: Deque[PiezoDualData] = deque([], maxlen=buffer_size)

        self.left_side_present = False
        self.right_side_present = False
        self.debug = debug
        self.left_processor = BiometricProcessor(side='left', sensor_count=self.sensor_count, insertion_frequency=60, debug=debug)
        self.right_processor = BiometricProcessor(side='right', sensor_count=self.sensor_count, insertion_frequency=60, debug=debug)
        self.midpoint = math.floor(buffer_size / 2)
        self.iteration_count = 0

    def check_presence(self, left1_signal: np.ndarray, right1_signal: np.ndarray):
        self.left_processor.detect_presence(left1_signal)
        self.right_processor.detect_presence(right1_signal)

    def process_piezo_record(self, piezo_record: PiezoDualData):
        self.piezo_buffer.append(piezo_record)
        if len(self.piezo_buffer) == self.buffer_size:
            left1_signal = np.concatenate([entry["left1"] for entry in self.piezo_buffer])
            right1_signal = np.concatenate([entry["right1"] for entry in self.piezo_buffer])

            self.iteration_count += 1
            log = self.iteration_count % 60 == 0

            epoch = self.piezo_buffer[-1]['ts']
            self.check_presence(left1_signal, right1_signal)
            time = datetime.fromtimestamp(epoch)

            if self.left_processor.present:
                if log:
                    logger.debug(f'Presence detected for left side @ {time.isoformat()}')
                if self.sensor_count == 2:
                    left2_signal = np.concatenate([entry["left2"] for entry in self.piezo_buffer])
                else:
                    left2_signal = None

                self.left_processor.calculate_vitals(epoch, left1_signal, left2_signal)

            if self.right_processor.present:
                if log:
                    logger.debug(f'Presence detected for right side @ {time.isoformat()}')
                if self.sensor_count == 2:
                    right2_signal = np.concatenate([entry["right2"] for entry in self.piezo_buffer])
                else:
                    right2_signal = None
                self.right_processor.calculate_vitals(epoch, right1_signal, right2_signal)

