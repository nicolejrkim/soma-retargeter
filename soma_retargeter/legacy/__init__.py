# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""
The v0.1-lineage retargeting pipeline (``NewtonPipeline``) and everything it
needs to reproduce the retargeter-suite campaign recipes bit for bit.

Kept beside the v0.2.0 ``SomaRetargetingPipeline`` on purpose: the two
pipelines use different scaler config formats (per-joint ``joint_scales`` vs
one ``human_scale_ratio``), different smooth-joint-filter residual layouts and
different post-processing (``FeetStabilizer`` vs ``LimbStabilizer`` + contact
processing), so sharing modules would change the numbers of recipes that are
already published. Robots and configs for this pipeline live in
``legacy.robot_registry`` and ``soma_retargeter/configs/<robot>/``.
"""
