#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import attr
import numpy as np

from habitat_sim.registry import registry
from habitat_sim.sensor import SensorType
from habitat_sim.sensors.noise_models.sensor_noise_model import SensorNoiseModel


def _simulate(image, s_vs_p, amount):
    noisy_rgb = np.copy(image)
    # Salt
    num_salt = np.ceil(amount * image.size * s_vs_p)
    coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape]
    noisy_rgb[tuple(coords)] = 1

    # Pepper
    num_pepper = np.ceil(amount * image.size * (1.0 - s_vs_p))
    coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape]
    noisy_rgb[tuple(coords)] = 0

    return noisy_rgb


@attr.s(auto_attribs=True)
class SaltAndPepperNoiseModelCPUImpl:
    s_vs_p: float
    amount: float

    def simulate(self, image):
        return _simulate(image, self.s_vs_p, self.amount)


@registry.register_noise_model
@attr.s(auto_attribs=True, kw_only=True)
class SaltAndPepperNoiseModel(SensorNoiseModel):
    s_vs_p: float = 0.5
    amount: float = 0.05

    def __attrs_post_init__(self):
        self._impl = SaltAndPepperNoiseModelCPUImpl(self.s_vs_p, self.amount)

    @staticmethod
    def is_valid_sensor_type(sensor_type: SensorType) -> bool:
        return sensor_type == SensorType.COLOR

    def simulate(self, image):
        return self._impl.simulate(image)

    def apply(self, image):
        r"""Alias of `simulate()` to conform to base-class and expected API"""
        return self.simulate(image)
